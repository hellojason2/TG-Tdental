"""Inventory/stock API endpoints."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
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

router = APIRouter(prefix="/api", tags=["inventory"])

_INCOMING_TYPES = ("incoming", "inbound", "in", "receipt", "receive")
_OUTGOING_TYPES = ("outgoing", "outbound", "out", "delivery", "issue")


class StockReportRequest(BaseModel):
    companyId: str | None = None
    dateFrom: date | None = None
    dateTo: date | None = None
    productId: str | None = None
    pickingType: str | None = None


@router.get("/stock-pickings")
async def list_stock_pickings(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=0, le=500),
    offset: int | None = Query(default=None, ge=0),
    limit: int | None = Query(default=None, ge=0, le=5000),
    companyId: str | None = Query(default=None),
    pickingType: str | None = Query(default=None),
    state: str | None = Query(default=None),
    dateFrom: date | None = Query(default=None),
    dateTo: date | None = Query(default=None),
    _user: dict = Depends(require_auth),
):
    """Return paginated stock picking documents."""
    effective_offset, effective_limit = page_window(
        page=page,
        per_page=per_page,
        offset=offset,
        limit=limit,
        default_limit=20,
    )

    try:
        with get_conn() as conn:
            pickings_table = resolve_table(
                conn,
                "stock_pickings",
                "stockpicking",
                "stockpickings",
            )
            if not pickings_table:
                return empty_page(effective_offset, effective_limit)

            cols = table_columns(conn, pickings_table)
            id_col = pick_column(cols, "id")
            if not id_col:
                return empty_page(effective_offset, effective_limit)

            name_col = pick_column(cols, "name", "display_name", "reference", "ref")
            date_col = pick_column(cols, "date", "date_done", "scheduled_date", "created_at")
            picking_type_col = pick_column(cols, "picking_type", "picking_type_code", "type", "direction")
            picking_type_id_col = pick_column(cols, "picking_type_id", "pickingtypeid")
            state_col = pick_column(cols, "state", "status")
            partner_id_col = pick_column(cols, "partner_id", "partnerid")
            partner_name_col = pick_column(cols, "partner_name", "partnername")
            company_id_col = pick_column(cols, "company_id", "companyid")
            company_name_col = pick_column(cols, "company_name", "companyname")
            origin_col = pick_column(cols, "origin", "source_document", "source")

            joins: list[str] = []
            partner_name_expr = (
                f'p.{quote_ident(partner_name_col)}' if partner_name_col else "NULL::text"
            )
            company_name_expr = (
                f'p.{quote_ident(company_name_col)}' if company_name_col else "NULL::text"
            )
            picking_type_expr = (
                f"LOWER(COALESCE(p.{quote_ident(picking_type_col)}::text, ''))"
                if picking_type_col
                else "NULL::text"
            )
            picking_type_filter_expr = (
                f"LOWER(COALESCE(p.{quote_ident(picking_type_col)}::text, ''))"
                if picking_type_col
                else None
            )

            if not partner_name_col and partner_id_col:
                partners_table = resolve_table(conn, "partners", "respartners", "res_partners")
                if partners_table:
                    partner_cols = table_columns(conn, partners_table)
                    pt_id_col = pick_column(partner_cols, "id")
                    pt_name_col = pick_column(partner_cols, "name", "display_name")
                    if pt_id_col and pt_name_col:
                        joins.append(
                            f" LEFT JOIN {partners_table.qualified_name} pt"
                            f" ON p.{quote_ident(partner_id_col)} = pt.{quote_ident(pt_id_col)}"
                        )
                        partner_name_expr = f"pt.{quote_ident(pt_name_col)}"

            if not company_name_col and company_id_col:
                companies_table = resolve_table(conn, "companies", "company")
                if companies_table:
                    company_cols = table_columns(conn, companies_table)
                    c_id_col = pick_column(company_cols, "id")
                    c_name_col = pick_column(company_cols, "name", "display_name")
                    if c_id_col and c_name_col:
                        joins.append(
                            f" LEFT JOIN {companies_table.qualified_name} c"
                            f" ON p.{quote_ident(company_id_col)} = c.{quote_ident(c_id_col)}"
                        )
                        company_name_expr = f"c.{quote_ident(c_name_col)}"

            if not picking_type_col and picking_type_id_col:
                picking_types_table = resolve_table(
                    conn,
                    "stock_picking_types",
                    "stockpickingtypes",
                    "stock_picking_type",
                )
                if picking_types_table:
                    picking_type_cols = table_columns(conn, picking_types_table)
                    spt_id_col = pick_column(picking_type_cols, "id")
                    spt_code_col = pick_column(picking_type_cols, "code")
                    spt_name_col = pick_column(picking_type_cols, "name", "display_name")
                    if spt_id_col and (spt_code_col or spt_name_col):
                        joins.append(
                            f" LEFT JOIN {picking_types_table.qualified_name} spt"
                            f" ON p.{quote_ident(picking_type_id_col)} = spt.{quote_ident(spt_id_col)}"
                        )
                        type_display_col = spt_code_col or spt_name_col
                        picking_type_expr = (
                            f"LOWER(COALESCE(spt.{quote_ident(type_display_col)}::text, ''))"
                        )
                        picking_type_filter_expr = (
                            f"LOWER(COALESCE(spt.{quote_ident(type_display_col)}::text, ''))"
                        )

            select_fields = [
                f'p.{quote_ident(id_col)}::text AS id',
                (
                    f"COALESCE(p.{quote_ident(name_col)}, p.{quote_ident(id_col)}::text) AS name"
                    if name_col
                    else f'p.{quote_ident(id_col)}::text AS name'
                ),
                (
                    f'p.{quote_ident(date_col)} AS date'
                    if date_col
                    else "NULL::timestamp AS date"
                ),
                (
                    f'{picking_type_expr} AS "pickingType"'
                ),
                (
                    f'p.{quote_ident(state_col)} AS state'
                    if state_col
                    else "NULL::text AS state"
                ),
                f'{partner_name_expr} AS "partnerName"',
                (
                    f'p.{quote_ident(company_id_col)}::text AS "companyId"'
                    if company_id_col
                    else 'NULL::text AS "companyId"'
                ),
                f'{company_name_expr} AS "companyName"',
                (
                    f'p.{quote_ident(origin_col)} AS origin'
                    if origin_col
                    else "NULL::text AS origin"
                ),
            ]

            where_clauses: list[str] = []
            params: list = []

            if companyId:
                if not company_id_col:
                    return empty_page(effective_offset, effective_limit)
                where_clauses.append(f"p.{quote_ident(company_id_col)}::text = %s")
                params.append(companyId)

            if pickingType:
                if not picking_type_filter_expr:
                    return empty_page(effective_offset, effective_limit)
                where_clauses.append(f"{picking_type_filter_expr} = %s")
                params.append(pickingType.strip().lower())

            if state:
                if not state_col:
                    return empty_page(effective_offset, effective_limit)
                where_clauses.append(f"LOWER(COALESCE(p.{quote_ident(state_col)}::text, '')) = %s")
                params.append(state.strip().lower())

            if dateFrom:
                if not date_col:
                    return empty_page(effective_offset, effective_limit)
                where_clauses.append(f"p.{quote_ident(date_col)}::date >= %s")
                params.append(dateFrom)

            if dateTo:
                if not date_col:
                    return empty_page(effective_offset, effective_limit)
                where_clauses.append(f"p.{quote_ident(date_col)}::date <= %s")
                params.append(dateTo)

            base_query = (
                f"SELECT {', '.join(select_fields)} FROM {pickings_table.qualified_name} p"
                + "".join(joins)
            )
            if where_clauses:
                base_query += " WHERE " + " AND ".join(where_clauses)
            if date_col:
                base_query += (
                    f" ORDER BY p.{quote_ident(date_col)} DESC NULLS LAST, "
                    f"p.{quote_ident(id_col)} DESC"
                )
            else:
                base_query += f" ORDER BY p.{quote_ident(id_col)} DESC"

            return paginate(
                query=base_query,
                params=tuple(params),
                conn=conn,
                offset=effective_offset,
                limit=effective_limit,
            )
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")


@router.get("/stock-moves")
async def list_stock_moves(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=0, le=500),
    offset: int | None = Query(default=None, ge=0),
    limit: int | None = Query(default=None, ge=0, le=5000),
    companyId: str | None = Query(default=None),
    productId: str | None = Query(default=None),
    pickingType: str | None = Query(default=None),
    dateFrom: date | None = Query(default=None),
    dateTo: date | None = Query(default=None),
    search: str = Query(default=""),
    _user: dict = Depends(require_auth),
):
    """Return paginated stock movement history."""
    effective_offset, effective_limit = page_window(
        page=page,
        per_page=per_page,
        offset=offset,
        limit=limit,
        default_limit=20,
    )

    try:
        with get_conn() as conn:
            context = _stock_move_context(conn)
            if not context:
                return empty_page(effective_offset, effective_limit)

            select_fields = [
                f'm.{quote_ident(context["id_col"])}::text AS id',
                (
                    f'm.{quote_ident(context["date_col"])} AS date'
                    if context["date_col"]
                    else "NULL::timestamp AS date"
                ),
                (
                    f'm.{quote_ident(context["product_id_col"])}::text AS "productId"'
                    if context["product_id_col"]
                    else 'NULL::text AS "productId"'
                ),
                f'{context["product_name_expr"]} AS "productName"',
                context["qty_expr"] + ' AS "quantity"',
                f'{context["picking_type_expr"]} AS "pickingType"',
                (
                    f'm.{quote_ident(context["state_col"])} AS state'
                    if context["state_col"]
                    else "NULL::text AS state"
                ),
                (
                    f'm.{quote_ident(context["company_id_col"])}::text AS "companyId"'
                    if context["company_id_col"]
                    else 'NULL::text AS "companyId"'
                ),
                f'{context["company_name_expr"]} AS "companyName"',
                f'{context["reference_expr"]} AS reference',
            ]

            where_clauses, params = _stock_move_filters(
                context=context,
                company_id=companyId,
                product_id=productId,
                picking_type=pickingType,
                date_from=dateFrom,
                date_to=dateTo,
                search=search,
            )
            if where_clauses is None:
                return empty_page(effective_offset, effective_limit)

            base_query = (
                f"SELECT {', '.join(select_fields)} "
                f"FROM {context['table'].qualified_name} m"
                + context["joins"]
            )
            if where_clauses:
                base_query += " WHERE " + " AND ".join(where_clauses)
            if context["date_col"]:
                base_query += (
                    f" ORDER BY m.{quote_ident(context['date_col'])} DESC NULLS LAST, "
                    f"m.{quote_ident(context['id_col'])} DESC"
                )
            else:
                base_query += f" ORDER BY m.{quote_ident(context['id_col'])} DESC"

            return paginate(
                query=base_query,
                params=tuple(params),
                conn=conn,
                offset=effective_offset,
                limit=effective_limit,
            )
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")


@router.get("/stock-moves/summary")
async def stock_moves_summary(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=0, le=500),
    offset: int | None = Query(default=None, ge=0),
    limit: int | None = Query(default=None, ge=0, le=5000),
    companyId: str | None = Query(default=None),
    productId: str | None = Query(default=None),
    pickingType: str | None = Query(default=None),
    dateFrom: date | None = Query(default=None),
    dateTo: date | None = Query(default=None),
    search: str = Query(default=""),
    _user: dict = Depends(require_auth),
):
    """Return aggregated incoming/outgoing/balance quantities per product."""
    effective_offset, effective_limit = page_window(
        page=page,
        per_page=per_page,
        offset=offset,
        limit=limit,
        default_limit=20,
    )

    try:
        with get_conn() as conn:
            context = _stock_move_context(conn)
            if not context:
                return empty_page(effective_offset, effective_limit)

            where_clauses, params = _stock_move_filters(
                context=context,
                company_id=companyId,
                product_id=productId,
                picking_type=pickingType,
                date_from=dateFrom,
                date_to=dateTo,
                search=search,
            )
            if where_clauses is None:
                return empty_page(effective_offset, effective_limit)

            incoming_sum = (
                f"SUM(CASE WHEN {context['incoming_condition']} "
                f"THEN {context['qty_abs_expr']} ELSE 0 END)"
            )
            outgoing_sum = (
                f"SUM(CASE WHEN {context['outgoing_condition']} "
                f"THEN {context['qty_abs_expr']} ELSE 0 END)"
            )
            product_id_expr = (
                f'm.{quote_ident(context["product_id_col"])}::text'
                if context["product_id_col"]
                else "NULL::text"
            )

            base_query = (
                "SELECT "
                f"{product_id_expr} AS \"productId\", "
                f"{context['product_name_expr']} AS \"productName\", "
                f"{incoming_sum} AS \"incomingQty\", "
                f"{outgoing_sum} AS \"outgoingQty\", "
                f"({incoming_sum} - {outgoing_sum}) AS \"balanceQty\" "
                f"FROM {context['table'].qualified_name} m"
                + context["joins"]
            )
            if where_clauses:
                base_query += " WHERE " + " AND ".join(where_clauses)
            base_query += f" GROUP BY {product_id_expr}, {context['product_name_expr']}"
            base_query += f" ORDER BY {context['product_name_expr']} ASC NULLS LAST"

            return paginate(
                query=base_query,
                params=tuple(params),
                conn=conn,
                offset=effective_offset,
                limit=effective_limit,
            )
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")


@router.post("/reports/stock")
async def stock_report(
    body: StockReportRequest,
    _user: dict = Depends(require_auth),
):
    """Return stock import/export totals for a date range."""
    try:
        with get_conn() as conn:
            context = _stock_move_context(conn)
            if not context:
                return {
                    "companyId": body.companyId,
                    "dateFrom": body.dateFrom,
                    "dateTo": body.dateTo,
                    "totals": {"incomingQty": 0, "outgoingQty": 0, "balanceQty": 0},
                    "totalItems": 0,
                    "items": [],
                }

            where_clauses, params = _stock_move_filters(
                context=context,
                company_id=body.companyId,
                product_id=body.productId,
                picking_type=body.pickingType,
                date_from=body.dateFrom,
                date_to=body.dateTo,
                search="",
            )
            if where_clauses is None:
                return {
                    "companyId": body.companyId,
                    "dateFrom": body.dateFrom,
                    "dateTo": body.dateTo,
                    "totals": {"incomingQty": 0, "outgoingQty": 0, "balanceQty": 0},
                    "totalItems": 0,
                    "items": [],
                }

            incoming_sum = (
                f"SUM(CASE WHEN {context['incoming_condition']} "
                f"THEN {context['qty_abs_expr']} ELSE 0 END)"
            )
            outgoing_sum = (
                f"SUM(CASE WHEN {context['outgoing_condition']} "
                f"THEN {context['qty_abs_expr']} ELSE 0 END)"
            )
            product_id_expr = (
                f'm.{quote_ident(context["product_id_col"])}::text'
                if context["product_id_col"]
                else "NULL::text"
            )

            detail_query = (
                "SELECT "
                f"{product_id_expr} AS \"productId\", "
                f"{context['product_name_expr']} AS \"productName\", "
                f"{incoming_sum} AS \"incomingQty\", "
                f"{outgoing_sum} AS \"outgoingQty\", "
                f"({incoming_sum} - {outgoing_sum}) AS \"balanceQty\" "
                f"FROM {context['table'].qualified_name} m"
                + context["joins"]
            )
            if where_clauses:
                detail_query += " WHERE " + " AND ".join(where_clauses)
            detail_query += f" GROUP BY {product_id_expr}, {context['product_name_expr']}"
            detail_query += f" ORDER BY {context['product_name_expr']} ASC NULLS LAST"

            totals_query = (
                "SELECT "
                f"{incoming_sum} AS incoming, "
                f"{outgoing_sum} AS outgoing "
                f"FROM {context['table'].qualified_name} m"
                + context["joins"]
            )
            if where_clauses:
                totals_query += " WHERE " + " AND ".join(where_clauses)

            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(detail_query, tuple(params))
                detail_rows = [dict(row) for row in cur.fetchall()]
                cur.execute(totals_query, tuple(params))
                totals_row = cur.fetchone() or {}

            incoming_qty = float(totals_row.get("incoming") or 0)
            outgoing_qty = float(totals_row.get("outgoing") or 0)
            return {
                "companyId": body.companyId,
                "dateFrom": body.dateFrom,
                "dateTo": body.dateTo,
                "totals": {
                    "incomingQty": incoming_qty,
                    "outgoingQty": outgoing_qty,
                    "balanceQty": incoming_qty - outgoing_qty,
                },
                "totalItems": len(detail_rows),
                "items": detail_rows,
            }
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")


# ---------------------------------------------------------------------------
# GET /api/labo-orders
# ---------------------------------------------------------------------------


@router.get("/labo-orders")
async def list_labo_orders(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=0, le=500),
    offset: int | None = Query(default=None, ge=0),
    limit: int | None = Query(default=None, ge=0, le=5000),
    companyId: str | None = Query(default=None),
    search: str = Query(default=""),
    state: str | None = Query(default=None),
    dateFrom: date | None = Query(default=None),
    dateTo: date | None = Query(default=None),
    _user: dict = Depends(require_auth),
):
    """Return paginated labo orders list."""
    effective_offset, effective_limit = page_window(
        page=page,
        per_page=per_page,
        offset=offset,
        limit=limit,
        default_limit=20,
    )

    try:
        with get_conn() as conn:
            labo_table = resolve_table(
                conn,
                "labo_orders", "laboorders", "labo_order", "laboorder",
                "labo", "labos",
            )
            if not labo_table:
                return empty_page(effective_offset, effective_limit)

            cols = table_columns(conn, labo_table)
            id_col = pick_column(cols, "id")
            if not id_col:
                return empty_page(effective_offset, effective_limit)

            name_col = pick_column(cols, "name", "display_name", "reference", "ref", "order_name")
            date_col = pick_column(cols, "date", "order_date", "date_order", "created_at", "created_date")
            date_planned_col = pick_column(cols, "date_planned", "planned_date", "date_expected", "delivery_date")
            date_received_col = pick_column(cols, "date_received", "received_date", "date_done")
            state_col = pick_column(cols, "state", "status")
            partner_id_col = pick_column(cols, "partner_id", "partnerid", "supplier_id", "supplierid", "labo_id", "laboid")
            partner_name_col = pick_column(cols, "partner_name", "partnername", "supplier_name", "suppliername", "labo_name", "laboname")
            company_id_col = pick_column(cols, "company_id", "companyid")
            company_name_col = pick_column(cols, "company_name", "companyname")
            amount_col = pick_column(cols, "amount", "amount_total", "total", "price_total")
            warranty_col = pick_column(cols, "warranty", "warranty_name", "warranty_code")
            note_col = pick_column(cols, "note", "memo", "description")
            customer_name_col = pick_column(cols, "customer_name", "customername", "patient_name", "patientname")
            product_name_col = pick_column(cols, "product_name", "productname", "service_name")

            joins: list[str] = []
            partner_name_expr = (
                f'l.{quote_ident(partner_name_col)}' if partner_name_col else "NULL::text"
            )
            company_name_expr = (
                f'l.{quote_ident(company_name_col)}' if company_name_col else "NULL::text"
            )

            if not partner_name_col and partner_id_col:
                partners_table = resolve_table(conn, "partners", "res_partners", "respartners")
                if partners_table:
                    partner_cols = table_columns(conn, partners_table)
                    p_id_col = pick_column(partner_cols, "id")
                    p_name_col = pick_column(partner_cols, "name", "display_name")
                    if p_id_col and p_name_col:
                        joins.append(
                            f" LEFT JOIN {partners_table.qualified_name} pt"
                            f" ON l.{quote_ident(partner_id_col)} = pt.{quote_ident(p_id_col)}"
                        )
                        partner_name_expr = f"pt.{quote_ident(p_name_col)}"

            if not company_name_col and company_id_col:
                companies_table = resolve_table(conn, "companies", "company")
                if companies_table:
                    company_cols = table_columns(conn, companies_table)
                    c_id_col = pick_column(company_cols, "id")
                    c_name_col = pick_column(company_cols, "name", "display_name")
                    if c_id_col and c_name_col:
                        joins.append(
                            f" LEFT JOIN {companies_table.qualified_name} c"
                            f" ON l.{quote_ident(company_id_col)} = c.{quote_ident(c_id_col)}"
                        )
                        company_name_expr = f"c.{quote_ident(c_name_col)}"

            amount_expr = f"COALESCE(l.{quote_ident(amount_col)}, 0)" if amount_col else "0::numeric"

            select_fields = [
                f'l.{quote_ident(id_col)}::text AS id',
                (f"COALESCE(l.{quote_ident(name_col)}, l.{quote_ident(id_col)}::text) AS name"
                 if name_col else f'l.{quote_ident(id_col)}::text AS name'),
                (f'l.{quote_ident(date_col)} AS date' if date_col else "NULL::timestamp AS date"),
                (f'l.{quote_ident(date_planned_col)} AS "datePlanned"'
                 if date_planned_col else 'NULL::timestamp AS "datePlanned"'),
                (f'l.{quote_ident(date_received_col)} AS "dateReceived"'
                 if date_received_col else 'NULL::timestamp AS "dateReceived"'),
                (f'l.{quote_ident(state_col)} AS state' if state_col else "NULL::text AS state"),
                f'{partner_name_expr} AS "partnerName"',
                (f'l.{quote_ident(company_id_col)}::text AS "companyId"'
                 if company_id_col else 'NULL::text AS "companyId"'),
                f'{company_name_expr} AS "companyName"',
                f'{amount_expr} AS amount',
                (f'l.{quote_ident(warranty_col)} AS warranty'
                 if warranty_col else "NULL::text AS warranty"),
                (f'l.{quote_ident(note_col)} AS note' if note_col else "NULL::text AS note"),
                (f'l.{quote_ident(customer_name_col)} AS "customerName"'
                 if customer_name_col else 'NULL::text AS "customerName"'),
                (f'l.{quote_ident(product_name_col)} AS "productName"'
                 if product_name_col else 'NULL::text AS "productName"'),
            ]

            where_clauses: list[str] = []
            params: list = []

            if companyId:
                if not company_id_col:
                    return empty_page(effective_offset, effective_limit)
                where_clauses.append(f"l.{quote_ident(company_id_col)}::text = %s")
                params.append(companyId)

            if state:
                if not state_col:
                    return empty_page(effective_offset, effective_limit)
                where_clauses.append(f"LOWER(COALESCE(l.{quote_ident(state_col)}::text, '')) = %s")
                params.append(state.strip().lower())

            if search.strip():
                pattern = f"%{search.strip()}%"
                search_parts: list[str] = []
                if name_col:
                    search_parts.append(f"l.{quote_ident(name_col)} ILIKE %s")
                    params.append(pattern)
                if partner_name_col:
                    search_parts.append(f"l.{quote_ident(partner_name_col)} ILIKE %s")
                    params.append(pattern)
                if customer_name_col:
                    search_parts.append(f"l.{quote_ident(customer_name_col)} ILIKE %s")
                    params.append(pattern)
                if search_parts:
                    where_clauses.append("(" + " OR ".join(search_parts) + ")")

            if dateFrom:
                if not date_col:
                    return empty_page(effective_offset, effective_limit)
                where_clauses.append(f"l.{quote_ident(date_col)}::date >= %s")
                params.append(dateFrom)
            if dateTo:
                if not date_col:
                    return empty_page(effective_offset, effective_limit)
                where_clauses.append(f"l.{quote_ident(date_col)}::date <= %s")
                params.append(dateTo)

            base_query = (
                f"SELECT {', '.join(select_fields)} FROM {labo_table.qualified_name} l"
                + "".join(joins)
            )
            if where_clauses:
                base_query += " WHERE " + " AND ".join(where_clauses)
            if date_col:
                base_query += (
                    f" ORDER BY l.{quote_ident(date_col)} DESC NULLS LAST, "
                    f"l.{quote_ident(id_col)} DESC"
                )
            else:
                base_query += f" ORDER BY l.{quote_ident(id_col)} DESC"

            return paginate(
                query=base_query,
                params=tuple(params),
                conn=conn,
                offset=effective_offset,
                limit=effective_limit,
            )
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")


def _stock_move_filters(
    *,
    context: dict,
    company_id: str | None,
    product_id: str | None,
    picking_type: str | None,
    date_from: date | None,
    date_to: date | None,
    search: str,
) -> tuple[list[str] | None, list]:
    where_clauses: list[str] = []
    params: list = []

    if company_id:
        if not context["company_id_col"]:
            return None, []
        where_clauses.append(f"m.{quote_ident(context['company_id_col'])}::text = %s")
        params.append(company_id)

    if product_id:
        if not context["product_id_col"]:
            return None, []
        where_clauses.append(f"m.{quote_ident(context['product_id_col'])}::text = %s")
        params.append(product_id)

    if picking_type:
        if context["picking_type_filter_expr"]:
            where_clauses.append(f"{context['picking_type_filter_expr']} = %s")
            params.append(picking_type.strip().lower())
        else:
            return None, []

    if date_from:
        if not context["date_col"]:
            return None, []
        where_clauses.append(f"m.{quote_ident(context['date_col'])}::date >= %s")
        params.append(date_from)

    if date_to:
        if not context["date_col"]:
            return None, []
        where_clauses.append(f"m.{quote_ident(context['date_col'])}::date <= %s")
        params.append(date_to)

    search_text = search.strip()
    if search_text:
        pattern = f"%{search_text}%"
        where_clauses.append(f"{context['product_name_expr']} ILIKE %s")
        params.append(pattern)

    return where_clauses, params


def _stock_move_context(conn) -> dict | None:
    table = resolve_table(
        conn,
        "stock_moves",
        "stockmove",
        "stockmoves",
    )
    if not table:
        return None

    cols = table_columns(conn, table)
    id_col = pick_column(cols, "id")
    if not id_col:
        return None

    date_col = pick_column(cols, "date", "date_done", "create_date", "created_at")
    company_id_col = pick_column(cols, "company_id", "companyid")
    company_name_col = pick_column(cols, "company_name", "companyname")
    product_id_col = pick_column(cols, "product_id", "productid")
    product_name_col = pick_column(cols, "product_name", "productname")
    qty_col = pick_column(cols, "quantity_done", "qty_done", "quantity", "product_qty", "qty")
    state_col = pick_column(cols, "state", "status")
    picking_id_col = pick_column(cols, "picking_id", "pickingid")
    picking_type_col = pick_column(cols, "picking_type", "picking_type_code", "direction", "type")
    picking_type_id_col = pick_column(cols, "picking_type_id", "pickingtypeid")
    reference_col = pick_column(cols, "reference", "ref", "origin", "name")
    direction_col = pick_column(cols, "direction", "move_type", "type", "picking_type", "picking_type_code")
    is_in_col = pick_column(cols, "is_in", "isin", "is_inbound", "isinbound")

    joins = ""
    product_name_expr = (
        f'm.{quote_ident(product_name_col)}' if product_name_col else "NULL::text"
    )
    company_name_expr = (
        f'm.{quote_ident(company_name_col)}' if company_name_col else "NULL::text"
    )
    reference_expr = (
        f'm.{quote_ident(reference_col)}' if reference_col else "NULL::text"
    )

    if not product_name_col and product_id_col:
        products_table = resolve_table(conn, "products", "product")
        if products_table:
            product_cols = table_columns(conn, products_table)
            p_id_col = pick_column(product_cols, "id")
            p_name_col = pick_column(product_cols, "name", "display_name")
            if p_id_col and p_name_col:
                joins += (
                    f" LEFT JOIN {products_table.qualified_name} pr"
                    f" ON m.{quote_ident(product_id_col)} = pr.{quote_ident(p_id_col)}"
                )
                product_name_expr = f"pr.{quote_ident(p_name_col)}"

    if not company_name_col and company_id_col:
        companies_table = resolve_table(conn, "companies", "company")
        if companies_table:
            company_cols = table_columns(conn, companies_table)
            c_id_col = pick_column(company_cols, "id")
            c_name_col = pick_column(company_cols, "name", "display_name")
            if c_id_col and c_name_col:
                joins += (
                    f" LEFT JOIN {companies_table.qualified_name} c"
                    f" ON m.{quote_ident(company_id_col)} = c.{quote_ident(c_id_col)}"
                )
                company_name_expr = f"c.{quote_ident(c_name_col)}"

    picking_join_type_col = None
    picking_type_expr = (
        f"LOWER(COALESCE(m.{quote_ident(picking_type_col)}::text, ''))"
        if picking_type_col
        else "NULL::text"
    )
    picking_type_filter_expr = (
        f"LOWER(COALESCE(m.{quote_ident(picking_type_col)}::text, ''))"
        if picking_type_col
        else None
    )

    picking_types_table = resolve_table(
        conn,
        "stock_picking_types",
        "stockpickingtypes",
        "stock_picking_type",
    )
    picking_type_cols = table_columns(conn, picking_types_table) if picking_types_table else ()
    spt_id_col = pick_column(picking_type_cols, "id") if picking_types_table else None
    spt_code_col = pick_column(picking_type_cols, "code") if picking_types_table else None
    spt_name_col = pick_column(picking_type_cols, "name", "display_name") if picking_types_table else None
    picking_type_display_col = spt_code_col or spt_name_col

    if (
        not picking_type_col
        and picking_type_id_col
        and picking_types_table
        and spt_id_col
        and picking_type_display_col
    ):
        joins += (
            f" LEFT JOIN {picking_types_table.qualified_name} sptm"
            f" ON m.{quote_ident(picking_type_id_col)} = sptm.{quote_ident(spt_id_col)}"
        )
        picking_type_expr = (
            f"LOWER(COALESCE(sptm.{quote_ident(picking_type_display_col)}::text, ''))"
        )
        picking_type_filter_expr = (
            f"LOWER(COALESCE(sptm.{quote_ident(picking_type_display_col)}::text, ''))"
        )

    if picking_id_col:
        pickings_table = resolve_table(conn, "stock_pickings", "stockpicking", "stockpickings")
        if pickings_table:
            picking_cols = table_columns(conn, pickings_table)
            sp_id_col = pick_column(picking_cols, "id")
            picking_join_type_col = pick_column(
                picking_cols,
                "picking_type",
                "picking_type_code",
                "type",
                "direction",
            )
            sp_picking_type_id_col = pick_column(picking_cols, "picking_type_id", "pickingtypeid")
            sp_name_col = pick_column(picking_cols, "name", "display_name", "reference")
            if sp_id_col:
                joins += (
                    f" LEFT JOIN {pickings_table.qualified_name} sp"
                    f" ON m.{quote_ident(picking_id_col)} = sp.{quote_ident(sp_id_col)}"
                )
                if not reference_col and sp_name_col:
                    reference_expr = f"sp.{quote_ident(sp_name_col)}"
                if not picking_type_filter_expr and picking_join_type_col:
                    picking_type_expr = (
                        f"LOWER(COALESCE(sp.{quote_ident(picking_join_type_col)}::text, ''))"
                    )
                    picking_type_filter_expr = (
                        f"LOWER(COALESCE(sp.{quote_ident(picking_join_type_col)}::text, ''))"
                    )
                if (
                    not picking_type_filter_expr
                    and sp_picking_type_id_col
                    and picking_types_table
                    and spt_id_col
                    and picking_type_display_col
                ):
                    joins += (
                        f" LEFT JOIN {picking_types_table.qualified_name} sptp"
                        f" ON sp.{quote_ident(sp_picking_type_id_col)} = sptp.{quote_ident(spt_id_col)}"
                    )
                    picking_type_expr = (
                        f"LOWER(COALESCE(sptp.{quote_ident(picking_type_display_col)}::text, ''))"
                    )
                    picking_type_filter_expr = (
                        f"LOWER(COALESCE(sptp.{quote_ident(picking_type_display_col)}::text, ''))"
                    )

    qty_expr = (
        f"COALESCE(m.{quote_ident(qty_col)}, 0)"
        if qty_col
        else "0::numeric"
    )
    qty_abs_expr = (
        f"ABS(COALESCE(m.{quote_ident(qty_col)}, 0))"
        if qty_col
        else "0::numeric"
    )

    incoming_condition = "TRUE"
    outgoing_condition = "FALSE"
    if direction_col:
        incoming_values = ", ".join([f"'{value}'" for value in _INCOMING_TYPES])
        outgoing_values = ", ".join([f"'{value}'" for value in _OUTGOING_TYPES])
        incoming_condition = (
            f"LOWER(COALESCE(m.{quote_ident(direction_col)}::text, '')) IN ({incoming_values})"
        )
        outgoing_condition = (
            f"LOWER(COALESCE(m.{quote_ident(direction_col)}::text, '')) IN ({outgoing_values})"
        )
    elif picking_type_col:
        incoming_values = ", ".join([f"'{value}'" for value in _INCOMING_TYPES])
        outgoing_values = ", ".join([f"'{value}'" for value in _OUTGOING_TYPES])
        incoming_condition = (
            f"LOWER(COALESCE(m.{quote_ident(picking_type_col)}::text, '')) IN ({incoming_values})"
        )
        outgoing_condition = (
            f"LOWER(COALESCE(m.{quote_ident(picking_type_col)}::text, '')) IN ({outgoing_values})"
        )
    elif picking_type_filter_expr:
        incoming_values = ", ".join([f"'{value}'" for value in _INCOMING_TYPES])
        outgoing_values = ", ".join([f"'{value}'" for value in _OUTGOING_TYPES])
        incoming_condition = f"{picking_type_filter_expr} IN ({incoming_values})"
        outgoing_condition = f"{picking_type_filter_expr} IN ({outgoing_values})"
    elif is_in_col:
        incoming_condition = f"COALESCE(m.{quote_ident(is_in_col)}, FALSE) = TRUE"
        outgoing_condition = f"COALESCE(m.{quote_ident(is_in_col)}, FALSE) = FALSE"
    elif qty_col:
        incoming_condition = f"COALESCE(m.{quote_ident(qty_col)}, 0) >= 0"
        outgoing_condition = f"COALESCE(m.{quote_ident(qty_col)}, 0) < 0"

    return {
        "table": table,
        "id_col": id_col,
        "date_col": date_col,
        "company_id_col": company_id_col,
        "company_name_col": company_name_col,
        "product_id_col": product_id_col,
        "product_name_col": product_name_col,
        "qty_col": qty_col,
        "state_col": state_col,
        "picking_id_col": picking_id_col,
        "picking_type_col": picking_type_col,
        "picking_type_id_col": picking_type_id_col,
        "picking_join_type_col": picking_join_type_col,
        "picking_type_filter_expr": picking_type_filter_expr,
        "joins": joins,
        "product_name_expr": product_name_expr,
        "company_name_expr": company_name_expr,
        "qty_expr": qty_expr,
        "qty_abs_expr": qty_abs_expr,
        "picking_type_expr": picking_type_expr,
        "reference_expr": reference_expr,
        "incoming_condition": incoming_condition,
        "outgoing_condition": outgoing_condition,
    }
