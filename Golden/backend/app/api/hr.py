"""HR endpoints powering salary/admin pages."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from psycopg2.extras import RealDictCursor

from app.core.database import get_conn
from app.core.lookup_sql import pick_column, quote_ident, resolve_table, table_columns
from app.core.middleware import require_auth

router = APIRouter(prefix="/api/hr", tags=["hr"])

_NUMERIC_TYPES = {
    "smallint",
    "integer",
    "bigint",
    "decimal",
    "numeric",
    "real",
    "double precision",
    "money",
}
_BOOLEAN_TYPES = {"boolean", "bool"}


@router.get("/salary")
async def salary_overview(
    dateFrom: date | None = Query(default=None),
    dateTo: date | None = Query(default=None),
    companyId: str | None = Query(default=None),
    _user: dict = Depends(require_auth),
):
    try:
        with get_conn() as conn:
            employees = _load_employees(conn, company_id=companyId)
            timekeeping = _load_timekeeping(
                conn,
                date_from=dateFrom,
                date_to=dateTo,
                company_id=companyId,
            )
            advances = _load_advances(
                conn,
                date_from=dateFrom,
                date_to=dateTo,
                company_id=companyId,
            )

            has_salary_values = any(item.get("monthlySalary") not in (None, 0, 0.0) for item in employees)
            has_data = bool(timekeeping or advances or has_salary_values)

            if not has_data:
                employees = []

            return {
                "hasData": has_data,
                "employees": employees,
                "timekeeping": timekeeping,
                "advances": advances,
                "meta": {
                    "dateFrom": dateFrom.isoformat() if dateFrom else None,
                    "dateTo": dateTo.isoformat() if dateTo else None,
                    "companyId": companyId,
                },
            }
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")


def _load_employees(conn, *, company_id: str | None) -> list[dict]:
    table = resolve_table(conn, "employees", "employee")
    if not table:
        return []

    cols = table_columns(conn, table)
    id_col = pick_column(cols, "id")
    name_col = pick_column(cols, "name", "display_name")
    if not id_col or not name_col:
        return []

    job_col = pick_column(cols, "hr_job", "job_name", "job")
    company_id_col = pick_column(cols, "company_id", "companyid")
    company_name_col = pick_column(cols, "company_name", "companyname")
    active_col = pick_column(cols, "active", "is_active")

    salary_col = pick_column(
        cols,
        "salary",
        "basic_salary",
        "wage",
        "luong",
        "salary_base",
    )
    allowance_col = pick_column(cols, "allowance", "allowances")
    commission_col = pick_column(cols, "commission", "commission_rate", "commissionrate")

    joins = ""
    company_name_expr = (
        f'e.{quote_ident(company_name_col)}' if company_name_col else "NULL::text"
    )
    if not company_name_col and company_id_col:
        company_table = resolve_table(conn, "companies", "company")
        if company_table:
            company_cols = table_columns(conn, company_table)
            c_id_col = pick_column(company_cols, "id")
            c_name_col = pick_column(company_cols, "name", "display_name")
            if c_id_col and c_name_col:
                joins = (
                    f" LEFT JOIN {company_table.qualified_name} c"
                    f" ON e.{quote_ident(company_id_col)} = c.{quote_ident(c_id_col)}"
                )
                company_name_expr = f"c.{quote_ident(c_name_col)}"

    select_fields = [
        f'e.{quote_ident(id_col)}::text AS id',
        f'e.{quote_ident(name_col)} AS name',
        (
            f'e.{quote_ident(job_col)} AS "jobTitle"'
            if job_col
            else 'NULL::text AS "jobTitle"'
        ),
        (
            f'e.{quote_ident(company_id_col)}::text AS "companyId"'
            if company_id_col
            else 'NULL::text AS "companyId"'
        ),
        f'{company_name_expr} AS "companyName"',
        (
            f'COALESCE(e.{quote_ident(salary_col)}, 0) AS "monthlySalary"'
            if salary_col
            else 'NULL::numeric AS "monthlySalary"'
        ),
        (
            f'COALESCE(e.{quote_ident(allowance_col)}, 0) AS allowance'
            if allowance_col
            else '0::numeric AS allowance'
        ),
        (
            f'COALESCE(e.{quote_ident(commission_col)}, 0) AS commission'
            if commission_col
            else '0::numeric AS commission'
        ),
    ]

    where: list[str] = []
    params: list = []

    if active_col:
        where.append(f"COALESCE(e.{quote_ident(active_col)}, TRUE) = TRUE")

    if company_id:
        if company_id_col:
            where.append(f"e.{quote_ident(company_id_col)}::text = %s")
            params.append(company_id)
        else:
            return []

    where_sql = ""
    if where:
        where_sql = " WHERE " + " AND ".join(where)

    query = (
        f"SELECT {', '.join(select_fields)} "
        f"FROM {table.qualified_name} e"
        f"{joins}"
        f"{where_sql} "
        f"ORDER BY e.{quote_ident(name_col)} ASC NULLS LAST "
        "LIMIT 500"
    )

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(query, tuple(params))
        rows = cur.fetchall()
    return [dict(row) for row in rows]


def _load_timekeeping(
    conn,
    *,
    date_from: date | None,
    date_to: date | None,
    company_id: str | None,
) -> list[dict]:
    table = resolve_table(conn, "chamcongs", "timekeepings", "timesheets", "attendance")
    if not table:
        return []

    cols = table_columns(conn, table)
    column_types = _table_column_data_types(conn, table)
    id_col = pick_column(cols, "id")
    employee_id_col = pick_column(cols, "employee_id", "employeeid", "staff_id", "staffid")
    employee_name_col = pick_column(cols, "employee_name", "employeename", "staff_name", "staffname")
    date_col = pick_column(cols, "date", "work_date", "workdate", "created_at")
    hours_col = pick_column(cols, "hours", "work_hours", "workhours", "total_hours")
    overtime_col = pick_column(cols, "overtime", "ot_hours", "overtime_hours")
    state_col = pick_column(cols, "state", "status")
    company_id_col = pick_column(cols, "company_id", "companyid")

    if not id_col or not date_col:
        return []

    hours_expr = (
        _numeric_select_expr("t", hours_col, column_types.get(hours_col, ""))
        if hours_col
        else "0::numeric"
    )
    overtime_expr = (
        _numeric_select_expr("t", overtime_col, column_types.get(overtime_col, ""))
        if overtime_col
        else "0::numeric"
    )

    select_fields = [
        f't.{quote_ident(id_col)}::text AS id',
        f't.{quote_ident(date_col)}::date AS date',
        (
            f't.{quote_ident(employee_id_col)}::text AS "employeeId"'
            if employee_id_col
            else 'NULL::text AS "employeeId"'
        ),
        (
            f't.{quote_ident(employee_name_col)} AS "employeeName"'
            if employee_name_col
            else 'NULL::text AS "employeeName"'
        ),
        f"{hours_expr} AS hours",
        f"{overtime_expr} AS overtime",
        (
            f't.{quote_ident(state_col)} AS state'
            if state_col
            else 'NULL::text AS state'
        ),
    ]

    where: list[str] = []
    params: list = []

    if date_from:
        where.append(f"t.{quote_ident(date_col)}::date >= %s")
        params.append(date_from)
    if date_to:
        where.append(f"t.{quote_ident(date_col)}::date <= %s")
        params.append(date_to)
    if company_id:
        if company_id_col:
            where.append(f"t.{quote_ident(company_id_col)}::text = %s")
            params.append(company_id)
        else:
            return []

    where_sql = ""
    if where:
        where_sql = " WHERE " + " AND ".join(where)

    query = (
        f"SELECT {', '.join(select_fields)} "
        f"FROM {table.qualified_name} t"
        f"{where_sql} "
        f"ORDER BY t.{quote_ident(date_col)} DESC NULLS LAST "
        "LIMIT 500"
    )
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(query, tuple(params))
        rows = cur.fetchall()
    return [dict(row) for row in rows]


def _table_column_data_types(conn, table_ref) -> dict[str, str]:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT lower(column_name), lower(data_type)
            FROM information_schema.columns
            WHERE table_schema = %s
              AND table_name = %s
            """,
            (table_ref.schema, table_ref.table),
        )
        rows = cur.fetchall()
    return {row[0]: row[1] for row in rows}


