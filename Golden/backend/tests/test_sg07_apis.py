import asyncio
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date, datetime, timedelta

import app.api.categories as categories_module
import app.api.commission as commission_module
import app.api.dashboard as dashboard_module
import app.api.reports as reports_module
import app.api.tasks as tasks_module


@dataclass
class FakeTable:
    qualified_name: str


@contextmanager
def _conn_ctx(conn):
    yield conn


class RecordingCursor:
    def __init__(self, *, rows=None, row=None):
        self.rows = rows if rows is not None else []
        self.row = row
        self.sql = ""
        self.params = ()
        self.rowcount = 1

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, sql, params=None):
        self.sql = sql
        self.params = params or ()

    def fetchall(self):
        return self.rows

    def fetchone(self):
        if self.row is None:
            return None
        return self.row


class RecordingConn:
    def __init__(self, *, rows=None, row=None):
        self.cursor_obj = RecordingCursor(rows=rows, row=row)

    def cursor(self, **kwargs):
        del kwargs
        return self.cursor_obj


def test_summary_returns_zero_when_source_tables_missing(monkeypatch):
    conn = object()
    monkeypatch.setattr(dashboard_module, "get_conn", lambda: _conn_ctx(conn))
    monkeypatch.setattr(dashboard_module, "resolve_table", lambda *_args, **_kwargs: None)

    result = asyncio.run(
        dashboard_module.reports_summary(
            dashboard_module.SummaryRequest(
                companyId="cmp-1",
                dateFrom=date(2026, 2, 1),
                dateTo=date(2026, 2, 1),
            ),
            _user={"id": "u-1"},
        )
    )

    assert result == {
        "totalCash": 0.0,
        "totalBank": 0.0,
        "totalOther": 0.0,
        "totalAmount": 0.0,
        "totalAmountYesterday": 0.0,
    }


def test_daily_report_applies_date_company_filters(monkeypatch):
    conn = object()
    captured = {}

    monkeypatch.setattr(reports_module, "get_conn", lambda: _conn_ctx(conn))
    monkeypatch.setattr(reports_module, "page_window", lambda **_kwargs: (0, 20))

    def fake_resolve_table(_conn, *candidates):
        if "account_payments" in candidates or "accountpayments" in candidates:
            return FakeTable('"public"."accountpayments"')
        if "account_journals" in candidates or "accountjournals" in candidates:
            return FakeTable('"public"."accountjournals"')
        return None

    monkeypatch.setattr(reports_module, "resolve_table", fake_resolve_table)

    def fake_columns(_conn, table):
        if "accountpayments" in table.qualified_name:
            return (
                "id",
                "companyid",
                "paymentdate",
                "journalid",
                "state",
                "amount",
                "partnerjournaltype",
                "paymenttype",
            )
        return ("id", "type", "name")

    monkeypatch.setattr(reports_module, "table_columns", fake_columns)

    def fake_paginate(**kwargs):
        captured.update(kwargs)
        return {"offset": 0, "limit": 20, "totalItems": 0, "items": []}

    monkeypatch.setattr(reports_module, "paginate", fake_paginate)

    _ = asyncio.run(
        reports_module.report_daily(
            dateFrom=date(2026, 2, 1),
            dateTo=date(2026, 2, 28),
            companyId="cmp-1",
            page=1,
            per_page=20,
            offset=None,
            limit=None,
            _user={"id": "u-1"},
        )
    )

    assert "GROUP BY" in captured["query"]
    assert captured["params"][2] == "cmp-1"
    assert captured["params"][0] == date(2026, 2, 1)
    assert captured["params"][1] == date(2026, 2, 28)


