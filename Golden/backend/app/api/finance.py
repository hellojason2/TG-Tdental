"""Finance and cashbook API endpoints."""

from __future__ import annotations

from datetime import date as dt_date, datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
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

router = APIRouter(prefix="/api", tags=["finance"])

_INBOUND_TYPES = ("inbound", "incoming", "in", "receipt", "customer", "thu")
_OUTBOUND_TYPES = ("outbound", "outgoing", "out", "payment", "vendor", "chi")


class PaymentCreateRequest(BaseModel):
    date: dt_date | None = None
    paymentType: str = "inbound"
    method: str = "cash"
    category: str | None = None
    partnerName: str | None = None
    partnerId: str | None = None
    companyId: str | None = None
    journalId: str | None = None
    amount: float = Field(gt=0)
    note: str | None = None
    state: str | None = None


def _normalize_payment_type(value: str | None) -> str:
    normalized = (value or "").strip().lower()
    if normalized in _OUTBOUND_TYPES:
        return "outbound"
    if normalized in _INBOUND_TYPES:
        return "inbound"
    if normalized in {"transfer", "internal"}:
        return "transfer"
    return "inbound"


def _build_payment_name(payment_type: str) -> str:
    now = datetime.utcnow()
    prefix = "PMT" if payment_type == "outbound" else "RCT"
    return f"MANUAL.{prefix}/{now:%Y%m%d}/{uuid4().hex[:6].upper()}"


def _resolve_default_journal(
    conn,
    *,
    method: str,
    company_id: str | None,
) -> dict | None:
    journals_table = resolve_table(
        conn,
        "account_journals",
        "accountjournals",
        "journals",
        "journal",
    )
    if not journals_table:
        return None

    cols = table_columns(conn, journals_table)
    id_col = pick_column(cols, "id")
    name_col = pick_column(cols, "name", "display_name")
    type_col = pick_column(cols, "type", "journal_type")
    company_id_col = pick_column(cols, "company_id", "companyid")
    active_col = pick_column(cols, "active", "is_active")
    if not id_col:
        return None

    select_fields = [f"j.{quote_ident(id_col)}::text AS id"]
    select_fields.append(
        f"j.{quote_ident(name_col)} AS name" if name_col else "NULL::text AS name"
    )
    select_fields.append(
        f"j.{quote_ident(type_col)} AS type" if type_col else "NULL::text AS type"
    )
    select_fields.append(
        f'j.{quote_ident(company_id_col)}::text AS "companyId"'
        if company_id_col
        else 'NULL::text AS "companyId"'
    )
    select_fields.append(
        f"COALESCE(j.{quote_ident(active_col)}, TRUE) AS active"
        if active_col
        else "TRUE AS active"
    )

    where_clauses: list[str] = []
    params: list = []
    if company_id and company_id_col:
        where_clauses.append(f"j.{quote_ident(company_id_col)}::text = %s")
        params.append(company_id)
    if active_col:
        where_clauses.append(f"COALESCE(j.{quote_ident(active_col)}, TRUE) = TRUE")

    query = (
        f"SELECT {', '.join(select_fields)} "
        f"FROM {journals_table.qualified_name} j"
    )
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)
    query += " ORDER BY j." + quote_ident(id_col) + " ASC LIMIT 200"

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(query, tuple(params))
        rows = [dict(row) for row in cur.fetchall()]

    if not rows and company_id and company_id_col:
        fallback_query = (
            f"SELECT {', '.join(select_fields)} "
            f"FROM {journals_table.qualified_name} j"
        )
        if active_col:
            fallback_query += f" WHERE COALESCE(j.{quote_ident(active_col)}, TRUE) = TRUE"
        fallback_query += " ORDER BY j." + quote_ident(id_col) + " ASC LIMIT 200"
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(fallback_query)
            rows = [dict(row) for row in cur.fetchall()]

    if not rows:
        return None

    wants_bank = (method or "").strip().lower() in {"bank", "transfer", "wire", "card"}

    def score(row: dict) -> int:
        text = f"{row.get('type') or ''} {row.get('name') or ''}".lower()
        row_company_id = str(row.get("companyId") or "")
        row_score = 0
        if wants_bank:
            if "bank" in text or "chuyển khoản" in text:
                row_score += 20
            if "cash" in text or "tiền mặt" in text:
                row_score -= 4
        else:
            if "cash" in text or "tiền mặt" in text:
                row_score += 20
            if "bank" in text or "chuyển khoản" in text:
                row_score -= 4
        if company_id and row_company_id == company_id:
            row_score += 10
        if row.get("active") is True:
            row_score += 3
        return row_score

    rows.sort(key=score, reverse=True)
    return rows[0]


