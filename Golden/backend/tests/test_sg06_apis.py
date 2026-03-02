import asyncio
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date

import app.api.exam_sessions as exam_sessions_module
import app.api.finance as finance_module
import app.api.hr as hr_module
import app.api.inventory as inventory_module
import app.api.treatments as treatments_module


@dataclass
class FakeTable:
    qualified_name: str


@contextmanager
def _conn_ctx(conn):
    yield conn


class _ExecCursor:
    def __init__(self):
        self.sql_history: list[str] = []
        self.params_history: list[tuple] = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, sql, params=None):
        self.sql_history.append(sql)
        self.params_history.append(tuple(params or ()))


class _ExecConn:
    def __init__(self):
        self.cursor_obj = _ExecCursor()

    def cursor(self, **kwargs):
        del kwargs
        return self.cursor_obj


def test_payments_endpoint_filters_and_pagination(monkeypatch):
    conn = object()
    captured: dict = {}

    monkeypatch.setattr(finance_module, "get_conn", lambda: _conn_ctx(conn))
    monkeypatch.setattr(finance_module, "page_window", lambda **_kwargs: (20, 20))
    monkeypatch.setattr(
        finance_module,
        "resolve_table",
        lambda _conn, *_candidates: FakeTable('"public"."account_payments"'),
    )
    monkeypatch.setattr(
        finance_module,
        "table_columns",
        lambda _conn, _table: (
            "id",
            "name",
            "date",
            "amount",
            "payment_type",
            "journal_name",
            "partner_name",
            "state",
            "company_id",
            "company_name",
        ),
    )

    def fake_paginate(**kwargs):
        captured.update(kwargs)
        return {"offset": 20, "limit": 20, "totalItems": 1, "items": [{"id": "pm-1"}]}

    monkeypatch.setattr(finance_module, "paginate", fake_paginate)

    result = asyncio.run(
        finance_module.list_payments(
            page=2,
            per_page=20,
            companyId="cmp-1",
            partnerId=None,
            paymentType="inbound",
            dateFrom=date(2026, 2, 1),
            dateTo=date(2026, 2, 28),
            state=None,
            _user={"id": "u-1"},
        )
    )

    assert result["totalItems"] == 1
    assert result["items"][0]["id"] == "pm-1"
    assert captured["offset"] == 20
    assert captured["limit"] == 20
    assert captured["params"][0] == "cmp-1"
    assert captured["params"][1] == date(2026, 2, 1)
    assert captured["params"][2] == date(2026, 2, 28)
    assert "paymentType" in captured["query"]


def test_create_payment_inserts_required_fields(monkeypatch):
    conn = _ExecConn()

    monkeypatch.setattr(finance_module, "get_conn", lambda: _conn_ctx(conn))
    monkeypatch.setattr(
        finance_module,
        "resolve_table",
        lambda _conn, *_candidates: FakeTable('"public"."accountpayments"'),
    )
    monkeypatch.setattr(
        finance_module,
        "table_columns",
        lambda _conn, _table: (
            "id",
            "paymentdate",
            "amount",
            "paymenttype",
            "journalid",
            "companyid",
            "name",
            "state",
            "communication",
            "isintercompany",
            "isprepayment",
        ),
    )
    monkeypatch.setattr(
        finance_module,
        "_resolve_default_journal",
        lambda _conn, **_kwargs: {"id": "journal-001", "companyId": "cmp-01", "name": "Tiền mặt"},
    )

    result = asyncio.run(
        finance_module.create_payment(
            finance_module.PaymentCreateRequest(
                date=date(2026, 3, 1),
                paymentType="outbound",
                method="cash",
                category="salary",
                partnerName="Nguyen Van A",
                amount=1250000,
                note="Tam ung",
            ),
            _user={"id": "user-01"},
        )
    )

    assert result["paymentType"] == "outbound"
    assert result["journalId"] == "journal-001"
    assert result["companyId"] == "cmp-01"
    assert result["state"] == "draft"
    assert result["name"].startswith("MANUAL.PMT/")
    assert conn.cursor_obj.sql_history
    assert conn.cursor_obj.sql_history[0].startswith("INSERT INTO")
    assert "journalid" in conn.cursor_obj.sql_history[0]
    assert "journal-001" in conn.cursor_obj.params_history[0]


