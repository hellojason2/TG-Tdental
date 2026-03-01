"""CRM tasks APIs with list/counts/categories and CRUD."""

from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
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

router = APIRouter(prefix="/api", tags=["tasks"])

_APP_TASKS_TABLE = "app_tasks"
_APP_TASK_CATEGORIES_TABLE = "app_task_categories"


class TaskCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    description: str | None = None
    stage: int = 0
    priority: bool = False
    active: bool = True
    categoryId: str | None = None
    companyId: str | None = None
    partnerId: str | None = None
    dateAssign: datetime | None = None
    dateStart: datetime | None = None
    dateDone: datetime | None = None
    dateExpire: datetime | None = None
    cancelReason: str | None = None
    result: str | None = None
    note: str | None = None


class TaskUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=500)
    description: str | None = None
    stage: int | None = None
    priority: bool | None = None
    active: bool | None = None
    categoryId: str | None = None
    companyId: str | None = None
    partnerId: str | None = None
    dateAssign: datetime | None = None
    dateStart: datetime | None = None
    dateDone: datetime | None = None
    dateExpire: datetime | None = None
    cancelReason: str | None = None
    result: str | None = None
    note: str | None = None


def _ensure_app_task_tables(conn) -> None:
    with conn.cursor() as cur:
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS public.{quote_ident(_APP_TASKS_TABLE)} (
                id UUID PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                stage INTEGER NOT NULL DEFAULT 0,
                priority BOOLEAN NOT NULL DEFAULT FALSE,
                active BOOLEAN NOT NULL DEFAULT TRUE,
                category_id UUID,
                company_id UUID,
                partner_id UUID,
                date_assign TIMESTAMP,
                date_start TIMESTAMP,
                date_done TIMESTAMP,
                date_expire TIMESTAMP,
                cancel_reason TEXT,
                result TEXT,
                note TEXT,
                ref_code BIGINT NOT NULL DEFAULT 0,
                notify_count INTEGER NOT NULL DEFAULT 0,
                is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
                date_created TIMESTAMP NOT NULL DEFAULT NOW(),
                last_updated TIMESTAMP NOT NULL DEFAULT NOW()
            );
            """
        )
        cur.execute(
            f"""
            CREATE INDEX IF NOT EXISTS idx_{_APP_TASKS_TABLE}_company_id
            ON public.{quote_ident(_APP_TASKS_TABLE)} (company_id);
            """
        )
        cur.execute(
            f"""
            CREATE INDEX IF NOT EXISTS idx_{_APP_TASKS_TABLE}_stage
            ON public.{quote_ident(_APP_TASKS_TABLE)} (stage);
            """
        )
        cur.execute(
            f"""
            CREATE INDEX IF NOT EXISTS idx_{_APP_TASKS_TABLE}_date_created
            ON public.{quote_ident(_APP_TASKS_TABLE)} (date_created);
            """
        )

        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS public.{quote_ident(_APP_TASK_CATEGORIES_TABLE)} (
                id UUID PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                active BOOLEAN NOT NULL DEFAULT TRUE,
                is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
                is_template BOOLEAN NOT NULL DEFAULT FALSE,
                date_created TIMESTAMP NOT NULL DEFAULT NOW(),
                last_updated TIMESTAMP NOT NULL DEFAULT NOW()
            );
            """
        )

        cur.execute(
            f"""
            INSERT INTO public.{quote_ident(_APP_TASK_CATEGORIES_TABLE)}
                (id, name, description, active, is_deleted, is_template)
            VALUES
                ('11111111-1111-1111-1111-111111111111', 'Consulting', 'Consulting and sales tasks', TRUE, FALSE, FALSE),
                ('22222222-2222-2222-2222-222222222222', 'Customer Care', 'Customer follow-up and reminders', TRUE, FALSE, FALSE),
                ('33333333-3333-3333-3333-333333333333', 'Internal', 'Internal operations tasks', TRUE, FALSE, FALSE)
            ON CONFLICT (id) DO NOTHING;
            """
        )


def _resolve_tasks_table(conn) -> TableRef:
    table_ref = resolve_table(
        conn,
        "crm_tasks",
        "crmtasks",
        "tasks",
        "task",
    )
    if table_ref:
        return table_ref

    _ensure_app_task_tables(conn)
    return TableRef(schema="public", table=_APP_TASKS_TABLE)


