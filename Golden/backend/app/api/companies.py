"""Companies lookup endpoint."""

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

            partner_rel_col = pick_column(columns, "partner_id", "partnerid")
            address_col = pick_column(columns, "address", "address_v2")
            street_col = pick_column(
                columns,
                "street",
                "street2",
                "street_2",
                "address_line1",
                "address1",
            )
            ward_col = pick_column(columns, "ward_name", "wardname", "ward")
            district_col = pick_column(columns, "district_name", "districtname", "district")
            city_col = pick_column(
                columns,
                "city_name",
                "cityname",
                "city",
                "province_name",
                "provincename",
                "state_name",
                "statename",
            )
            phone_col = pick_column(columns, "phone", "hotline", "tax_phone", "mobile", "mobile_phone")
            active_col = pick_column(columns, "active", "is_active", "enabled")
            is_head_col = pick_column(columns, "is_head", "ishead", "is_head_office")

            joins = ""
            partner_address_candidates: list[str] = []
            partner_phone_expr: str | None = None
            if partner_rel_col:
                partners_table = resolve_table(conn, "partners", "res_partners", "respartners")
                if partners_table:
                    partner_cols = table_columns(conn, partners_table)
                    p_id_col = pick_column(partner_cols, "id")
                    if p_id_col:
                        joins = (
                            f" LEFT JOIN {partners_table.qualified_name} p"
                            f" ON t.{quote_ident(partner_rel_col)} = p.{quote_ident(p_id_col)}"
                        )
                        p_address_col = pick_column(partner_cols, "address", "address_v2")
                        p_street_col = pick_column(
                            partner_cols,
                            "street",
                            "street2",
                            "street_2",
                            "address_line1",
                            "address1",
                        )
                        p_ward_col = pick_column(partner_cols, "ward_name", "wardname", "ward")
                        p_district_col = pick_column(
                            partner_cols,
                            "district_name",
                            "districtname",
                            "district",
                        )
                        p_city_col = pick_column(
                            partner_cols,
                            "city_name",
                            "cityname",
                            "city",
                            "province_name",
                            "provincename",
                            "state_name",
                            "statename",
                        )
                        if p_address_col:
                            partner_address_candidates.append(
                                f"NULLIF(p.{quote_ident(p_address_col)}::text, '')"
                            )
                        partner_structured_parts: list[str] = []
                        for candidate in (p_street_col, p_ward_col, p_district_col, p_city_col):
                            if candidate:
                                partner_structured_parts.append(
                                    f"NULLIF(p.{quote_ident(candidate)}::text, '')"
                                )
                        if partner_structured_parts:
                            partner_address_candidates.append(
                                "NULLIF(CONCAT_WS(', ', "
                                + ", ".join(partner_structured_parts)
                                + "), '')"
                            )
                        p_phone_col = pick_column(
                            partner_cols,
                            "phone",
                            "mobile",
                            "mobile_phone",
                            "hotline",
                        )
                        if p_phone_col:
                            partner_phone_expr = f"NULLIF(p.{quote_ident(p_phone_col)}::text, '')"

            address_candidates: list[str] = []
            if address_col:
                address_candidates.append(f"NULLIF(t.{quote_ident(address_col)}::text, '')")

            structured_parts: list[str] = []
            for candidate in (street_col, ward_col, district_col, city_col):
                if candidate:
                    structured_parts.append(f"NULLIF(t.{quote_ident(candidate)}::text, '')")
            if structured_parts:
                address_candidates.append(
                    "NULLIF(CONCAT_WS(', ', " + ", ".join(structured_parts) + "), '')"
                )
            address_candidates.extend(partner_address_candidates)

            address_expr = (
                "COALESCE(" + ", ".join(address_candidates + ["NULL::text"]) + ") AS address"
                if address_candidates
                else "NULL::text AS address"
            )
            phone_candidates: list[str] = []
            if phone_col:
                phone_candidates.append(f"NULLIF(t.{quote_ident(phone_col)}::text, '')")
            if partner_phone_expr:
                phone_candidates.append(partner_phone_expr)
            phone_expr = (
                "COALESCE(" + ", ".join(phone_candidates + ["NULL::text"]) + ") AS phone"
                if phone_candidates
                else "NULL::text AS phone"
            )

            select_fields = [
                f't.{quote_ident(id_col)}::text AS id',
                f't.{quote_ident(name_col)} AS name',
                address_expr,
                phone_expr,
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
                f"{joins}"
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
