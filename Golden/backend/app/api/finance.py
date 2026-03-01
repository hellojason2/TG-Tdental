"""Finance and cashbook API endpoints."""

from __future__ import annotations

from datetime import date

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

router = APIRouter(prefix="/api", tags=["finance"])

_INBOUND_TYPES = ("inbound", "incoming", "in", "receipt", "customer", "thu")
_OUTBOUND_TYPES = ("outbound", "outgoing", "out", "payment", "vendor", "chi")


@router.get("/payments")
async def list_payments(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=0, le=500),
    offset: int | None = Query(default=None, ge=0),
    limit: int | None = Query(default=None, ge=0, le=5000),
    companyId: str | None = Query(default=None),
    partnerId: str | None = Query(default=None),
    paymentType: str | None = Query(default=None),
    dateFrom: date | None = Query(default=None),
    dateTo: date | None = Query(default=None),
    state: str | None = Query(default=None),
    _user: dict = Depends(require_auth),
):
    """Return paginated cashbook payments with optional filters."""
    effective_offset, effective_limit = page_window(
        page=page,
        per_page=per_page,
        offset=offset,
        limit=limit,
        default_limit=20,
    )

    try:
        with get_conn() as conn:
            payments_table = resolve_table(
                conn,
                "account_payments",
                "accountpayments",
                "accountpayment",
                "sale_order_payments",
                "saleorderpayments",
                "customer_receipts",
                "customerreceipts",
                "payments",
                "payment",
            )
            if not payments_table:
                return empty_page(effective_offset, effective_limit)

            cols = table_columns(conn, payments_table)
            id_col = pick_column(cols, "id")
            if not id_col:
                return empty_page(effective_offset, effective_limit)

            name_col = pick_column(cols, "name", "display_name", "description", "reference", "ref")
            date_col = pick_column(cols, "date", "payment_date", "created_at", "created_date")
            amount_col = pick_column(cols, "amount", "amount_total", "payment_amount", "total")
            payment_type_col = pick_column(cols, "payment_type", "paymenttype", "type", "direction")
            journal_id_col = pick_column(cols, "journal_id", "journalid")
            journal_name_col = pick_column(cols, "journal_name", "journalname")
            partner_id_col = pick_column(cols, "partner_id", "partnerid", "customer_id", "customerid")
            partner_name_col = pick_column(cols, "partner_name", "partnername", "customer_name", "customername")
            company_id_col = pick_column(cols, "company_id", "companyid")
            company_name_col = pick_column(cols, "company_name", "companyname")
            state_col = pick_column(cols, "state", "status")

            joins: list[str] = []
            partner_name_expr = (
                f't.{quote_ident(partner_name_col)}' if partner_name_col else "NULL::text"
            )
            journal_name_expr = (
                f't.{quote_ident(journal_name_col)}' if journal_name_col else "NULL::text"
            )
            company_name_expr = (
                f't.{quote_ident(company_name_col)}' if company_name_col else "NULL::text"
            )

            if not partner_name_col and partner_id_col:
                partners_table = resolve_table(conn, "partners", "res_partners", "respartners")
                if partners_table:
                    partner_cols = table_columns(conn, partners_table)
                    p_id_col = pick_column(partner_cols, "id")
                    p_name_col = pick_column(partner_cols, "name", "display_name")
                    if p_id_col and p_name_col:
                        joins.append(
                            f" LEFT JOIN {partners_table.qualified_name} p"
                            f" ON t.{quote_ident(partner_id_col)} = p.{quote_ident(p_id_col)}"
                        )
                        partner_name_expr = f"p.{quote_ident(p_name_col)}"

            if not journal_name_col and journal_id_col:
                journals_table = resolve_table(
                    conn,
                    "account_journals",
                    "accountjournals",
                    "journals",
                    "journal",
                )
                if journals_table:
                    journal_cols = table_columns(conn, journals_table)
                    j_id_col = pick_column(journal_cols, "id")
                    j_name_col = pick_column(journal_cols, "name", "display_name")
                    if j_id_col and j_name_col:
                        joins.append(
                            f" LEFT JOIN {journals_table.qualified_name} j"
                            f" ON t.{quote_ident(journal_id_col)} = j.{quote_ident(j_id_col)}"
                        )
                        journal_name_expr = f"j.{quote_ident(j_name_col)}"

            if not company_name_col and company_id_col:
                companies_table = resolve_table(conn, "companies", "company")
                if companies_table:
                    company_cols = table_columns(conn, companies_table)
                    c_id_col = pick_column(company_cols, "id")
                    c_name_col = pick_column(company_cols, "name", "display_name")
                    if c_id_col and c_name_col:
                        joins.append(
                            f" LEFT JOIN {companies_table.qualified_name} c"
                            f" ON t.{quote_ident(company_id_col)} = c.{quote_ident(c_id_col)}"
                        )
                        company_name_expr = f"c.{quote_ident(c_name_col)}"

            amount_expr = (
                f"COALESCE(t.{quote_ident(amount_col)}, 0)"
                if amount_col
                else "0::numeric"
            )
            payment_type_expr = (
                f"LOWER(COALESCE(t.{quote_ident(payment_type_col)}::text, ''))"
                if payment_type_col
                else f"CASE WHEN {amount_expr} < 0 THEN 'outbound' ELSE 'inbound' END"
            )

            select_fields = [
                f't.{quote_ident(id_col)}::text AS id',
                (
                    f"COALESCE(t.{quote_ident(name_col)}, t.{quote_ident(id_col)}::text) AS name"
                    if name_col
                    else f't.{quote_ident(id_col)}::text AS name'
                ),
                (
                    f't.{quote_ident(date_col)} AS date'
                    if date_col
                    else "NULL::timestamp AS date"
                ),
                f"{amount_expr} AS amount",
                f'{payment_type_expr} AS "paymentType"',
                f'{journal_name_expr} AS "journalName"',
                f'{partner_name_expr} AS "partnerName"',
                (
                    f't.{quote_ident(state_col)} AS state'
                    if state_col
                    else "NULL::text AS state"
                ),
                (
                    f't.{quote_ident(company_id_col)}::text AS "companyId"'
                    if company_id_col
                    else 'NULL::text AS "companyId"'
                ),
                f'{company_name_expr} AS "companyName"',
            ]

            where_clauses: list[str] = []
            params: list = []

            if companyId:
                if not company_id_col:
                    return empty_page(effective_offset, effective_limit)
                where_clauses.append(f"t.{quote_ident(company_id_col)}::text = %s")
                params.append(companyId)

            if partnerId:
                if not partner_id_col:
                    return empty_page(effective_offset, effective_limit)
                where_clauses.append(f"t.{quote_ident(partner_id_col)}::text = %s")
                params.append(partnerId)

            if dateFrom:
                if not date_col:
                    return empty_page(effective_offset, effective_limit)
                where_clauses.append(f"t.{quote_ident(date_col)}::date >= %s")
                params.append(dateFrom)
            if dateTo:
                if not date_col:
                    return empty_page(effective_offset, effective_limit)
                where_clauses.append(f"t.{quote_ident(date_col)}::date <= %s")
                params.append(dateTo)

            if state:
                if not state_col:
                    return empty_page(effective_offset, effective_limit)
                where_clauses.append(f"LOWER(COALESCE(t.{quote_ident(state_col)}::text, '')) = %s")
                params.append(state.strip().lower())

            if paymentType:
                normalized_type = paymentType.strip().lower()
                if payment_type_col:
                    if normalized_type in _INBOUND_TYPES:
                        placeholders = ", ".join(["%s"] * len(_INBOUND_TYPES))
                        where_clauses.append(
                            f"LOWER(COALESCE(t.{quote_ident(payment_type_col)}::text, '')) IN ({placeholders})"
                        )
                        params.extend(_INBOUND_TYPES)
                    elif normalized_type in _OUTBOUND_TYPES:
                        placeholders = ", ".join(["%s"] * len(_OUTBOUND_TYPES))
                        where_clauses.append(
                            f"LOWER(COALESCE(t.{quote_ident(payment_type_col)}::text, '')) IN ({placeholders})"
                        )
                        params.extend(_OUTBOUND_TYPES)
                    else:
                        where_clauses.append(
                            f"LOWER(COALESCE(t.{quote_ident(payment_type_col)}::text, '')) = %s"
                        )
                        params.append(normalized_type)
                elif amount_col:
                    if normalized_type in _INBOUND_TYPES:
                        where_clauses.append(f"{amount_expr} >= 0")
                    elif normalized_type in _OUTBOUND_TYPES:
                        where_clauses.append(f"{amount_expr} < 0")
                    else:
                        return empty_page(effective_offset, effective_limit)
                else:
                    return empty_page(effective_offset, effective_limit)

            base_query = (
                f"SELECT {', '.join(select_fields)} "
                f"FROM {payments_table.qualified_name} t"
                + "".join(joins)
            )
            if where_clauses:
                base_query += " WHERE " + " AND ".join(where_clauses)

            if date_col:
                base_query += (
                    f" ORDER BY t.{quote_ident(date_col)} DESC NULLS LAST, "
                    f"t.{quote_ident(id_col)} DESC"
                )
            else:
                base_query += f" ORDER BY t.{quote_ident(id_col)} DESC"

            return paginate(
                query=base_query,
                params=tuple(params),
                conn=conn,
                offset=effective_offset,
                limit=effective_limit,
            )
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")
