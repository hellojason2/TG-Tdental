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
