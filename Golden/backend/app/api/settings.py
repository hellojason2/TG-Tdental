"""Settings and user management endpoints."""

from __future__ import annotations

from uuid import uuid4

import psycopg2
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
from app.core.middleware import require_admin
from app.core.pagination import paginate

router = APIRouter(prefix="/api", tags=["settings"])


class UserCreatePayload(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=6, max_length=128)
    role: str = Field(default="viewer", max_length=50)
    active: bool = True


class UserUpdatePayload(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    email: str | None = Field(default=None, min_length=3, max_length=255)
    password: str | None = Field(default=None, min_length=6, max_length=128)
    role: str | None = Field(default=None, max_length=50)
    active: bool | None = None


class SettingItemPayload(BaseModel):
    key: str = Field(min_length=1, max_length=255)
    value: str | int | float | bool | None = None


class SettingsUpsertPayload(BaseModel):
    items: list[SettingItemPayload] = Field(default_factory=list)


def _normalise_email(email: str) -> str:
    value = email.strip().lower()
    if "@" not in value or value.startswith("@") or value.endswith("@"):
        raise HTTPException(status_code=422, detail="Email không hợp lệ")
    return value


def _normalise_role(role: str | None) -> str:
    raw = (role or "viewer").strip().lower()
    if not raw:
        return "viewer"
    if raw not in {"admin", "viewer", "manager", "staff"}:
        return raw
    return raw


def _ensure_settings_table(conn) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS app_settings (
                id UUID PRIMARY KEY,
                key TEXT UNIQUE NOT NULL,
                value TEXT,
                updated_by UUID NULL REFERENCES app_users(id) ON DELETE SET NULL,
                updated_at TIMESTAMP DEFAULT NOW()
            )
            """
        )


@router.get("/users")
async def list_users(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=0, le=500),
    offset: int | None = Query(default=None, ge=0),
    limit: int | None = Query(default=None, ge=0, le=5000),
    search: str = Query(default=""),
    _user: dict = Depends(require_admin),
):
    try:
        with get_conn() as conn:
            where: list[str] = []
            params: list = []

            search_text = search.strip()
            if search_text:
                pattern = f"%{search_text}%"
                where.append("(u.name ILIKE %s OR u.email ILIKE %s)")
                params.extend([pattern, pattern])

            where_sql = ""
            if where:
                where_sql = " WHERE " + " AND ".join(where)

            query = (
                "SELECT "
                "u.id::text AS id, "
                "u.name AS name, "
                "u.email AS email, "
                "u.role AS role, "
                "COALESCE(u.active, TRUE) AS active, "
                "u.created_at AS \"createdAt\", "
                "u.updated_at AS \"updatedAt\" "
                "FROM app_users u"
                f"{where_sql} "
                "ORDER BY u.created_at DESC NULLS LAST, u.name ASC"
            )
            return paginate(
                query=query,
                params=tuple(params),
                conn=conn,
                page=page,
                per_page=per_page,
                offset=offset,
                limit=limit,
            )
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")


@router.post("/users", status_code=201)
async def create_user(body: UserCreatePayload, _user: dict = Depends(require_admin)):
    from app.core.security import hash_password

    email = _normalise_email(body.email)

    try:
        with get_conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    INSERT INTO app_users (id, name, email, password, role, active, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
                    RETURNING
                        id::text AS id,
                        name,
                        email,
                        role,
                        COALESCE(active, TRUE) AS active,
                        created_at AS "createdAt",
                        updated_at AS "updatedAt"
                    """,
                    (
                        str(uuid4()),
                        body.name.strip(),
                        email,
                        hash_password(body.password),
                        _normalise_role(body.role),
                        bool(body.active),
                    ),
                )
                row = cur.fetchone()
                return dict(row)
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")
    except psycopg2.Error as exc:
        if "duplicate" in str(exc).lower() or "unique" in str(exc).lower():
            raise HTTPException(status_code=409, detail="Email đã tồn tại")
        raise HTTPException(status_code=400, detail="Không thể tạo tài khoản")


