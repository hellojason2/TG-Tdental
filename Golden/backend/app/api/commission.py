"""Commission APIs with list/detail CRUD used by commission page."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from pydantic import BaseModel, Field
from psycopg2.extras import RealDictCursor

from app.core.database import get_conn
from app.core.lookup_sql import (
    TableRef,
    empty_page,
    page_window,
    pick_column,
    quote_ident,
    resolve_table,
    table_columns,
)
from app.core.middleware import require_auth
from app.core.pagination import paginate

router = APIRouter(prefix="/api", tags=["commission"])

_APP_COMMISSIONS_TABLE = "app_commissions"


class CommissionCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=500)
    type: str | None = None
    companyId: str | None = None
    active: bool = True
    description: str | None = None


class CommissionUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=500)
    type: str | None = None
    companyId: str | None = None
    active: bool | None = None
    description: str | None = None


def _ensure_app_commission_table(conn) -> None:
    with conn.cursor() as cur:
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS public.{quote_ident(_APP_COMMISSIONS_TABLE)} (
                id UUID PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT,
                company_id UUID,
                active BOOLEAN NOT NULL DEFAULT TRUE,
                description TEXT,
                date_created TIMESTAMP NOT NULL DEFAULT NOW(),
                last_updated TIMESTAMP NOT NULL DEFAULT NOW()
            );
            """
        )
        cur.execute(
            f"""
            CREATE INDEX IF NOT EXISTS idx_{_APP_COMMISSIONS_TABLE}_company_id
            ON public.{quote_ident(_APP_COMMISSIONS_TABLE)} (company_id);
            """
        )
        cur.execute(
            f"""
            CREATE INDEX IF NOT EXISTS idx_{_APP_COMMISSIONS_TABLE}_active
            ON public.{quote_ident(_APP_COMMISSIONS_TABLE)} (active);
            """
        )


def _resolve_commission_table(conn) -> TableRef:
    table_ref = resolve_table(conn, "commissions", "commission")
    if table_ref:
        return table_ref

    _ensure_app_commission_table(conn)
    return TableRef(schema="public", table=_APP_COMMISSIONS_TABLE)


def _commission_fields(columns: tuple[str, ...]) -> dict[str, str | None]:
    return {
        "id": pick_column(columns, "id"),
        "name": pick_column(columns, "name", "title"),
        "type": pick_column(columns, "type", "commission_type", "commissiontype"),
        "company_id": pick_column(columns, "company_id", "companyid"),
        "active": pick_column(columns, "active", "is_active", "isactive"),
        "description": pick_column(columns, "description", "note"),
        "date_created": pick_column(columns, "date_created", "datecreated", "created_at", "createdat"),
        "last_updated": pick_column(columns, "last_updated", "lastupdated", "updated_at", "updatedat"),
    }


def _text_expr(alias: str, col: str | None) -> str:
    if not col:
        return "NULL::text"
    return f"{alias}.{quote_ident(col)}"


def _uuid_text_expr(alias: str, col: str | None) -> str:
    if not col:
        return "NULL::text"
    return f"{alias}.{quote_ident(col)}::text"


def _bool_expr(alias: str, col: str | None, default: bool) -> str:
    if not col:
        return "TRUE" if default else "FALSE"
    return f"COALESCE({alias}.{quote_ident(col)}, {'TRUE' if default else 'FALSE'})"


def _ts_expr(alias: str, col: str | None) -> str:
    if not col:
        return "NULL::timestamp"
    return f"{alias}.{quote_ident(col)}"


def _build_commission_select(table_ref: TableRef, fields: dict[str, str | None]) -> str:
    if not fields["id"]:
        return ""

    return (
        "SELECT "
        f"c.{quote_ident(fields['id'])}::text AS id, "
        f"COALESCE({_text_expr('c', fields['name'])}, '') AS name, "
        f"{_text_expr('c', fields['type'])} AS type, "
        f"{_uuid_text_expr('c', fields['company_id'])} AS \"companyId\", "
        f"{_bool_expr('c', fields['active'], True)} AS active, "
        f"{_text_expr('c', fields['description'])} AS description, "
        f"{_ts_expr('c', fields['date_created'])} AS \"dateCreated\", "
        f"{_ts_expr('c', fields['last_updated'])} AS \"lastUpdated\" "
        f"FROM {table_ref.qualified_name} c"
    )