def test_create_hr_advance_maps_to_payment_create(monkeypatch):
    conn = object()
    captured: dict = {}

    monkeypatch.setattr(hr_module, "get_conn", lambda: _conn_ctx(conn))

    def fake_create_payment_record(conn_obj, payload, user):
        captured["conn"] = conn_obj
        captured["payload"] = payload
        captured["user"] = user
        return {
            "id": "payment-001",
            "date": "2026-03-01T00:00:00",
            "state": "draft",
            "companyId": "cmp-01",
        }

    monkeypatch.setattr(hr_module, "create_payment_record", fake_create_payment_record)

    result = asyncio.run(
        hr_module.create_hr_advance(
            hr_module.HrAdvanceCreateRequest(
                date=date(2026, 3, 1),
                employeeName="Employee A",
                type="advance",
                method="cash",
                amount=550000,
                reason="Tam ung thang",
                companyId="cmp-01",
            ),
            _user={"id": "admin-1"},
        )
    )

    assert captured["conn"] is conn
    assert captured["payload"].paymentType == "outbound"
    assert captured["payload"].partnerName == "Employee A"
    assert captured["payload"].amount == 550000
    assert captured["payload"].companyId == "cmp-01"
    assert result["paymentId"] == "payment-001"
    assert result["employeeName"] == "Employee A"


def test_dot_khams_partner_filter(monkeypatch):
    conn = object()
    captured: dict = {}

    monkeypatch.setattr(exam_sessions_module, "get_conn", lambda: _conn_ctx(conn))
    monkeypatch.setattr(exam_sessions_module, "page_window", lambda **_kwargs: (0, 20))
    monkeypatch.setattr(
        exam_sessions_module,
        "resolve_table",
        lambda _conn, *_candidates: FakeTable('"public"."dot_khams"'),
    )
    monkeypatch.setattr(
        exam_sessions_module,
        "table_columns",
        lambda _conn, _table: (
            "id",
            "name",
            "date",
            "state",
            "doctor_name",
            "company_name",
            "reason",
            "partner_id",
            "company_id",
        ),
    )

    def fake_paginate(**kwargs):
        captured.update(kwargs)
        return {"offset": 0, "limit": 20, "totalItems": 1, "items": [{"id": "dk-1"}]}

    monkeypatch.setattr(exam_sessions_module, "paginate", fake_paginate)

    result = asyncio.run(
        exam_sessions_module.list_dot_khams(
            page=1,
            per_page=20,
            partnerId="partner-001",
            companyId=None,
            dateFrom=None,
            dateTo=None,
            state=None,
            _user={"id": "u-1"},
        )
    )

    assert result["items"][0]["id"] == "dk-1"
    assert captured["params"] == ("partner-001",)
    assert '"partnerId"' in captured["query"]


def test_sale_orders_list_with_search_and_state(monkeypatch):
    conn = object()
    captured: dict = {}

    monkeypatch.setattr(treatments_module, "get_conn", lambda: _conn_ctx(conn))
    monkeypatch.setattr(treatments_module, "page_window", lambda **_kwargs: (0, 20))
    monkeypatch.setattr(
        treatments_module,
        "_resolve_sale_order_meta",
        lambda _conn: {
            "table": FakeTable('"public"."sale_orders"'),
            "id_col": "id",
            "name_col": "name",
            "date_col": "date_order",
            "state_col": "state",
            "amount_col": "amount_total",
            "partner_id_col": "partner_id",
            "partner_name_col": "partner_name",
            "doctor_id_col": "doctor_id",
            "doctor_name_col": "doctor_name",
            "company_id_col": "company_id",
            "company_name_col": "company_name",
        },
    )

    def fake_paginate(**kwargs):
        captured.update(kwargs)
        return {"offset": 0, "limit": 20, "totalItems": 2, "items": [{"id": "so-1"}]}

    monkeypatch.setattr(treatments_module, "paginate", fake_paginate)

    result = asyncio.run(
        treatments_module.list_sale_orders(
            page=1,
            per_page=20,
            search="Nguyen",
            companyId="cmp-1",
            partnerId="pt-1",
            state="sale",
            dateFrom=None,
            dateTo=None,
            _user={"id": "u-1"},
        )
    )

    assert result["totalItems"] == 2
    assert captured["params"][0] == "%Nguyen%"
    assert captured["params"][1] == "%Nguyen%"
    assert captured["params"][-3:] == ("cmp-1", "pt-1", "sale")
    assert '"amountTotal"' in captured["query"]