@router.put("/users/{user_id}")
async def update_user(user_id: str, body: UserUpdatePayload, _user: dict = Depends(require_admin)):
    from app.core.security import hash_password

    updates: list[str] = []
    params: list = []

    if body.name is not None:
        updates.append("name = %s")
        params.append(body.name.strip())

    if body.email is not None:
        updates.append("email = %s")
        params.append(_normalise_email(body.email))

    if body.password is not None:
        updates.append("password = %s")
        params.append(hash_password(body.password))

    if body.role is not None:
        updates.append("role = %s")
        params.append(_normalise_role(body.role))

    if body.active is not None:
        updates.append("active = %s")
        params.append(bool(body.active))

    if not updates:
        raise HTTPException(status_code=422, detail="Không có dữ liệu cập nhật")

    updates.append("updated_at = NOW()")

    try:
        with get_conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    f"""
                    UPDATE app_users
                    SET {', '.join(updates)}
                    WHERE id::text = %s
                    RETURNING
                        id::text AS id,
                        name,
                        email,
                        role,
                        COALESCE(active, TRUE) AS active,
                        created_at AS "createdAt",
                        updated_at AS "updatedAt"
                    """,
                    (*params, user_id),
                )
                row = cur.fetchone()
                if not row:
                    raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản")
                return dict(row)
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")
    except HTTPException:
        raise
    except psycopg2.Error as exc:
        if "duplicate" in str(exc).lower() or "unique" in str(exc).lower():
            raise HTTPException(status_code=409, detail="Email đã tồn tại")
        raise HTTPException(status_code=400, detail="Không thể cập nhật tài khoản")


@router.delete("/users/{user_id}")
async def delete_user(user_id: str, _user: dict = Depends(require_admin)):
    if user_id == str(_user.get("id") or ""):
        raise HTTPException(status_code=400, detail="Không thể xóa tài khoản đang đăng nhập")

    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM app_users WHERE id::text = %s RETURNING id::text",
                    (user_id,),
                )
                row = cur.fetchone()
                if not row:
                    raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản")
                return {"id": row[0], "deleted": True}
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")


@router.get("/settings")
async def list_settings(
    prefix: str | None = Query(default=None),
    _user: dict = Depends(require_admin),
):
    try:
        with get_conn() as conn:
            _ensure_settings_table(conn)
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                if prefix and prefix.strip():
                    like_pattern = f"{prefix.strip()}%"
                    cur.execute(
                        """
                        SELECT key, value, updated_at AS "updatedAt"
                        FROM app_settings
                        WHERE key ILIKE %s
                        ORDER BY key ASC
                        """,
                        (like_pattern,),
                    )
                else:
                    cur.execute(
                        """
                        SELECT key, value, updated_at AS "updatedAt"
                        FROM app_settings
                        ORDER BY key ASC
                        """
                    )
                rows = [dict(row) for row in cur.fetchall()]
                return {
                    "items": rows,
                    "map": {row["key"]: row.get("value") for row in rows},
                }
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")


@router.post("/settings")
async def upsert_settings(body: SettingsUpsertPayload, _user: dict = Depends(require_admin)):
    if not body.items:
        raise HTTPException(status_code=422, detail="Danh sách cài đặt trống")

    try:
        with get_conn() as conn:
            _ensure_settings_table(conn)
            saved: list[dict] = []
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                for item in body.items:
                    key = item.key.strip()
                    if not key:
                        continue
                    value = item.value
                    value_text = None if value is None else str(value)
                    cur.execute(
                        """
                        INSERT INTO app_settings (id, key, value, updated_by, updated_at)
                        VALUES (%s, %s, %s, %s::uuid, NOW())
                        ON CONFLICT (key)
                        DO UPDATE SET
                            value = EXCLUDED.value,
                            updated_by = EXCLUDED.updated_by,
                            updated_at = NOW()
                        RETURNING key, value, updated_at AS "updatedAt"
                        """,
                        (
                            str(uuid4()),
                            key,
                            value_text,
                            str(_user.get("id")) if _user.get("id") else None,
                        ),
                    )
                    row = cur.fetchone()
                    if row:
                        saved.append(dict(row))

            return {
                "saved": len(saved),
                "items": saved,
                "message": "Đã lưu cài đặt",
            }
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")


# ---------------------------------------------------------------------------
# GET /api/settings/logs  (activity / audit logs)
# ---------------------------------------------------------------------------


