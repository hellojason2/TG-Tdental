"""Exam session (dot-kham) API endpoints."""

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

router = APIRouter(prefix="/api", tags=["exam-sessions"])


@router.get("/dot-khams")
async def list_dot_khams(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=0, le=500),
    offset: int | None = Query(default=None, ge=0),
    limit: int | None = Query(default=None, ge=0, le=5000),
    partnerId: str | None = Query(default=None),
    companyId: str | None = Query(default=None),
    dateFrom: date | None = Query(default=None),
    dateTo: date | None = Query(default=None),
    state: str | None = Query(default=None),
    _user: dict = Depends(require_auth),
):
    """Return paginated exam sessions with optional patient/company filters."""
    effective_offset, effective_limit = page_window(
        page=page,
        per_page=per_page,
        offset=offset,
        limit=limit,
        default_limit=20,
    )

    try:
        with get_conn() as conn:
            sessions_table = resolve_table(
                conn,
                "dot_khams",
                "dotkham",
                "dotkhams",
                "exam_sessions",
                "exam_session",
            )
            if not sessions_table:
                return empty_page(effective_offset, effective_limit)

            cols = table_columns(conn, sessions_table)
            id_col = pick_column(cols, "id")
            if not id_col:
                return empty_page(effective_offset, effective_limit)

            name_col = pick_column(cols, "name", "display_name", "session_name")
            date_col = pick_column(cols, "date", "exam_date", "kham_date", "created_at")
            state_col = pick_column(cols, "state", "status")
            doctor_name_col = pick_column(cols, "doctor_name", "doctorname")
            doctor_id_col = pick_column(cols, "doctor_id", "doctorid", "employee_id")
            company_name_col = pick_column(cols, "company_name", "companyname")
            company_id_col = pick_column(cols, "company_id", "companyid")
            partner_id_col = pick_column(cols, "partner_id", "partnerid", "customer_id", "customerid")
            reason_col = pick_column(cols, "reason", "note", "description")

            joins: list[str] = []
            doctor_name_expr = (
                f's.{quote_ident(doctor_name_col)}' if doctor_name_col else "NULL::text"
            )
            company_name_expr = (
                f's.{quote_ident(company_name_col)}' if company_name_col else "NULL::text"
            )

            if not doctor_name_col and doctor_id_col:
                employees_table = resolve_table(conn, "employees", "employee")
                if employees_table:
                    employee_cols = table_columns(conn, employees_table)
                    e_id_col = pick_column(employee_cols, "id")
                    e_name_col = pick_column(employee_cols, "name", "display_name")
                    if e_id_col and e_name_col:
                        joins.append(
                            f" LEFT JOIN {employees_table.qualified_name} e"
                            f" ON s.{quote_ident(doctor_id_col)} = e.{quote_ident(e_id_col)}"
                        )
                        doctor_name_expr = f"e.{quote_ident(e_name_col)}"

            if not company_name_col and company_id_col:
                companies_table = resolve_table(conn, "companies", "company")
                if companies_table:
                    company_cols = table_columns(conn, companies_table)
                    c_id_col = pick_column(company_cols, "id")
                    c_name_col = pick_column(company_cols, "name", "display_name")
                    if c_id_col and c_name_col:
                        joins.append(
                            f" LEFT JOIN {companies_table.qualified_name} c"
                            f" ON s.{quote_ident(company_id_col)} = c.{quote_ident(c_id_col)}"
                        )
                        company_name_expr = f"c.{quote_ident(c_name_col)}"

            select_fields = [
                f's.{quote_ident(id_col)}::text AS id',
                (
                    f"COALESCE(s.{quote_ident(name_col)}, s.{quote_ident(id_col)}::text) AS name"
                    if name_col
                    else f's.{quote_ident(id_col)}::text AS name'
                ),
                (
                    f's.{quote_ident(date_col)} AS date'
                    if date_col
                    else "NULL::timestamp AS date"
                ),
                (
                    f's.{quote_ident(state_col)} AS state'
                    if state_col
                    else "NULL::text AS state"
                ),
                f'{doctor_name_expr} AS "doctorName"',
                f'{company_name_expr} AS "companyName"',
                (
                    f's.{quote_ident(reason_col)} AS reason'
                    if reason_col
                    else "NULL::text AS reason"
                ),
                (
                    f's.{quote_ident(partner_id_col)}::text AS "partnerId"'
                    if partner_id_col
                    else 'NULL::text AS "partnerId"'
                ),
                (
                    f's.{quote_ident(company_id_col)}::text AS "companyId"'
                    if company_id_col
                    else 'NULL::text AS "companyId"'
                ),
            ]

            where_clauses: list[str] = []
            params: list = []

            if partnerId:
                if not partner_id_col:
                    return empty_page(effective_offset, effective_limit)
                where_clauses.append(f"s.{quote_ident(partner_id_col)}::text = %s")
                params.append(partnerId)

            if companyId:
                if not company_id_col:
                    return empty_page(effective_offset, effective_limit)
                where_clauses.append(f"s.{quote_ident(company_id_col)}::text = %s")
                params.append(companyId)

            if dateFrom:
                if not date_col:
                    return empty_page(effective_offset, effective_limit)
                where_clauses.append(f"s.{quote_ident(date_col)}::date >= %s")
                params.append(dateFrom)

            if dateTo:
                if not date_col:
                    return empty_page(effective_offset, effective_limit)
                where_clauses.append(f"s.{quote_ident(date_col)}::date <= %s")
                params.append(dateTo)

            if state:
                if not state_col:
                    return empty_page(effective_offset, effective_limit)
                where_clauses.append(f"LOWER(COALESCE(s.{quote_ident(state_col)}::text, '')) = %s")
                params.append(state.strip().lower())

            base_query = (
                f"SELECT {', '.join(select_fields)} "
                f"FROM {sessions_table.qualified_name} s"
                + "".join(joins)
            )
            if where_clauses:
                base_query += " WHERE " + " AND ".join(where_clauses)
            if date_col:
                base_query += (
                    f" ORDER BY s.{quote_ident(date_col)} DESC NULLS LAST, "
                    f"s.{quote_ident(id_col)} DESC"
                )
            else:
                base_query += f" ORDER BY s.{quote_ident(id_col)} DESC"

            return paginate(
                query=base_query,
                params=tuple(params),
                conn=conn,
                offset=effective_offset,
                limit=effective_limit,
            )
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")
