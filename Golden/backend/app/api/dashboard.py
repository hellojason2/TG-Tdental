"""Dashboard analytics endpoints used by KPI cards and overview widgets."""

from __future__ import annotations

from datetime import date, datetime, time, timedelta
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from psycopg2.extras import RealDictCursor

from app.core.database import get_conn
from app.core.lookup_sql import pick_column, quote_ident, resolve_table, table_columns
from app.core.middleware import require_auth

router = APIRouter(prefix="/api/reports", tags=["dashboard"])


class SummaryRequest(BaseModel):
    companyId: str | None = None
    dateFrom: date
    dateTo: date


def _to_float(value: Decimal | int | float | None) -> float:
    if value is None:
        return 0.0
    if isinstance(value, Decimal):
        return float(value)
    return float(value)


def _resolve_payment_context(conn) -> dict | None:
    payment_table = resolve_table(
        conn,
        "account_payments",
        "accountpayments",
        "sale_order_payments",
        "saleorderpayments",
        "sale_order_payment",
        "saleorderpayment",
    )
    if not payment_table:
        return None

    payment_cols = table_columns(conn, payment_table)
    amount_col = pick_column(payment_cols, "amount", "price_total", "pricetotal")
    date_col = pick_column(
        payment_cols,
        "payment_date",
        "paymentdate",
        "date",
        "date_created",
        "datecreated",
    )
    if not amount_col or not date_col:
        return None

    journal_col = pick_column(payment_cols, "journal_id", "journalid")
    company_col = pick_column(payment_cols, "company_id", "companyid")
    state_col = pick_column(payment_cols, "state", "status")
    partner_journal_type_col = pick_column(
        payment_cols,
        "partner_journal_type",
        "partnerjournaltype",
    )
    payment_type_col = pick_column(payment_cols, "payment_type", "paymenttype")

    journal_table = None
    journal_id_col = None
    journal_type_col = None
    journal_name_col = None
    join_sql = ""

    if journal_col:
        journal_table = resolve_table(conn, "account_journals", "accountjournals", "journals")
        if journal_table:
            journal_cols = table_columns(conn, journal_table)
            journal_id_col = pick_column(journal_cols, "id")
            journal_type_col = pick_column(journal_cols, "type", "journal_type", "journaltype")
            journal_name_col = pick_column(journal_cols, "name", "display_name", "displayname")
            if journal_id_col and (journal_type_col or journal_name_col):
                join_sql = (
                    f" LEFT JOIN {journal_table.qualified_name} j"
                    f" ON p.{quote_ident(journal_col)} = j.{quote_ident(journal_id_col)}"
                )

    return {
        "payment_table": payment_table,
        "amount_col": amount_col,
        "date_col": date_col,
        "journal_col": journal_col,
        "company_col": company_col,
        "state_col": state_col,
        "partner_journal_type_col": partner_journal_type_col,
        "payment_type_col": payment_type_col,
        "journal_type_col": journal_type_col,
        "journal_name_col": journal_name_col,
        "join_sql": join_sql,
    }


def _date_window(date_from: date, date_to: date) -> tuple[datetime, datetime]:
    start_dt = datetime.combine(date_from, time.min)
    end_dt = datetime.combine(date_to + timedelta(days=1), time.min)
    return start_dt, end_dt


def _build_payment_where(
    ctx: dict,
    *,
    start_dt: datetime,
    end_dt: datetime,
    company_id: str | None,
) -> tuple[str, tuple]:
    conditions = [
        f"p.{quote_ident(ctx['date_col'])} >= %s",
        f"p.{quote_ident(ctx['date_col'])} < %s",
    ]
    params: list = [start_dt, end_dt]

    if company_id:
        if ctx["company_col"]:
            conditions.append(f"p.{quote_ident(ctx['company_col'])}::text = %s")
            params.append(company_id)
        else:
            conditions.append("1 = 0")

    if ctx["state_col"]:
        conditions.append(
            f"COALESCE(LOWER(p.{quote_ident(ctx['state_col'])}::text), '') NOT IN ('cancel', 'cancelled')"
        )

    return " WHERE " + " AND ".join(conditions), tuple(params)