def create_payment_record(conn, payload: PaymentCreateRequest, user: dict | None) -> dict:
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
        raise HTTPException(status_code=503, detail="Payment table is unavailable")

    cols = table_columns(conn, payments_table)
    id_col = pick_column(cols, "id")
    date_col = pick_column(cols, "date", "payment_date", "paymentdate", "created_at", "created_date")
    amount_col = pick_column(cols, "amount", "amount_total", "payment_amount", "total")
    payment_type_col = pick_column(cols, "payment_type", "paymenttype", "type", "direction")
    journal_id_col = pick_column(cols, "journal_id", "journalid")
    if not all([id_col, date_col, amount_col, payment_type_col, journal_id_col]):
        raise HTTPException(status_code=500, detail="Payments schema does not support inserts")

    name_col = pick_column(cols, "name", "display_name", "description", "reference", "ref")
    state_col = pick_column(cols, "state", "status")
    communication_col = pick_column(cols, "communication", "note", "memo", "description", "reason")
    company_id_col = pick_column(cols, "company_id", "companyid")
    partner_id_col = pick_column(cols, "partner_id", "partnerid", "customer_id", "customerid")
    method_col = pick_column(cols, "payment_method", "paymentmethod", "method")
    date_created_col = pick_column(cols, "date_created", "datecreated", "created_at", "createdat")
    last_updated_col = pick_column(cols, "last_updated", "lastupdated", "updated_at", "updatedat")
    intercompany_col = pick_column(cols, "is_intercompany", "isintercompany")
    prepayment_col = pick_column(cols, "is_prepayment", "isprepayment")

    payment_type = _normalize_payment_type(payload.paymentType)
    payment_name = _build_payment_name(payment_type)
    payment_date = datetime.combine(payload.date or dt_date.today(), datetime.min.time())
    journal_row = None
    if payload.journalId:
        journal_row = {"id": payload.journalId, "companyId": payload.companyId, "name": None}
    else:
        journal_row = _resolve_default_journal(
            conn,
            method=payload.method,
            company_id=payload.companyId,
        )
    if not journal_row or not journal_row.get("id"):
        raise HTTPException(status_code=400, detail="No active journal is configured")

    company_id = payload.companyId or journal_row.get("companyId")
    message_parts = [payload.partnerName, payload.category, payload.note]
    communication = " - ".join([part.strip() for part in message_parts if part and part.strip()]) or None

    insert_cols: list[str] = [id_col, date_col, amount_col, payment_type_col, journal_id_col]
    insert_vals: list = [str(uuid4()), payment_date, float(payload.amount), payment_type, journal_row["id"]]

    if name_col:
        insert_cols.append(name_col)
        insert_vals.append(payment_name)
    if state_col:
        insert_cols.append(state_col)
        insert_vals.append((payload.state or "draft").strip().lower())
    if communication_col:
        insert_cols.append(communication_col)
        insert_vals.append(communication)
    if company_id_col and company_id:
        insert_cols.append(company_id_col)
        insert_vals.append(company_id)
    if partner_id_col and payload.partnerId:
        insert_cols.append(partner_id_col)
        insert_vals.append(payload.partnerId)
    if method_col:
        insert_cols.append(method_col)
        insert_vals.append(payload.method)
    if intercompany_col:
        insert_cols.append(intercompany_col)
        insert_vals.append(False)
    if prepayment_col:
        insert_cols.append(prepayment_col)
        insert_vals.append(False)

    now = datetime.utcnow()
    if date_created_col:
        insert_cols.append(date_created_col)
        insert_vals.append(now)
    if last_updated_col:
        insert_cols.append(last_updated_col)
        insert_vals.append(now)

    placeholders = ", ".join(["%s"] * len(insert_cols))
    columns_sql = ", ".join(quote_ident(col) for col in insert_cols)
    insert_sql = (
        f"INSERT INTO {payments_table.qualified_name} ({columns_sql}) "
        f"VALUES ({placeholders})"
    )
    with conn.cursor() as cur:
        cur.execute(insert_sql, tuple(insert_vals))

    return {
        "id": insert_vals[0],
        "name": payment_name,
        "date": payment_date.isoformat(),
        "amount": float(payload.amount),
        "paymentType": payment_type,
        "journalId": journal_row["id"],
        "journalName": journal_row.get("name"),
        "partnerName": payload.partnerName,
        "state": (payload.state or "draft").strip().lower(),
        "companyId": company_id,
        "communication": communication,
    }