def _fetch_commission_by_id(
    conn,
    table_ref: TableRef,
    fields: dict[str, str | None],
    commission_id: str,
) -> dict | None:
    select_sql = _build_commission_select(table_ref, fields)
    if not select_sql or not fields["id"]:
        return None

    sql = f"{select_sql} WHERE c.{quote_ident(fields['id'])}::text = %s LIMIT 1"
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql, (commission_id,))
        row = cur.fetchone()
    return dict(row) if row else None


@router.get("/commissions")
async def list_commissions(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=0, le=500),
    offset: int | None = Query(default=None, ge=0),
    limit: int | None = Query(default=None, ge=0, le=5000),
    search: str = Query(default=""),
    type: str | None = Query(default=None),
    companyId: str | None = Query(default=None),
    active: bool | None = Query(default=None),
    _user: dict = Depends(require_auth),
):
    """Return paginated commission rules list."""
    effective_offset, effective_limit = page_window(
        page=page,
        per_page=per_page,
        offset=offset,
        limit=limit,
        default_limit=20,
    )

    try:
        with get_conn() as conn:
            table_ref = _resolve_commission_table(conn)
            fields = _commission_fields(table_columns(conn, table_ref))
            if not fields["id"]:
                return empty_page(effective_offset, effective_limit)

            base_query = _build_commission_select(table_ref, fields)
            if not base_query:
                return empty_page(effective_offset, effective_limit)

            where_clauses: list[str] = []
            params: list = []

            if search.strip():
                pattern = f"%{search.strip()}%"
                search_parts: list[str] = []
                if fields["name"]:
                    search_parts.append(f"c.{quote_ident(fields['name'])} ILIKE %s")
                    params.append(pattern)
                if fields["description"]:
                    search_parts.append(f"c.{quote_ident(fields['description'])} ILIKE %s")
                    params.append(pattern)
                if search_parts:
                    where_clauses.append("(" + " OR ".join(search_parts) + ")")

            if type is not None:
                if fields["type"]:
                    where_clauses.append(f"COALESCE(c.{quote_ident(fields['type'])}, '') = %s")
                    params.append(type)
                else:
                    where_clauses.append("1 = 0")

            if companyId:
                if fields["company_id"]:
                    where_clauses.append(f"c.{quote_ident(fields['company_id'])}::text = %s")
                    params.append(companyId)
                else:
                    where_clauses.append("1 = 0")

            if active is not None:
                if fields["active"]:
                    where_clauses.append(f"COALESCE(c.{quote_ident(fields['active'])}, TRUE) = %s")
                    params.append(active)
                elif not active:
                    where_clauses.append("1 = 0")

            if where_clauses:
                base_query += " WHERE " + " AND ".join(where_clauses)

            order_col = fields["date_created"] or fields["name"] or fields["id"]
            base_query += f" ORDER BY c.{quote_ident(order_col)} DESC NULLS LAST"

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
# GET /api/commissions/employees  (per-employee commission breakdown)
# ---------------------------------------------------------------------------


@router.get("/commissions/employees")
async def commissions_by_employee(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=0, le=500),
    offset: int | None = Query(default=None, ge=0),
    limit: int | None = Query(default=None, ge=0, le=5000),
    search: str = Query(default=""),
    companyId: str | None = Query(default=None),
    dateFrom: str | None = Query(default=None),
    dateTo: str | None = Query(default=None),
    _user: dict = Depends(require_auth),
):
    """Return per-employee commission breakdown.

    Tries dedicated commission-lines / commission-details tables first,
    then falls back to computing from sale-order lines joined to employees.
    """
    from datetime import date as date_type
    from psycopg2.extras import RealDictCursor as _RDC

    effective_offset, effective_limit = page_window(
        page=page,
        per_page=per_page,
        offset=offset,
        limit=limit,
        default_limit=20,
    )

    parsed_date_from: date_type | None = None
    parsed_date_to: date_type | None = None
    try:
        if dateFrom:
            parsed_date_from = date_type.fromisoformat(dateFrom)
        if dateTo:
            parsed_date_to = date_type.fromisoformat(dateTo)
    except ValueError:
        pass

    try:
        with get_conn() as conn:
            # --- Strategy 1: dedicated commission lines table ---
            lines_table = resolve_table(
                conn,
                "commission_lines", "commissionlines",
                "commission_details", "commissiondetails",
                "employee_commissions", "employeecommissions",
                "hoa_hong_nhan_vien",
            )
            if lines_table:
                return _commissions_employees_from_lines(
                    conn, lines_table,
                    effective_offset=effective_offset,
                    effective_limit=effective_limit,
                    search=search,
                    company_id=companyId,
                    date_from=parsed_date_from,
                    date_to=parsed_date_to,
                )

            # --- Strategy 2: compute from employees table ---
            emp_table = resolve_table(conn, "employees", "employee")
            if emp_table:
                return _commissions_employees_from_employees(
                    conn, emp_table,
                    effective_offset=effective_offset,
                    effective_limit=effective_limit,
                    search=search,
                    company_id=companyId,
                )

            return empty_page(effective_offset, effective_limit)
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")