def _resolve_task_categories_table(conn) -> TableRef:
    table_ref = resolve_table(
        conn,
        "crm_task_categories",
        "crmtaskcategories",
        "task_categories",
        "taskcategory",
    )
    if table_ref:
        return table_ref

    _ensure_app_task_tables(conn)
    return TableRef(schema="public", table=_APP_TASK_CATEGORIES_TABLE)


def _task_field_map(columns: tuple[str, ...]) -> dict[str, str | None]:
    return {
        "id": pick_column(columns, "id"),
        "title": pick_column(columns, "title", "name"),
        "description": pick_column(columns, "description"),
        "stage": pick_column(columns, "stage", "state"),
        "priority": pick_column(columns, "priority"),
        "active": pick_column(columns, "active", "is_active", "isactive"),
        "category_id": pick_column(
            columns,
            "crm_task_category_id",
            "crmtaskcategoryid",
            "category_id",
            "categoryid",
        ),
        "company_id": pick_column(columns, "company_id", "companyid"),
        "partner_id": pick_column(columns, "partner_id", "partnerid", "order_partner_id", "orderpartnerid"),
        "date_assign": pick_column(columns, "date_assign", "dateassign"),
        "date_start": pick_column(columns, "date_start", "datestart"),
        "date_done": pick_column(columns, "date_done", "datedone"),
        "date_expire": pick_column(columns, "date_expire", "dateexpire"),
        "cancel_reason": pick_column(columns, "cancel_reason", "cancelreason"),
        "result": pick_column(columns, "result"),
        "note": pick_column(columns, "note"),
        "ref_code": pick_column(columns, "ref_code", "refcode"),
        "notify_count": pick_column(columns, "notify_count", "notifycount"),
        "is_deleted": pick_column(columns, "is_deleted", "isdeleted"),
        "date_created": pick_column(columns, "date_created", "datecreated", "created_at", "createdat"),
        "last_updated": pick_column(columns, "last_updated", "lastupdated", "updated_at", "updatedat"),
    }


def _task_categories_field_map(columns: tuple[str, ...]) -> dict[str, str | None]:
    return {
        "id": pick_column(columns, "id"),
        "name": pick_column(columns, "name", "title"),
        "description": pick_column(columns, "description"),
        "active": pick_column(columns, "active", "is_active", "isactive"),
        "is_deleted": pick_column(columns, "is_deleted", "isdeleted"),
        "is_template": pick_column(columns, "is_template", "istemplate"),
        "date_created": pick_column(columns, "date_created", "datecreated", "created_at", "createdat"),
        "last_updated": pick_column(columns, "last_updated", "lastupdated", "updated_at", "updatedat"),
    }


def _build_task_select(table_ref: TableRef, fields: dict[str, str | None]) -> str:
    id_col = fields["id"]
    if not id_col:
        return ""

    title_expr = (
        f"t.{quote_ident(fields['title'])}"
        if fields["title"]
        else "NULL::text"
    )
    description_expr = (
        f"t.{quote_ident(fields['description'])}"
        if fields["description"]
        else "NULL::text"
    )
    stage_expr = (
        f"COALESCE(t.{quote_ident(fields['stage'])}, 0)"
        if fields["stage"]
        else "0"
    )
    priority_expr = (
        f"COALESCE(t.{quote_ident(fields['priority'])}, FALSE)"
        if fields["priority"]
        else "FALSE"
    )
    active_expr = (
        f"COALESCE(t.{quote_ident(fields['active'])}, TRUE)"
        if fields["active"]
        else "TRUE"
    )

    def expr_or_null(key: str) -> str:
        if not fields[key]:
            return "NULL::text"
        return f"t.{quote_ident(fields[key])}::text"

    def datetime_expr_or_null(key: str) -> str:
        if not fields[key]:
            return "NULL::timestamp"
        return f"t.{quote_ident(fields[key])}"

    ref_code_expr = (
        f"COALESCE(t.{quote_ident(fields['ref_code'])}, 0)"
        if fields["ref_code"]
        else "0"
    )
    notify_count_expr = (
        f"COALESCE(t.{quote_ident(fields['notify_count'])}, 0)"
        if fields["notify_count"]
        else "0"
    )
    cancel_reason_expr = (
        f"t.{quote_ident(fields['cancel_reason'])}"
        if fields["cancel_reason"]
        else "NULL::text"
    )
    result_expr = (
        f"t.{quote_ident(fields['result'])}"
        if fields["result"]
        else "NULL::text"
    )
    note_expr = (
        f"t.{quote_ident(fields['note'])}"
        if fields["note"]
        else "NULL::text"
    )

    return (
        "SELECT "
        f"t.{quote_ident(id_col)}::text AS id, "
        f"COALESCE({title_expr}, '') AS title, "
        f"{description_expr} AS description, "
        f"{stage_expr} AS stage, "
        f"{priority_expr} AS priority, "
        f"{active_expr} AS active, "
        f"{expr_or_null('category_id')} AS \"categoryId\", "
        f"{expr_or_null('company_id')} AS \"companyId\", "
        f"{expr_or_null('partner_id')} AS \"partnerId\", "
        f"{datetime_expr_or_null('date_assign')} AS \"dateAssign\", "
        f"{datetime_expr_or_null('date_start')} AS \"dateStart\", "
        f"{datetime_expr_or_null('date_done')} AS \"dateDone\", "
        f"{datetime_expr_or_null('date_expire')} AS \"dateExpire\", "
        f"{datetime_expr_or_null('date_created')} AS \"dateCreated\", "
        f"{datetime_expr_or_null('last_updated')} AS \"lastUpdated\", "
        f"{cancel_reason_expr} AS \"cancelReason\", "
        f"{result_expr} AS result, "
        f"{note_expr} AS note, "
        f"{ref_code_expr} AS \"refCode\", "
        f"{notify_count_expr} AS \"notifyCount\" "
        f"FROM {table_ref.qualified_name} t"
    )