@router.post("/payments")
async def create_payment(
    payload: PaymentCreateRequest,
    _user: dict = Depends(require_auth),
):
    """Create a payment voucher used by cashbook and salary-advance flows."""
    try:
        with get_conn() as conn:
            return create_payment_record(conn, payload, _user)
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")


@router.get("/payments")
async def list_payments(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=0, le=500),
    offset: int | None = Query(default=None, ge=0),
    limit: int | None = Query(default=None, ge=0, le=5000),
    companyId: str | None = Query(default=None),
    partnerId: str | None = Query(default=None),
    paymentType: str | None = Query(default=None),
    dateFrom: dt_date | None = Query(default=None),
    dateTo: dt_date | None = Query(default=None),
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
            date_col = pick_column(cols, "date", "payment_date", "paymentdate", "created_at", "created_date")
            amount_col = pick_column(cols, "amount", "amount_total", "payment_amount", "total")
            payment_type_col = pick_column(cols, "payment_type", "paymenttype", "type", "direction")
            journal_id_col = pick_column(cols, "journal_id", "journalid")
            journal_name_col = pick_column(cols, "journal_name", "journalname")
            partner_id_col = pick_column(cols, "partner_id", "partnerid", "customer_id", "customerid")
            partner_name_col = pick_column(cols, "partner_name", "partnername", "customer_name", "customername")
            company_id_col = pick_column(cols, "company_id", "companyid")
            company_name_col = pick_column(cols, "company_name", "companyname")
            state_col = pick_column(cols, "state", "status")
            communication_col = pick_column(cols, "communication", "note", "memo", "description", "reason")

            joins: list[str] = []
            partner_name_expr = (
                f't.{quote_ident(partner_name_col)}'
                if partner_name_col
                else (
                    f't.{quote_ident(communication_col)}'
                    if communication_col
                    else "NULL::text"
                )
            )
            journal_name_expr = (
                f't.{quote_ident(journal_name_col)}' if journal_name_col else "NULL::text"
            )
            company_name_expr = (
                f't.{quote_ident(company_name_col)}' if company_name_col else "NULL::text"
            )
            communication_expr = (
                f't.{quote_ident(communication_col)}'
                if communication_col
                else "NULL::text"
            )

            if not partner_name_col and partner_id_col:
                partners_table = resolve_table(conn, "partners", "res_partners", "respartners")
                if partners_table:
                    partner_cols = table_columns(conn, partners_table)
                    p_id_col = pick_column(partner_cols, "id")
                    p_name_col = pick_column(partner_cols, "name", "display_name")
                    if p_id_col and p_name_col:
                        partner_fallback = (
                            f"t.{quote_ident(communication_col)}"
                            if communication_col
                            else "NULL::text"
                        )
                        joins.append(
                            f" LEFT JOIN {partners_table.qualified_name} p"
                            f" ON t.{quote_ident(partner_id_col)} = p.{quote_ident(p_id_col)}"
                        )
                        partner_name_expr = f"COALESCE(p.{quote_ident(p_name_col)}, {partner_fallback})"

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
                (
                    f't.{quote_ident(partner_id_col)}::text AS "partnerId"'
                    if partner_id_col
                    else 'NULL::text AS "partnerId"'
                ),
                f'{partner_name_expr} AS "partnerName"',
                f'{communication_expr} AS communication',
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


# ---------------------------------------------------------------------------
# GET /api/receipts  (Phieu thu - receipt vouchers)
# ---------------------------------------------------------------------------