@router.get("/settings/logs")
async def list_activity_logs(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=0, le=500),
    offset: int | None = Query(default=None, ge=0),
    limit: int | None = Query(default=None, ge=0, le=5000),
    search: str = Query(default=""),
    companyId: str | None = Query(default=None),
    dateFrom: str | None = Query(default=None),
    dateTo: str | None = Query(default=None),
    _user: dict = Depends(require_admin),
):
    """Return activity/audit log entries."""
    from datetime import date as date_type

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
            log_table = resolve_table(
                conn,
                "activity_logs",
                "activitylogs",
                "audit_logs",
                "auditlogs",
                "app_logs",
                "logs",
                "log",
            )
            if not log_table:
                return empty_page(effective_offset, effective_limit)

            cols = table_columns(conn, log_table)
            id_col = pick_column(cols, "id")
            if not id_col:
                return empty_page(effective_offset, effective_limit)

            date_col = pick_column(cols, "date", "created_at", "created_date", "log_date", "timestamp")
            action_col = pick_column(cols, "action", "activity", "event", "type")
            description_col = pick_column(cols, "description", "message", "detail", "note")
            user_id_col = pick_column(cols, "user_id", "userid", "created_by")
            user_name_col = pick_column(cols, "user_name", "username", "created_by_name")
            model_col = pick_column(cols, "model", "resource", "entity", "table_name")
            record_id_col = pick_column(cols, "record_id", "recordid", "res_id")
            company_id_col = pick_column(cols, "company_id", "companyid")

            select_fields = [
                f'l.{quote_ident(id_col)}::text AS id',
                (f'l.{quote_ident(date_col)} AS date' if date_col else "NULL::timestamp AS date"),
                (f'l.{quote_ident(action_col)} AS action' if action_col else "NULL::text AS action"),
                (f'l.{quote_ident(description_col)} AS description'
                 if description_col else "NULL::text AS description"),
                (f'l.{quote_ident(user_id_col)}::text AS "userId"'
                 if user_id_col else 'NULL::text AS "userId"'),
                (f'l.{quote_ident(user_name_col)} AS "userName"'
                 if user_name_col else 'NULL::text AS "userName"'),
                (f'l.{quote_ident(model_col)} AS model' if model_col else "NULL::text AS model"),
                (f'l.{quote_ident(record_id_col)}::text AS "recordId"'
                 if record_id_col else 'NULL::text AS "recordId"'),
                (f'l.{quote_ident(company_id_col)}::text AS "companyId"'
                 if company_id_col else 'NULL::text AS "companyId"'),
            ]

            where_clauses: list[str] = []
            params: list = []

            if search.strip():
                pattern = f"%{search.strip()}%"
                search_parts: list[str] = []
                if action_col:
                    search_parts.append(f"l.{quote_ident(action_col)} ILIKE %s")
                    params.append(pattern)
                if description_col:
                    search_parts.append(f"l.{quote_ident(description_col)} ILIKE %s")
                    params.append(pattern)
                if user_name_col:
                    search_parts.append(f"l.{quote_ident(user_name_col)} ILIKE %s")
                    params.append(pattern)
                if search_parts:
                    where_clauses.append("(" + " OR ".join(search_parts) + ")")

            if companyId:
                if not company_id_col:
                    return empty_page(effective_offset, effective_limit)
                where_clauses.append(f"l.{quote_ident(company_id_col)}::text = %s")
                params.append(companyId)

            if parsed_date_from and date_col:
                where_clauses.append(f"l.{quote_ident(date_col)}::date >= %s")
                params.append(parsed_date_from)
            if parsed_date_to and date_col:
                where_clauses.append(f"l.{quote_ident(date_col)}::date <= %s")
                params.append(parsed_date_to)

            base_query = f"SELECT {', '.join(select_fields)} FROM {log_table.qualified_name} l"
            if where_clauses:
                base_query += " WHERE " + " AND ".join(where_clauses)
            if date_col:
                base_query += (
                    f" ORDER BY l.{quote_ident(date_col)} DESC NULLS LAST, "
                    f"l.{quote_ident(id_col)} DESC"
                )
            else:
                base_query += f" ORDER BY l.{quote_ident(id_col)} DESC"

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
# Teams CRUD (simple stub for settings-team page)
# ---------------------------------------------------------------------------


@router.get("/teams")
async def list_teams(_user: dict = Depends(require_admin)):
    """Return teams list. Tries to find a teams table; returns empty if none."""
    try:
        with get_conn() as conn:
            tbl = resolve_table(conn, "teams", "app_teams", "user_teams")
            if not tbl:
                return empty_page(0, 20)
            cols = table_columns(conn, tbl)
            id_col = pick_column(cols, "id")
            if not id_col:
                return empty_page(0, 20)
            name_col = pick_column(cols, "name", "team_name", "title")
            desc_col = pick_column(cols, "description", "note", "desc")
            select_fields = [
                f't.{quote_ident(id_col)}::text AS id',
                (f't.{quote_ident(name_col)} AS name' if name_col else "'Unnamed' AS name"),
                (f't.{quote_ident(desc_col)} AS description' if desc_col else "NULL::text AS description"),
            ]
            q = f"SELECT {', '.join(select_fields)} FROM {tbl.qualified_name} t ORDER BY t.{quote_ident(name_col or id_col)}"
            return paginate(query=q, params=(), conn=conn, offset=0, limit=100)
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")


@router.post("/teams")
async def create_team(body: dict, _user: dict = Depends(require_admin)):
    """Stub: create a team. Returns success for now."""
    return {"ok": True, "message": "Team created"}


@router.get("/teams/{team_id}/members")
async def team_members(team_id: str, _user: dict = Depends(require_admin)):
    """Return team members. Stub returns empty."""
    return {"offset": 0, "limit": 20, "totalItems": 0, "items": []}
