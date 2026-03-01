"""Sale order (treatment) API endpoints."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from psycopg2.extras import RealDictCursor

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

router = APIRouter(prefix="/api", tags=["sale-orders"])

_STATE_BUCKETS = ("draft", "sale", "done", "cancel")


@router.get("/sale-orders")
async def list_sale_orders(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=0, le=500),
    offset: int | None = Query(default=None, ge=0),
    limit: int | None = Query(default=None, ge=0, le=5000),
    search: str = Query(default=""),
    companyId: str | None = Query(default=None),
    partnerId: str | None = Query(default=None),
    state: str | None = Query(default=None),
    dateFrom: date | None = Query(default=None),
    dateTo: date | None = Query(default=None),
    _user: dict = Depends(require_auth),
):
    """Return paginated sale orders/treatments."""
    effective_offset, effective_limit = page_window(
        page=page,
        per_page=per_page,
        offset=offset,
        limit=limit,
        default_limit=20,
    )

    try:
        with get_conn() as conn:
            order_meta = _resolve_sale_order_meta(conn)
            if not order_meta:
                return empty_page(effective_offset, effective_limit)

            table = order_meta["table"]
            id_col = order_meta["id_col"]
            name_col = order_meta["name_col"]
            date_col = order_meta["date_col"]
            state_col = order_meta["state_col"]
            amount_col = order_meta["amount_col"]
            partner_id_col = order_meta["partner_id_col"]
            partner_name_col = order_meta["partner_name_col"]
            doctor_id_col = order_meta["doctor_id_col"]
            doctor_name_col = order_meta["doctor_name_col"]
            company_id_col = order_meta["company_id_col"]
            company_name_col = order_meta["company_name_col"]

            joins: list[str] = []
            partner_name_expr = (
                f'o.{quote_ident(partner_name_col)}' if partner_name_col else "NULL::text"
            )
            doctor_name_expr = (
                f'o.{quote_ident(doctor_name_col)}' if doctor_name_col else "NULL::text"
            )
            company_name_expr = (
                f'o.{quote_ident(company_name_col)}' if company_name_col else "NULL::text"
            )

            if not partner_name_col and partner_id_col:
                partners_table = resolve_table(conn, "partners", "respartners", "res_partners")
                if partners_table:
                    partner_cols = table_columns(conn, partners_table)
                    p_id_col = pick_column(partner_cols, "id")
                    p_name_col = pick_column(partner_cols, "name", "display_name")
                    if p_id_col and p_name_col:
                        joins.append(
                            f" LEFT JOIN {partners_table.qualified_name} p"
                            f" ON o.{quote_ident(partner_id_col)} = p.{quote_ident(p_id_col)}"
                        )
                        partner_name_expr = f"p.{quote_ident(p_name_col)}"

            if not doctor_name_col and doctor_id_col:
                employees_table = resolve_table(conn, "employees", "employee")
                if employees_table:
                    employee_cols = table_columns(conn, employees_table)
                    e_id_col = pick_column(employee_cols, "id")
                    e_name_col = pick_column(employee_cols, "name", "display_name")
                    if e_id_col and e_name_col:
                        joins.append(
                            f" LEFT JOIN {employees_table.qualified_name} d"
                            f" ON o.{quote_ident(doctor_id_col)} = d.{quote_ident(e_id_col)}"
                        )
                        doctor_name_expr = f"d.{quote_ident(e_name_col)}"

            if not company_name_col and company_id_col:
                companies_table = resolve_table(conn, "companies", "company")
                if companies_table:
                    company_cols = table_columns(conn, companies_table)
                    c_id_col = pick_column(company_cols, "id")
                    c_name_col = pick_column(company_cols, "name", "display_name")
                    if c_id_col and c_name_col:
                        joins.append(
                            f" LEFT JOIN {companies_table.qualified_name} c"
                            f" ON o.{quote_ident(company_id_col)} = c.{quote_ident(c_id_col)}"
                        )
                        company_name_expr = f"c.{quote_ident(c_name_col)}"

            select_fields = [
                f'o.{quote_ident(id_col)}::text AS id',
                (
                    f"COALESCE(o.{quote_ident(name_col)}, o.{quote_ident(id_col)}::text) AS name"
                    if name_col
                    else f'o.{quote_ident(id_col)}::text AS name'
                ),
                (
                    f'o.{quote_ident(date_col)} AS date'
                    if date_col
                    else "NULL::timestamp AS date"
                ),
                (
                    f'o.{quote_ident(state_col)} AS state'
                    if state_col
                    else "NULL::text AS state"
                ),
                (
                    f"COALESCE(o.{quote_ident(amount_col)}, 0) AS \"amountTotal\""
                    if amount_col
                    else '0::numeric AS "amountTotal"'
                ),
                (
                    f'o.{quote_ident(partner_id_col)}::text AS "partnerId"'
                    if partner_id_col
                    else 'NULL::text AS "partnerId"'
                ),
                f'{partner_name_expr} AS "partnerName"',
                (
                    f'o.{quote_ident(doctor_id_col)}::text AS "doctorId"'
                    if doctor_id_col
                    else 'NULL::text AS "doctorId"'
                ),
                f'{doctor_name_expr} AS "doctorName"',
                (
                    f'o.{quote_ident(company_id_col)}::text AS "companyId"'
                    if company_id_col
                    else 'NULL::text AS "companyId"'
                ),
                f'{company_name_expr} AS "companyName"',
            ]

            where_clauses: list[str] = []
            params: list = []

            search_text = search.strip()
            if search_text:
                pattern = f"%{search_text}%"
                search_parts: list[str] = []
                if name_col:
                    search_parts.append(f"o.{quote_ident(name_col)} ILIKE %s")
                    params.append(pattern)
                if partner_name_col:
                    search_parts.append(f"o.{quote_ident(partner_name_col)} ILIKE %s")
                    params.append(pattern)
                elif "p." in partner_name_expr:
                    search_parts.append(f"{partner_name_expr} ILIKE %s")
                    params.append(pattern)
                if search_parts:
                    where_clauses.append(f"({' OR '.join(search_parts)})")

            if companyId:
                if not company_id_col:
                    return empty_page(effective_offset, effective_limit)
                where_clauses.append(f"o.{quote_ident(company_id_col)}::text = %s")
                params.append(companyId)

            if partnerId:
                if not partner_id_col:
                    return empty_page(effective_offset, effective_limit)
                where_clauses.append(f"o.{quote_ident(partner_id_col)}::text = %s")
                params.append(partnerId)

            if state:
                if not state_col:
                    return empty_page(effective_offset, effective_limit)
                where_clauses.append(f"LOWER(COALESCE(o.{quote_ident(state_col)}::text, '')) = %s")
                params.append(state.strip().lower())

            if dateFrom:
                if not date_col:
                    return empty_page(effective_offset, effective_limit)
                where_clauses.append(f"o.{quote_ident(date_col)}::date >= %s")
                params.append(dateFrom)
            if dateTo:
                if not date_col:
                    return empty_page(effective_offset, effective_limit)
                where_clauses.append(f"o.{quote_ident(date_col)}::date <= %s")
                params.append(dateTo)

            base_query = (
                f"SELECT {', '.join(select_fields)} FROM {table.qualified_name} o"
                + "".join(joins)
            )
            if where_clauses:
                base_query += " WHERE " + " AND ".join(where_clauses)
            if date_col:
                base_query += (
                    f" ORDER BY o.{quote_ident(date_col)} DESC NULLS LAST, "
                    f"o.{quote_ident(id_col)} DESC"
                )
            else:
                base_query += f" ORDER BY o.{quote_ident(id_col)} DESC"

            return paginate(
                query=base_query,
                params=tuple(params),
                conn=conn,
                offset=effective_offset,
                limit=effective_limit,
            )
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")


@router.get("/sale-orders/states")
async def sale_order_states(
    companyId: str | None = Query(default=None),
    dateFrom: date | None = Query(default=None),
    dateTo: date | None = Query(default=None),
    _user: dict = Depends(require_auth),
):
    """Return sale-order states with counts."""
    payload = _state_payload(company_id=companyId, date_from=dateFrom, date_to=dateTo)
    return {
        "offset": 0,
        "limit": 0,
        "totalItems": len(payload["items"]),
        "items": payload["items"],
    }


@router.get("/sale-orders/states/summary")
async def sale_order_states_summary(
    companyId: str | None = Query(default=None),
    dateFrom: date | None = Query(default=None),
    dateTo: date | None = Query(default=None),
    _user: dict = Depends(require_auth),
):
    """Return canonical state summary counts (draft/sale/done/cancel)."""
    payload = _state_payload(company_id=companyId, date_from=dateFrom, date_to=dateTo)
    return payload


@router.get("/sale-orders/{sale_order_id}")
async def get_sale_order_detail(
    sale_order_id: str,
    _user: dict = Depends(require_auth),
):
    """Return one sale order with nested line items."""
    try:
        with get_conn() as conn:
            order_meta = _resolve_sale_order_meta(conn)
            if not order_meta:
                raise HTTPException(status_code=404, detail="Sale order not found")

            table = order_meta["table"]
            id_col = order_meta["id_col"]
            name_col = order_meta["name_col"]
            date_col = order_meta["date_col"]
            state_col = order_meta["state_col"]
            amount_col = order_meta["amount_col"]
            partner_id_col = order_meta["partner_id_col"]
            partner_name_col = order_meta["partner_name_col"]
            doctor_id_col = order_meta["doctor_id_col"]
            doctor_name_col = order_meta["doctor_name_col"]
            company_id_col = order_meta["company_id_col"]
            company_name_col = order_meta["company_name_col"]

            joins: list[str] = []
            partner_name_expr = (
                f'o.{quote_ident(partner_name_col)}' if partner_name_col else "NULL::text"
            )
            doctor_name_expr = (
                f'o.{quote_ident(doctor_name_col)}' if doctor_name_col else "NULL::text"
            )
            company_name_expr = (
                f'o.{quote_ident(company_name_col)}' if company_name_col else "NULL::text"
            )

            if not partner_name_col and partner_id_col:
                partners_table = resolve_table(conn, "partners", "respartners", "res_partners")
                if partners_table:
                    partner_cols = table_columns(conn, partners_table)
                    p_id_col = pick_column(partner_cols, "id")
                    p_name_col = pick_column(partner_cols, "name", "display_name")
                    if p_id_col and p_name_col:
                        joins.append(
                            f" LEFT JOIN {partners_table.qualified_name} p"
                            f" ON o.{quote_ident(partner_id_col)} = p.{quote_ident(p_id_col)}"
                        )
                        partner_name_expr = f"p.{quote_ident(p_name_col)}"

            if not doctor_name_col and doctor_id_col:
                employees_table = resolve_table(conn, "employees", "employee")
                if employees_table:
                    employee_cols = table_columns(conn, employees_table)
                    e_id_col = pick_column(employee_cols, "id")
                    e_name_col = pick_column(employee_cols, "name", "display_name")
                    if e_id_col and e_name_col:
                        joins.append(
                            f" LEFT JOIN {employees_table.qualified_name} d"
                            f" ON o.{quote_ident(doctor_id_col)} = d.{quote_ident(e_id_col)}"
                        )
                        doctor_name_expr = f"d.{quote_ident(e_name_col)}"

            if not company_name_col and company_id_col:
                companies_table = resolve_table(conn, "companies", "company")
                if companies_table:
                    company_cols = table_columns(conn, companies_table)
                    c_id_col = pick_column(company_cols, "id")
                    c_name_col = pick_column(company_cols, "name", "display_name")
                    if c_id_col and c_name_col:
                        joins.append(
                            f" LEFT JOIN {companies_table.qualified_name} c"
                            f" ON o.{quote_ident(company_id_col)} = c.{quote_ident(c_id_col)}"
                        )
                        company_name_expr = f"c.{quote_ident(c_name_col)}"

            order_query = (
                "SELECT "
                f"o.{quote_ident(id_col)}::text AS id, "
                + (
                    f"COALESCE(o.{quote_ident(name_col)}, o.{quote_ident(id_col)}::text) AS name, "
                    if name_col
                    else f"o.{quote_ident(id_col)}::text AS name, "
                )
                + (
                    f"o.{quote_ident(date_col)} AS date, "
                    if date_col
                    else "NULL::timestamp AS date, "
                )
                + (
                    f"o.{quote_ident(state_col)} AS state, "
                    if state_col
                    else "NULL::text AS state, "
                )
                + (
                    f"COALESCE(o.{quote_ident(amount_col)}, 0) AS \"amountTotal\", "
                    if amount_col
                    else '0::numeric AS "amountTotal", '
                )
                + (
                    f'o.{quote_ident(partner_id_col)}::text AS "partnerId", '
                    if partner_id_col
                    else 'NULL::text AS "partnerId", '
                )
                + f'{partner_name_expr} AS "partnerName", '
                + (
                    f'o.{quote_ident(doctor_id_col)}::text AS "doctorId", '
                    if doctor_id_col
                    else 'NULL::text AS "doctorId", '
                )
                + f'{doctor_name_expr} AS "doctorName", '
                + (
                    f'o.{quote_ident(company_id_col)}::text AS "companyId", '
                    if company_id_col
                    else 'NULL::text AS "companyId", '
                )
                + f'{company_name_expr} AS "companyName" '
                f"FROM {table.qualified_name} o"
                + "".join(joins)
                + f" WHERE o.{quote_ident(id_col)}::text = %s"
                + " LIMIT 1"
            )

            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(order_query, (sale_order_id,))
                row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Sale order not found")

            order_payload = dict(row)
            order_payload["lines"] = _load_sale_order_lines(conn=conn, sale_order_id=sale_order_id)
            return order_payload
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")


def _state_payload(company_id: str | None, date_from: date | None, date_to: date | None) -> dict:
    """Build response payload for sale-order states and summary."""
    try:
        with get_conn() as conn:
            order_meta = _resolve_sale_order_meta(conn)
            if not order_meta:
                return {
                    "draft": 0,
                    "sale": 0,
                    "done": 0,
                    "cancel": 0,
                    "other": 0,
                    "items": [],
                    "totalItems": 0,
                }

            table = order_meta["table"]
            state_col = order_meta["state_col"]
            company_id_col = order_meta["company_id_col"]
            date_col = order_meta["date_col"]

            if not state_col:
                return {
                    "draft": 0,
                    "sale": 0,
                    "done": 0,
                    "cancel": 0,
                    "other": 0,
                    "items": [],
                    "totalItems": 0,
                }

            where_clauses: list[str] = []
            params: list = []

            if company_id:
                if not company_id_col:
                    return {
                        "draft": 0,
                        "sale": 0,
                        "done": 0,
                        "cancel": 0,
                        "other": 0,
                        "items": [],
                        "totalItems": 0,
                    }
                where_clauses.append(f"o.{quote_ident(company_id_col)}::text = %s")
                params.append(company_id)

            if date_from:
                if not date_col:
                    return {
                        "draft": 0,
                        "sale": 0,
                        "done": 0,
                        "cancel": 0,
                        "other": 0,
                        "items": [],
                        "totalItems": 0,
                    }
                where_clauses.append(f"o.{quote_ident(date_col)}::date >= %s")
                params.append(date_from)

            if date_to:
                if not date_col:
                    return {
                        "draft": 0,
                        "sale": 0,
                        "done": 0,
                        "cancel": 0,
                        "other": 0,
                        "items": [],
                        "totalItems": 0,
                    }
                where_clauses.append(f"o.{quote_ident(date_col)}::date <= %s")
                params.append(date_to)

            query = (
                f"SELECT LOWER(COALESCE(o.{quote_ident(state_col)}::text, 'unknown')) AS state, "
                "COUNT(*)::bigint AS count "
                f"FROM {table.qualified_name} o"
            )
            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)
            query += " GROUP BY 1 ORDER BY 1"

            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, tuple(params))
                rows = cur.fetchall()
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")

    counts = {state: 0 for state in _STATE_BUCKETS}
    extras: dict[str, int] = {}
    for row in rows:
        state_name = str(row["state"] or "unknown").lower()
        count = int(row["count"] or 0)
        if state_name in counts:
            counts[state_name] += count
        else:
            extras[state_name] = extras.get(state_name, 0) + count

    items = [
        {"state": state_name, "count": counts[state_name]}
        for state_name in _STATE_BUCKETS
    ]
    items.extend(
        {"state": state_name, "count": count}
        for state_name, count in sorted(extras.items())
    )
    other_total = sum(extras.values())
    return {
        "draft": counts["draft"],
        "sale": counts["sale"],
        "done": counts["done"],
        "cancel": counts["cancel"],
        "other": other_total,
        "items": items,
        "totalItems": len(items),
    }


def _load_sale_order_lines(conn, sale_order_id: str) -> list[dict]:
    """Load nested line items for a sale order detail response."""
    lines_table = resolve_table(
        conn,
        "sale_order_lines",
        "saleorderlines",
        "sale_order_line",
    )
    if not lines_table:
        return []

    cols = table_columns(conn, lines_table)
    id_col = pick_column(cols, "id")
    sale_order_id_col = pick_column(
        cols,
        "sale_order_id",
        "saleorder_id",
        "order_id",
        "so_id",
    )
    if not id_col or not sale_order_id_col:
        return []

    name_col = pick_column(cols, "name", "display_name", "description")
    product_id_col = pick_column(cols, "product_id", "productid")
    product_name_col = pick_column(cols, "product_name", "productname")
    qty_col = pick_column(cols, "qty", "quantity", "product_uom_qty", "qty_done")
    unit_price_col = pick_column(cols, "price_unit", "unit_price", "price")
    subtotal_col = pick_column(cols, "price_subtotal", "subtotal", "amount")
    state_col = pick_column(cols, "state", "status")

    product_name_expr = (
        f'l.{quote_ident(product_name_col)}' if product_name_col else "NULL::text"
    )
    joins = ""
    if not product_name_col and product_id_col:
        products_table = resolve_table(conn, "products", "product")
        if products_table:
            product_cols = table_columns(conn, products_table)
            p_id_col = pick_column(product_cols, "id")
            p_name_col = pick_column(product_cols, "name", "display_name")
            if p_id_col and p_name_col:
                joins = (
                    f" LEFT JOIN {products_table.qualified_name} pr"
                    f" ON l.{quote_ident(product_id_col)} = pr.{quote_ident(p_id_col)}"
                )
                product_name_expr = f"pr.{quote_ident(p_name_col)}"

    query = (
        "SELECT "
        f"l.{quote_ident(id_col)}::text AS id, "
        + (
            f"COALESCE(l.{quote_ident(name_col)}, l.{quote_ident(id_col)}::text) AS name, "
            if name_col
            else f"l.{quote_ident(id_col)}::text AS name, "
        )
        + (
            f'l.{quote_ident(product_id_col)}::text AS "productId", '
            if product_id_col
            else 'NULL::text AS "productId", '
        )
        + f'{product_name_expr} AS "productName", '
        + (
            f"COALESCE(l.{quote_ident(qty_col)}, 0) AS qty, "
            if qty_col
            else "0::numeric AS qty, "
        )
        + (
            f'COALESCE(l.{quote_ident(unit_price_col)}, 0) AS "unitPrice", '
            if unit_price_col
            else '0::numeric AS "unitPrice", '
        )
        + (
            f'COALESCE(l.{quote_ident(subtotal_col)}, 0) AS subtotal, '
            if subtotal_col
            else "0::numeric AS subtotal, "
        )
        + (
            f"l.{quote_ident(state_col)} AS state "
            if state_col
            else "NULL::text AS state "
        )
        + f"FROM {lines_table.qualified_name} l"
        + joins
        + f" WHERE l.{quote_ident(sale_order_id_col)}::text = %s"
        + (
            f" ORDER BY l.{quote_ident(id_col)} ASC"
            if id_col
            else ""
        )
    )

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(query, (sale_order_id,))
        rows = cur.fetchall()
    return [dict(row) for row in rows]


def _resolve_sale_order_meta(conn) -> dict | None:
    """Resolve sale-order table metadata used by multiple handlers."""
    table = resolve_table(
        conn,
        "sale_orders",
        "saleorders",
        "sale_order",
    )
    if not table:
        return None

    cols = table_columns(conn, table)
    id_col = pick_column(cols, "id")
    if not id_col:
        return None

    return {
        "table": table,
        "id_col": id_col,
        "name_col": pick_column(cols, "name", "display_name", "order_name", "code"),
        "date_col": pick_column(cols, "date_order", "order_date", "date", "created_at"),
        "state_col": pick_column(cols, "state", "status"),
        "amount_col": pick_column(cols, "amount_total", "total_amount", "amount"),
        "partner_id_col": pick_column(cols, "partner_id", "partnerid", "customer_id", "customerid"),
        "partner_name_col": pick_column(cols, "partner_name", "partnername", "customer_name", "customername"),
        "doctor_id_col": pick_column(cols, "doctor_id", "doctorid", "employee_id"),
        "doctor_name_col": pick_column(cols, "doctor_name", "doctorname"),
        "company_id_col": pick_column(cols, "company_id", "companyid"),
        "company_name_col": pick_column(cols, "company_name", "companyname"),
    }
