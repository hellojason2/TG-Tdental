"""Settings and user management endpoints."""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

import psycopg2
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
from app.core.middleware import require_admin
from app.core.pagination import paginate


class CompanyCreatePayload(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    address: str | None = None
    phone: str | None = None
    active: bool = True
    isHead: bool = False


class CompanyUpdatePayload(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    address: str | None = None
    phone: str | None = None
    active: bool | None = None
    isHead: bool | None = None

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
# Teams CRUD for settings-team page
# ---------------------------------------------------------------------------


@router.get("/teams")
async def list_teams(_user: dict = Depends(require_admin)):
    """Return teams list from CRM/app team tables."""
    try:
        with get_conn() as conn:
            tbl = resolve_table(
                conn,
                "crm_teams",
                "crmteams",
                "teams",
                "app_teams",
                "user_teams",
            )
            if not tbl:
                return empty_page(0, 20)
            cols = table_columns(conn, tbl)
            id_col = pick_column(cols, "id")
            if not id_col:
                return empty_page(0, 20)
            name_col = pick_column(cols, "name", "team_name", "title")
            desc_col = pick_column(
                cols,
                "description",
                "note",
                "desc",
                "lead_properties_definition",
                "leadpropertiesdefinition",
            )
            active_col = pick_column(cols, "active", "is_active")
            select_fields = [
                f't.{quote_ident(id_col)}::text AS id',
                (f't.{quote_ident(name_col)} AS name' if name_col else "'Unnamed' AS name"),
                (f't.{quote_ident(desc_col)} AS description' if desc_col else "NULL::text AS description"),
            ]
            q = f"SELECT {', '.join(select_fields)} FROM {tbl.qualified_name} t"
            if active_col:
                q += f" WHERE COALESCE(t.{quote_ident(active_col)}, TRUE)"
            q += f" ORDER BY t.{quote_ident(name_col or id_col)}"
            return paginate(query=q, params=(), conn=conn, offset=0, limit=100)
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")


@router.post("/teams")
async def create_team(body: dict, _user: dict = Depends(require_admin)):
    """Create a team in the resolved CRM/app team table."""
    name = str((body or {}).get("name") or "").strip()
    description = str((body or {}).get("description") or "").strip() or None
    if not name:
        raise HTTPException(status_code=422, detail="name is required")

    try:
        with get_conn() as conn:
            tbl = resolve_table(
                conn,
                "crm_teams",
                "crmteams",
                "teams",
                "app_teams",
                "user_teams",
            )
            if not tbl:
                raise HTTPException(status_code=503, detail="Team table not found")

            cols = table_columns(conn, tbl)
            id_col = pick_column(cols, "id")
            name_col = pick_column(cols, "name", "team_name", "title")
            if not name_col:
                raise HTTPException(status_code=500, detail="Team name column not found")

            desc_col = pick_column(
                cols,
                "description",
                "note",
                "desc",
                "lead_properties_definition",
                "leadpropertiesdefinition",
            )
            active_col = pick_column(cols, "active", "is_active")
            company_col = pick_column(cols, "company_id", "companyid")
            user_col = pick_column(cols, "user_id", "userid", "owner_id", "ownerid")
            is_ho_col = pick_column(cols, "is_ho", "isho")
            created_col = pick_column(cols, "date_created", "datecreated", "created_at")
            updated_col = pick_column(cols, "lastupdated", "updated_at")
            created_by_col = pick_column(cols, "created_by_id", "createdbyid")
            write_by_col = pick_column(cols, "write_by_id", "writebyid")

            insert_cols: list[str] = []
            values: list = []

            if id_col:
                insert_cols.append(id_col)
                values.append(str(uuid4()))

            insert_cols.append(name_col)
            values.append(name)

            if desc_col:
                insert_cols.append(desc_col)
                values.append(description)
            if active_col:
                insert_cols.append(active_col)
                values.append(True)
            if is_ho_col:
                insert_cols.append(is_ho_col)
                values.append(bool((body or {}).get("isHo", False)))
            if company_col:
                insert_cols.append(company_col)
                values.append((body or {}).get("companyId"))
            if user_col and (body or {}).get("userId"):
                insert_cols.append(user_col)
                values.append((body or {}).get("userId"))
            now = datetime.utcnow()
            if created_col:
                insert_cols.append(created_col)
                values.append(now)
            if updated_col:
                insert_cols.append(updated_col)
                values.append(now)
            if created_by_col and (body or {}).get("createdById"):
                insert_cols.append(created_by_col)
                values.append((body or {}).get("createdById"))
            if write_by_col and (body or {}).get("writeById"):
                insert_cols.append(write_by_col)
                values.append((body or {}).get("writeById"))

            quoted_cols = ", ".join(quote_ident(c) for c in insert_cols)
            placeholders = ", ".join(["%s"] * len(values))
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    f"INSERT INTO {tbl.qualified_name} ({quoted_cols}) VALUES ({placeholders})",
                    tuple(values),
                )

            return {"ok": True, "id": values[0] if id_col else None, "name": name, "description": description}
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")
    except psycopg2.Error as exc:
        raise HTTPException(status_code=500, detail=f"Failed to create team: {exc.pgerror or str(exc)}")


@router.get("/teams/{team_id}/members")
async def team_members(team_id: str, _user: dict = Depends(require_admin)):
    """Return team members with user info when available."""
    try:
        with get_conn() as conn:
            members_tbl = resolve_table(
                conn,
                "crm_team_members",
                "crmteammembers",
                "team_members",
                "teammembers",
                "app_team_members",
                "appteammembers",
            )
            if not members_tbl:
                return empty_page(0, 20)

            cols = table_columns(conn, members_tbl)
            id_col = pick_column(cols, "id")
            team_col = pick_column(cols, "crm_team_id", "crmteamid", "team_id", "teamid")
            user_col = pick_column(cols, "user_id", "userid", "employee_id", "employeeid", "member_id", "memberid")
            role_col = pick_column(cols, "role")
            active_col = pick_column(cols, "active", "is_active")
            if not team_col or not user_col:
                return empty_page(0, 20)

            joins = ""
            name_expr = f"m.{quote_ident(user_col)}::text"
            email_expr = "NULL::text"
            role_expr = (
                f"NULLIF(m.{quote_ident(role_col)}::text, '')"
                if role_col
                else "NULL::text"
            )

            user_tbl = resolve_table(conn, "app_users", "users", "application_users", "applicationusers")
            if user_tbl:
                u_cols = table_columns(conn, user_tbl)
                u_id = pick_column(u_cols, "id")
                u_name = pick_column(u_cols, "name", "display_name")
                u_email = pick_column(u_cols, "email")
                u_role = pick_column(u_cols, "role")
                if u_id:
                    joins += (
                        f" LEFT JOIN {user_tbl.qualified_name} u"
                        f" ON m.{quote_ident(user_col)}::text = u.{quote_ident(u_id)}::text"
                    )
                    if u_name:
                        name_expr = f"COALESCE(NULLIF(u.{quote_ident(u_name)}::text, ''), {name_expr})"
                    if u_email:
                        email_expr = f"NULLIF(u.{quote_ident(u_email)}::text, '')"
                    if u_role and role_col is None:
                        role_expr = f"NULLIF(u.{quote_ident(u_role)}::text, '')"

            employee_tbl = resolve_table(conn, "employees", "employee")
            if employee_tbl:
                e_cols = table_columns(conn, employee_tbl)
                e_user_id = pick_column(e_cols, "user_id", "userid")
                e_name = pick_column(e_cols, "name", "display_name")
                e_email = pick_column(e_cols, "email")
                e_is_doctor = pick_column(e_cols, "is_doctor", "isdoctor")
                e_is_assistant = pick_column(e_cols, "is_assistant", "isassistant")
                e_is_receptionist = pick_column(e_cols, "is_receptionist", "isreceptionist")
                if e_user_id:
                    joins += (
                        f" LEFT JOIN {employee_tbl.qualified_name} e"
                        f" ON m.{quote_ident(user_col)}::text = e.{quote_ident(e_user_id)}::text"
                    )
                    if e_name:
                        name_expr = (
                            f"COALESCE(NULLIF(e.{quote_ident(e_name)}::text, ''), {name_expr})"
                        )
                    if e_email:
                        email_expr = (
                            f"COALESCE(NULLIF(e.{quote_ident(e_email)}::text, ''), {email_expr})"
                        )
                    if role_col is None and role_expr == "NULL::text":
                        role_parts: list[str] = []
                        if e_is_doctor:
                            role_parts.append(f"WHEN COALESCE(e.{quote_ident(e_is_doctor)}, FALSE) THEN 'doctor'")
                        if e_is_assistant:
                            role_parts.append(
                                f"WHEN COALESCE(e.{quote_ident(e_is_assistant)}, FALSE) THEN 'assistant'"
                            )
                        if e_is_receptionist:
                            role_parts.append(
                                f"WHEN COALESCE(e.{quote_ident(e_is_receptionist)}, FALSE) THEN 'receptionist'"
                            )
                        if role_parts:
                            role_expr = "CASE " + " ".join(role_parts) + " ELSE NULL END"

            select_id_expr = (
                f"m.{quote_ident(id_col)}::text"
                if id_col
                else f"m.{quote_ident(user_col)}::text"
            )
            select_active_expr = (
                f"COALESCE(m.{quote_ident(active_col)}, TRUE)"
                if active_col
                else "TRUE"
            )

            query = (
                "SELECT "
                f"{select_id_expr} AS id, "
                f"m.{quote_ident(user_col)}::text AS \"userId\", "
                f"{name_expr} AS name, "
                f"{email_expr} AS email, "
                f"{role_expr} AS role, "
                f"{select_active_expr} AS active "
                f"FROM {members_tbl.qualified_name} m"
                f"{joins} "
                f"WHERE m.{quote_ident(team_col)}::text = %s"
            )
            params: list = [team_id]
            if active_col:
                query += f" AND COALESCE(m.{quote_ident(active_col)}, TRUE)"
            query += " ORDER BY name ASC NULLS LAST"
            return paginate(query=query, params=tuple(params), conn=conn, offset=0, limit=200)
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")


# ---------------------------------------------------------------------------
# Team member management
# ---------------------------------------------------------------------------


def _resolve_team_members_table(conn):
    """Resolve team members table and key columns."""
    members_tbl = resolve_table(
        conn,
        "crm_team_members",
        "crmteammembers",
        "team_members",
        "teammembers",
        "app_team_members",
        "appteammembers",
    )
    if not members_tbl:
        return None, None
    cols = table_columns(conn, members_tbl)
    return members_tbl, cols


@router.post("/teams/{team_id}/members", status_code=201)
async def add_team_member(
    team_id: str = Path(..., min_length=1),
    body: dict = Body(...),
    _user: dict = Depends(require_admin),
):
    """Add a member to a team."""
    user_id = str((body or {}).get("userId") or "").strip()
    if not user_id:
        raise HTTPException(status_code=422, detail="userId is required")

    try:
        with get_conn() as conn:
            members_tbl, cols = _resolve_team_members_table(conn)
            if not members_tbl:
                raise HTTPException(status_code=503, detail="Team members table not found")

            id_col = pick_column(cols, "id")
            team_col = pick_column(cols, "crm_team_id", "crmteamid", "team_id", "teamid")
            user_col = pick_column(cols, "user_id", "userid", "employee_id", "employeeid", "member_id", "memberid")
            active_col = pick_column(cols, "active", "is_active")
            role_col = pick_column(cols, "role")

            if not team_col or not user_col:
                raise HTTPException(status_code=503, detail="Team members table schema incomplete")

            insert_cols: list[str] = []
            values: list = []

            if id_col:
                insert_cols.append(id_col)
                values.append(str(uuid4()))
            insert_cols.append(team_col)
            values.append(team_id)
            insert_cols.append(user_col)
            values.append(user_id)
            if active_col:
                insert_cols.append(active_col)
                values.append(True)
            if role_col and (body or {}).get("role"):
                insert_cols.append(role_col)
                values.append((body or {}).get("role"))

            created_col = pick_column(cols, "date_created", "datecreated", "created_at")
            if created_col:
                insert_cols.append(created_col)
                values.append(datetime.utcnow())

            quoted_cols = ", ".join(quote_ident(c) for c in insert_cols)
            placeholders = ", ".join(["%s"] * len(values))
            with conn.cursor() as cur:
                cur.execute(
                    f"INSERT INTO {members_tbl.qualified_name} ({quoted_cols}) VALUES ({placeholders})",
                    tuple(values),
                )

            return {
                "ok": True,
                "teamId": team_id,
                "userId": user_id,
                "id": values[0] if id_col else None,
            }
    except HTTPException:
        raise
    except psycopg2.Error as exc:
        if "duplicate" in str(exc).lower() or "unique" in str(exc).lower():
            raise HTTPException(status_code=409, detail="Member already exists in this team")
        raise HTTPException(status_code=500, detail=f"Failed to add team member: {exc.pgerror or str(exc)}")
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")


@router.delete("/teams/{team_id}/members/{member_id}")
async def remove_team_member(
    team_id: str = Path(..., min_length=1),
    member_id: str = Path(..., min_length=1),
    _user: dict = Depends(require_admin),
):
    """Remove a member from a team."""
    try:
        with get_conn() as conn:
            members_tbl, cols = _resolve_team_members_table(conn)
            if not members_tbl:
                raise HTTPException(status_code=503, detail="Team members table not found")

            id_col = pick_column(cols, "id")
            team_col = pick_column(cols, "crm_team_id", "crmteamid", "team_id", "teamid")
            user_col = pick_column(cols, "user_id", "userid", "employee_id", "employeeid", "member_id", "memberid")

            if not team_col:
                raise HTTPException(status_code=503, detail="Team members table schema incomplete")

            with conn.cursor() as cur:
                # Try matching by id first, then by user_id
                if id_col:
                    sql = (
                        f"DELETE FROM {members_tbl.qualified_name} "
                        f"WHERE {quote_ident(id_col)}::text = %s "
                        f"AND {quote_ident(team_col)}::text = %s"
                    )
                    cur.execute(sql, (member_id, team_id))
                    if cur.rowcount == 0 and user_col:
                        # Fallback: try matching by user_id
                        sql = (
                            f"DELETE FROM {members_tbl.qualified_name} "
                            f"WHERE {quote_ident(user_col)}::text = %s "
                            f"AND {quote_ident(team_col)}::text = %s"
                        )
                        cur.execute(sql, (member_id, team_id))
                elif user_col:
                    sql = (
                        f"DELETE FROM {members_tbl.qualified_name} "
                        f"WHERE {quote_ident(user_col)}::text = %s "
                        f"AND {quote_ident(team_col)}::text = %s"
                    )
                    cur.execute(sql, (member_id, team_id))
                else:
                    raise HTTPException(status_code=503, detail="Team members table schema incomplete")

                if cur.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Team member not found")

            return {"teamId": team_id, "memberId": member_id, "deleted": True}
    except HTTPException:
        raise
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")


# ---------------------------------------------------------------------------
# Team update/delete
# ---------------------------------------------------------------------------


def _resolve_teams_table(conn):
    """Resolve teams table and return (table_ref, cols) or (None, None)."""
    tbl = resolve_table(
        conn,
        "crm_teams",
        "crmteams",
        "teams",
        "app_teams",
        "user_teams",
    )
    if not tbl:
        return None, None
    cols = table_columns(conn, tbl)
    id_col = pick_column(cols, "id")
    if not id_col:
        return None, None
    return tbl, cols


@router.put("/teams/{team_id}")
async def update_team(
    team_id: str = Path(..., min_length=1),
    body: dict = Body(...),
    _user: dict = Depends(require_admin),
):
    """Update a team."""
    try:
        with get_conn() as conn:
            tbl, cols = _resolve_teams_table(conn)
            if not tbl:
                raise HTTPException(status_code=503, detail="Team table not found")

            id_col = pick_column(cols, "id")
            name_col = pick_column(cols, "name", "team_name", "title")
            desc_col = pick_column(
                cols,
                "description",
                "note",
                "desc",
                "lead_properties_definition",
                "leadpropertiesdefinition",
            )
            active_col = pick_column(cols, "active", "is_active")
            updated_col = pick_column(cols, "lastupdated", "updated_at")

            updates: list[str] = []
            params: list = []

            if body.get("name") is not None and name_col:
                updates.append(f"{quote_ident(name_col)} = %s")
                params.append(str(body["name"]).strip())
            if body.get("description") is not None and desc_col:
                updates.append(f"{quote_ident(desc_col)} = %s")
                params.append(str(body["description"]).strip() or None)
            if body.get("active") is not None and active_col:
                updates.append(f"{quote_ident(active_col)} = %s")
                params.append(bool(body["active"]))
            if updated_col:
                updates.append(f"{quote_ident(updated_col)} = %s")
                params.append(datetime.utcnow())

            if not updates:
                raise HTTPException(status_code=422, detail="No fields to update")

            params.append(team_id)
            sql = (
                f"UPDATE {tbl.qualified_name} "
                f"SET {', '.join(updates)} "
                f"WHERE {quote_ident(id_col)}::text = %s"
            )

            with conn.cursor() as cur:
                cur.execute(sql, tuple(params))
                if cur.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Team not found")

            return {"id": team_id, "updated": True}
    except HTTPException:
        raise
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")


@router.delete("/teams/{team_id}")
async def delete_team(
    team_id: str = Path(..., min_length=1),
    _user: dict = Depends(require_admin),
):
    """Delete a team (soft-delete via active=false if possible, else hard delete)."""
    try:
        with get_conn() as conn:
            tbl, cols = _resolve_teams_table(conn)
            if not tbl:
                raise HTTPException(status_code=503, detail="Team table not found")

            id_col = pick_column(cols, "id")
            active_col = pick_column(cols, "active", "is_active")
            updated_col = pick_column(cols, "lastupdated", "updated_at")

            with conn.cursor() as cur:
                if active_col:
                    set_clauses = [f"{quote_ident(active_col)} = %s"]
                    params: list = [False]
                    if updated_col:
                        set_clauses.append(f"{quote_ident(updated_col)} = %s")
                        params.append(datetime.utcnow())
                    params.append(team_id)
                    sql = (
                        f"UPDATE {tbl.qualified_name} "
                        f"SET {', '.join(set_clauses)} "
                        f"WHERE {quote_ident(id_col)}::text = %s"
                    )
                    cur.execute(sql, tuple(params))
                else:
                    sql = (
                        f"DELETE FROM {tbl.qualified_name} "
                        f"WHERE {quote_ident(id_col)}::text = %s"
                    )
                    cur.execute(sql, (team_id,))

                if cur.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Team not found")

            return {"id": team_id, "deleted": True}
    except HTTPException:
        raise
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")


# ---------------------------------------------------------------------------
# Company/branch CRUD (settings context)
# ---------------------------------------------------------------------------


@router.post("/settings/companies", status_code=201)
async def create_company(
    body: CompanyCreatePayload = Body(...),
    _user: dict = Depends(require_admin),
):
    """Create a new company/branch."""
    try:
        with get_conn() as conn:
            companies_table = resolve_table(conn, "companies", "company")
            if not companies_table:
                raise HTTPException(status_code=503, detail="Companies table not found")

            cols = table_columns(conn, companies_table)
            id_col = pick_column(cols, "id")
            name_col = pick_column(cols, "name", "display_name", "company_name")
            if not id_col or not name_col:
                raise HTTPException(status_code=503, detail="Companies table schema incomplete")

            address_col = pick_column(cols, "address", "address_v2")
            phone_col = pick_column(cols, "phone", "hotline", "tax_phone", "mobile")
            active_col = pick_column(cols, "active", "is_active", "enabled")
            is_head_col = pick_column(cols, "is_head", "ishead", "is_head_office")
            created_col = pick_column(cols, "date_created", "datecreated", "created_at", "create_date")

            new_id = str(uuid4())
            insert_cols: list[str] = [id_col, name_col]
            values: list = [new_id, body.name.strip()]

            if address_col and body.address:
                insert_cols.append(address_col)
                values.append(body.address)
            if phone_col and body.phone:
                insert_cols.append(phone_col)
                values.append(body.phone)
            if active_col:
                insert_cols.append(active_col)
                values.append(body.active)
            if is_head_col:
                insert_cols.append(is_head_col)
                values.append(body.isHead)
            if created_col:
                insert_cols.append(created_col)
                values.append(datetime.utcnow())

            quoted_cols = ", ".join(quote_ident(c) for c in insert_cols)
            placeholders = ", ".join(["%s"] * len(values))
            with conn.cursor() as cur:
                cur.execute(
                    f"INSERT INTO {companies_table.qualified_name} ({quoted_cols}) VALUES ({placeholders})",
                    tuple(values),
                )

            return {"id": new_id, "name": body.name.strip(), "active": body.active}
    except HTTPException:
        raise
    except psycopg2.Error as exc:
        if "duplicate" in str(exc).lower() or "unique" in str(exc).lower():
            raise HTTPException(status_code=409, detail="Company name already exists")
        raise HTTPException(status_code=500, detail=f"Failed to create company: {exc.pgerror or str(exc)}")
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")


@router.put("/settings/companies/{company_id}")
async def update_company(
    company_id: str = Path(..., min_length=1),
    body: CompanyUpdatePayload = Body(...),
    _user: dict = Depends(require_admin),
):
    """Update a company/branch."""
    try:
        with get_conn() as conn:
            companies_table = resolve_table(conn, "companies", "company")
            if not companies_table:
                raise HTTPException(status_code=503, detail="Companies table not found")

            cols = table_columns(conn, companies_table)
            id_col = pick_column(cols, "id")
            name_col = pick_column(cols, "name", "display_name", "company_name")
            address_col = pick_column(cols, "address", "address_v2")
            phone_col = pick_column(cols, "phone", "hotline", "tax_phone", "mobile")
            active_col = pick_column(cols, "active", "is_active", "enabled")
            is_head_col = pick_column(cols, "is_head", "ishead", "is_head_office")
            updated_col = pick_column(cols, "write_date", "updated_at", "last_updated")

            if not id_col:
                raise HTTPException(status_code=503, detail="Companies table schema incomplete")

            updates: list[str] = []
            params: list = []

            if body.name is not None and name_col:
                updates.append(f"{quote_ident(name_col)} = %s")
                params.append(body.name.strip())
            if body.address is not None and address_col:
                updates.append(f"{quote_ident(address_col)} = %s")
                params.append(body.address)
            if body.phone is not None and phone_col:
                updates.append(f"{quote_ident(phone_col)} = %s")
                params.append(body.phone)
            if body.active is not None and active_col:
                updates.append(f"{quote_ident(active_col)} = %s")
                params.append(body.active)
            if body.isHead is not None and is_head_col:
                updates.append(f"{quote_ident(is_head_col)} = %s")
                params.append(body.isHead)
            if updated_col:
                updates.append(f"{quote_ident(updated_col)} = NOW()")

            if not updates:
                raise HTTPException(status_code=422, detail="No fields to update")

            params.append(company_id)
            sql = (
                f"UPDATE {companies_table.qualified_name} "
                f"SET {', '.join(updates)} "
                f"WHERE {quote_ident(id_col)}::text = %s"
            )

            with conn.cursor() as cur:
                cur.execute(sql, tuple(params))
                if cur.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Company not found")

            return {"id": company_id, "updated": True}
    except HTTPException:
        raise
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")


@router.delete("/settings/companies/{company_id}")
async def delete_company(
    company_id: str = Path(..., min_length=1),
    _user: dict = Depends(require_admin),
):
    """Soft-delete a company by setting active=false, or hard-delete if no active column."""
    try:
        with get_conn() as conn:
            companies_table = resolve_table(conn, "companies", "company")
            if not companies_table:
                raise HTTPException(status_code=503, detail="Companies table not found")

            cols = table_columns(conn, companies_table)
            id_col = pick_column(cols, "id")
            active_col = pick_column(cols, "active", "is_active", "enabled")
            updated_col = pick_column(cols, "write_date", "updated_at", "last_updated")

            if not id_col:
                raise HTTPException(status_code=503, detail="Companies table schema incomplete")

            with conn.cursor() as cur:
                if active_col:
                    set_clauses = [f"{quote_ident(active_col)} = %s"]
                    params: list = [False]
                    if updated_col:
                        set_clauses.append(f"{quote_ident(updated_col)} = NOW()")
                    params.append(company_id)
                    sql = (
                        f"UPDATE {companies_table.qualified_name} "
                        f"SET {', '.join(set_clauses)} "
                        f"WHERE {quote_ident(id_col)}::text = %s"
                    )
                    cur.execute(sql, tuple(params))
                else:
                    sql = (
                        f"DELETE FROM {companies_table.qualified_name} "
                        f"WHERE {quote_ident(id_col)}::text = %s"
                    )
                    cur.execute(sql, (company_id,))

                if cur.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Company not found")

            return {"id": company_id, "deleted": True}
    except HTTPException:
        raise
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")