def _channel_expr(ctx: dict) -> str:
    pieces: list[str] = []
    if ctx["journal_type_col"]:
        pieces.append(f"j.{quote_ident(ctx['journal_type_col'])}::text")
    if ctx["partner_journal_type_col"]:
        pieces.append(f"p.{quote_ident(ctx['partner_journal_type_col'])}::text")
    if ctx["payment_type_col"]:
        pieces.append(f"p.{quote_ident(ctx['payment_type_col'])}::text")
    if ctx["journal_name_col"]:
        pieces.append(f"j.{quote_ident(ctx['journal_name_col'])}::text")

    if not pieces:
        return "''"

    return "LOWER(COALESCE(" + ", ".join(pieces) + ", ''))"


def _cash_predicate(channel_expr: str) -> str:
    return (
        f"({channel_expr} LIKE '%%cash%%'"
        f" OR {channel_expr} LIKE '%%tien mat%%')"
    )


def _bank_predicate(channel_expr: str) -> str:
    return (
        f"({channel_expr} LIKE '%%bank%%'"
        f" OR {channel_expr} LIKE '%%ngan hang%%')"
    )


def _build_daily_items(rows: list[dict], start_date: date, end_date: date) -> list[dict]:
    by_day: dict[str, dict] = {}
    cursor = start_date
    while cursor <= end_date:
        key = cursor.isoformat()
        by_day[key] = {
            "date": key,
            "cash": 0.0,
            "bank": 0.0,
            "other": 0.0,
            "totalAmount": 0.0,
        }
        cursor += timedelta(days=1)

    for row in rows:
        row_date = row.get("bucket_date")
        if isinstance(row_date, date):
            key = row_date.isoformat()
        else:
            key = str(row_date or "")[:10]
        if key not in by_day:
            continue

        by_day[key]["cash"] = _to_float(row.get("total_cash"))
        by_day[key]["bank"] = _to_float(row.get("total_bank"))
        by_day[key]["other"] = _to_float(row.get("total_other"))
        by_day[key]["totalAmount"] = _to_float(row.get("total_amount"))

    return [by_day[key] for key in sorted(by_day.keys())]


@router.post("/summary")
async def reports_summary(body: SummaryRequest, _user: dict = Depends(require_auth)):
    """Return dashboard totals by payment channel for a date range."""
    if body.dateFrom > body.dateTo:
        raise HTTPException(status_code=422, detail="dateFrom must be <= dateTo")

    company_id = body.companyId.strip() if body.companyId else None

    try:
        with get_conn() as conn:
            ctx = _resolve_payment_context(conn)
            if not ctx:
                return {
                    "totalCash": 0.0,
                    "totalBank": 0.0,
                    "totalOther": 0.0,
                    "totalAmount": 0.0,
                    "totalAmountYesterday": 0.0,
                }

            start_dt, end_dt = _date_window(body.dateFrom, body.dateTo)
            where_sql, params = _build_payment_where(
                ctx,
                start_dt=start_dt,
                end_dt=end_dt,
                company_id=company_id,
            )

            amount_expr = f"COALESCE(p.{quote_ident(ctx['amount_col'])}, 0)"
            channel_expr = _channel_expr(ctx)
            cash_pred = _cash_predicate(channel_expr)
            bank_pred = _bank_predicate(channel_expr)

            summary_sql = (
                "SELECT "
                f"COALESCE(SUM(CASE WHEN {cash_pred} THEN {amount_expr} ELSE 0 END), 0) AS total_cash, "
                f"COALESCE(SUM(CASE WHEN {bank_pred} THEN {amount_expr} ELSE 0 END), 0) AS total_bank, "
                f"COALESCE(SUM(CASE WHEN NOT ({cash_pred} OR {bank_pred}) THEN {amount_expr} ELSE 0 END), 0) AS total_other, "
                f"COALESCE(SUM({amount_expr}), 0) AS total_amount "
                f"FROM {ctx['payment_table'].qualified_name} p"
                f"{ctx['join_sql']}"
                f"{where_sql}"
            )

            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(summary_sql, params)
                row = dict(cur.fetchone() or {})

                y_start, y_end = _date_window(body.dateTo - timedelta(days=1), body.dateTo - timedelta(days=1))
                y_where_sql, y_params = _build_payment_where(
                    ctx,
                    start_dt=y_start,
                    end_dt=y_end,
                    company_id=company_id,
                )
                yesterday_sql = (
                    "SELECT "
                    f"COALESCE(SUM({amount_expr}), 0) AS total_amount_yesterday "
                    f"FROM {ctx['payment_table'].qualified_name} p"
                    f"{ctx['join_sql']}"
                    f"{y_where_sql}"
                )
                cur.execute(yesterday_sql, y_params)
                y_row = dict(cur.fetchone() or {})

            return {
                "totalCash": _to_float(row.get("total_cash")),
                "totalBank": _to_float(row.get("total_bank")),
                "totalOther": _to_float(row.get("total_other")),
                "totalAmount": _to_float(row.get("total_amount")),
                "totalAmountYesterday": _to_float(y_row.get("total_amount_yesterday")),
            }
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")