def _task_time_window(date_from: date, date_to: date) -> tuple[datetime, datetime]:
    start_dt = datetime.combine(date_from, time.min)
    end_dt = datetime.combine(date_to + timedelta(days=1), time.min)
    return start_dt, end_dt


def _append_task_common_filters(
    *,
    where_clauses: list[str],
    params: list,
    fields: dict[str, str | None],
    search: str,
    stage: int | None,
    category_id: str | None,
    company_id: str | None,
    date_from: date | None,
    date_to: date | None,
) -> None:
    if fields["is_deleted"]:
        where_clauses.append(f"COALESCE(t.{quote_ident(fields['is_deleted'])}, FALSE) = FALSE")

    if search.strip():
        pattern = f"%{search.strip()}%"
        search_parts: list[str] = []
        if fields["title"]:
            search_parts.append(f"t.{quote_ident(fields['title'])} ILIKE %s")
            params.append(pattern)
        if fields["description"]:
            search_parts.append(f"t.{quote_ident(fields['description'])} ILIKE %s")
            params.append(pattern)
        if search_parts:
            where_clauses.append("(" + " OR ".join(search_parts) + ")")

    if stage is not None:
        if fields["stage"]:
            where_clauses.append(f"t.{quote_ident(fields['stage'])} = %s")
            params.append(stage)
        else:
            where_clauses.append("1 = 0")

    if category_id:
        if fields["category_id"]:
            where_clauses.append(f"t.{quote_ident(fields['category_id'])}::text = %s")
            params.append(category_id)
        else:
            where_clauses.append("1 = 0")

    if company_id:
        if fields["company_id"]:
            where_clauses.append(f"t.{quote_ident(fields['company_id'])}::text = %s")
            params.append(company_id)
        else:
            where_clauses.append("1 = 0")

    if date_from or date_to:
        if fields["date_created"]:
            resolved_to = date_to or (date_from or date.today())
            resolved_from = date_from or resolved_to
            if resolved_from > resolved_to:
                raise HTTPException(status_code=422, detail="dateCreateFrom must be <= dateCreateTo")
            start_dt, end_dt = _task_time_window(resolved_from, resolved_to)
            where_clauses.append(f"t.{quote_ident(fields['date_created'])} >= %s")
            where_clauses.append(f"t.{quote_ident(fields['date_created'])} < %s")
            params.extend([start_dt, end_dt])
        else:
            where_clauses.append("1 = 0")


def _fetch_task_by_id(conn, table_ref: TableRef, fields: dict[str, str | None], task_id: str) -> dict | None:
    id_col = fields["id"]
    if not id_col:
        return None

    select_sql = _build_task_select(table_ref, fields)
    if not select_sql:
        return None

    where = [f"t.{quote_ident(id_col)}::text = %s"]
    if fields["is_deleted"]:
        where.append(f"COALESCE(t.{quote_ident(fields['is_deleted'])}, FALSE) = FALSE")

    sql = f"{select_sql} WHERE {' AND '.join(where)} LIMIT 1"
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql, (task_id,))
        row = cur.fetchone()
    return dict(row) if row else None