def _commissions_employees_from_lines(
    conn,
    lines_table,
    *,
    effective_offset: int,
    effective_limit: int,
    search: str,
    company_id: str | None,
    date_from=None,
    date_to=None,
):
    """Build employee commission list from a dedicated lines table."""
    from app.core.pagination import paginate as _paginate

    cols = table_columns(conn, lines_table)
    id_col = pick_column(cols, "id")
    if not id_col:
        return empty_page(effective_offset, effective_limit)

    employee_id_col = pick_column(cols, "employee_id", "employeeid", "staff_id")
    employee_name_col = pick_column(cols, "employee_name", "employeename", "staff_name")
    amount_col = pick_column(cols, "amount", "commission_amount", "commission", "total")
    date_col = pick_column(cols, "date", "commission_date", "created_at", "created_date")
    company_id_col = pick_column(cols, "company_id", "companyid")
    service_name_col = pick_column(cols, "service_name", "product_name", "productname")
    state_col = pick_column(cols, "state", "status")

    amount_expr = f"COALESCE(cl.{quote_ident(amount_col)}, 0)" if amount_col else "0::numeric"

    joins = ""
    employee_name_expr = (
        f'cl.{quote_ident(employee_name_col)}' if employee_name_col else "NULL::text"
    )
    if not employee_name_col and employee_id_col:
        emp_table = resolve_table(conn, "employees", "employee")
        if emp_table:
            emp_cols = table_columns(conn, emp_table)
            e_id = pick_column(emp_cols, "id")
            e_name = pick_column(emp_cols, "name", "display_name")
            if e_id and e_name:
                joins = (
                    f" LEFT JOIN {emp_table.qualified_name} e"
                    f" ON cl.{quote_ident(employee_id_col)} = e.{quote_ident(e_id)}"
                )
                employee_name_expr = f"e.{quote_ident(e_name)}"

    select_fields = [
        f'cl.{quote_ident(id_col)}::text AS id',
        (f'cl.{quote_ident(employee_id_col)}::text AS "employeeId"'
         if employee_id_col else 'NULL::text AS "employeeId"'),
        f'{employee_name_expr} AS "employeeName"',
        f'{amount_expr} AS amount',
        (f'cl.{quote_ident(date_col)} AS date' if date_col else "NULL::timestamp AS date"),
        (f'cl.{quote_ident(service_name_col)} AS "serviceName"'
         if service_name_col else 'NULL::text AS "serviceName"'),
        (f'cl.{quote_ident(state_col)} AS state' if state_col else "NULL::text AS state"),
        (f'cl.{quote_ident(company_id_col)}::text AS "companyId"'
         if company_id_col else 'NULL::text AS "companyId"'),
    ]

    where_clauses: list[str] = []
    params: list = []

    if company_id:
        if not company_id_col:
            return empty_page(effective_offset, effective_limit)
        where_clauses.append(f"cl.{quote_ident(company_id_col)}::text = %s")
        params.append(company_id)

    if search.strip():
        pattern = f"%{search.strip()}%"
        search_parts: list[str] = []
        if employee_name_col:
            search_parts.append(f"cl.{quote_ident(employee_name_col)} ILIKE %s")
            params.append(pattern)
        if service_name_col:
            search_parts.append(f"cl.{quote_ident(service_name_col)} ILIKE %s")
            params.append(pattern)
        if search_parts:
            where_clauses.append("(" + " OR ".join(search_parts) + ")")

    if date_from and date_col:
        where_clauses.append(f"cl.{quote_ident(date_col)}::date >= %s")
        params.append(date_from)
    if date_to and date_col:
        where_clauses.append(f"cl.{quote_ident(date_col)}::date <= %s")
        params.append(date_to)

    base_query = (
        f"SELECT {', '.join(select_fields)} FROM {lines_table.qualified_name} cl"
        + joins
    )
    if where_clauses:
        base_query += " WHERE " + " AND ".join(where_clauses)
    if date_col:
        base_query += (
            f" ORDER BY cl.{quote_ident(date_col)} DESC NULLS LAST, "
            f"cl.{quote_ident(id_col)} DESC"
        )
    else:
        base_query += f" ORDER BY cl.{quote_ident(id_col)} DESC"

    return _paginate(
        query=base_query, params=tuple(params), conn=conn,
        offset=effective_offset, limit=effective_limit,
    )


