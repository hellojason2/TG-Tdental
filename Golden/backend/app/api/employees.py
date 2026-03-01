"""Employees lookup endpoint."""

from __future__ import annotations

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

router = APIRouter(prefix="/api", tags=["employees"])


@router.get("/employees")
async def list_employees(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=0, le=500),
    offset: int | None = Query(default=None, ge=0),
    limit: int | None = Query(default=None, ge=0, le=5000),
    search: str = Query(default=""),
    companyId: str | None = Query(default=None),
    isDoctor: bool | None = Query(default=None),
    _user: dict = Depends(require_auth),
):
    """Return paginated employees with doctor/search filters."""
    effective_offset, effective_limit = page_window(
        page=page,
        per_page=per_page,
        offset=offset,
        limit=limit,
        default_limit=20,
    )

    try:
        with get_conn() as conn:
            employees_table = resolve_table(conn, "employees", "employee")
            if not employees_table:
                return empty_page(effective_offset, effective_limit)

            employee_cols = table_columns(conn, employees_table)
            id_col = pick_column(employee_cols, "id")
            name_col = pick_column(employee_cols, "name", "display_name")
            if not id_col or not name_col:
                return empty_page(effective_offset, effective_limit)

            hr_job_col = pick_column(employee_cols, "hr_job", "job_name", "job")
            company_id_col = pick_column(employee_cols, "company_id", "companyid")
            company_name_col = pick_column(employee_cols, "company_name", "companyname")
            is_doctor_col = pick_column(employee_cols, "is_doctor", "isdoctor")
            active_col = pick_column(employee_cols, "active", "is_active")

            companies_table = resolve_table(conn, "companies", "company")
            company_join = ""
            company_name_expr = "NULL::text"
            if company_name_col:
                company_name_expr = f"e.{quote_ident(company_name_col)}"
            elif companies_table and company_id_col:
                company_cols = table_columns(conn, companies_table)
                comp_id_col = pick_column(company_cols, "id")
                comp_name_col = pick_column(company_cols, "name", "display_name")
                if comp_id_col and comp_name_col:
                    company_join = (
                        f" LEFT JOIN {companies_table.qualified_name} c"
                        f" ON e.{quote_ident(company_id_col)} = c.{quote_ident(comp_id_col)}"
                    )
                    company_name_expr = f"c.{quote_ident(comp_name_col)}"

            select_fields = [
                f'e.{quote_ident(id_col)}::text AS id',
                f'e.{quote_ident(name_col)} AS name',
                (
                    f'e.{quote_ident(hr_job_col)} AS "hrJob"'
                    if hr_job_col
                    else 'NULL::text AS "hrJob"'
                ),
                (
                    f'e.{quote_ident(company_id_col)}::text AS "companyId"'
                    if company_id_col
                    else 'NULL::text AS "companyId"'
                ),
                f'{company_name_expr} AS "companyName"',
                (
                    f'COALESCE(e.{quote_ident(is_doctor_col)}, FALSE) AS "isDoctor"'
                    if is_doctor_col
                    else 'FALSE AS "isDoctor"'
                ),
                (
                    f"COALESCE(e.{quote_ident(active_col)}, TRUE) AS active"
                    if active_col
                    else "TRUE AS active"
                ),
            ]

            where_clauses: list[str] = []
            params: list = []

            search_text = search.strip()
            if search_text:
                pattern = f"%{search_text}%"
                if hr_job_col:
                    where_clauses.append(
                        f"(e.{quote_ident(name_col)} ILIKE %s OR e.{quote_ident(hr_job_col)} ILIKE %s)"
                    )
                    params.extend([pattern, pattern])
                else:
                    where_clauses.append(f"e.{quote_ident(name_col)} ILIKE %s")
                    params.append(pattern)

            if companyId:
                if company_id_col:
                    where_clauses.append(f"e.{quote_ident(company_id_col)}::text = %s")
                    params.append(companyId)
                else:
                    return empty_page(effective_offset, effective_limit)

            if isDoctor is not None:
                if is_doctor_col:
                    where_clauses.append(f"COALESCE(e.{quote_ident(is_doctor_col)}, FALSE) = %s")
                    params.append(isDoctor)
                elif isDoctor:
                    return empty_page(effective_offset, effective_limit)

            order_col = quote_ident(name_col)
            base_query = (
                f"SELECT {', '.join(select_fields)} "
                f"FROM {employees_table.qualified_name} e{company_join}"
            )
            if where_clauses:
                base_query += " WHERE " + " AND ".join(where_clauses)
            base_query += f" ORDER BY e.{order_col} ASC NULLS LAST"

            return paginate(
                query=base_query,
                params=tuple(params),
                conn=conn,
                offset=effective_offset,
                limit=effective_limit,
            )
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")