def test_task_counts_returns_stage_totals(monkeypatch):
    conn = RecordingConn(rows=[{"stage": 1, "total": 2}, {"stage": 3, "total": 5}])

    monkeypatch.setattr(tasks_module, "get_conn", lambda: _conn_ctx(conn))
    monkeypatch.setattr(tasks_module, "_resolve_tasks_table", lambda _conn: FakeTable('"public"."app_tasks"'))
    monkeypatch.setattr(
        tasks_module,
        "table_columns",
        lambda _conn, _table: (
            "id",
            "title",
            "stage",
            "company_id",
            "is_deleted",
            "date_created",
        ),
    )

    result = asyncio.run(
        tasks_module.task_counts(
            companyId="cmp-1",
            dateCreateFrom=date(2026, 2, 1),
            dateCreateTo=date(2026, 2, 28),
            _user={"id": "u-1"},
        )
    )

    assert result == [{"stage": 1, "total": 2}, {"stage": 3, "total": 5}]
    assert "GROUP BY" in conn.cursor_obj.sql


def test_task_crud_smoke(monkeypatch):
    conn = RecordingConn()

    monkeypatch.setattr(tasks_module, "get_conn", lambda: _conn_ctx(conn))
    monkeypatch.setattr(tasks_module, "_resolve_tasks_table", lambda _conn: FakeTable('"public"."app_tasks"'))
    monkeypatch.setattr(
        tasks_module,
        "table_columns",
        lambda _conn, _table: (
            "id",
            "title",
            "description",
            "stage",
            "priority",
            "active",
            "category_id",
            "company_id",
            "partner_id",
            "date_assign",
            "date_start",
            "date_done",
            "date_expire",
            "cancel_reason",
            "result",
            "note",
            "ref_code",
            "notify_count",
            "is_deleted",
            "date_created",
            "last_updated",
        ),
    )

    monkeypatch.setattr(
        tasks_module,
        "_fetch_task_by_id",
        lambda _conn, _table, _fields, task_id: {
            "id": task_id,
            "title": "Task title",
            "stage": 1,
        },
    )

    created = asyncio.run(
        tasks_module.create_task(
            tasks_module.TaskCreateRequest(title="Task title", stage=1),
            user={"id": "u-1"},
        )
    )
    assert created["title"] == "Task title"

    updated = asyncio.run(
        tasks_module.update_task(
            tasks_module.TaskUpdateRequest(stage=2),
            task_id=created["id"],
            user={"id": "u-1"},
        )
    )
    assert updated["id"] == created["id"]

    deleted = asyncio.run(
        tasks_module.delete_task(
            task_id=created["id"],
            user={"id": "u-1"},
        )
    )
    assert deleted == {"id": created["id"], "deleted": True}


def test_commission_list_filters_and_pagination(monkeypatch):
    conn = object()
    captured = {}

    monkeypatch.setattr(commission_module, "get_conn", lambda: _conn_ctx(conn))
    monkeypatch.setattr(commission_module, "page_window", lambda **_kwargs: (0, 20))
    monkeypatch.setattr(
        commission_module,
        "_resolve_commission_table",
        lambda _conn: FakeTable('"public"."commissions"'),
    )
    monkeypatch.setattr(
        commission_module,
        "table_columns",
        lambda _conn, _table: (
            "id",
            "name",
            "type",
            "company_id",
            "active",
            "description",
            "date_created",
            "last_updated",
        ),
    )

    def fake_paginate(**kwargs):
        captured.update(kwargs)
        return {"offset": 0, "limit": 20, "totalItems": 0, "items": []}

    monkeypatch.setattr(commission_module, "paginate", fake_paginate)

    _ = asyncio.run(
        commission_module.list_commissions(
            page=1,
            per_page=20,
            offset=None,
            limit=None,
            search="doctor",
            type="doctor",
            companyId="cmp-1",
            active=True,
            _user={"id": "u-1"},
        )
    )

    assert captured["params"] == ("%doctor%", "%doctor%", "doctor", "cmp-1", True)
    assert "companyId" in captured["query"]