def _numeric_select_expr(alias: str, column_name: str, data_type: str) -> str:
    col = f"{alias}.{quote_ident(column_name)}"
    normalized_type = (data_type or "").lower()

    if normalized_type in _NUMERIC_TYPES:
        return f"COALESCE({col}::numeric, 0::numeric)"

    if normalized_type in _BOOLEAN_TYPES:
        return f"CASE WHEN COALESCE({col}, FALSE) THEN 1::numeric ELSE 0::numeric END"

    cleaned = f"NULLIF(REGEXP_REPLACE({col}::text, '[^0-9+\\.-]', '', 'g'), '')"
    return (
        "CASE "
        f"WHEN {cleaned} IS NULL THEN 0::numeric "
        f"WHEN {cleaned} ~ '^[+-]?([0-9]+(\\.[0-9]+)?|\\.[0-9]+)$' THEN {cleaned}::numeric "
        "ELSE 0::numeric "
        "END"
    )


def _load_advances(
    conn,
    *,
    date_from: date | None,
    date_to: date | None,
    company_id: str | None,
) -> list[dict]:
    table = resolve_table(
        conn,
        "salary_advances",
        "salaryadvance",
        "salaryadvancerequests",
        "employee_advances",
        "tam_ungs",
        "tamung",
    )
    if not table:
        return []

    cols = table_columns(conn, table)
    id_col = pick_column(cols, "id")
    employee_id_col = pick_column(cols, "employee_id", "employeeid", "staff_id", "staffid")
    employee_name_col = pick_column(cols, "employee_name", "employeename", "staff_name", "staffname")
    amount_col = pick_column(cols, "amount", "advance_amount", "money")
    date_col = pick_column(cols, "date", "advance_date", "created_at", "created_date")
    reason_col = pick_column(cols, "reason", "note", "description")
    state_col = pick_column(cols, "state", "status")
    company_id_col = pick_column(cols, "company_id", "companyid")

    if not id_col or not amount_col or not date_col:
        return []

    select_fields = [
        f'a.{quote_ident(id_col)}::text AS id',
        f'a.{quote_ident(date_col)}::date AS date',
        (
            f'a.{quote_ident(employee_id_col)}::text AS "employeeId"'
            if employee_id_col
            else 'NULL::text AS "employeeId"'
        ),
        (
            f'a.{quote_ident(employee_name_col)} AS "employeeName"'
            if employee_name_col
            else 'NULL::text AS "employeeName"'
        ),
        f'COALESCE(a.{quote_ident(amount_col)}, 0) AS amount',
        (
            f'a.{quote_ident(reason_col)} AS reason'
            if reason_col
            else 'NULL::text AS reason'
        ),
        (
            f'a.{quote_ident(state_col)} AS state'
            if state_col
            else 'NULL::text AS state'
        ),
    ]

    where: list[str] = []
    params: list = []

    if date_from:
        where.append(f"a.{quote_ident(date_col)}::date >= %s")
        params.append(date_from)
    if date_to:
        where.append(f"a.{quote_ident(date_col)}::date <= %s")
        params.append(date_to)
    if company_id:
        if company_id_col:
            where.append(f"a.{quote_ident(company_id_col)}::text = %s")
            params.append(company_id)
        else:
            return []

    where_sql = ""
    if where:
        where_sql = " WHERE " + " AND ".join(where)

    query = (
        f"SELECT {', '.join(select_fields)} "
        f"FROM {table.qualified_name} a"
        f"{where_sql} "
        f"ORDER BY a.{quote_ident(date_col)} DESC NULLS LAST "
        "LIMIT 500"
    )

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(query, tuple(params))
        rows = cur.fetchall()
    return [dict(row) for row in rows]