@router.get("/receipts")
async def list_receipts(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=0, le=500),
    offset: int | None = Query(default=None, ge=0),
    limit: int | None = Query(default=None, ge=0, le=5000),
    companyId: str | None = Query(default=None),
    search: str = Query(default=""),
    dateFrom: dt_date | None = Query(default=None),
    dateTo: dt_date | None = Query(default=None),
    _user: dict = Depends(require_auth),
):
    """Return receipt vouchers (phieu thu) -- inbound payments."""
    return _payment_type_endpoint(
        type_filter="inbound", page=page, per_page=per_page,
        offset=offset, limit=limit, companyId=companyId,
        dateFrom=dateFrom, dateTo=dateTo,
    )


# ---------------------------------------------------------------------------
# GET /api/payment-vouchers  (Phieu chi - payment vouchers)
# ---------------------------------------------------------------------------


@router.get("/payment-vouchers")
async def list_payment_vouchers(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=0, le=500),
    offset: int | None = Query(default=None, ge=0),
    limit: int | None = Query(default=None, ge=0, le=5000),
    companyId: str | None = Query(default=None),
    search: str = Query(default=""),
    dateFrom: dt_date | None = Query(default=None),
    dateTo: dt_date | None = Query(default=None),
    _user: dict = Depends(require_auth),
):
    """Return payment vouchers (phieu chi) -- outbound payments."""
    return _payment_type_endpoint(
        type_filter="outbound", page=page, per_page=per_page,
        offset=offset, limit=limit, companyId=companyId,
        dateFrom=dateFrom, dateTo=dateTo,
    )


# ---------------------------------------------------------------------------
# GET /api/account-payments  (internal transfers)
# ---------------------------------------------------------------------------


