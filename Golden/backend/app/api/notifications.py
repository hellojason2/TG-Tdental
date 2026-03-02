"""Notification bell and inbox endpoints."""

from __future__ import annotations

import psycopg2
from fastapi import APIRouter, Depends, HTTPException, Query
from psycopg2.extras import RealDictCursor

from app.core.database import get_conn
from app.core.lookup_sql import pick_column, quote_ident, resolve_table, table_columns
from app.core.middleware import require_auth

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


def _resolve_notification_context(conn) -> dict | None:
    table = resolve_table(
        conn,
        "mail_messages",
        "mailmessages",
        "messages",
        "notification_messages",
        "notifications",
        "inbox_messages",
    )
    if not table:
        return None

    cols = table_columns(conn, table)
    id_col = pick_column(cols, "id")
    if not id_col:
        return None

    return {
        "table": table,
        "id_col": id_col,
        "subject_col": pick_column(cols, "subject", "title", "name"),
        "body_col": pick_column(cols, "body", "preview", "content", "message"),
        "date_col": pick_column(
            cols,
            "date",
            "created_at",
            "created_date",
            "create_date",
            "sent_at",
        ),
        "sender_col": pick_column(cols, "sender_name", "sender", "from_name", "author"),
        "type_col": pick_column(cols, "type", "level", "category"),
        "read_col": pick_column(cols, "is_read", "isread", "read", "seen"),
        "state_col": pick_column(cols, "state", "status"),
    }


def _unread_predicate(ctx: dict, alias: str = "m") -> str:
    if ctx.get("read_col"):
        return f"COALESCE({alias}.{quote_ident(ctx['read_col'])}, FALSE) = FALSE"
    if ctx.get("state_col"):
        return (
            f"LOWER(COALESCE({alias}.{quote_ident(ctx['state_col'])}::text, '')) "
            "NOT IN ('read', 'done', 'processed')"
        )
    return "FALSE"


@router.get("/init")
async def notifications_init(_user: dict = Depends(require_auth)):
    try:
        with get_conn() as conn:
            ctx = _resolve_notification_context(conn)
            if not ctx:
                return {"count": 0}

            unread_sql = (
                "SELECT "
                f"COALESCE(COUNT(*), 0)::bigint AS count "
                f"FROM {ctx['table'].qualified_name} m "
                f"WHERE {_unread_predicate(ctx, 'm')}"
            )
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(unread_sql)
                row = dict(cur.fetchone() or {})
            return {"count": int(row.get("count") or 0)}
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")


@router.get("/inbox")
async def notifications_inbox(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=0, le=200),
    _user: dict = Depends(require_auth),
):
    try:
        with get_conn() as conn:
            ctx = _resolve_notification_context(conn)
            if not ctx:
                return {"offset": offset, "limit": limit, "totalItems": 0, "items": []}

            subject_expr = (
                f"COALESCE(NULLIF(m.{quote_ident(ctx['subject_col'])}::text, ''), 'Thông báo')"
                if ctx.get("subject_col")
                else "'Thông báo'::text"
            )
            body_expr = (
                f"COALESCE(m.{quote_ident(ctx['body_col'])}::text, '')"
                if ctx.get("body_col")
                else "''::text"
            )
            date_expr = (
                f"m.{quote_ident(ctx['date_col'])}"
                if ctx.get("date_col")
                else "NULL::timestamp"
            )
            sender_expr = (
                f"m.{quote_ident(ctx['sender_col'])}"
                if ctx.get("sender_col")
                else "NULL::text"
            )
            type_expr = (
                f"m.{quote_ident(ctx['type_col'])}"
                if ctx.get("type_col")
                else "NULL::text"
            )
            is_read_expr = (
                f"COALESCE(m.{quote_ident(ctx['read_col'])}, FALSE)"
                if ctx.get("read_col")
                else f"NOT ({_unread_predicate(ctx, 'm')})"
            )

            count_sql = f"SELECT COUNT(*)::bigint AS total FROM {ctx['table'].qualified_name} m"
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(count_sql)
                total = int((cur.fetchone() or {}).get("total") or 0)

                if total == 0:
                    return {"offset": offset, "limit": limit, "totalItems": 0, "items": []}

                query = (
                    "SELECT "
                    f"m.{quote_ident(ctx['id_col'])}::text AS id, "
                    f"{subject_expr} AS title, "
                    f"{body_expr} AS content, "
                    f"LEFT({body_expr}, 160) AS preview, "
                    f"{date_expr} AS \"createdAt\", "
                    f"{sender_expr} AS sender, "
                    f"{type_expr} AS type, "
                    f"{is_read_expr} AS \"isRead\" "
                    f"FROM {ctx['table'].qualified_name} m "
                    + (
                        f"ORDER BY m.{quote_ident(ctx['date_col'])} DESC NULLS LAST, "
                        f"m.{quote_ident(ctx['id_col'])} DESC "
                        if ctx.get("date_col")
                        else f"ORDER BY m.{quote_ident(ctx['id_col'])} DESC "
                    )
                )

                if limit == 0:
                    if offset > 0:
                        query += "OFFSET %s"
                        cur.execute(query, (offset,))
                    else:
                        cur.execute(query)
                else:
                    query += "LIMIT %s OFFSET %s"
                    cur.execute(query, (limit, offset))

                rows = [dict(row) for row in cur.fetchall()]

            return {
                "offset": offset,
                "limit": limit,
                "totalItems": total,
                "items": rows,
            }
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")


@router.post("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    _user: dict = Depends(require_auth),
):
    """Mark a notification as read."""
    try:
        with get_conn() as conn:
            ctx = _resolve_notification_context(conn)
            if not ctx:
                return {"success": False, "message": "No notification table found"}

            # Try to update is_read column
            if ctx.get("read_col"):
                update_sql = f"UPDATE {ctx['table'].qualified_name} SET {quote_ident(ctx['read_col'])} = TRUE WHERE {quote_ident(ctx['id_col'])} = %s"
            elif ctx.get("state_col"):
                update_sql = f"UPDATE {ctx['table'].qualified_name} SET {quote_ident(ctx['state_col'])} = 'read' WHERE {quote_ident(ctx['id_col'])} = %s"
            else:
                return {"success": False, "message": "No way to mark as read"}

            with conn.cursor() as cur:
                try:
                    cur.execute(update_sql, (notification_id,))
                except psycopg2.Error:
                    raise HTTPException(
                        status_code=400,
                        detail="Invalid notification ID",
                    )
                if cur.rowcount == 0:
                    raise HTTPException(
                        status_code=404,
                        detail="Notification not found",
                    )

            return {"success": True, "message": "Notification marked as read"}
    except HTTPException:
        raise
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")