@router.get("/tasks")
async def list_tasks(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=0, le=500),
    offset: int | None = Query(default=None, ge=0),
    limit: int | None = Query(default=None, ge=0, le=5000),
    search: str = Query(default=""),
    stage: int | None = Query(default=None),
    categoryId: str | None = Query(default=None),
    companyId: str | None = Query(default=None),
    dateCreateFrom: date | None = Query(default=None),
    dateCreateTo: date | None = Query(default=None),
    _user: dict = Depends(require_auth),
):
    """Return paginated tasks list with filters."""
    effective_offset, effective_limit = page_window(
        page=page,
        per_page=per_page,
        offset=offset,
        limit=limit,
        default_limit=20,
    )

    try:
        with get_conn() as conn:
            table_ref = _resolve_tasks_table(conn)
            fields = _task_field_map(table_columns(conn, table_ref))
            if not fields["id"]:
                return empty_page(effective_offset, effective_limit)

            base_select = _build_task_select(table_ref, fields)
            if not base_select:
                return empty_page(effective_offset, effective_limit)

            where_clauses: list[str] = []
            params: list = []
            _append_task_common_filters(
                where_clauses=where_clauses,
                params=params,
                fields=fields,
                search=search,
                stage=stage,
                category_id=categoryId,
                company_id=companyId,
                date_from=dateCreateFrom,
                date_to=dateCreateTo,
            )

            base_query = base_select
            if where_clauses:
                base_query += " WHERE " + " AND ".join(where_clauses)

            order_col = fields["date_created"] or fields["last_updated"] or fields["id"]
            base_query += f" ORDER BY t.{quote_ident(order_col)} DESC NULLS LAST"

            return paginate(
                query=base_query,
                params=tuple(params),
                conn=conn,
                offset=effective_offset,
                limit=effective_limit,
            )
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")


@router.get("/tasks/counts")
async def task_counts(
    companyId: str | None = Query(default=None),
    dateCreateFrom: date | None = Query(default=None),
    dateCreateTo: date | None = Query(default=None),
    _user: dict = Depends(require_auth),
):
    """Return task counts grouped by stage."""
    try:
        with get_conn() as conn:
            table_ref = _resolve_tasks_table(conn)
            fields = _task_field_map(table_columns(conn, table_ref))
            if not fields["id"]:
                return []

            where_clauses: list[str] = []
            params: list = []
            _append_task_common_filters(
                where_clauses=where_clauses,
                params=params,
                fields=fields,
                search="",
                stage=None,
                category_id=None,
                company_id=companyId,
                date_from=dateCreateFrom,
                date_to=dateCreateTo,
            )

            if fields["stage"]:
                sql = (
                    "SELECT "
                    f"t.{quote_ident(fields['stage'])} AS stage, "
                    "COUNT(*)::bigint AS total "
                    f"FROM {table_ref.qualified_name} t"
                )
                if where_clauses:
                    sql += " WHERE " + " AND ".join(where_clauses)
                sql += f" GROUP BY t.{quote_ident(fields['stage'])} ORDER BY t.{quote_ident(fields['stage'])}"
            else:
                sql = (
                    "SELECT 0::int AS stage, COUNT(*)::bigint AS total "
                    f"FROM {table_ref.qualified_name} t"
                )
                if where_clauses:
                    sql += " WHERE " + " AND ".join(where_clauses)

            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql, tuple(params))
                rows = cur.fetchall()

            return [
                {"stage": int(row["stage"] or 0), "total": int(row["total"] or 0)}
                for row in rows
            ]
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")