@router.get("/account-payments")
async def list_account_payments(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=0, le=500),
    offset: int | None = Query(default=None, ge=0),
    limit: int | None = Query(default=None, ge=0, le=5000),
    companyId: str | None = Query(default=None),
    search: str = Query(default=""),
    dateFrom: dt_date | None = Query(default=None),
    dateTo: dt_date | None = Query(default=None),
    _user: dict = Depends(require_auth),
):
    """Return all account payments (internal transfers and all types)."""
    effective_offset, effective_limit = page_window(
        page=page, per_page=per_page, offset=offset, limit=limit, default_limit=20,
    )

    try:
        with get_conn() as conn:
            payments_table = resolve_table(
                conn,
                "account_payments", "accountpayments", "accountpayment",
                "sale_order_payments", "saleorderpayments",
                "payments", "payment",
            )
            if not payments_table:
                return empty_page(effective_offset, effective_limit)

            cols = table_columns(conn, payments_table)
            id_col = pick_column(cols, "id")
            if not id_col:
                return empty_page(effective_offset, effective_limit)

            name_col = pick_column(cols, "name", "display_name", "description", "reference", "ref")
            date_col = pick_column(cols, "date", "payment_date", "paymentdate", "created_at", "created_date")
            amount_col = pick_column(cols, "amount", "amount_total", "payment_amount", "total")
            payment_type_col = pick_column(cols, "payment_type", "paymenttype", "type", "direction")
            partner_name_col = pick_column(cols, "partner_name", "partnername", "customer_name")
            partner_id_col = pick_column(cols, "partner_id", "partnerid", "customer_id")
            journal_name_col = pick_column(cols, "journal_name", "journalname")
            journal_id_col = pick_column(cols, "journal_id", "journalid")
            company_id_col = pick_column(cols, "company_id", "companyid")
            state_col = pick_column(cols, "state", "status")
            note_col = pick_column(cols, "note", "memo", "description", "reason")
            communication_col = pick_column(cols, "communication")

            amount_expr = f"COALESCE(t.{quote_ident(amount_col)}, 0)" if amount_col else "0::numeric"
            payment_type_expr = (
                f"LOWER(COALESCE(t.{quote_ident(payment_type_col)}::text, ''))"
                if payment_type_col
                else f"CASE WHEN {amount_expr} < 0 THEN 'outbound' ELSE 'inbound' END"
            )

            joins: list[str] = []
            partner_name_expr = (
                f't.{quote_ident(partner_name_col)}'
                if partner_name_col
                else (
                    f't.{quote_ident(communication_col)}'
                    if communication_col
                    else "NULL::text"
                )
            )
            journal_name_expr = (
                f't.{quote_ident(journal_name_col)}' if journal_name_col else "NULL::text"
            )

            if not partner_name_col and partner_id_col:
                partners_table = resolve_table(conn, "partners", "res_partners", "respartners")
                if partners_table:
                    partner_cols = table_columns(conn, partners_table)
                    p_id_col = pick_column(partner_cols, "id")
                    p_name_col = pick_column(partner_cols, "name", "display_name")
                    if p_id_col and p_name_col:
                        partner_fallback = (
                            f"t.{quote_ident(communication_col)}"
                            if communication_col
                            else "NULL::text"
                        )
                        joins.append(
                            f" LEFT JOIN {partners_table.qualified_name} p"
                            f" ON t.{quote_ident(partner_id_col)} = p.{quote_ident(p_id_col)}"
                        )
                        partner_name_expr = f"COALESCE(p.{quote_ident(p_name_col)}, {partner_fallback})"

            if not journal_name_col and journal_id_col:
                journals_table = resolve_table(
                    conn, "account_journals", "accountjournals", "journals", "journal",
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

            select_fields = [
                f't.{quote_ident(id_col)}::text AS id',
                (f"COALESCE(t.{quote_ident(name_col)}, t.{quote_ident(id_col)}::text) AS name"
                 if name_col else f't.{quote_ident(id_col)}::text AS name'),
                (f't.{quote_ident(date_col)} AS date' if date_col else "NULL::timestamp AS date"),
                f"{amount_expr} AS amount",
                f'{payment_type_expr} AS "paymentType"',
                f'{partner_name_expr} AS "partnerName"',
                f'{journal_name_expr} AS "journalName"',
                (f't.{quote_ident(state_col)} AS state' if state_col else "NULL::text AS state"),
                (f't.{quote_ident(note_col)} AS note' if note_col else "NULL::text AS note"),
                (f't.{quote_ident(company_id_col)}::text AS "companyId"'
                 if company_id_col else 'NULL::text AS "companyId"'),
            ]

            where_clauses: list[str] = []
            params: list = []

            if companyId:
                if not company_id_col:
                    return empty_page(effective_offset, effective_limit)
                where_clauses.append(f"t.{quote_ident(company_id_col)}::text = %s")
                params.append(companyId)

            if search.strip():
                pattern = f"%{search.strip()}%"
                search_parts: list[str] = []
                if name_col:
                    search_parts.append(f"t.{quote_ident(name_col)} ILIKE %s")
                    params.append(pattern)
                if partner_name_col:
                    search_parts.append(f"t.{quote_ident(partner_name_col)} ILIKE %s")
                    params.append(pattern)
                if search_parts:
                    where_clauses.append("(" + " OR ".join(search_parts) + ")")

            if dateFrom and date_col:
                where_clauses.append(f"t.{quote_ident(date_col)}::date >= %s")
                params.append(dateFrom)
            if dateTo and date_col:
                where_clauses.append(f"t.{quote_ident(date_col)}::date <= %s")
                params.append(dateTo)

            base_query = (
                f"SELECT {', '.join(select_fields)} FROM {payments_table.qualified_name} t"
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
                query=base_query, params=tuple(params), conn=conn,
                offset=effective_offset, limit=effective_limit,
            )
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")


# ---------------------------------------------------------------------------
# Shared helper for payment-type filtered endpoints
# ---------------------------------------------------------------------------

def _payment_type_endpoint(
    *,
    type_filter: str,
    page: int,
    per_page: int,
    offset: int | None,
    limit: int | None,
    companyId: str | None,
    dateFrom: dt_date | None,
    dateTo: dt_date | None,
):
    """Shared logic for receipts, expenses, transfers."""
    effective_offset, effective_limit = page_window(
        page=page, per_page=per_page, offset=offset, limit=limit, default_limit=20,
    )

    try:
        with get_conn() as conn:
            payments_table = resolve_table(
                conn,
                "account_payments", "accountpayments", "accountpayment",
                "sale_order_payments", "saleorderpayments",
                "customer_receipts", "customerreceipts",
                "payments", "payment",
            )
            if not payments_table:
                return empty_page(effective_offset, effective_limit)

            cols = table_columns(conn, payments_table)
            id_col = pick_column(cols, "id")
            if not id_col:
                return empty_page(effective_offset, effective_limit)

            name_col = pick_column(cols, "name", "display_name", "description", "reference", "ref")
            date_col = pick_column(cols, "date", "payment_date", "paymentdate", "created_at", "created_date")
            amount_col = pick_column(cols, "amount", "amount_total", "payment_amount", "total")
            payment_type_col = pick_column(cols, "payment_type", "paymenttype", "type", "direction")
            partner_name_col = pick_column(cols, "partner_name", "partnername", "customer_name")
            company_id_col = pick_column(cols, "company_id", "companyid")
            state_col = pick_column(cols, "state", "status")
            note_col = pick_column(cols, "note", "memo", "description", "reason")
            communication_col = pick_column(cols, "communication")

            amount_expr = f"COALESCE(t.{quote_ident(amount_col)}, 0)" if amount_col else "0::numeric"

            select_fields = [
                f't.{quote_ident(id_col)}::text AS id',
                (f"COALESCE(t.{quote_ident(name_col)}, t.{quote_ident(id_col)}::text) AS name"
                 if name_col else f't.{quote_ident(id_col)}::text AS name'),
                (f't.{quote_ident(date_col)} AS date' if date_col else "NULL::timestamp AS date"),
                f"{amount_expr} AS amount",
                (
                    f't.{quote_ident(partner_name_col)} AS "partnerName"'
                    if partner_name_col
                    else (
                        f't.{quote_ident(communication_col)} AS "partnerName"'
                        if communication_col
                        else 'NULL::text AS "partnerName"'
                    )
                ),
                (f't.{quote_ident(state_col)} AS state' if state_col else "NULL::text AS state"),
                (f't.{quote_ident(note_col)} AS note' if note_col else "NULL::text AS note"),
                (f't.{quote_ident(company_id_col)}::text AS "companyId"'
                 if company_id_col else 'NULL::text AS "companyId"'),
            ]

            where_clauses: list[str] = []
            params: list = []

            # Filter by payment type
            if payment_type_col:
                if type_filter == "inbound":
                    placeholders = ", ".join(["%s"] * len(_INBOUND_TYPES))
                    where_clauses.append(
                        f"LOWER(COALESCE(t.{quote_ident(payment_type_col)}::text, '')) IN ({placeholders})"
                    )
                    params.extend(_INBOUND_TYPES)
                elif type_filter == "outbound":
                    placeholders = ", ".join(["%s"] * len(_OUTBOUND_TYPES))
                    where_clauses.append(
                        f"LOWER(COALESCE(t.{quote_ident(payment_type_col)}::text, '')) IN ({placeholders})"
                    )
                    params.extend(_OUTBOUND_TYPES)
                elif type_filter == "transfer":
                    where_clauses.append(
                        f"LOWER(COALESCE(t.{quote_ident(payment_type_col)}::text, '')) IN ('transfer', 'internal')"
                    )
            elif amount_col:
                if type_filter == "inbound":
                    where_clauses.append(f"{amount_expr} >= 0")
                elif type_filter == "outbound":
                    where_clauses.append(f"{amount_expr} < 0")

            if companyId:
                if not company_id_col:
                    return empty_page(effective_offset, effective_limit)
                where_clauses.append(f"t.{quote_ident(company_id_col)}::text = %s")
                params.append(companyId)

            if dateFrom and date_col:
                where_clauses.append(f"t.{quote_ident(date_col)}::date >= %s")
                params.append(dateFrom)
            if dateTo and date_col:
                where_clauses.append(f"t.{quote_ident(date_col)}::date <= %s")
                params.append(dateTo)

            base_query = f"SELECT {', '.join(select_fields)} FROM {payments_table.qualified_name} t"
            if where_clauses:
                base_query += " WHERE " + " AND ".join(where_clauses)
            if date_col:
                base_query += f" ORDER BY t.{quote_ident(date_col)} DESC NULLS LAST, t.{quote_ident(id_col)} DESC"
            else:
                base_query += f" ORDER BY t.{quote_ident(id_col)} DESC"

            return paginate(
                query=base_query, params=tuple(params), conn=conn,
                offset=effective_offset, limit=effective_limit,
            )
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")


# ---------------------------------------------------------------------------
# GET /api/finance/receipts  (Thu khac - inbound other receipts)
# ---------------------------------------------------------------------------


@router.get("/finance/receipts")
async def finance_receipts(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=0, le=500),
    offset: int | None = Query(default=None, ge=0),
    limit: int | None = Query(default=None, ge=0, le=5000),
    companyId: str | None = Query(default=None),
    dateFrom: dt_date | None = Query(default=None),
    dateTo: dt_date | None = Query(default=None),
    _user: dict = Depends(require_auth),
):
    """Return receipt vouchers (Thu khac)."""
    return _payment_type_endpoint(
        type_filter="inbound", page=page, per_page=per_page,
        offset=offset, limit=limit, companyId=companyId,
        dateFrom=dateFrom, dateTo=dateTo,
    )


