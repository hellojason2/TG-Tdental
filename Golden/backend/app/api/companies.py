"""Companies lookup endpoint."""

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

router = APIRouter(prefix="/api", tags=["companies"])


@router.get("/companies")
async def list_companies(
    active: bool | None = Query(default=None),
    page: int | None = Query(default=None, ge=1),
    per_page: int | None = Query(default=None, ge=0, le=500),
    offset: int | None = Query(default=None, ge=0),
    limit: int | None = Query(default=None, ge=0, le=5000),
    _user: dict = Depends(require_auth),
):
    """Return companies with optional active filter and paged response shape."""
    effective_offset, effective_limit = page_window(
        page=page,
        per_page=per_page,
        offset=offset,
        limit=limit,
        default_limit=0,
    )

    try:
        with get_conn() as conn:
            companies_table = resolve_table(conn, "companies", "company")
            if not companies_table:
                return empty_page(effective_offset, effective_limit)

            columns = table_columns(conn, companies_table)
            id_col = pick_column(columns, "id")
            name_col = pick_column(columns, "name", "display_name", "company_name")
            if not id_col or not name_col:
                return empty_page(effective_offset, effective_limit)

            address_col = pick_column(columns, "address", "address_v2", "street")
            phone_col = pick_column(columns, "phone", "hotline", "tax_phone")
            active_col = pick_column(columns, "active", "is_active", "enabled")
            is_head_col = pick_column(columns, "is_head", "ishead", "is_head_office")

            select_fields = [
                f't.{quote_ident(id_col)}::text AS id',
                f't.{quote_ident(name_col)} AS name',
                (
                    f't.{quote_ident(address_col)} AS address'
                    if address_col
                    else "NULL::text AS address"
                ),
                (
                    f't.{quote_ident(phone_col)} AS phone'
                    if phone_col
                    else "NULL::text AS phone"
                ),
                (
                    f"COALESCE(t.{quote_ident(active_col)}, TRUE) AS active"
                    if active_col
                    else "TRUE AS active"
                ),
                (
                    f'COALESCE(t.{quote_ident(is_head_col)}, FALSE) AS "isHead"'
                    if is_head_col
                    else 'FALSE AS "isHead"'
                ),
            ]

            where_clauses: list[str] = []
            params: list = []

            if active is not None:
                if active_col:
                    where_clauses.append(f"COALESCE(t.{quote_ident(active_col)}, FALSE) = %s")
                    params.append(active)
                elif not active:
                    return empty_page(effective_offset, effective_limit)

            order_col = quote_ident(name_col)
            base_query = (
                f"SELECT {', '.join(select_fields)} "
                f"FROM {companies_table.qualified_name} t"
            )
            if where_clauses:
                base_query += " WHERE " + " AND ".join(where_clauses)
            base_query += f" ORDER BY t.{order_col} ASC NULLS LAST"

            return paginate(
                query=base_query,
                params=tuple(params),
                conn=conn,
                offset=effective_offset,
                limit=effective_limit,
            )
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Database is unavailable")