class _SingleRowCursor:
    def __init__(self, row):
        self._row = row
        self.sql = ""
        self.params = ()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, sql, params=None):
        self.sql = sql
        self.params = params or ()

    def fetchone(self):
        return self._row


class _SingleRowConn:
    def __init__(self, row):
        self.cursor_obj = _SingleRowCursor(row=row)

    def cursor(self, **kwargs):
        del kwargs
        return self.cursor_obj


class _RowsCursor:
    def __init__(self, rows):
        self._rows = rows
        self.sql = ""
        self.params = ()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, sql, params=None):
        self.sql = sql
        self.params = params or ()

    def fetchall(self):
        return self._rows


class _RowsConn:
    def __init__(self, rows):
        self.cursor_obj = _RowsCursor(rows=rows)

    def cursor(self, **kwargs):
        del kwargs
        return self.cursor_obj


def test_sale_order_detail_returns_nested_lines(monkeypatch):
    conn = _SingleRowConn(
        {
            "id": "so-100",
            "name": "SO100",
            "date": "2026-02-20",
            "state": "sale",
            "amountTotal": 1200,
            "partnerId": "pt-1",
            "partnerName": "Patient A",
            "doctorId": "dr-1",
            "doctorName": "Doctor B",
            "companyId": "cmp-1",
            "companyName": "Branch 1",
        }
    )
    monkeypatch.setattr(treatments_module, "get_conn", lambda: _conn_ctx(conn))
    monkeypatch.setattr(
        treatments_module,
        "_resolve_sale_order_meta",
        lambda _conn: {
            "table": FakeTable('"public"."sale_orders"'),
            "id_col": "id",
            "name_col": "name",
            "date_col": "date_order",
            "state_col": "state",
            "amount_col": "amount_total",
            "partner_id_col": "partner_id",
            "partner_name_col": "partner_name",
            "doctor_id_col": "doctor_id",
            "doctor_name_col": "doctor_name",
            "company_id_col": "company_id",
            "company_name_col": "company_name",
        },
    )
    monkeypatch.setattr(
        treatments_module,
        "_load_sale_order_lines",
        lambda conn, sale_order_id: [
            {"id": "line-1", "productName": "Service A", "qty": 1, "subtotal": 1200}
        ],
    )

    result = asyncio.run(
        treatments_module.get_sale_order_detail("so-100", _user={"id": "u-1"})
    )

    assert result["id"] == "so-100"
    assert len(result["lines"]) == 1


def test_hr_timekeeping_handles_boolean_overtime(monkeypatch):
    conn = _RowsConn(
        rows=[
            {
                "id": "tk-1",
                "date": date(2026, 2, 15),
                "employeeId": "emp-1",
                "employeeName": "Nguyen Van A",
                "hours": 8,
                "overtime": 1,
                "state": "done",
            }
        ]
    )

    monkeypatch.setattr(
        hr_module,
        "resolve_table",
        lambda _conn, *_candidates: FakeTable('"public"."chamcongs"'),
    )
    monkeypatch.setattr(
        hr_module,
        "table_columns",
        lambda _conn, _table: (
            "id",
            "employee_id",
            "employee_name",
            "date",
            "hours",
            "overtime",
            "state",
            "company_id",
        ),
    )
    monkeypatch.setattr(
        hr_module,
        "_table_column_data_types",
        lambda _conn, _table: {"hours": "numeric", "overtime": "boolean"},
    )

    result = hr_module._load_timekeeping(
        conn,
        date_from=date(2026, 2, 1),
        date_to=date(2026, 2, 28),
        company_id="cmp-1",
    )

    assert result[0]["id"] == "tk-1"
    assert 'CASE WHEN COALESCE(t."overtime", FALSE)' in conn.cursor_obj.sql
    assert conn.cursor_obj.params == (date(2026, 2, 1), date(2026, 2, 28), "cmp-1")


