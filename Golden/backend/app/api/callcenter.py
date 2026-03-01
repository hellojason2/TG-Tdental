"""Call center history API endpoints."""

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

router = APIRouter(prefix="/api/callcenter", tags=["callcenter"])


@router.get("/history")
async def callcenter_history(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=0, le=500),
    offset: int | None = Query(default=None, ge=0),
    limit: int | None = Query(default=None, ge=0, le=5000),
    companyId: str | None = Query(default=None),
    dateFrom: date | None = Query(default=None),
    dateTo: date | None = Query(default=None),
    search: str = Query(default=""),
    _user: dict = Depends(require_auth),
):
    """Return call history log."""
    effective_offset, effective_limit = page_window(
        page=page,
        per_page=per_page,
        offset=offset,
        limit=limit,
        default_limit=20,
    )

    try:
        with get_conn() as conn:
            call_table = resolve_table(
                conn,
                "call_logs",
                "calllogs",
                "call_history",
                "callhistory",
                "phone_calls",
                "phonecalls",
                "callcenter",
            )
            if not call_table:
                return empty_page(effective_offset, effective_limit)

            cols = table_columns(conn, call_table)
            id_col = pick_column(cols, "id")
            if not id_col:
                return empty_page(effective_offset, effective_limit)

            date_col = pick_column(cols, "date", "call_date", "created_at", "created_date")
            phone_col = pick_column(cols, "phone", "phone_number", "caller_number", "number")
            partner_id_col = pick_column(cols, "partner_id", "partnerid", "customer_id")
            partner_name_col = pick_column(cols, "partner_name", "partnername", "customer_name", "caller_name")
            direction_col = pick_column(cols, "direction", "call_type", "type")
            duration_col = pick_column(cols, "duration", "call_duration", "seconds")
            state_col = pick_column(cols, "state", "status", "result")
            note_col = pick_column(cols, "note", "memo", "description")
            company_id_col = pick_column(cols, "company_id", "companyid")
            employee_col = pick_column(cols, "employee_name", "user_name", "agent_name")

            select_fields = [
                f'c.{quote_ident(id_col)}::text AS id',
                (f'c.{quote_ident(date_col)} AS date' if date_col else "NULL::timestamp AS date"),
                (f'c.{quote_ident(phone_col)} AS phone' if phone_col else "NULL::text AS phone"),
                (f'c.{quote_ident(partner_id_col)}::text AS "partnerId"'
                 if partner_id_col else 'NULL::text AS "partnerId"'),
                (f'c.{quote_ident(partner_name_col)} AS "partnerName"'
                 if partner_name_col else 'NULL::text AS "partnerName"'),
                (f'c.{quote_ident(direction_col)} AS direction'
                 if direction_col else "NULL::text AS direction"),
                (f'COALESCE(c.{quote_ident(duration_col)}, 0) AS duration'
                 if duration_col else "0::numeric AS duration"),
                (f'c.{quote_ident(state_col)} AS state' if state_col else "NULL::text AS state"),
                (f'c.{quote_ident(note_col)} AS note' if note_col else "NULL::text AS note"),
                (f'c.{quote_ident(employee_col)} AS "employeeName"'
                 if employee_col else 'NULL::text AS "employeeName"'),
                (f'c.{quote_ident(company_id_col)}::text AS "companyId"'
                 if company_id_col else 'NULL::text AS "companyId"'),
            ]

            where_clauses: list[str] = []
            params: list = []

            search_text = search.strip()
            if search_text:
                pattern = f"%{search_text}%"
                search_parts: list[str] = []
                if phone_col:
                    search_parts.append(f"c.{quote_ident(phone_col)} ILIKE %s")
                    params.append(pattern)
                if partner_name_col:
                    search_parts.append(f"c.{quote_ident(partner_name_col)} ILIKE %s")
                    params.append(pattern)
                if search_parts:
                    where_clauses.append(f"({' OR '.join(search_parts)})")

            if companyId:
                if not company_id_col:
                    return empty_page(effective_offset, effective_limit)
                where_clauses.append(f"c.{quote_ident(company_id_col)}::text = %s")
                params.append(companyId)

            if dateFrom and date_col:
                where_clauses.append(f"c.{quote_ident(date_col)}::date >= %s")
                params.append(dateFrom)
            if dateTo and date_col:
                where_clauses.append(f"c.{quote_ident(date_col)}::date <= %s")
                params.append(dateTo)

            base_query = f"SELECT {', '.join(select_fields)} FROM {call_table.qualified_name} c"
            if where_clauses:
                base_query += " WHERE " + " AND ".join(where_clauses)
            if date_col:
                base_query += (
                    f" ORDER BY c.{quote_ident(date_col)} DESC NULLS LAST, "
                    f"c.{quote_ident(id_col)} DESC"
                )
            else:
                base_query += f" ORDER BY c.{quote_ident(id_col)} DESC"

            return paginate(
                query=base_query,
                params=tuple(params),
                conn=conn,
                offset=effective_offset,
                limit=effective_limit,
            )
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")


@router.get("/calls")
async def callcenter_calls(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=0, le=500),
    offset: int | None = Query(default=None, ge=0),
    limit: int | None = Query(default=None, ge=0, le=5000),
    companyId: str | None = Query(default=None),
    dateFrom: date | None = Query(default=None),
    dateTo: date | None = Query(default=None),
    search: str = Query(default=""),
    _user: dict = Depends(require_auth),
):
    """Alias for /history."""
    return await callcenter_history(
        page=page, per_page=per_page, offset=offset, limit=limit,
        companyId=companyId, dateFrom=dateFrom, dateTo=dateTo,
        search=search, _user=_user,
    )
