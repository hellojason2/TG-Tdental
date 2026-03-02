"""Employees lookup endpoint."""

from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query
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

router = APIRouter(prefix="/api", tags=["employees"])


class EmployeeCreatePayload(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    hrJob: str | None = None
    companyId: str | None = None
    isDoctor: bool = False
    active: bool = True


class EmployeeUpdatePayload(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    hrJob: str | None = None
    companyId: str | None = None
    isDoctor: bool | None = None
    active: bool | None = None


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


def _resolve_employees_table(conn):
    """Resolve employees table and return (table_ref, cols) or (None, None)."""
    employees_table = resolve_table(conn, "employees", "employee")
    if not employees_table:
        return None, None
    cols = table_columns(conn, employees_table)
    id_col = pick_column(cols, "id")
    if not id_col:
        return None, None
    return employees_table, cols


@router.post("/employees", status_code=201)
async def create_employee(
    body: EmployeeCreatePayload = Body(...),
    _user: dict = Depends(require_auth),
):
    """Create a new employee."""
    try:
        with get_conn() as conn:
            employees_table, employee_cols = _resolve_employees_table(conn)
            if not employees_table:
                raise HTTPException(status_code=503, detail="Employees table not found")

            id_col = pick_column(employee_cols, "id")
            name_col = pick_column(employee_cols, "name", "display_name")
            hr_job_col = pick_column(employee_cols, "hr_job", "job_name", "job")
            company_id_col = pick_column(employee_cols, "company_id", "companyid")
            is_doctor_col = pick_column(employee_cols, "is_doctor", "isdoctor")
            active_col = pick_column(employee_cols, "active", "is_active")
            created_col = pick_column(employee_cols, "date_created", "datecreated", "created_at", "create_date")

            new_id = str(uuid4())
            insert_cols: list[str] = [id_col]
            values: list = [new_id]

            if name_col:
                insert_cols.append(name_col)
                values.append(body.name.strip())

            if hr_job_col and body.hrJob:
                insert_cols.append(hr_job_col)
                values.append(body.hrJob)

            if company_id_col and body.companyId:
                insert_cols.append(company_id_col)
                values.append(body.companyId)

            if is_doctor_col:
                insert_cols.append(is_doctor_col)
                values.append(body.isDoctor)

            if active_col:
                insert_cols.append(active_col)
                values.append(body.active)

            if created_col:
                insert_cols.append(created_col)
                values.append("NOW()")

            # Build placeholders
            placeholders: list[str] = []
            actual_params: list = []
            for i, col in enumerate(insert_cols):
                if values[i] == "NOW()":
                    placeholders.append("NOW()")
                else:
                    placeholders.append("%s")
                    actual_params.append(values[i])

            sql = (
                f"INSERT INTO {employees_table.qualified_name} "
                f"({', '.join(quote_ident(c) for c in insert_cols)}) "
                f"VALUES ({', '.join(placeholders)})"
            )

            with conn.cursor() as cur:
                cur.execute(sql, tuple(actual_params))

            return {
                "id": new_id,
                "name": body.name.strip(),
                "isDoctor": body.isDoctor,
                "active": body.active,
            }
    except HTTPException:
        raise
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")


@router.put("/employees/{emp_id}")
async def update_employee(
    emp_id: str = Path(..., min_length=1),
    body: EmployeeUpdatePayload = Body(...),
    _user: dict = Depends(require_auth),
):
    """Update an existing employee."""
    try:
        with get_conn() as conn:
            employees_table, employee_cols = _resolve_employees_table(conn)
            if not employees_table:
                raise HTTPException(status_code=503, detail="Employees table not found")

            id_col = pick_column(employee_cols, "id")
            name_col = pick_column(employee_cols, "name", "display_name")
            hr_job_col = pick_column(employee_cols, "hr_job", "job_name", "job")
            company_id_col = pick_column(employee_cols, "company_id", "companyid")
            is_doctor_col = pick_column(employee_cols, "is_doctor", "isdoctor")
            active_col = pick_column(employee_cols, "active", "is_active")
            updated_col = pick_column(employee_cols, "write_date", "updated_at", "last_updated")

            updates: list[str] = []
            params: list = []

            if body.name is not None and name_col:
                updates.append(f"{quote_ident(name_col)} = %s")
                params.append(body.name.strip())
            if body.hrJob is not None and hr_job_col:
                updates.append(f"{quote_ident(hr_job_col)} = %s")
                params.append(body.hrJob)
            if body.companyId is not None and company_id_col:
                updates.append(f"{quote_ident(company_id_col)} = %s")
                params.append(body.companyId)
            if body.isDoctor is not None and is_doctor_col:
                updates.append(f"{quote_ident(is_doctor_col)} = %s")
                params.append(body.isDoctor)
            if body.active is not None and active_col:
                updates.append(f"{quote_ident(active_col)} = %s")
                params.append(body.active)
            if updated_col:
                updates.append(f"{quote_ident(updated_col)} = NOW()")

            if not updates:
                raise HTTPException(status_code=422, detail="No fields to update")

            params.append(emp_id)
            sql = (
                f"UPDATE {employees_table.qualified_name} "
                f"SET {', '.join(updates)} "
                f"WHERE {quote_ident(id_col)}::text = %s"
            )

            with conn.cursor() as cur:
                cur.execute(sql, tuple(params))
                if cur.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Employee not found")

            return {"id": emp_id, "updated": True}
    except HTTPException:
        raise
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")


@router.delete("/employees/{emp_id}")
async def delete_employee(
    emp_id: str = Path(..., min_length=1),
    _user: dict = Depends(require_auth),
):
    """Deactivate an employee (soft-delete via active=false, or hard-delete)."""
    try:
        with get_conn() as conn:
            employees_table, employee_cols = _resolve_employees_table(conn)
            if not employees_table:
                raise HTTPException(status_code=503, detail="Employees table not found")

            id_col = pick_column(employee_cols, "id")
            active_col = pick_column(employee_cols, "active", "is_active")
            updated_col = pick_column(employee_cols, "write_date", "updated_at", "last_updated")

            with conn.cursor() as cur:
                if active_col:
                    # Soft-delete: deactivate
                    set_clauses = [f"{quote_ident(active_col)} = %s"]
                    params: list = [False]
                    if updated_col:
                        set_clauses.append(f"{quote_ident(updated_col)} = NOW()")
                    params.append(emp_id)
                    sql = (
                        f"UPDATE {employees_table.qualified_name} "
                        f"SET {', '.join(set_clauses)} "
                        f"WHERE {quote_ident(id_col)}::text = %s"
                    )
                    cur.execute(sql, tuple(params))
                else:
                    sql = (
                        f"DELETE FROM {employees_table.qualified_name} "
                        f"WHERE {quote_ident(id_col)}::text = %s"
                    )
                    cur.execute(sql, (emp_id,))

                if cur.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Employee not found")

            return {"id": emp_id, "deleted": True}
    except HTTPException:
        raise
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")
