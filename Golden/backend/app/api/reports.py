"""Business report endpoints for admin report tabs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.database import get_conn
from app.core.lookup_sql import (
    empty_page,
    page_window,
    pick_column,
    quote_ident,
    resolve_table,
    table_columns,
)
from app.core.middleware import require_auth
from app.core.pagination import paginate

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/revenue-trend")
async def report_revenue_trend(
    dateFrom: date | None = Query(default=None),
    dateTo: date | None = Query(default=None),
    companyId: str | None = Query(default=None),
    _user: dict = Depends(require_auth),
):
    """Revenue trend data for charts."""
    date_from, date_to = _resolve_window(dateFrom, dateTo)
    try:
        with get_conn() as conn:
            ctx = _payment_context(conn)
            if not ctx:
                return {"items": []}

            where: list[str] = []
            params: list = []
            _append_date_filter(
                where, params,
                expr=f"p.{quote_ident(ctx.date_col)}",
                date_from=date_from, date_to=date_to,
            )
            if companyId and ctx.company_id_col:
                where.append(f"p.{quote_ident(ctx.company_id_col)}::text = %s")
                params.append(companyId)

            where_sql = " WHERE " + " AND ".join(where) if where else ""
            amount_expr = f"COALESCE(p.{quote_ident(ctx.amount_col)}, 0)"
            date_expr = f"p.{quote_ident(ctx.date_col)}::date"

            sql = (
                f"SELECT {date_expr} AS report_date, "
                f"COALESCE(SUM(CASE WHEN {amount_expr} > 0 THEN {amount_expr} ELSE 0 END), 0) AS income, "
                f"COALESCE(SUM(CASE WHEN {amount_expr} < 0 THEN ABS({amount_expr}) ELSE 0 END), 0) AS expense, "
                f"COALESCE(SUM({amount_expr}), 0) AS revenue "
                f"FROM {ctx.table.qualified_name} p{where_sql} "
                f"GROUP BY {date_expr} ORDER BY {date_expr} ASC"
            )
            cur = conn.cursor()
            cur.execute(sql, params)
            cols = [d[0] for d in cur.description]
            items = []
            for row in cur.fetchall():
                r = dict(zip(cols, row))
                items.append({
                    "date": str(r.get("report_date", "")),
                    "revenue": float(r.get("revenue", 0)),
                    "income": float(r.get("income", 0)),
                    "expense": float(r.get("expense", 0)),
                })
            cur.close()
            return {"items": items}
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")


@router.get("/appointments")
async def report_appointments(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=0, le=500),
    offset: int | None = Query(default=None, ge=0),
    limit: int | None = Query(default=None, ge=0, le=5000),
    dateFrom: date | None = Query(default=None),
    dateTo: date | None = Query(default=None),
    companyId: str | None = Query(default=None),
    _user: dict = Depends(require_auth),
):
    """Appointment report grouped by status."""
    resolved_offset, resolved_limit = page_window(
        page=page, per_page=per_page, offset=offset, limit=limit, default_limit=20,
    )
    date_from, date_to = _resolve_window(dateFrom, dateTo)
    try:
        with get_conn() as conn:
            from app.core.lookup_sql import resolve_table, table_columns, pick_column
            apt_table = resolve_table(conn, "appointments", "appointment")
            if not apt_table:
                return empty_page(resolved_offset, resolved_limit)

            cols = table_columns(conn, apt_table)
            state_col = pick_column(cols, "state", "status", "stage")
            date_col = pick_column(cols, "date", "appointment_date", "date_start", "created_at")
            company_col = pick_column(cols, "company_id", "companyid")

            if not state_col or not date_col:
                return empty_page(resolved_offset, resolved_limit)

            where: list[str] = []
            params: list = []
            _append_date_filter(where, params, expr=f"a.{quote_ident(date_col)}", date_from=date_from, date_to=date_to)
            if companyId and company_col:
                where.append(f"a.{quote_ident(company_col)}::text = %s")
                params.append(companyId)

            where_sql = " WHERE " + " AND ".join(where) if where else ""
            query = (
                f"SELECT COALESCE(a.{quote_ident(state_col)}::text, 'unknown') AS state, "
                f"COUNT(*)::bigint AS count "
                f"FROM {apt_table.qualified_name} a{where_sql} "
                f"GROUP BY a.{quote_ident(state_col)} "
                f"ORDER BY count DESC"
            )
            return paginate(query=query, params=tuple(params), conn=conn, offset=resolved_offset, limit=resolved_limit)
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")


@router.get("/reception")
async def report_reception(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=0, le=500),
    offset: int | None = Query(default=None, ge=0),
    limit: int | None = Query(default=None, ge=0, le=5000),
    dateFrom: date | None = Query(default=None),
    dateTo: date | None = Query(default=None),
    companyId: str | None = Query(default=None),
    _user: dict = Depends(require_auth),
):
    """Reception report grouped by hour."""
    resolved_offset, resolved_limit = page_window(
        page=page, per_page=per_page, offset=offset, limit=limit, default_limit=24,
    )
    date_from, date_to = _resolve_window(dateFrom, dateTo)
    try:
        with get_conn() as conn:
            apt_table = resolve_table(conn, "appointments", "appointment")
            if not apt_table:
                return empty_page(resolved_offset, resolved_limit)

            cols = table_columns(conn, apt_table)
            date_col = pick_column(cols, "date", "appointment_date", "date_start", "created_at")
            company_col = pick_column(cols, "company_id", "companyid")

            if not date_col:
                return empty_page(resolved_offset, resolved_limit)

            where: list[str] = []
            params: list = []
            _append_date_filter(where, params, expr=f"a.{quote_ident(date_col)}", date_from=date_from, date_to=date_to)
            if companyId and company_col:
                where.append(f"a.{quote_ident(company_col)}::text = %s")
                params.append(companyId)

            where_sql = " WHERE " + " AND ".join(where) if where else ""
            query = (
                f"SELECT EXTRACT(HOUR FROM a.{quote_ident(date_col)})::int AS hour, "
                f"COUNT(*)::bigint AS count "
                f"FROM {apt_table.qualified_name} a{where_sql} "
                f"GROUP BY 1 ORDER BY 1 ASC"
            )
            return paginate(query=query, params=tuple(params), conn=conn, offset=resolved_offset, limit=resolved_limit)
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")


@dataclass()
class PaymentContext:
    table: object
    amount_col: str
    date_col: str
    partner_id_col: str | None
    partner_name_col: str | None
    company_id_col: str | None
    company_name_col: str | None


@dataclass()
class SaleOrderContext:
    table: object
    id_col: str
    amount_col: str | None
    date_col: str | None
    partner_id_col: str | None
    partner_name_col: str | None
    doctor_id_col: str | None
    doctor_name_col: str | None
    company_id_col: str | None
    company_name_col: str | None


def _resolve_window(date_from: date | None, date_to: date | None) -> tuple[date, date]:
    end = date_to or date.today()
    start = date_from or (end - timedelta(days=29))
    if start > end:
        raise HTTPException(status_code=422, detail="dateFrom must be <= dateTo")
    return start, end


def _payment_context(conn) -> PaymentContext | None:
    payment_table = resolve_table(
        conn,
        "account_payments",
        "accountpayments",
        "accountpayment",
        "sale_order_payments",
        "saleorderpayments",
        "customer_receipts",
        "customerreceipts",
        "payments",
    )
    if not payment_table:
        return None

    cols = table_columns(conn, payment_table)
    amount_col = pick_column(cols, "amount", "amount_total", "payment_amount", "total")
    date_col = pick_column(
        cols,
        "payment_date",
        "paymentdate",
        "date",
        "created_at",
        "created_date",
        "createdon",
    )
    if not amount_col or not date_col:
        return None

    return PaymentContext(
        table=payment_table,
        amount_col=amount_col,
        date_col=date_col,
        partner_id_col=pick_column(cols, "partner_id", "partnerid", "customer_id", "customerid"),
        partner_name_col=pick_column(
            cols,
            "partner_name",
            "partnername",
            "customer_name",
            "customername",
        ),
        company_id_col=pick_column(cols, "company_id", "companyid"),
        company_name_col=pick_column(cols, "company_name", "companyname"),
    )


def _sale_order_context(conn) -> SaleOrderContext | None:
    order_table = resolve_table(conn, "sale_orders", "saleorder", "saleorders", "sale_order")
    if not order_table:
        return None

    cols = table_columns(conn, order_table)
    id_col = pick_column(cols, "id")
    if not id_col:
        return None

    return SaleOrderContext(
        table=order_table,
        id_col=id_col,
        amount_col=pick_column(cols, "amount_total", "total", "amount"),
        date_col=pick_column(cols, "date_order", "date", "created_at", "created_date"),
        partner_id_col=pick_column(cols, "partner_id", "partnerid", "customer_id", "customerid"),
        partner_name_col=pick_column(
            cols,
            "partner_name",
            "partnername",
            "customer_name",
            "customername",
        ),
        doctor_id_col=pick_column(
            cols,
            "doctor_id",
            "doctorid",
            "employee_id",
            "employeeid",
            "staff_id",
            "staffid",
        ),
        doctor_name_col=pick_column(
            cols,
            "doctor_name",
            "doctorname",
            "employee_name",
            "employeename",
            "staff_name",
            "staffname",
        ),
        company_id_col=pick_column(cols, "company_id", "companyid"),
        company_name_col=pick_column(cols, "company_name", "companyname"),
    )


def _append_date_filter(
    where_clauses: list[str],
    params: list,
    *,
    expr: str,
    date_from: date,
    date_to: date,
) -> None:
    where_clauses.append(f"{expr}::date >= %s")
    where_clauses.append(f"{expr}::date <= %s")
    params.extend([date_from, date_to])


@router.get("/daily")
async def report_daily(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=0, le=500),
    offset: int | None = Query(default=None, ge=0),
    limit: int | None = Query(default=None, ge=0, le=5000),
    dateFrom: date | None = Query(default=None),
    dateTo: date | None = Query(default=None),
    companyId: str | None = Query(default=None),
    _user: dict = Depends(require_auth),
):
    resolved_offset, resolved_limit = page_window(
        page=page,
        per_page=per_page,
        offset=offset,
        limit=limit,
        default_limit=20,
    )
    date_from, date_to = _resolve_window(dateFrom, dateTo)

    try:
        with get_conn() as conn:
            ctx = _payment_context(conn)
            if not ctx:
                return empty_page(resolved_offset, resolved_limit)

            where: list[str] = []
            params: list = []
            _append_date_filter(
                where,
                params,
                expr=f"p.{quote_ident(ctx.date_col)}",
                date_from=date_from,
                date_to=date_to,
            )

            if companyId:
                if not ctx.company_id_col:
                    return empty_page(resolved_offset, resolved_limit)
                where.append(f"p.{quote_ident(ctx.company_id_col)}::text = %s")
                params.append(companyId)

            where_sql = ""
            if where:
                where_sql = " WHERE " + " AND ".join(where)

            date_expr = f"p.{quote_ident(ctx.date_col)}::date"
            amount_expr = f"COALESCE(p.{quote_ident(ctx.amount_col)}, 0)"
            query = (
                "SELECT "
                f"{date_expr} AS \"reportDate\", "
                f"COALESCE(SUM({amount_expr}), 0) AS \"totalAmount\", "
                "COUNT(*)::bigint AS \"paymentCount\" "
                f"FROM {ctx.table.qualified_name} p"
                f"{where_sql} "
                f"GROUP BY {date_expr} "
                f"ORDER BY {date_expr} DESC"
            )

            return paginate(
                query=query,
                params=tuple(params),
                conn=conn,
                offset=resolved_offset,
                limit=resolved_limit,
            )
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")


@router.get("/services")
async def report_services(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=0, le=500),
    offset: int | None = Query(default=None, ge=0),
    limit: int | None = Query(default=None, ge=0, le=5000),
    dateFrom: date | None = Query(default=None),
    dateTo: date | None = Query(default=None),
    companyId: str | None = Query(default=None),
    _user: dict = Depends(require_auth),
):
    resolved_offset, resolved_limit = page_window(
        page=page,
        per_page=per_page,
        offset=offset,
        limit=limit,
        default_limit=20,
    )
    date_from, date_to = _resolve_window(dateFrom, dateTo)

    try:
        with get_conn() as conn:
            line_table = resolve_table(
                conn,
                "sale_order_lines",
                "saleorderlines",
                "sale_order_line",
                "saleorderline",
            )
            if not line_table:
                return empty_page(resolved_offset, resolved_limit)

            line_cols = table_columns(conn, line_table)
            line_id_col = pick_column(line_cols, "id")
            product_id_col = pick_column(line_cols, "product_id", "productid")
            product_name_col = pick_column(
                line_cols,
                "product_name",
                "productname",
                "name",
                "display_name",
            )
            qty_col = pick_column(line_cols, "qty", "quantity", "product_uom_qty", "uom_qty")
            subtotal_col = pick_column(
                line_cols,
                "price_subtotal",
                "pricesubtotal",
                "subtotal",
                "amount_total",
                "amount",
                "price_total",
            )
            unit_price_col = pick_column(line_cols, "price_unit", "unit_price", "price")
            order_id_col = pick_column(
                line_cols,
                "sale_order_id",
                "saleorder_id",
                "order_id",
                "orderid",
            )

            if not line_id_col:
                return empty_page(resolved_offset, resolved_limit)

            order_ctx = _sale_order_context(conn)
            joins = ""
            where: list[str] = []
            params: list = []

            if (
                order_ctx
                and order_id_col
                and order_ctx.id_col
                and (order_ctx.date_col or order_ctx.company_id_col)
            ):
                joins = (
                    f" LEFT JOIN {order_ctx.table.qualified_name} o"
                    f" ON l.{quote_ident(order_id_col)} = o.{quote_ident(order_ctx.id_col)}"
                )
                if order_ctx.date_col:
                    _append_date_filter(
                        where,
                        params,
                        expr=f"o.{quote_ident(order_ctx.date_col)}",
                        date_from=date_from,
                        date_to=date_to,
                    )
                if companyId:
                    if not order_ctx.company_id_col:
                        return empty_page(resolved_offset, resolved_limit)
                    where.append(f"o.{quote_ident(order_ctx.company_id_col)}::text = %s")
                    params.append(companyId)
            else:
                line_date_col = pick_column(line_cols, "date", "created_at", "created_date")
                line_company_col = pick_column(line_cols, "company_id", "companyid")
                if line_date_col:
                    _append_date_filter(
                        where,
                        params,
                        expr=f"l.{quote_ident(line_date_col)}",
                        date_from=date_from,
                        date_to=date_to,
                    )
                if companyId:
                    if not line_company_col:
                        return empty_page(resolved_offset, resolved_limit)
                    where.append(f"l.{quote_ident(line_company_col)}::text = %s")
                    params.append(companyId)

            service_id_expr = (
                f"l.{quote_ident(product_id_col)}::text"
                if product_id_col
                else f"l.{quote_ident(line_id_col)}::text"
            )
            service_name_expr = (
                f"COALESCE(NULLIF(l.{quote_ident(product_name_col)}::text, ''), 'N/A')"
                if product_name_col
                else "'N/A'::text"
            )

            if subtotal_col:
                amount_expr = f"COALESCE(l.{quote_ident(subtotal_col)}, 0)"
            elif qty_col and unit_price_col:
                amount_expr = (
                    f"COALESCE(l.{quote_ident(qty_col)}, 0) * COALESCE(l.{quote_ident(unit_price_col)}, 0)"
                )
            else:
                amount_expr = "0::numeric"

            qty_expr = f"COALESCE(l.{quote_ident(qty_col)}, 1)" if qty_col else "1::numeric"

            where_sql = ""
            if where:
                where_sql = " WHERE " + " AND ".join(where)

            query = (
                "SELECT "
                f"{service_id_expr} AS \"serviceId\", "
                f"{service_name_expr} AS \"serviceName\", "
                "COUNT(*)::bigint AS \"orderCount\", "
                f"COALESCE(SUM({qty_expr}), 0) AS quantity, "
                f"COALESCE(SUM({amount_expr}), 0) AS \"totalAmount\" "
                f"FROM {line_table.qualified_name} l"
                f"{joins}"
                f"{where_sql} "
                f"GROUP BY {service_id_expr}, {service_name_expr} "
                "ORDER BY \"totalAmount\" DESC, \"serviceName\" ASC"
            )

            return paginate(
                query=query,
                params=tuple(params),
                conn=conn,
                offset=resolved_offset,
                limit=resolved_limit,
            )
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")


@router.get("/customers")
async def report_customers(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=0, le=500),
    offset: int | None = Query(default=None, ge=0),
    limit: int | None = Query(default=None, ge=0, le=5000),
    dateFrom: date | None = Query(default=None),
    dateTo: date | None = Query(default=None),
    companyId: str | None = Query(default=None),
    _user: dict = Depends(require_auth),
):
    resolved_offset, resolved_limit = page_window(
        page=page,
        per_page=per_page,
        offset=offset,
        limit=limit,
        default_limit=20,
    )
    date_from, date_to = _resolve_window(dateFrom, dateTo)

    try:
        with get_conn() as conn:
            payment_ctx = _payment_context(conn)
            if payment_ctx and payment_ctx.partner_id_col:
                where: list[str] = []
                params: list = []
                _append_date_filter(
                    where,
                    params,
                    expr=f"p.{quote_ident(payment_ctx.date_col)}",
                    date_from=date_from,
                    date_to=date_to,
                )
                if companyId:
                    if not payment_ctx.company_id_col:
                        return empty_page(resolved_offset, resolved_limit)
                    where.append(f"p.{quote_ident(payment_ctx.company_id_col)}::text = %s")
                    params.append(companyId)

                where_sql = ""
                if where:
                    where_sql = " WHERE " + " AND ".join(where)

                customer_name_expr = (
                    f"COALESCE(NULLIF(p.{quote_ident(payment_ctx.partner_name_col)}::text, ''), 'N/A')"
                    if payment_ctx.partner_name_col
                    else "'N/A'::text"
                )
                query = (
                    "SELECT "
                    f"p.{quote_ident(payment_ctx.partner_id_col)}::text AS \"customerId\", "
                    f"{customer_name_expr} AS \"customerName\", "
                    "COUNT(*)::bigint AS \"paymentCount\", "
                    f"COALESCE(SUM(COALESCE(p.{quote_ident(payment_ctx.amount_col)}, 0)), 0) AS \"totalAmount\" "
                    f"FROM {payment_ctx.table.qualified_name} p"
                    f"{where_sql} "
                    f"GROUP BY p.{quote_ident(payment_ctx.partner_id_col)}, {customer_name_expr} "
                    "ORDER BY \"totalAmount\" DESC, \"customerName\" ASC"
                )
                return paginate(
                    query=query,
                    params=tuple(params),
                    conn=conn,
                    offset=resolved_offset,
                    limit=resolved_limit,
                )

            order_ctx = _sale_order_context(conn)
            if not order_ctx or not order_ctx.partner_id_col:
                return empty_page(resolved_offset, resolved_limit)

            where = []
            params = []
            if order_ctx.date_col:
                _append_date_filter(
                    where,
                    params,
                    expr=f"o.{quote_ident(order_ctx.date_col)}",
                    date_from=date_from,
                    date_to=date_to,
                )
            if companyId:
                if not order_ctx.company_id_col:
                    return empty_page(resolved_offset, resolved_limit)
                where.append(f"o.{quote_ident(order_ctx.company_id_col)}::text = %s")
                params.append(companyId)

            where_sql = ""
            if where:
                where_sql = " WHERE " + " AND ".join(where)

            customer_name_expr = (
                f"COALESCE(NULLIF(o.{quote_ident(order_ctx.partner_name_col)}::text, ''), 'N/A')"
                if order_ctx.partner_name_col
                else "'N/A'::text"
            )
            amount_expr = (
                f"COALESCE(o.{quote_ident(order_ctx.amount_col)}, 0)"
                if order_ctx.amount_col
                else "0::numeric"
            )
            query = (
                "SELECT "
                f"o.{quote_ident(order_ctx.partner_id_col)}::text AS \"customerId\", "
                f"{customer_name_expr} AS \"customerName\", "
                "COUNT(*)::bigint AS \"paymentCount\", "
                f"COALESCE(SUM({amount_expr}), 0) AS \"totalAmount\" "
                f"FROM {order_ctx.table.qualified_name} o"
                f"{where_sql} "
                f"GROUP BY o.{quote_ident(order_ctx.partner_id_col)}, {customer_name_expr} "
                "ORDER BY \"totalAmount\" DESC, \"customerName\" ASC"
            )
            return paginate(
                query=query,
                params=tuple(params),
                conn=conn,
                offset=resolved_offset,
                limit=resolved_limit,
            )
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")


@router.get("/sources")
async def report_sources(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=0, le=500),
    offset: int | None = Query(default=None, ge=0),
    limit: int | None = Query(default=None, ge=0, le=5000),
    dateFrom: date | None = Query(default=None),
    dateTo: date | None = Query(default=None),
    companyId: str | None = Query(default=None),
    _user: dict = Depends(require_auth),
):
    resolved_offset, resolved_limit = page_window(
        page=page,
        per_page=per_page,
        offset=offset,
        limit=limit,
        default_limit=20,
    )
    date_from, date_to = _resolve_window(dateFrom, dateTo)

    try:
        with get_conn() as conn:
            partner_table = resolve_table(conn, "partners", "res_partners", "respartners")
            if not partner_table:
                return empty_page(resolved_offset, resolved_limit)

            partner_cols = table_columns(conn, partner_table)
            partner_id_col = pick_column(partner_cols, "id")
            if not partner_id_col:
                return empty_page(resolved_offset, resolved_limit)

            source_id_col = pick_column(
                partner_cols,
                "source_id",
                "sourceid",
                "partner_source_id",
                "partnersourceid",
            )
            source_name_col = pick_column(
                partner_cols,
                "source_name",
                "sourcename",
                "source",
            )
            partner_company_col = pick_column(partner_cols, "company_id", "companyid")
            if not source_id_col and not source_name_col:
                return empty_page(resolved_offset, resolved_limit)

            source_table = resolve_table(conn, "partner_sources", "partnersources", "sources")
            source_join = ""
            source_label_expr = (
                f"COALESCE(NULLIF(p.{quote_ident(source_name_col)}::text, ''), 'Không xác định')"
                if source_name_col
                else "'Không xác định'::text"
            )
            source_id_expr = (
                f"p.{quote_ident(source_id_col)}::text" if source_id_col else "NULL::text"
            )

            if source_table and source_id_col:
                source_cols = table_columns(conn, source_table)
                s_id_col = pick_column(source_cols, "id")
                s_name_col = pick_column(source_cols, "name", "display_name")
                if s_id_col and s_name_col:
                    source_join = (
                        f" LEFT JOIN {source_table.qualified_name} s"
                        f" ON p.{quote_ident(source_id_col)} = s.{quote_ident(s_id_col)}"
                    )
                    source_id_expr = f"s.{quote_ident(s_id_col)}::text"
                    source_label_expr = (
                        f"COALESCE(NULLIF(s.{quote_ident(s_name_col)}::text, ''), {source_label_expr})"
                    )

            payment_ctx = _payment_context(conn)
            payment_join = ""
            payment_amount_expr = "0::numeric"
            if payment_ctx and payment_ctx.partner_id_col:
                payment_conditions = [
                    f"pm.{quote_ident(payment_ctx.partner_id_col)} = p.{quote_ident(partner_id_col)}"
                ]
                if payment_ctx.date_col:
                    payment_conditions.append(f"pm.{quote_ident(payment_ctx.date_col)}::date >= %s")
                    payment_conditions.append(f"pm.{quote_ident(payment_ctx.date_col)}::date <= %s")
                payment_join = (
                    f" LEFT JOIN {payment_ctx.table.qualified_name} pm"
                    f" ON {' AND '.join(payment_conditions)}"
                )
                payment_amount_expr = f"COALESCE(pm.{quote_ident(payment_ctx.amount_col)}, 0)"

            where: list[str] = []
            params: list = []

            if payment_join and payment_ctx and payment_ctx.date_col:
                params.extend([date_from, date_to])

            if companyId:
                if partner_company_col:
                    where.append(f"p.{quote_ident(partner_company_col)}::text = %s")
                    params.append(companyId)
                else:
                    return empty_page(resolved_offset, resolved_limit)

            where_sql = ""
            if where:
                where_sql = " WHERE " + " AND ".join(where)

            query = (
                "SELECT "
                f"COALESCE({source_id_expr}, 'unknown') AS \"sourceId\", "
                f"{source_label_expr} AS \"sourceName\", "
                f"COUNT(DISTINCT p.{quote_ident(partner_id_col)})::bigint AS \"customerCount\", "
                f"COALESCE(SUM({payment_amount_expr}), 0) AS \"totalAmount\" "
                f"FROM {partner_table.qualified_name} p"
                f"{source_join}"
                f"{payment_join}"
                f"{where_sql} "
                f"GROUP BY COALESCE({source_id_expr}, 'unknown'), {source_label_expr} "
                "ORDER BY \"totalAmount\" DESC, \"sourceName\" ASC"
            )

            return paginate(
                query=query,
                params=tuple(params),
                conn=conn,
                offset=resolved_offset,
                limit=resolved_limit,
            )
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")


@router.get("/staff")
async def report_staff(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=0, le=500),
    offset: int | None = Query(default=None, ge=0),
    limit: int | None = Query(default=None, ge=0, le=5000),
    dateFrom: date | None = Query(default=None),
    dateTo: date | None = Query(default=None),
    companyId: str | None = Query(default=None),
    _user: dict = Depends(require_auth),
):
    resolved_offset, resolved_limit = page_window(
        page=page,
        per_page=per_page,
        offset=offset,
        limit=limit,
        default_limit=20,
    )
    date_from, date_to = _resolve_window(dateFrom, dateTo)

    try:
        with get_conn() as conn:
            ctx = _sale_order_context(conn)
            if not ctx or not ctx.doctor_id_col:
                return empty_page(resolved_offset, resolved_limit)

            joins = ""
            staff_name_expr = (
                f"COALESCE(NULLIF(o.{quote_ident(ctx.doctor_name_col)}::text, ''), 'N/A')"
                if ctx.doctor_name_col
                else "'N/A'::text"
            )
            if not ctx.doctor_name_col:
                employees_table = resolve_table(conn, "employees", "employee")
                if employees_table:
                    employee_cols = table_columns(conn, employees_table)
                    e_id_col = pick_column(employee_cols, "id")
                    e_name_col = pick_column(employee_cols, "name", "display_name")
                    if e_id_col and e_name_col:
                        joins = (
                            f" LEFT JOIN {employees_table.qualified_name} e"
                            f" ON o.{quote_ident(ctx.doctor_id_col)} = e.{quote_ident(e_id_col)}"
                        )
                        staff_name_expr = (
                            f"COALESCE(NULLIF(e.{quote_ident(e_name_col)}::text, ''), 'N/A')"
                        )

            where: list[str] = []
            params: list = []
            if ctx.date_col:
                _append_date_filter(
                    where,
                    params,
                    expr=f"o.{quote_ident(ctx.date_col)}",
                    date_from=date_from,
                    date_to=date_to,
                )
            if companyId:
                if not ctx.company_id_col:
                    return empty_page(resolved_offset, resolved_limit)
                where.append(f"o.{quote_ident(ctx.company_id_col)}::text = %s")
                params.append(companyId)

            where_sql = ""
            if where:
                where_sql = " WHERE " + " AND ".join(where)

            amount_expr = (
                f"COALESCE(o.{quote_ident(ctx.amount_col)}, 0)"
                if ctx.amount_col
                else "0::numeric"
            )

            query = (
                "SELECT "
                f"o.{quote_ident(ctx.doctor_id_col)}::text AS \"staffId\", "
                f"{staff_name_expr} AS \"staffName\", "
                "COUNT(*)::bigint AS \"orderCount\", "
                f"COALESCE(SUM({amount_expr}), 0) AS \"totalAmount\" "
                f"FROM {ctx.table.qualified_name} o"
                f"{joins}"
                f"{where_sql} "
                f"GROUP BY o.{quote_ident(ctx.doctor_id_col)}, {staff_name_expr} "
                "ORDER BY \"totalAmount\" DESC, \"staffName\" ASC"
            )
            return paginate(
                query=query,
                params=tuple(params),
                conn=conn,
                offset=resolved_offset,
                limit=resolved_limit,
            )
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")


@router.get("/branches")
async def report_branches(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=0, le=500),
    offset: int | None = Query(default=None, ge=0),
    limit: int | None = Query(default=None, ge=0, le=5000),
    dateFrom: date | None = Query(default=None),
    dateTo: date | None = Query(default=None),
    companyId: str | None = Query(default=None),
    _user: dict = Depends(require_auth),
):
    resolved_offset, resolved_limit = page_window(
        page=page,
        per_page=per_page,
        offset=offset,
        limit=limit,
        default_limit=20,
    )
    date_from, date_to = _resolve_window(dateFrom, dateTo)

    try:
        with get_conn() as conn:
            payment_ctx = _payment_context(conn)
            if payment_ctx and payment_ctx.company_id_col:
                joins = ""
                branch_name_expr = (
                    f"COALESCE(NULLIF(p.{quote_ident(payment_ctx.company_name_col)}::text, ''), 'N/A')"
                    if payment_ctx.company_name_col
                    else "'N/A'::text"
                )

                if not payment_ctx.company_name_col:
                    company_table = resolve_table(conn, "companies", "company")
                    if company_table:
                        company_cols = table_columns(conn, company_table)
                        c_id_col = pick_column(company_cols, "id")
                        c_name_col = pick_column(company_cols, "name", "display_name")
                        if c_id_col and c_name_col:
                            joins = (
                                f" LEFT JOIN {company_table.qualified_name} c"
                                f" ON p.{quote_ident(payment_ctx.company_id_col)} = c.{quote_ident(c_id_col)}"
                            )
                            branch_name_expr = (
                                f"COALESCE(NULLIF(c.{quote_ident(c_name_col)}::text, ''), 'N/A')"
                            )

                where: list[str] = []
                params: list = []
                _append_date_filter(
                    where,
                    params,
                    expr=f"p.{quote_ident(payment_ctx.date_col)}",
                    date_from=date_from,
                    date_to=date_to,
                )
                if companyId:
                    where.append(f"p.{quote_ident(payment_ctx.company_id_col)}::text = %s")
                    params.append(companyId)

                where_sql = ""
                if where:
                    where_sql = " WHERE " + " AND ".join(where)

                query = (
                    "SELECT "
                    f"p.{quote_ident(payment_ctx.company_id_col)}::text AS \"branchId\", "
                    f"{branch_name_expr} AS \"branchName\", "
                    "COUNT(*)::bigint AS \"transactionCount\", "
                    f"COALESCE(SUM(COALESCE(p.{quote_ident(payment_ctx.amount_col)}, 0)), 0) AS \"totalAmount\" "
                    f"FROM {payment_ctx.table.qualified_name} p"
                    f"{joins}"
                    f"{where_sql} "
                    f"GROUP BY p.{quote_ident(payment_ctx.company_id_col)}, {branch_name_expr} "
                    "ORDER BY \"totalAmount\" DESC, \"branchName\" ASC"
                )
                return paginate(
                    query=query,
                    params=tuple(params),
                    conn=conn,
                    offset=resolved_offset,
                    limit=resolved_limit,
                )

            order_ctx = _sale_order_context(conn)
            if not order_ctx or not order_ctx.company_id_col:
                return empty_page(resolved_offset, resolved_limit)

            joins = ""
            branch_name_expr = (
                f"COALESCE(NULLIF(o.{quote_ident(order_ctx.company_name_col)}::text, ''), 'N/A')"
                if order_ctx.company_name_col
                else "'N/A'::text"
            )
            if not order_ctx.company_name_col:
                company_table = resolve_table(conn, "companies", "company")
                if company_table:
                    company_cols = table_columns(conn, company_table)
                    c_id_col = pick_column(company_cols, "id")
                    c_name_col = pick_column(company_cols, "name", "display_name")
                    if c_id_col and c_name_col:
                        joins = (
                            f" LEFT JOIN {company_table.qualified_name} c"
                            f" ON o.{quote_ident(order_ctx.company_id_col)} = c.{quote_ident(c_id_col)}"
                        )
                        branch_name_expr = (
                            f"COALESCE(NULLIF(c.{quote_ident(c_name_col)}::text, ''), 'N/A')"
                        )

            where = []
            params = []
            if order_ctx.date_col:
                _append_date_filter(
                    where,
                    params,
                    expr=f"o.{quote_ident(order_ctx.date_col)}",
                    date_from=date_from,
                    date_to=date_to,
                )
            if companyId:
                where.append(f"o.{quote_ident(order_ctx.company_id_col)}::text = %s")
                params.append(companyId)

            where_sql = ""
            if where:
                where_sql = " WHERE " + " AND ".join(where)

            amount_expr = (
                f"COALESCE(o.{quote_ident(order_ctx.amount_col)}, 0)"
                if order_ctx.amount_col
                else "0::numeric"
            )
            query = (
                "SELECT "
                f"o.{quote_ident(order_ctx.company_id_col)}::text AS \"branchId\", "
                f"{branch_name_expr} AS \"branchName\", "
                "COUNT(*)::bigint AS \"transactionCount\", "
                f"COALESCE(SUM({amount_expr}), 0) AS \"totalAmount\" "
                f"FROM {order_ctx.table.qualified_name} o"
                f"{joins}"
                f"{where_sql} "
                f"GROUP BY o.{quote_ident(order_ctx.company_id_col)}, {branch_name_expr} "
                "ORDER BY \"totalAmount\" DESC, \"branchName\" ASC"
            )
            return paginate(
                query=query,
                params=tuple(params),
                conn=conn,
                offset=resolved_offset,
                limit=resolved_limit,
            )
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")


# ---------------------------------------------------------------------------
# GET /api/reports/summary  (fund overview for report tab)
# ---------------------------------------------------------------------------

from decimal import Decimal
from psycopg2.extras import RealDictCursor


def _to_float(value) -> float:
    if value is None:
        return 0.0
    if isinstance(value, Decimal):
        return float(value)
    return float(value)


@router.get("/summary")
async def reports_fund_summary(
    companyId: str | None = Query(default=None),
    dateFrom: date | None = Query(default=None),
    dateTo: date | None = Query(default=None),
    _user: dict = Depends(require_auth),
):
    """Return fund overview: cash_fund, bank_fund, supplier_debt,
    customer_debt, insurance_debt, expected_revenue."""
    date_from, date_to = _resolve_window(dateFrom, dateTo)

    try:
        with get_conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                payment_ctx = _payment_context(conn)

                cash_fund = 0.0
                bank_fund = 0.0
                if payment_ctx:
                    amount_expr = f"COALESCE(p.{quote_ident(payment_ctx.amount_col)}, 0)"
                    where: list[str] = []
                    params: list = []
                    _append_date_filter(
                        where, params,
                        expr=f"p.{quote_ident(payment_ctx.date_col)}",
                        date_from=date_from, date_to=date_to,
                    )
                    if companyId and payment_ctx.company_id_col:
                        where.append(f"p.{quote_ident(payment_ctx.company_id_col)}::text = %s")
                        params.append(companyId)

                    journal_table = resolve_table(conn, "account_journals", "accountjournals", "journals")
                    join_sql = ""
                    channel_expr = "''"
                    pay_cols = table_columns(conn, payment_ctx.table)
                    journal_col = pick_column(pay_cols, "journal_id", "journalid")
                    if journal_col and journal_table:
                        j_cols = table_columns(conn, journal_table)
                        j_id = pick_column(j_cols, "id")
                        j_type = pick_column(j_cols, "type", "journal_type")
                        j_name = pick_column(j_cols, "name", "display_name")
                        if j_id:
                            join_sql = (
                                f" LEFT JOIN {journal_table.qualified_name} j"
                                f" ON p.{quote_ident(journal_col)} = j.{quote_ident(j_id)}"
                            )
                            parts = []
                            if j_type:
                                parts.append(f"j.{quote_ident(j_type)}::text")
                            if j_name:
                                parts.append(f"j.{quote_ident(j_name)}::text")
                            if parts:
                                channel_expr = "LOWER(COALESCE(" + ", ".join(parts) + ", ''))"

                    where_sql = (" WHERE " + " AND ".join(where)) if where else ""
                    cash_pred = f"({channel_expr} LIKE '%%cash%%' OR {channel_expr} LIKE '%%tien mat%%')"
                    bank_pred = f"({channel_expr} LIKE '%%bank%%' OR {channel_expr} LIKE '%%ngan hang%%')"

                    sql = (
                        "SELECT "
                        f"COALESCE(SUM(CASE WHEN {cash_pred} THEN {amount_expr} ELSE 0 END), 0) AS cash_fund, "
                        f"COALESCE(SUM(CASE WHEN {bank_pred} THEN {amount_expr} ELSE 0 END), 0) AS bank_fund "
                        f"FROM {payment_ctx.table.qualified_name} p{join_sql}{where_sql}"
                    )
                    cur.execute(sql, tuple(params))
                    row = dict(cur.fetchone() or {})
                    cash_fund = _to_float(row.get("cash_fund"))
                    bank_fund = _to_float(row.get("bank_fund"))

                supplier_debt = 0.0
                customer_debt = 0.0
                insurance_debt = 0.0
                expected_revenue = 0.0

                order_ctx = _sale_order_context(conn)
                if order_ctx and order_ctx.amount_col:
                    so_amount_expr = f"COALESCE(o.{quote_ident(order_ctx.amount_col)}, 0)"
                    so_where: list[str] = []
                    so_params: list = []
                    if order_ctx.date_col:
                        _append_date_filter(
                            so_where, so_params,
                            expr=f"o.{quote_ident(order_ctx.date_col)}",
                            date_from=date_from, date_to=date_to,
                        )
                    if companyId and order_ctx.company_id_col:
                        so_where.append(f"o.{quote_ident(order_ctx.company_id_col)}::text = %s")
                        so_params.append(companyId)

                    so_cols = table_columns(conn, order_ctx.table)
                    residual_col = pick_column(so_cols, "residual", "amount_residual", "residual_amount", "debt")
                    state_col = pick_column(so_cols, "state", "status")

                    if residual_col:
                        residual_expr = f"COALESCE(o.{quote_ident(residual_col)}, 0)"
                        debt_where = list(so_where)
                        if state_col:
                            debt_where.append(
                                f"LOWER(COALESCE(o.{quote_ident(state_col)}::text, '')) NOT IN ('cancel', 'cancelled', 'draft')"
                            )
                        debt_where_sql = (" WHERE " + " AND ".join(debt_where)) if debt_where else ""
                        cur.execute(
                            f"SELECT COALESCE(SUM({residual_expr}), 0) AS total_debt "
                            f"FROM {order_ctx.table.qualified_name} o{debt_where_sql}",
                            tuple(so_params),
                        )
                        customer_debt = _to_float((cur.fetchone() or {}).get("total_debt"))

                    rev_where = list(so_where)
                    if state_col:
                        rev_where.append(
                            f"LOWER(COALESCE(o.{quote_ident(state_col)}::text, '')) IN ('sale', 'done', 'confirmed')"
                        )
                    rev_where_sql = (" WHERE " + " AND ".join(rev_where)) if rev_where else ""
                    cur.execute(
                        f"SELECT COALESCE(SUM({so_amount_expr}), 0) AS expected "
                        f"FROM {order_ctx.table.qualified_name} o{rev_where_sql}",
                        tuple(so_params),
                    )
                    expected_revenue = _to_float((cur.fetchone() or {}).get("expected"))

            return {
                "cashFund": cash_fund,
                "bankFund": bank_fund,
                "supplierDebt": supplier_debt,
                "customerDebt": customer_debt,
                "insuranceDebt": insurance_debt,
                "expectedRevenue": expected_revenue,
                "dateFrom": date_from.isoformat(),
                "dateTo": date_to.isoformat(),
                "companyId": companyId,
            }
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")


# ---------------------------------------------------------------------------
# GET /api/reports/supplier-debt  (Công nợ NCC)
# ---------------------------------------------------------------------------

@router.get("/supplier-debt")
async def report_supplier_debt(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=0, le=500),
    offset: int | None = Query(default=None, ge=0),
    limit: int | None = Query(default=None, ge=0, le=5000),
    dateFrom: date | None = Query(default=None),
    dateTo: date | None = Query(default=None),
    companyId: str | None = Query(default=None),
    _user: dict = Depends(require_auth),
):
    """Supplier debt report -- returns empty items (placeholder)."""
    resolved_offset, resolved_limit = page_window(
        page=page, per_page=per_page, offset=offset, limit=limit, default_limit=20,
    )
    # Placeholder: real implementation would query purchase orders / account_move_line
    return empty_page(resolved_offset, resolved_limit)


# ---------------------------------------------------------------------------
# GET /api/reports/insurance-debt  (Công nợ bảo hiểm)
# ---------------------------------------------------------------------------

@router.get("/insurance-debt")
async def report_insurance_debt(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=0, le=500),
    offset: int | None = Query(default=None, ge=0),
    limit: int | None = Query(default=None, ge=0, le=5000),
    dateFrom: date | None = Query(default=None),
    dateTo: date | None = Query(default=None),
    companyId: str | None = Query(default=None),
    _user: dict = Depends(require_auth),
):
    """Insurance debt report -- returns empty items (placeholder)."""
    resolved_offset, resolved_limit = page_window(
        page=page, per_page=per_page, offset=offset, limit=limit, default_limit=20,
    )
    # Placeholder: real implementation would query insurance claims
    return empty_page(resolved_offset, resolved_limit)