@router.get("/revenue-trend")
async def reports_revenue_trend(
    companyId: str | None = Query(default=None),
    days: int = Query(default=7, ge=1, le=90),
    dateTo: date | None = Query(default=None),
    _user: dict = Depends(require_auth),
):
    """Return daily revenue buckets for dashboard trend chart."""
    end_date = dateTo or date.today()
    start_date = end_date - timedelta(days=days - 1)
    company_id = companyId.strip() if companyId else None

    try:
        with get_conn() as conn:
            ctx = _resolve_payment_context(conn)
            if not ctx:
                return {
                    "dateFrom": start_date.isoformat(),
                    "dateTo": end_date.isoformat(),
                    "companyId": company_id,
                    "items": _build_daily_items([], start_date, end_date),
                }

            start_dt, end_dt = _date_window(start_date, end_date)
            where_sql, params = _build_payment_where(
                ctx,
                start_dt=start_dt,
                end_dt=end_dt,
                company_id=company_id,
            )

            amount_expr = f"COALESCE(p.{quote_ident(ctx['amount_col'])}, 0)"
            channel_expr = _channel_expr(ctx)
            cash_pred = _cash_predicate(channel_expr)
            bank_pred = _bank_predicate(channel_expr)

            trend_sql = (
                "SELECT "
                f"DATE(p.{quote_ident(ctx['date_col'])}) AS bucket_date, "
                f"COALESCE(SUM(CASE WHEN {cash_pred} THEN {amount_expr} ELSE 0 END), 0) AS total_cash, "
                f"COALESCE(SUM(CASE WHEN {bank_pred} THEN {amount_expr} ELSE 0 END), 0) AS total_bank, "
                f"COALESCE(SUM(CASE WHEN NOT ({cash_pred} OR {bank_pred}) THEN {amount_expr} ELSE 0 END), 0) AS total_other, "
                f"COALESCE(SUM({amount_expr}), 0) AS total_amount "
                f"FROM {ctx['payment_table'].qualified_name} p"
                f"{ctx['join_sql']}"
                f"{where_sql}"
                " GROUP BY 1"
                " ORDER BY 1 ASC"
            )

            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(trend_sql, params)
                rows = [dict(row) for row in cur.fetchall()]

            return {
                "dateFrom": start_date.isoformat(),
                "dateTo": end_date.isoformat(),
                "companyId": company_id,
                "items": _build_daily_items(rows, start_date, end_date),
            }
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")