# ---------------------------------------------------------------------------
# GET /api/finance/expenses  (Chi khac - outbound expense vouchers)
# ---------------------------------------------------------------------------


@router.get("/finance/expenses")
async def finance_expenses(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=0, le=500),
    offset: int | None = Query(default=None, ge=0),
    limit: int | None = Query(default=None, ge=0, le=5000),
    companyId: str | None = Query(default=None),
    dateFrom: dt_date | None = Query(default=None),
    dateTo: dt_date | None = Query(default=None),
    _user: dict = Depends(require_auth),
):
    """Return expense vouchers (Chi khac)."""
    return _payment_type_endpoint(
        type_filter="outbound", page=page, per_page=per_page,
        offset=offset, limit=limit, companyId=companyId,
        dateFrom=dateFrom, dateTo=dateTo,
    )


# ---------------------------------------------------------------------------
# GET /api/finance/transfers  (internal transfer vouchers)
# ---------------------------------------------------------------------------


@router.get("/finance/transfers")
async def finance_transfers(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=0, le=500),
    offset: int | None = Query(default=None, ge=0),
    limit: int | None = Query(default=None, ge=0, le=5000),
    companyId: str | None = Query(default=None),
    dateFrom: dt_date | None = Query(default=None),
    dateTo: dt_date | None = Query(default=None),
    _user: dict = Depends(require_auth),
):
    """Return internal transfer vouchers."""
    return _payment_type_endpoint(
        type_filter="transfer", page=page, per_page=per_page,
        offset=offset, limit=limit, companyId=companyId,
        dateFrom=dateFrom, dateTo=dateTo,
    )