# ---------------------------------------------------------------------------
# GET /api/hr/timekeeping
# ---------------------------------------------------------------------------


@router.get("/timekeeping")
async def hr_timekeeping(
    dateFrom: date | None = Query(default=None),
    dateTo: date | None = Query(default=None),
    companyId: str | None = Query(default=None),
    employeeId: str | None = Query(default=None),
    _user: dict = Depends(require_auth),
):
    """Return attendance/timekeeping records by month."""
    try:
        with get_conn() as conn:
            records = _load_timekeeping(
                conn, date_from=dateFrom, date_to=dateTo, company_id=companyId,
            )
            if employeeId:
                records = [r for r in records if r.get("employeeId") == employeeId]
            return {
                "items": records,
                "totalItems": len(records),
                "meta": {
                    "dateFrom": dateFrom.isoformat() if dateFrom else None,
                    "dateTo": dateTo.isoformat() if dateTo else None,
                    "companyId": companyId,
                },
            }
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")


# ---------------------------------------------------------------------------
# GET /api/hr/salary-advances
# ---------------------------------------------------------------------------


@router.get("/salary-advances")
async def hr_salary_advances(
    dateFrom: date | None = Query(default=None),
    dateTo: date | None = Query(default=None),
    companyId: str | None = Query(default=None),
    employeeId: str | None = Query(default=None),
    _user: dict = Depends(require_auth),
):
    """Return salary advance vouchers."""
    try:
        with get_conn() as conn:
            records = _load_advances(
                conn, date_from=dateFrom, date_to=dateTo, company_id=companyId,
            )
            if employeeId:
                records = [r for r in records if r.get("employeeId") == employeeId]
            return {
                "items": records,
                "totalItems": len(records),
                "meta": {
                    "dateFrom": dateFrom.isoformat() if dateFrom else None,
                    "dateTo": dateTo.isoformat() if dateTo else None,
                    "companyId": companyId,
                },
            }
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")