@router.get("/task-categories")
async def list_task_categories(
    active: bool | None = Query(default=None),
    _user: dict = Depends(require_auth),
):
    """Return task categories for task form filters."""
    try:
        with get_conn() as conn:
            table_ref = _resolve_task_categories_table(conn)
            fields = _task_categories_field_map(table_columns(conn, table_ref))
            if not fields["id"] or not fields["name"]:
                return []

            where_clauses: list[str] = []
            params: list = []
            if fields["is_deleted"]:
                where_clauses.append(f"COALESCE(c.{quote_ident(fields['is_deleted'])}, FALSE) = FALSE")
            if active is not None:
                if fields["active"]:
                    where_clauses.append(f"COALESCE(c.{quote_ident(fields['active'])}, TRUE) = %s")
                    params.append(active)
                elif not active:
                    return []

            description_expr = (
                f"c.{quote_ident(fields['description'])}"
                if fields["description"]
                else "NULL::text"
            )
            active_expr = (
                f"COALESCE(c.{quote_ident(fields['active'])}, TRUE)"
                if fields["active"]
                else "TRUE"
            )
            template_expr = (
                f"COALESCE(c.{quote_ident(fields['is_template'])}, FALSE)"
                if fields["is_template"]
                else "FALSE"
            )
            sql = (
                "SELECT "
                f"c.{quote_ident(fields['id'])}::text AS id, "
                f"c.{quote_ident(fields['name'])} AS name, "
                f"{description_expr} AS description, "
                f"{active_expr} AS active, "
                f"{template_expr} AS \"isTemplate\" "
                f"FROM {table_ref.qualified_name} c"
            )
            if where_clauses:
                sql += " WHERE " + " AND ".join(where_clauses)
            sql += f" ORDER BY c.{quote_ident(fields['name'])} ASC NULLS LAST"

            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql, tuple(params))
                rows = cur.fetchall()

            return [dict(row) for row in rows]
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")


@router.post("/tasks")
async def create_task(
    body: TaskCreateRequest,
    user: dict = Depends(require_auth),
):
    """Create a new task."""
    del user
    try:
        with get_conn() as conn:
            table_ref = _resolve_tasks_table(conn)
            fields = _task_field_map(table_columns(conn, table_ref))
            if not fields["id"] or not fields["title"]:
                raise HTTPException(status_code=503, detail="Task table schema is missing required columns")

            task_id = str(uuid4())
            now = datetime.now(timezone.utc)

            insert_values: dict[str, object] = {
                fields["id"]: task_id,
                fields["title"]: body.title.strip(),
            }

            if fields["description"] and body.description is not None:
                insert_values[fields["description"]] = body.description
            if fields["stage"]:
                insert_values[fields["stage"]] = body.stage
            if fields["priority"]:
                insert_values[fields["priority"]] = body.priority
            if fields["active"]:
                insert_values[fields["active"]] = body.active
            if fields["category_id"] and body.categoryId is not None:
                insert_values[fields["category_id"]] = body.categoryId
            if fields["company_id"] and body.companyId is not None:
                insert_values[fields["company_id"]] = body.companyId
            if fields["partner_id"] and body.partnerId is not None:
                insert_values[fields["partner_id"]] = body.partnerId
            if fields["date_assign"] and body.dateAssign is not None:
                insert_values[fields["date_assign"]] = body.dateAssign
            if fields["date_start"] and body.dateStart is not None:
                insert_values[fields["date_start"]] = body.dateStart
            if fields["date_done"] and body.dateDone is not None:
                insert_values[fields["date_done"]] = body.dateDone
            if fields["date_expire"] and body.dateExpire is not None:
                insert_values[fields["date_expire"]] = body.dateExpire
            if fields["cancel_reason"] and body.cancelReason is not None:
                insert_values[fields["cancel_reason"]] = body.cancelReason
            if fields["result"] and body.result is not None:
                insert_values[fields["result"]] = body.result
            if fields["note"] and body.note is not None:
                insert_values[fields["note"]] = body.note
            if fields["ref_code"]:
                insert_values[fields["ref_code"]] = int(now.timestamp() * 1000)
            if fields["notify_count"]:
                insert_values[fields["notify_count"]] = 0
            if fields["is_deleted"]:
                insert_values[fields["is_deleted"]] = False
            if fields["date_created"]:
                insert_values[fields["date_created"]] = now
            if fields["last_updated"]:
                insert_values[fields["last_updated"]] = now

            cols = list(insert_values.keys())
            params = [insert_values[col] for col in cols]
            placeholders = ["%s"] * len(cols)
            sql = (
                f"INSERT INTO {table_ref.qualified_name} "
                f"({', '.join(quote_ident(col) for col in cols)}) "
                f"VALUES ({', '.join(placeholders)})"
            )

            with conn.cursor() as cur:
                cur.execute(sql, tuple(params))

            created = _fetch_task_by_id(conn, table_ref, fields, task_id)
            if not created:
                raise HTTPException(status_code=500, detail="Failed to load created task")
            return created
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")