def test_commission_crud_smoke(monkeypatch):
    conn = RecordingConn()

    monkeypatch.setattr(commission_module, "get_conn", lambda: _conn_ctx(conn))
    monkeypatch.setattr(
        commission_module,
        "_resolve_commission_table",
        lambda _conn: FakeTable('"public"."app_commissions"'),
    )
    monkeypatch.setattr(
        commission_module,
        "table_columns",
        lambda _conn, _table: (
            "id",
            "name",
            "type",
            "company_id",
            "active",
            "description",
            "date_created",
            "last_updated",
        ),
    )
    monkeypatch.setattr(
        commission_module,
        "_fetch_commission_by_id",
        lambda _conn, _table, _fields, commission_id: {
            "id": commission_id,
            "name": "Rule 01",
            "active": True,
        },
    )

    created = asyncio.run(
        commission_module.create_commission(
            commission_module.CommissionCreateRequest(name="Rule 01", type="doctor"),
            user={"id": "u-1"},
        )
    )
    assert created["name"] == "Rule 01"

    updated = asyncio.run(
        commission_module.update_commission(
            commission_module.CommissionUpdateRequest(active=False),
            commission_id=created["id"],
            user={"id": "u-1"},
        )
    )
    assert updated["id"] == created["id"]

    deleted = asyncio.run(
        commission_module.delete_commission(
            commission_id=created["id"],
            user={"id": "u-1"},
        )
    )
    assert deleted == {"id": created["id"], "deleted": True}


def test_reports_overview_sql_escapes_percent_patterns(monkeypatch):
    conn = RecordingConn(row={"waiting": 2, "in_progress": 1, "done": 3, "total": 6})

    monkeypatch.setattr(dashboard_module, "get_conn", lambda: _conn_ctx(conn))
    monkeypatch.setattr(
        dashboard_module,
        "resolve_table",
        lambda *_args, **_kwargs: FakeTable('"public"."appointments"'),
    )
    monkeypatch.setattr(
        dashboard_module,
        "table_columns",
        lambda _conn, _table: ("id", "state", "date", "company_id"),
    )

    result = asyncio.run(
        dashboard_module.reports_overview(
            companyId="cmp-1",
            reportDate=date(2026, 2, 1),
            _user={"id": "u-1"},
        )
    )

    assert result["total"] == 6
    assert "LIKE '%%wait%%'" in conn.cursor_obj.sql
    assert "LIKE '%%progress%%'" in conn.cursor_obj.sql
    assert "LIKE '%%done%%'" in conn.cursor_obj.sql

    # Ensure pyformat placeholder interpolation is valid (no bare % tokens).
    conn.cursor_obj.sql % tuple("x" for _ in conn.cursor_obj.params)


def test_manage_categories_services_sql_escapes_percent_patterns(monkeypatch):
    conn = object()
    captured: dict = {}

    monkeypatch.setattr(categories_module, "get_conn", lambda: _conn_ctx(conn))
    monkeypatch.setattr(categories_module, "page_window", lambda **_kwargs: (0, 20))
    monkeypatch.setattr(
        categories_module,
        "_manage_context",
        lambda _conn, _spec: {
            "table": FakeTable('"public"."products"'),
            "id_col": "id",
            "name_col": "name",
            "code_col": "default_code",
            "type_col": "type",
            "active_col": "active",
            "company_id_col": "company_id",
            "company_name_col": None,
            "job_col": None,
            "updated_col": None,
        },
    )

    def fake_paginate(**kwargs):
        captured.update(kwargs)
        # Ensure pyformat placeholder interpolation is valid (no bare % tokens).
        kwargs["query"] % tuple("x" for _ in kwargs["params"])
        return {"offset": 0, "limit": 20, "totalItems": 0, "items": []}

    monkeypatch.setattr(categories_module, "paginate", fake_paginate)

    result = asyncio.run(
        categories_module.list_manage_categories(
            kind="services",
            page=1,
            per_page=20,
            offset=None,
            limit=None,
            search="",
            companyId="cmp-1",
            _user={"id": "u-1"},
        )
    )

    assert result["totalItems"] == 0
    assert "LIKE '%%service%%'" in captured["query"]