# ---------------------------------------------------------------------------
# GET /api/hr/salary-payments
# ---------------------------------------------------------------------------


@router.get("/salary-payments")
async def hr_salary_payments(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=0, le=500),
    offset: int | None = Query(default=None, ge=0),
    limit: int | None = Query(default=None, ge=0, le=5000),
    dateFrom: date | None = Query(default=None),
    dateTo: date | None = Query(default=None),
    companyId: str | None = Query(default=None),
    employeeId: str | None = Query(default=None),
    search: str = Query(default=""),
    _user: dict = Depends(require_auth),
):
    """Return salary payment records (actual disbursements)."""
    from app.core.lookup_sql import empty_page, page_window
    from app.core.pagination import paginate

    effective_offset, effective_limit = page_window(
        page=page, per_page=per_page, offset=offset, limit=limit, default_limit=20,
    )

    try:
        with get_conn() as conn:
            table = resolve_table(
                conn,
                "salary_payments", "salarypayments",
                "salary_payment", "salarypayment",
                "hr_payslips", "hrpayslips",
                "payslips", "payslip",
                "luong_thuc_linh",
            )
            if not table:
                return empty_page(effective_offset, effective_limit)

            cols = table_columns(conn, table)
            id_col = pick_column(cols, "id")
            if not id_col:
                return empty_page(effective_offset, effective_limit)

            name_col = pick_column(cols, "name", "display_name", "reference", "ref")
            date_col = pick_column(cols, "date", "payment_date", "date_from", "created_at")
            amount_col = pick_column(cols, "amount", "amount_total", "net_salary", "total")
            employee_id_col = pick_column(cols, "employee_id", "employeeid", "staff_id")
            employee_name_col = pick_column(cols, "employee_name", "employeename", "staff_name")
            company_id_col = pick_column(cols, "company_id", "companyid")
            state_col = pick_column(cols, "state", "status")
            note_col = pick_column(cols, "note", "memo", "description")

            amount_expr = f"COALESCE(t.{quote_ident(amount_col)}, 0)" if amount_col else "0::numeric"

            joins = ""
            employee_name_expr = (
                f't.{quote_ident(employee_name_col)}' if employee_name_col else "NULL::text"
            )
            if not employee_name_col and employee_id_col:
                emp_table = resolve_table(conn, "employees", "employee")
                if emp_table:
                    emp_cols = table_columns(conn, emp_table)
                    e_id_col = pick_column(emp_cols, "id")
                    e_name_col = pick_column(emp_cols, "name", "display_name")
                    if e_id_col and e_name_col:
                        joins = (
                            f" LEFT JOIN {emp_table.qualified_name} e"
                            f" ON t.{quote_ident(employee_id_col)} = e.{quote_ident(e_id_col)}"
                        )
                        employee_name_expr = f"e.{quote_ident(e_name_col)}"

            select_fields = [
                f't.{quote_ident(id_col)}::text AS id',
                (f"COALESCE(t.{quote_ident(name_col)}, t.{quote_ident(id_col)}::text) AS name"
                 if name_col else f't.{quote_ident(id_col)}::text AS name'),
                (f't.{quote_ident(date_col)} AS date' if date_col else "NULL::timestamp AS date"),
                f"{amount_expr} AS amount",
                (f't.{quote_ident(employee_id_col)}::text AS "employeeId"'
                 if employee_id_col else 'NULL::text AS "employeeId"'),
                f'{employee_name_expr} AS "employeeName"',
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

            if employeeId:
                if not employee_id_col:
                    return empty_page(effective_offset, effective_limit)
                where_clauses.append(f"t.{quote_ident(employee_id_col)}::text = %s")
                params.append(employeeId)

            if search.strip():
                pattern = f"%{search.strip()}%"
                search_parts: list[str] = []
                if name_col:
                    search_parts.append(f"t.{quote_ident(name_col)} ILIKE %s")
                    params.append(pattern)
                if employee_name_col:
                    search_parts.append(f"t.{quote_ident(employee_name_col)} ILIKE %s")
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
                f"SELECT {', '.join(select_fields)} FROM {table.qualified_name} t"
                + joins
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
# GET /api/hr/salary-reports
# ---------------------------------------------------------------------------


@router.get("/salary-reports")
async def hr_salary_reports(
    dateFrom: date | None = Query(default=None),
    dateTo: date | None = Query(default=None),
    companyId: str | None = Query(default=None),
    _user: dict = Depends(require_auth),
):
    """Return salary payment summary per employee."""
    try:
        with get_conn() as conn:
            employees = _load_employees(conn, company_id=companyId)
            timekeeping = _load_timekeeping(
                conn, date_from=dateFrom, date_to=dateTo, company_id=companyId,
            )
            advances = _load_advances(
                conn, date_from=dateFrom, date_to=dateTo, company_id=companyId,
            )

            tk_by_emp: dict[str, float] = {}
            for tk in timekeeping:
                eid = tk.get("employeeId") or ""
                tk_by_emp[eid] = tk_by_emp.get(eid, 0) + float(tk.get("hours") or 0)

            adv_by_emp: dict[str, float] = {}
            for adv in advances:
                eid = adv.get("employeeId") or ""
                adv_by_emp[eid] = adv_by_emp.get(eid, 0) + float(adv.get("amount") or 0)

            items = []
            for emp in employees:
                eid = emp.get("id") or ""
                monthly_salary = float(emp.get("monthlySalary") or 0)
                allowance = float(emp.get("allowance") or 0)
                commission = float(emp.get("commission") or 0)
                total_hours = tk_by_emp.get(eid, 0)
                total_advances = adv_by_emp.get(eid, 0)
                gross = monthly_salary + allowance + commission
                net = gross - total_advances
                items.append({
                    "employeeId": eid,
                    "employeeName": emp.get("name"),
                    "jobTitle": emp.get("jobTitle"),
                    "companyId": emp.get("companyId"),
                    "companyName": emp.get("companyName"),
                    "monthlySalary": monthly_salary,
                    "allowance": allowance,
                    "commission": commission,
                    "totalHours": total_hours,
                    "totalAdvances": total_advances,
                    "grossSalary": gross,
                    "netSalary": net,
                })

            return {
                "items": items,
                "totalItems": len(items),
                "meta": {
                    "dateFrom": dateFrom.isoformat() if dateFrom else None,
                    "dateTo": dateTo.isoformat() if dateTo else None,
                    "companyId": companyId,
                },
            }
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")