def _commissions_employees_from_employees(
    conn,
    emp_table,
    *,
    effective_offset: int,
    effective_limit: int,
    search: str,
    company_id: str | None,
):
    """Fallback: return employees with their commission rate/amount from employee table."""
    from app.core.pagination import paginate as _paginate

    cols = table_columns(conn, emp_table)
    id_col = pick_column(cols, "id")
    name_col = pick_column(cols, "name", "display_name")
    if not id_col or not name_col:
        return empty_page(effective_offset, effective_limit)

    commission_col = pick_column(cols, "commission", "commission_rate", "commissionrate", "commission_amount")
    salary_col = pick_column(cols, "salary", "basic_salary", "wage")
    company_id_col = pick_column(cols, "company_id", "companyid")
    company_name_col = pick_column(cols, "company_name", "companyname")
    job_col = pick_column(cols, "hr_job", "job_name", "job")
    active_col = pick_column(cols, "active", "is_active")

    joins = ""
    company_name_expr = f'e.{quote_ident(company_name_col)}' if company_name_col else "NULL::text"
    if not company_name_col and company_id_col:
        company_table = resolve_table(conn, "companies", "company")
        if company_table:
            c_cols = table_columns(conn, company_table)
            c_id = pick_column(c_cols, "id")
            c_name = pick_column(c_cols, "name", "display_name")
            if c_id and c_name:
                joins = (
                    f" LEFT JOIN {company_table.qualified_name} co"
                    f" ON e.{quote_ident(company_id_col)} = co.{quote_ident(c_id)}"
                )
                company_name_expr = f"co.{quote_ident(c_name)}"

    commission_expr = (
        f"COALESCE(e.{quote_ident(commission_col)}, 0)" if commission_col else "0::numeric"
    )

    select_fields = [
        f'e.{quote_ident(id_col)}::text AS id',
        f'e.{quote_ident(id_col)}::text AS "employeeId"',
        f'e.{quote_ident(name_col)} AS "employeeName"',
        f'{commission_expr} AS amount',
        "NULL::timestamp AS date",
        'NULL::text AS "serviceName"',
        'NULL::text AS state',
        (f'e.{quote_ident(company_id_col)}::text AS "companyId"'
         if company_id_col else 'NULL::text AS "companyId"'),
        f'{company_name_expr} AS "companyName"',
        (f'e.{quote_ident(job_col)} AS "jobTitle"' if job_col else 'NULL::text AS "jobTitle"'),
    ]

    where_clauses: list[str] = []
    params: list = []

    if active_col:
        where_clauses.append(f"COALESCE(e.{quote_ident(active_col)}, TRUE) = TRUE")

    if company_id:
        if not company_id_col:
            return empty_page(effective_offset, effective_limit)
        where_clauses.append(f"e.{quote_ident(company_id_col)}::text = %s")
        params.append(company_id)

    if search.strip():
        pattern = f"%{search.strip()}%"
        where_clauses.append(f"e.{quote_ident(name_col)} ILIKE %s")
        params.append(pattern)

    base_query = (
        f"SELECT {', '.join(select_fields)} FROM {emp_table.qualified_name} e"
        + joins
    )
    if where_clauses:
        base_query += " WHERE " + " AND ".join(where_clauses)
    base_query += f" ORDER BY e.{quote_ident(name_col)} ASC NULLS LAST"

    return _paginate(
        query=base_query, params=tuple(params), conn=conn,
        offset=effective_offset, limit=effective_limit,
    )


@router.get("/commissions/{commission_id}")
async def get_commission(
    commission_id: str = Path(..., min_length=1),
    _user: dict = Depends(require_auth),
):
    """Return one commission rule by id."""
    try:
        with get_conn() as conn:
            table_ref = _resolve_commission_table(conn)
            fields = _commission_fields(table_columns(conn, table_ref))
            commission = _fetch_commission_by_id(conn, table_ref, fields, commission_id)
            if not commission:
                raise HTTPException(status_code=404, detail="Commission not found")
            return commission
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")