@router.get("/overview")
async def reports_overview(
    companyId: str | None = Query(default=None),
    reportDate: date | None = Query(default=None, alias="date"),
    _user: dict = Depends(require_auth),
):
    """Return queue overview stats for the dashboard reception panel."""
    target_date = reportDate or date.today()

    try:
        with get_conn() as conn:
            appointment_table = resolve_table(conn, "appointments", "appointment")
            if not appointment_table:
                return {
                    "waiting": 0,
                    "inProgress": 0,
                    "done": 0,
                    "total": 0,
                    "queue": {
                        "waiting": 0,
                        "inProgress": 0,
                        "done": 0,
                        "all": 0,
                    },
                    "statusDistribution": [
                        {"state": "waiting", "count": 0},
                        {"state": "in_progress", "count": 0},
                        {"state": "done", "count": 0},
                    ],
                }

            cols = table_columns(conn, appointment_table)
            state_col = pick_column(cols, "state", "status", "stage")
            date_col = pick_column(
                cols,
                "date",
                "appointment_date",
                "appointmentdate",
                "date_start",
                "datestart",
            )
            company_col = pick_column(cols, "company_id", "companyid")

            conditions: list[str] = []
            params: list = []

            if date_col:
                day_start, day_end = _date_window(target_date, target_date)
                conditions.append(f"a.{quote_ident(date_col)} >= %s")
                conditions.append(f"a.{quote_ident(date_col)} < %s")
                params.extend([day_start, day_end])

            if companyId:
                if company_col:
                    conditions.append(f"a.{quote_ident(company_col)}::text = %s")
                    params.append(companyId)
                else:
                    conditions.append("1 = 0")

            where_sql = ""
            if conditions:
                where_sql = " WHERE " + " AND ".join(conditions)

            if state_col:
                state_expr = f"LOWER(COALESCE(a.{quote_ident(state_col)}::text, ''))"
                waiting_pred = (
                    f"({state_expr} IN ('waiting', 'pending', 'queued', 'draft')"
                    f" OR {state_expr} LIKE '%%wait%%')"
                )
                in_progress_pred = (
                    f"({state_expr} IN ('in_progress', 'in-progress', 'processing', 'treating')"
                    f" OR {state_expr} LIKE '%%progress%%')"
                )
                done_pred = (
                    f"({state_expr} IN ('done', 'completed', 'success')"
                    f" OR {state_expr} LIKE '%%done%%')"
                )
                sql = (
                    "SELECT "
                    f"COALESCE(SUM(CASE WHEN {waiting_pred} THEN 1 ELSE 0 END), 0)::bigint AS waiting, "
                    f"COALESCE(SUM(CASE WHEN {in_progress_pred} THEN 1 ELSE 0 END), 0)::bigint AS in_progress, "
                    f"COALESCE(SUM(CASE WHEN {done_pred} THEN 1 ELSE 0 END), 0)::bigint AS done, "
                    "COUNT(*)::bigint AS total "
                    f"FROM {appointment_table.qualified_name} a"
                    f"{where_sql}"
                )
            else:
                sql = (
                    "SELECT 0::bigint AS waiting, 0::bigint AS in_progress, "
                    "0::bigint AS done, COUNT(*)::bigint AS total "
                    f"FROM {appointment_table.qualified_name} a"
                    f"{where_sql}"
                )

            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql, tuple(params))
                row = dict(cur.fetchone() or {})

            waiting = int(row.get("waiting") or 0)
            in_progress = int(row.get("in_progress") or 0)
            done = int(row.get("done") or 0)
            total = int(row.get("total") or 0)

            return {
                "waiting": waiting,
                "inProgress": in_progress,
                "done": done,
                "total": total,
                "queue": {
                    "waiting": waiting,
                    "inProgress": in_progress,
                    "done": done,
                    "all": total,
                },
                "statusDistribution": [
                    {"state": "waiting", "count": waiting},
                    {"state": "in_progress", "count": in_progress},
                    {"state": "done", "count": done},
                ],
            }
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")