@router.put("/tasks/{task_id}")
async def update_task(
    body: TaskUpdateRequest,
    task_id: str = Path(..., min_length=1),
    user: dict = Depends(require_auth),
):
    """Update an existing task."""
    del user
    try:
        with get_conn() as conn:
            table_ref = _resolve_tasks_table(conn)
            fields = _task_field_map(table_columns(conn, table_ref))
            if not fields["id"]:
                raise HTTPException(status_code=503, detail="Task table schema is missing id column")

            updates: dict[str, object] = {}
            if body.title is not None and fields["title"]:
                updates[fields["title"]] = body.title.strip()
            if body.description is not None and fields["description"]:
                updates[fields["description"]] = body.description
            if body.stage is not None and fields["stage"]:
                updates[fields["stage"]] = body.stage
            if body.priority is not None and fields["priority"]:
                updates[fields["priority"]] = body.priority
            if body.active is not None and fields["active"]:
                updates[fields["active"]] = body.active
            if body.categoryId is not None and fields["category_id"]:
                updates[fields["category_id"]] = body.categoryId
            if body.companyId is not None and fields["company_id"]:
                updates[fields["company_id"]] = body.companyId
            if body.partnerId is not None and fields["partner_id"]:
                updates[fields["partner_id"]] = body.partnerId
            if body.dateAssign is not None and fields["date_assign"]:
                updates[fields["date_assign"]] = body.dateAssign
            if body.dateStart is not None and fields["date_start"]:
                updates[fields["date_start"]] = body.dateStart
            if body.dateDone is not None and fields["date_done"]:
                updates[fields["date_done"]] = body.dateDone
            if body.dateExpire is not None and fields["date_expire"]:
                updates[fields["date_expire"]] = body.dateExpire
            if body.cancelReason is not None and fields["cancel_reason"]:
                updates[fields["cancel_reason"]] = body.cancelReason
            if body.result is not None and fields["result"]:
                updates[fields["result"]] = body.result
            if body.note is not None and fields["note"]:
                updates[fields["note"]] = body.note

            if fields["last_updated"]:
                updates[fields["last_updated"]] = datetime.now(timezone.utc)

            if not updates:
                existing = _fetch_task_by_id(conn, table_ref, fields, task_id)
                if not existing:
                    raise HTTPException(status_code=404, detail="Task not found")
                return existing

            set_clauses = [f"{quote_ident(col)} = %s" for col in updates.keys()]
            params = list(updates.values()) + [task_id]
            sql = (
                f"UPDATE {table_ref.qualified_name} "
                f"SET {', '.join(set_clauses)} "
                f"WHERE {quote_ident(fields['id'])}::text = %s"
            )
            if fields["is_deleted"]:
                sql += f" AND COALESCE({quote_ident(fields['is_deleted'])}, FALSE) = FALSE"

            with conn.cursor() as cur:
                cur.execute(sql, tuple(params))
                if cur.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Task not found")

            updated = _fetch_task_by_id(conn, table_ref, fields, task_id)
            if not updated:
                raise HTTPException(status_code=404, detail="Task not found")
            return updated
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")


@router.delete("/tasks/{task_id}")
async def delete_task(
    task_id: str = Path(..., min_length=1),
    user: dict = Depends(require_auth),
):
    """Delete task (soft delete when the schema supports it)."""
    del user
    try:
        with get_conn() as conn:
            table_ref = _resolve_tasks_table(conn)
            fields = _task_field_map(table_columns(conn, table_ref))
            if not fields["id"]:
                raise HTTPException(status_code=503, detail="Task table schema is missing id column")

            with conn.cursor() as cur:
                if fields["is_deleted"]:
                    params: list = [True]
                    set_clauses = [f"{quote_ident(fields['is_deleted'])} = %s"]
                    if fields["last_updated"]:
                        set_clauses.append(f"{quote_ident(fields['last_updated'])} = %s")
                        params.append(datetime.now(timezone.utc))
                    params.append(task_id)
                    sql = (
                        f"UPDATE {table_ref.qualified_name} "
                        f"SET {', '.join(set_clauses)} "
                        f"WHERE {quote_ident(fields['id'])}::text = %s "
                        f"AND COALESCE({quote_ident(fields['is_deleted'])}, FALSE) = FALSE"
                    )
                    cur.execute(sql, tuple(params))
                else:
                    sql = (
                        f"DELETE FROM {table_ref.qualified_name} "
                        f"WHERE {quote_ident(fields['id'])}::text = %s"
                    )
                    cur.execute(sql, (task_id,))

                if cur.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Task not found")

            return {"id": task_id, "deleted": True}
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")