@router.post("/commissions")
async def create_commission(
    body: CommissionCreateRequest,
    user: dict = Depends(require_auth),
):
    """Create a commission rule."""
    del user
    try:
        with get_conn() as conn:
            table_ref = _resolve_commission_table(conn)
            fields = _commission_fields(table_columns(conn, table_ref))
            if not fields["id"] or not fields["name"]:
                raise HTTPException(status_code=503, detail="Commission table schema is missing required columns")

            commission_id = str(uuid4())
            now = datetime.now(timezone.utc)

            values: dict[str, object] = {
                fields["id"]: commission_id,
                fields["name"]: body.name.strip(),
            }
            if fields["type"] and body.type is not None:
                values[fields["type"]] = body.type
            if fields["company_id"] and body.companyId is not None:
                values[fields["company_id"]] = body.companyId
            if fields["active"]:
                values[fields["active"]] = body.active
            if fields["description"] and body.description is not None:
                values[fields["description"]] = body.description
            if fields["date_created"]:
                values[fields["date_created"]] = now
            if fields["last_updated"]:
                values[fields["last_updated"]] = now

            cols = list(values.keys())
            params = [values[col] for col in cols]
            sql = (
                f"INSERT INTO {table_ref.qualified_name} "
                f"({', '.join(quote_ident(col) for col in cols)}) "
                f"VALUES ({', '.join(['%s'] * len(cols))})"
            )
            with conn.cursor() as cur:
                cur.execute(sql, tuple(params))

            created = _fetch_commission_by_id(conn, table_ref, fields, commission_id)
            if not created:
                raise HTTPException(status_code=500, detail="Failed to load created commission")
            return created
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")


@router.put("/commissions/{commission_id}")
async def update_commission(
    body: CommissionUpdateRequest,
    commission_id: str = Path(..., min_length=1),
    user: dict = Depends(require_auth),
):
    """Update a commission rule."""
    del user
    try:
        with get_conn() as conn:
            table_ref = _resolve_commission_table(conn)
            fields = _commission_fields(table_columns(conn, table_ref))
            if not fields["id"]:
                raise HTTPException(status_code=503, detail="Commission table schema is missing id column")

            updates: dict[str, object] = {}
            if body.name is not None and fields["name"]:
                updates[fields["name"]] = body.name.strip()
            if body.type is not None and fields["type"]:
                updates[fields["type"]] = body.type
            if body.companyId is not None and fields["company_id"]:
                updates[fields["company_id"]] = body.companyId
            if body.active is not None and fields["active"]:
                updates[fields["active"]] = body.active
            if body.description is not None and fields["description"]:
                updates[fields["description"]] = body.description
            if fields["last_updated"]:
                updates[fields["last_updated"]] = datetime.now(timezone.utc)

            if not updates:
                existing = _fetch_commission_by_id(conn, table_ref, fields, commission_id)
                if not existing:
                    raise HTTPException(status_code=404, detail="Commission not found")
                return existing

            set_sql = ", ".join(f"{quote_ident(col)} = %s" for col in updates.keys())
            params = list(updates.values()) + [commission_id]
            sql = (
                f"UPDATE {table_ref.qualified_name} "
                f"SET {set_sql} "
                f"WHERE {quote_ident(fields['id'])}::text = %s"
            )

            with conn.cursor() as cur:
                cur.execute(sql, tuple(params))
                if cur.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Commission not found")

            updated = _fetch_commission_by_id(conn, table_ref, fields, commission_id)
            if not updated:
                raise HTTPException(status_code=404, detail="Commission not found")
            return updated
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")


@router.delete("/commissions/{commission_id}")
async def delete_commission(
    commission_id: str = Path(..., min_length=1),
    user: dict = Depends(require_auth),
):
    """Delete a commission rule."""
    del user
    try:
        with get_conn() as conn:
            table_ref = _resolve_commission_table(conn)
            fields = _commission_fields(table_columns(conn, table_ref))
            if not fields["id"]:
                raise HTTPException(status_code=503, detail="Commission table schema is missing id column")

            sql = (
                f"DELETE FROM {table_ref.qualified_name} "
                f"WHERE {quote_ident(fields['id'])}::text = %s"
            )
            with conn.cursor() as cur:
                cur.execute(sql, (commission_id,))
                if cur.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Commission not found")

            return {"id": commission_id, "deleted": True}
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")