# ---------------------------------------------------------------------------
# GET /api/finance/fund-book  (fund book with cash/bank split)
# ---------------------------------------------------------------------------

from decimal import Decimal


def _to_float_val(value) -> float:
    if value is None:
        return 0.0
    if isinstance(value, Decimal):
        return float(value)
    return float(value)


@router.get("/finance/fund-book")
async def finance_fund_book(
    companyId: str | None = Query(default=None),
    dateFrom: dt_date | None = Query(default=None),
    dateTo: dt_date | None = Query(default=None),
    _user: dict = Depends(require_auth),
):
    """Return fund book with cash/bank split summaries."""
    try:
        with get_conn() as conn:
            payments_table = resolve_table(
                conn,
                "account_payments", "accountpayments", "accountpayment",
                "sale_order_payments", "saleorderpayments",
                "payments", "payment",
            )
            if not payments_table:
                return {"cashInbound": 0, "cashOutbound": 0, "bankInbound": 0, "bankOutbound": 0, "items": []}

            cols = table_columns(conn, payments_table)
            id_col = pick_column(cols, "id")
            date_col = pick_column(cols, "date", "payment_date", "paymentdate", "created_at")
            amount_col = pick_column(cols, "amount", "amount_total", "payment_amount", "total")
            payment_type_col = pick_column(cols, "payment_type", "paymenttype", "type")
            journal_id_col = pick_column(cols, "journal_id", "journalid")
            company_id_col = pick_column(cols, "company_id", "companyid")
            state_col = pick_column(cols, "state", "status")

            if not id_col or not amount_col:
                return {"cashInbound": 0, "cashOutbound": 0, "bankInbound": 0, "bankOutbound": 0, "items": []}

            amount_expr = f"COALESCE(p.{quote_ident(amount_col)}, 0)"

            # Journal join for cash/bank detection
            journal_table = resolve_table(conn, "account_journals", "accountjournals", "journals")
            join_sql = ""
            channel_expr = "''"
            if journal_id_col and journal_table:
                j_cols = table_columns(conn, journal_table)
                j_id = pick_column(j_cols, "id")
                j_type = pick_column(j_cols, "type", "journal_type")
                j_name = pick_column(j_cols, "name", "display_name")
                if j_id:
                    join_sql = (
                        f" LEFT JOIN {journal_table.qualified_name} j"
                        f" ON p.{quote_ident(journal_id_col)} = j.{quote_ident(j_id)}"
                    )
                    parts = []
                    if j_type:
                        parts.append(f"j.{quote_ident(j_type)}::text")
                    if j_name:
                        parts.append(f"j.{quote_ident(j_name)}::text")
                    if parts:
                        channel_expr = "LOWER(COALESCE(" + ", ".join(parts) + ", ''))"

            where_clauses: list[str] = []
            params: list = []

            if state_col:
                where_clauses.append(
                    f"COALESCE(LOWER(p.{quote_ident(state_col)}::text), '') NOT IN ('cancel', 'cancelled')"
                )
            if companyId and company_id_col:
                where_clauses.append(f"p.{quote_ident(company_id_col)}::text = %s")
                params.append(companyId)
            if dateFrom and date_col:
                where_clauses.append(f"p.{quote_ident(date_col)}::date >= %s")
                params.append(dateFrom)
            if dateTo and date_col:
                where_clauses.append(f"p.{quote_ident(date_col)}::date <= %s")
                params.append(dateTo)

            where_sql = (" WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

            cash_pred = f"({channel_expr} LIKE '%%cash%%' OR {channel_expr} LIKE '%%tien mat%%')"
            bank_pred = f"({channel_expr} LIKE '%%bank%%' OR {channel_expr} LIKE '%%ngan hang%%')"

            # Inbound/outbound detection
            if payment_type_col:
                inbound_placeholders = ", ".join([f"'{t}'" for t in _INBOUND_TYPES])
                outbound_placeholders = ", ".join([f"'{t}'" for t in _OUTBOUND_TYPES])
                inbound_pred = f"LOWER(COALESCE(p.{quote_ident(payment_type_col)}::text, '')) IN ({inbound_placeholders})"
                outbound_pred = f"LOWER(COALESCE(p.{quote_ident(payment_type_col)}::text, '')) IN ({outbound_placeholders})"
            else:
                inbound_pred = f"{amount_expr} >= 0"
                outbound_pred = f"{amount_expr} < 0"

            sql = (
                "SELECT "
                f"COALESCE(SUM(CASE WHEN {cash_pred} AND {inbound_pred} THEN ABS({amount_expr}) ELSE 0 END), 0) AS cash_in, "
                f"COALESCE(SUM(CASE WHEN {cash_pred} AND {outbound_pred} THEN ABS({amount_expr}) ELSE 0 END), 0) AS cash_out, "
                f"COALESCE(SUM(CASE WHEN {bank_pred} AND {inbound_pred} THEN ABS({amount_expr}) ELSE 0 END), 0) AS bank_in, "
                f"COALESCE(SUM(CASE WHEN {bank_pred} AND {outbound_pred} THEN ABS({amount_expr}) ELSE 0 END), 0) AS bank_out "
                f"FROM {payments_table.qualified_name} p{join_sql}{where_sql}"
            )

            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql, tuple(params))
                row = dict(cur.fetchone() or {})

            return {
                "cashInbound": _to_float_val(row.get("cash_in")),
                "cashOutbound": _to_float_val(row.get("cash_out")),
                "bankInbound": _to_float_val(row.get("bank_in")),
                "bankOutbound": _to_float_val(row.get("bank_out")),
                "dateFrom": dateFrom.isoformat() if dateFrom else None,
                "dateTo": dateTo.isoformat() if dateTo else None,
                "companyId": companyId,
            }
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")