class _ReportCursor:
    def __init__(self):
        self.mode = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, sql, params=None):
        del params
        self.mode = "detail" if "GROUP BY" in sql else "totals"

    def fetchall(self):
        if self.mode == "detail":
            return [
                {
                    "productId": "prd-1",
                    "productName": "Material A",
                    "incomingQty": 15,
                    "outgoingQty": 4,
                    "balanceQty": 11,
                }
            ]
        return []

    def fetchone(self):
        if self.mode == "totals":
            return {"incoming": 15, "outgoing": 4}
        return None


class _ReportConn:
    def cursor(self, **kwargs):
        del kwargs
        return _ReportCursor()


def test_stock_report_returns_totals(monkeypatch):
    conn = _ReportConn()
    monkeypatch.setattr(inventory_module, "get_conn", lambda: _conn_ctx(conn))
    monkeypatch.setattr(
        inventory_module,
        "_stock_move_context",
        lambda _conn: {
            "table": FakeTable('"public"."stock_moves"'),
            "id_col": "id",
            "date_col": "date",
            "company_id_col": "company_id",
            "product_id_col": "product_id",
            "picking_type_col": "picking_type",
            "picking_join_type_col": None,
            "joins": "",
            "product_name_expr": "m.\"product_name\"",
            "company_name_expr": "m.\"company_name\"",
            "qty_expr": "COALESCE(m.\"quantity_done\", 0)",
            "qty_abs_expr": "ABS(COALESCE(m.\"quantity_done\", 0))",
            "picking_type_expr": "LOWER(COALESCE(m.\"picking_type\"::text, ''))",
            "reference_expr": "m.\"reference\"",
            "incoming_condition": "LOWER(COALESCE(m.\"picking_type\"::text, '')) = 'incoming'",
            "outgoing_condition": "LOWER(COALESCE(m.\"picking_type\"::text, '')) = 'outgoing'",
            "state_col": "state",
        },
    )
    monkeypatch.setattr(
        inventory_module,
        "_stock_move_filters",
        lambda **_kwargs: (['m."company_id"::text = %s'], ["cmp-1"]),
    )

    result = asyncio.run(
        inventory_module.stock_report(
            inventory_module.StockReportRequest(
                companyId="cmp-1",
                dateFrom=date(2026, 2, 1),
                dateTo=date(2026, 2, 28),
            ),
            _user={"id": "u-1"},
        )
    )

    assert result["companyId"] == "cmp-1"
    assert result["totals"]["incomingQty"] == 15
    assert result["totals"]["outgoingQty"] == 4
    assert result["totals"]["balanceQty"] == 11
    assert result["totalItems"] == 1


def test_stock_pickings_filter_by_joined_picking_type(monkeypatch):
    conn = object()
    captured: dict = {}

    monkeypatch.setattr(inventory_module, "get_conn", lambda: _conn_ctx(conn))
    monkeypatch.setattr(inventory_module, "page_window", lambda **_kwargs: (0, 20))

    def fake_resolve_table(_conn, *candidates):
        first = candidates[0]
        if first in {"stock_pickings", "stockpicking", "stockpickings"}:
            return FakeTable('"public"."stock_pickings"')
        if first in {"stock_picking_types", "stockpickingtypes", "stock_picking_type"}:
            return FakeTable('"public"."stock_picking_types"')
        return None

    def fake_columns(_conn, table):
        if table.qualified_name.endswith('"stock_pickings"'):
            return ("id", "name", "date", "picking_type_id", "state", "company_id")
        if table.qualified_name.endswith('"stock_picking_types"'):
            return ("id", "code", "name")
        return ()

    monkeypatch.setattr(inventory_module, "resolve_table", fake_resolve_table)
    monkeypatch.setattr(inventory_module, "table_columns", fake_columns)

    def fake_paginate(**kwargs):
        captured.update(kwargs)
        return {"offset": 0, "limit": 20, "totalItems": 1, "items": [{"id": "pk-1"}]}

    monkeypatch.setattr(inventory_module, "paginate", fake_paginate)

    result = asyncio.run(
        inventory_module.list_stock_pickings(
            page=1,
            per_page=20,
            companyId=None,
            pickingType="incoming",
            state=None,
            dateFrom=None,
            dateTo=None,
            _user={"id": "u-1"},
        )
    )

    assert result["items"][0]["id"] == "pk-1"
    assert captured["params"] == ("incoming",)
    assert "spt." in captured["query"]
