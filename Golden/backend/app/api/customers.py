"""Customer APIs (list/detail/history + CRUD) for MVP."""

from __future__ import annotations

import re
import time
import unicodedata
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

import psycopg2
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from psycopg2.extras import Json, RealDictCursor

from app.core.database import get_conn
from app.core.middleware import require_auth

router = APIRouter(
    prefix="/api/customers",
    tags=["customers"],
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CUSTOMER_TABLE_CANDIDATES = (
    "partners",
    "res_partners",
    "respartners",
    "getpagedpartnerscustomer",
)
COMPANY_TABLE_CANDIDATES = ("companies", "company")
APPOINTMENT_TABLE_CANDIDATES = ("appointments", "customer_appointments", "appointment")
TREATMENT_TABLE_CANDIDATES = ("sale_orders", "saleorder", "saleorders", "sale_order")
TREATMENT_LINE_TABLE_CANDIDATES = (
    "sale_order_lines",
    "saleorderlines",
    "sale_order_line",
    "saleorderline",
)

TEXT_DATA_TYPES = {"text", "character varying", "varchar", "char", "bpchar"}
BOOLEAN_DATA_TYPES = {"boolean", "bool"}
UUID_DATA_TYPES = {"uuid"}
JSON_DATA_TYPES = {"json", "jsonb"}

PHONE_ALLOWED_RE = re.compile(r"^\+?[0-9][0-9 .-]{6,18}$")

VIET_LOWER_SOURCE = "àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ"
VIET_LOWER_TARGET = "aaaaaaaaaaaaaaaaaeeeeeeeeeeeiiiiiooooooooooooooooouuuuuuuuuuuyyyyyd"


# ---------------------------------------------------------------------------
# Lightweight schema cache
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class TableMeta:
    schema: str
    table: str
    columns: list[str] = field(default_factory=list)
    data_types: dict[str, str] = field(default_factory=dict)
    nullable: dict[str, bool] = field(default_factory=dict)
    defaults: dict[str, str | None] = field(default_factory=dict)


_SCHEMA_CACHE_TTL_SECONDS = 30.0
_schema_cache_snapshot: dict[str, TableMeta] | None = None
_schema_cache_at: float = 0.0


def _q(identifier: str) -> str:
    """Quote SQL identifier safely."""
    return '"' + identifier.replace('"', '""') + '"'


def _qt(meta: TableMeta) -> str:
    return f"{_q(meta.schema)}.{_q(meta.table)}"


def _schema_priority(schema_name: str) -> int:
    lowered = schema_name.lower()
    if lowered == "public":
        return 0
    if lowered == "dbo":
        return 1
    return 2


def _load_schema_snapshot(conn, force_refresh: bool = False) -> dict[str, TableMeta]:
    """Load table/column metadata from information_schema (cached for 30s)."""
    global _schema_cache_snapshot, _schema_cache_at

    now = time.monotonic()
    if (
        not force_refresh
        and _schema_cache_snapshot is not None
        and (now - _schema_cache_at) < _SCHEMA_CACHE_TTL_SECONDS
    ):
        return _schema_cache_snapshot

    sql = """
        SELECT
            c.table_schema,
            c.table_name,
            c.column_name,
            c.data_type,
            c.is_nullable,
            c.column_default
        FROM information_schema.columns c
        JOIN information_schema.tables t
          ON t.table_schema = c.table_schema
         AND t.table_name = c.table_name
        WHERE t.table_type = 'BASE TABLE'
          AND c.table_schema NOT IN ('pg_catalog', 'information_schema')
        ORDER BY c.table_schema, c.table_name, c.ordinal_position
    """

    by_schema_table: dict[tuple[str, str], TableMeta] = {}
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql)
        rows = cur.fetchall()

    for row in rows:
        schema_name = str(row["table_schema"]).lower()
        table_name = str(row["table_name"]).lower()
        column_name = str(row["column_name"]).lower()
        meta = by_schema_table.setdefault(
            (schema_name, table_name),
            TableMeta(schema=schema_name, table=table_name),
        )
        meta.columns.append(column_name)
        meta.data_types[column_name] = str(row["data_type"]).lower()
        meta.nullable[column_name] = str(row["is_nullable"]).upper() == "YES"
        meta.defaults[column_name] = row["column_default"]

    # Collapse to table-name map using schema priority (public > dbo > others)
    by_table_name: dict[str, TableMeta] = {}
    for meta in by_schema_table.values():
        existing = by_table_name.get(meta.table)
        if existing is None:
            by_table_name[meta.table] = meta
            continue
        if _schema_priority(meta.schema) < _schema_priority(existing.schema):
            by_table_name[meta.table] = meta

    _schema_cache_snapshot = by_table_name
    _schema_cache_at = now
    return by_table_name


def _resolve_table(snapshot: dict[str, TableMeta], candidates: tuple[str, ...]) -> TableMeta | None:
    for candidate in candidates:
        meta = snapshot.get(candidate.lower())
        if meta:
            return meta
    return None


def _normalize_key(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.strip().lower())


def _find_column(meta: TableMeta, *candidates: str) -> str | None:
    available = set(meta.columns)
    for candidate in candidates:
        lowered = candidate.lower()
        if lowered in available:
            return lowered
    normalized_map = {_normalize_key(col): col for col in meta.columns}
    for candidate in candidates:
        found = normalized_map.get(_normalize_key(candidate))
        if found:
            return found
    return None


def _resolve_column_by_input_name(meta: TableMeta, input_name: str) -> str | None:
    normalized = _normalize_key(input_name)
    for col in meta.columns:
        if _normalize_key(col) == normalized:
            return col
    return None


def _is_text_column(meta: TableMeta, column_name: str) -> bool:
    return meta.data_types.get(column_name, "") in TEXT_DATA_TYPES


def _sql_fold_expr(expr: str) -> str:
    """Vietnamese-ish accent-insensitive SQL expression."""
    return (
        f"TRANSLATE(LOWER(COALESCE({expr}::text, '')), "
        f"'{VIET_LOWER_SOURCE}', '{VIET_LOWER_TARGET}')"
    )


def _fold_vietnamese(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    stripped = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    stripped = stripped.replace("đ", "d").replace("Đ", "D")
    return stripped.lower().strip()


def _parse_uuid(value: Any) -> UUID | None:
    try:
        return UUID(str(value))
    except (TypeError, ValueError):
        return None


def _first_non_empty(row: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = row.get(key)
        if value not in (None, ""):
            return value
    return None


def _error(
    status_code: int,
    code: str,
    detail: str,
    errors: list[dict[str, str]] | None = None,
) -> JSONResponse:
    payload: dict[str, Any] = {"detail": detail, "error": code}
    if errors:
        payload["errors"] = errors
    return JSONResponse(status_code=status_code, content=payload)


def _validation_error(errors: list[dict[str, str]]) -> JSONResponse:
    return _error(
        status_code=422,
        code="VALIDATION_ERROR",
        detail="Validation failed",
        errors=errors,
    )


def _coerce_db_value(meta: TableMeta, column_name: str, value: Any) -> Any:
    if value is None:
        return None

    data_type = meta.data_types.get(column_name, "")

    if data_type in JSON_DATA_TYPES and isinstance(value, (dict, list)):
        return Json(value)

    if data_type in BOOLEAN_DATA_TYPES and isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"1", "true", "yes", "y"}:
            return True
        if lowered in {"0", "false", "no", "n"}:
            return False

    if data_type in UUID_DATA_TYPES:
        parsed = _parse_uuid(value)
        return str(parsed) if parsed else value

    return value


def _resolve_sort_column(meta: TableMeta, sort: str | None) -> str | None:
    alias_candidates: dict[str, tuple[str, ...]] = {
        "displayname": ("displayname", "display_name"),
        "dateofbirth": ("dateofbirth", "date_of_birth", "birthday"),
        "companyname": ("companyname", "company_name"),
        "totaldebit": ("totaldebit", "total_debit"),
        "amounttreatmenttotal": ("amounttreatmenttotal", "amount_treatment_total"),
        "amountrevenuetotal": ("amountrevenuetotal", "amount_revenue_total"),
        "orderstate": ("orderstate", "order_state"),
    }

    if not sort:
        return (
            _find_column(meta, "name")
            or _find_column(meta, "displayname")
            or _find_column(meta, "date", "updated_at", "created_at")
            or _find_column(meta, "id")
        )

    exact = _resolve_column_by_input_name(meta, sort)
    if exact:
        return exact

    normalized = _normalize_key(sort)
    aliases = alias_candidates.get(normalized)
    if aliases:
        return _find_column(meta, *aliases)

    return None


def _resolve_paging(
    page: int,
    per_page: int,
    offset: int | None,
    limit: int | None,
) -> tuple[int, int]:
    if offset is not None or limit is not None:
        resolved_offset = 0 if offset is None else offset
        resolved_limit = per_page if limit is None else limit
        return resolved_offset, resolved_limit
    return (page - 1) * per_page, per_page


def _get_vi_collation(conn) -> str | None:
    candidates = ("vi-x-icu", "vi_VN", "vi-vn-x-icu")
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT collname
            FROM pg_collation
            WHERE collname = ANY(%s)
            ORDER BY CASE collname
                WHEN 'vi-x-icu' THEN 0
                WHEN 'vi_VN' THEN 1
                WHEN 'vi-vn-x-icu' THEN 2
                ELSE 9
            END
            LIMIT 1
            """,
            (list(candidates),),
        )
        row = cur.fetchone()
        if not row:
            return None
        return row[0]


def _customer_error_invalid_uuid() -> JSONResponse:
    return _error(
        status_code=404,
        code="CUSTOMER_NOT_FOUND",
        detail="Invalid customer id format. Expected UUID.",
    )


def _build_customer_aliases(item: dict[str, Any]) -> dict[str, Any]:
    row = dict(item)
    company_name = _first_non_empty(row, "__company_name", "companyname", "company_name")
    row.pop("__company_name", None)

    row["displayName"] = _first_non_empty(row, "displayname", "display_name", "name")
    row["dateOfBirth"] = _first_non_empty(row, "dateofbirth", "date_of_birth", "birthday")
    row["companyName"] = company_name
    row["orderState"] = _first_non_empty(row, "orderstate", "order_state")
    row["totalDebit"] = _first_non_empty(row, "totaldebit", "total_debit", "orderresidual")
    row["amountTreatmentTotal"] = _first_non_empty(
        row, "amounttreatmenttotal", "amount_treatment_total"
    )
    row["amountRevenueTotal"] = _first_non_empty(row, "amountrevenuetotal", "amount_revenue_total")
    row["companyId"] = _first_non_empty(row, "companyid", "company_id")
    return row


def _fetch_customer_by_id(
    conn,
    customer_meta: TableMeta,
    company_meta: TableMeta | None,
    customer_uuid: UUID,
    include_inactive: bool = False,
) -> dict[str, Any] | None:
    id_col = _find_column(customer_meta, "id")
    if not id_col:
        return None

    active_col = _find_column(customer_meta, "active", "isactive")
    company_col = _find_column(customer_meta, "companyid", "company_id")
    select_company = ""
    join_company = ""
    company_name_col = None
    company_id_col = None

    if company_meta and company_col:
        company_id_col = _find_column(company_meta, "id", "companyid", "company_id")
        company_name_col = _find_column(company_meta, "name", "companyname", "displayname")
        if company_id_col and company_name_col:
            join_company = (
                f" LEFT JOIN {_qt(company_meta)} c"
                f" ON p.{_q(company_col)} = c.{_q(company_id_col)}"
            )
            select_company = f", c.{_q(company_name_col)} AS __company_name"

    where = [f"p.{_q(id_col)} = %s"]
    params: list[Any] = [str(customer_uuid)]
    if active_col and not include_inactive:
        where.append(f"COALESCE(p.{_q(active_col)}, TRUE) = TRUE")

    sql = (
        f"SELECT p.*{select_company} "
        f"FROM {_qt(customer_meta)} p"
        f"{join_company} "
        f"WHERE {' AND '.join(where)} "
        f"LIMIT 1"
    )
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql, tuple(params))
        row = cur.fetchone()
    return dict(row) if row else None


def _parse_create_or_update_payload(
    payload: dict[str, Any],
    require_name_and_company: bool,
) -> tuple[dict[str, Any], list[dict[str, str]]]:
    errors: list[dict[str, str]] = []
    normalized: dict[str, Any] = {}

    name = _first_non_empty(payload, "name", "displayName", "display_name")
    company_raw = _first_non_empty(payload, "companyId", "company", "company_id", "companyid")
    phone = _first_non_empty(payload, "phone", "phoneNumber", "phonenumber")

    if require_name_and_company:
        if not name or not str(name).strip():
            errors.append({"field": "name", "message": "Name is required"})
        if not company_raw:
            errors.append({"field": "companyId", "message": "Company is required"})

    if name is not None:
        if not str(name).strip():
            errors.append({"field": "name", "message": "Name must not be empty"})
        else:
            normalized["name"] = str(name).strip()

    if company_raw is not None:
        company_uuid = _parse_uuid(company_raw)
        if company_uuid is None:
            errors.append({"field": "companyId", "message": "Company must be a valid UUID"})
        else:
            normalized["company_id"] = str(company_uuid)

    if phone is not None and str(phone).strip() != "":
        phone_str = str(phone).strip()
        only_digits = re.sub(r"\D+", "", phone_str)
        if not PHONE_ALLOWED_RE.match(phone_str) or not (8 <= len(only_digits) <= 15):
            errors.append({"field": "phone", "message": "Phone format is invalid"})
        else:
            normalized["phone"] = phone_str

    # Optional common fields
    optional_map = {
        "ref": ("ref",),
        "email": ("email",),
        "display_name": ("displayName", "display_name", "displayname"),
        "gender": ("gender", "genderDisplay", "gender_display"),
        "date_of_birth": ("dateOfBirth", "date_of_birth", "dateofbirth", "birthday"),
        "address": ("address", "street"),
        "address2": ("address2", "address_2", "addressv2", "street2"),
        "company_name": ("companyName", "company_name", "companyname"),
        "notes": ("notes", "note", "comment"),
        "active": ("active", "isActive", "is_active", "isactive"),
    }
    for canonical, keys in optional_map.items():
        for key in keys:
            if key in payload:
                normalized[canonical] = payload[key]
                break

    return normalized, errors


def _build_customer_column_values(
    customer_meta: TableMeta,
    normalized_payload: dict[str, Any],
    raw_payload: dict[str, Any],
    include_defaults: bool,
) -> dict[str, Any]:
    values: dict[str, Any] = {}

    # Canonical mapping first.
    canonical_to_columns: dict[str, tuple[str, ...]] = {
        "name": ("name",),
        "company_id": ("companyid", "company_id"),
        "phone": ("phone", "phonenumber"),
        "ref": ("ref",),
        "email": ("email",),
        "display_name": ("displayname", "display_name"),
        "gender": ("gender", "genderdisplay", "gender_display"),
        "date_of_birth": ("dateofbirth", "date_of_birth", "birthday"),
        "address": ("address", "street"),
        "address2": ("addressv2", "address_2", "street2"),
        "company_name": ("companyname", "company_name"),
        "notes": ("comment", "notes", "note"),
        "active": ("active", "isactive"),
    }
    for canonical, candidate_cols in canonical_to_columns.items():
        if canonical not in normalized_payload:
            continue
        db_col = _find_column(customer_meta, *candidate_cols)
        if not db_col:
            continue
        values[db_col] = normalized_payload[canonical]

    # Pass-through for fields that already map 1:1 to table columns.
    for key, value in raw_payload.items():
        db_col = _resolve_column_by_input_name(customer_meta, key)
        if not db_col:
            continue
        if db_col in values:
            continue
        if db_col in {"id"}:
            continue
        values[db_col] = value

    if include_defaults:
        id_col = _find_column(customer_meta, "id")
        if id_col and id_col not in values:
            if customer_meta.data_types.get(id_col) in UUID_DATA_TYPES:
                values[id_col] = str(uuid4())

        active_col = _find_column(customer_meta, "active", "isactive")
        if active_col and active_col not in values:
            values[active_col] = True

        display_col = _find_column(customer_meta, "displayname", "display_name")
        name_col = _find_column(customer_meta, "name")
        if display_col and display_col not in values and name_col and name_col in values:
            values[display_col] = values[name_col]

        ref_col = _find_column(customer_meta, "ref")
        if ref_col and ref_col not in values:
            values[ref_col] = f"KH-{uuid4().hex[:8].upper()}"

    # Coerce values according to data type.
    coerced: dict[str, Any] = {}
    for col, value in values.items():
        coerced[col] = _coerce_db_value(customer_meta, col, value)
    return coerced


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.get("")
def list_customers(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=200),
    offset: int | None = Query(default=None, ge=0),
    limit: int | None = Query(default=None, ge=1, le=200),
    search: str | None = Query(default=None),
    sort: str | None = Query(default=None),
    order: str = Query(default="desc"),
    company: str | None = Query(default=None),
    company_id: str | None = Query(default=None, alias="companyId"),
    _user: dict = Depends(require_auth),
):
    resolved_offset, resolved_limit = _resolve_paging(page, per_page, offset, limit)
    normalized_order = order.lower().strip()
    if normalized_order not in {"asc", "desc"}:
        return _validation_error([{"field": "order", "message": "Order must be asc or desc"}])

    company_filter_raw = company_id or company
    company_filter_uuid: UUID | None = None
    if company_filter_raw:
        company_filter_uuid = _parse_uuid(company_filter_raw)
        if company_filter_uuid is None:
            return _validation_error([{"field": "company", "message": "Company must be a UUID"}])

    try:
        with get_conn() as conn:
            snapshot = _load_schema_snapshot(conn)
            customer_meta = _resolve_table(snapshot, CUSTOMER_TABLE_CANDIDATES)
            company_meta = _resolve_table(snapshot, COMPANY_TABLE_CANDIDATES)

            if customer_meta is None:
                return _error(
                    status_code=503,
                    code="CUSTOMER_TABLE_NOT_FOUND",
                    detail="Customer table is not available in the current database.",
                )

            customer_id_col = _find_column(customer_meta, "id")
            if not customer_id_col:
                return _error(
                    status_code=503,
                    code="CUSTOMER_SCHEMA_INVALID",
                    detail="Customer table is missing id column.",
                )

            company_col = _find_column(customer_meta, "companyid", "company_id")
            active_col = _find_column(customer_meta, "active", "isactive")

            # Build optional join to companies.
            company_join_sql = ""
            company_select_sql = ""
            if company_meta and company_col:
                company_meta_id_col = _find_column(company_meta, "id", "companyid", "company_id")
                company_meta_name_col = _find_column(company_meta, "name", "companyname", "displayname")
                if company_meta_id_col and company_meta_name_col:
                    company_join_sql = (
                        f" LEFT JOIN {_qt(company_meta)} c"
                        f" ON p.{_q(company_col)} = c.{_q(company_meta_id_col)}"
                    )
                    company_select_sql = f", c.{_q(company_meta_name_col)} AS __company_name"

            where_clauses: list[str] = []
            params: list[Any] = []

            if active_col:
                where_clauses.append(f"COALESCE(p.{_q(active_col)}, TRUE) = TRUE")

            if company_filter_uuid and company_col:
                where_clauses.append(f"p.{_q(company_col)} = %s")
                params.append(str(company_filter_uuid))

            if search:
                cleaned = search.strip()
                folded = _fold_vietnamese(cleaned)
                search_columns = [
                    col
                    for col in (
                        _find_column(customer_meta, "name"),
                        _find_column(customer_meta, "displayname", "display_name"),
                        _find_column(customer_meta, "phone", "phonenumber"),
                        _find_column(customer_meta, "ref"),
                    )
                    if col is not None
                ]
                # Remove duplicates while preserving order.
                unique_search_columns: list[str] = []
                for col in search_columns:
                    if col not in unique_search_columns:
                        unique_search_columns.append(col)

                if unique_search_columns:
                    search_parts: list[str] = []
                    for col in unique_search_columns:
                        col_expr = f"p.{_q(col)}"
                        search_parts.append(f"{col_expr}::text ILIKE %s")
                        params.append(f"%{cleaned}%")
                        search_parts.append(f"{_sql_fold_expr(col_expr)} LIKE %s")
                        params.append(f"%{folded}%")
                    where_clauses.append("(" + " OR ".join(search_parts) + ")")

            where_sql = ""
            if where_clauses:
                where_sql = " WHERE " + " AND ".join(where_clauses)

            sort_col = _resolve_sort_column(customer_meta, sort)
            if sort and sort_col is None:
                return _validation_error(
                    [{"field": "sort", "message": "Sort column is not valid for customer table"}]
                )
            if sort_col is None:
                sort_col = customer_id_col

            sort_expr = f"p.{_q(sort_col)}"
            if _is_text_column(customer_meta, sort_col):
                vi_collation = _get_vi_collation(conn)
                if vi_collation:
                    sort_expr = f'{sort_expr} COLLATE "{vi_collation}"'
                else:
                    # Fallback when Vietnamese ICU collation is unavailable.
                    sort_expr = _sql_fold_expr(sort_expr)

            count_sql = f"SELECT COUNT(*) AS total FROM {_qt(customer_meta)} p{company_join_sql}{where_sql}"
            list_sql = (
                f"SELECT p.*{company_select_sql} "
                f"FROM {_qt(customer_meta)} p"
                f"{company_join_sql}"
                f"{where_sql} "
                f"ORDER BY {sort_expr} {normalized_order.upper()} "
                f"LIMIT %s OFFSET %s"
            )

            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(count_sql, tuple(params))
                total = int(cur.fetchone()["total"])

                if total == 0:
                    return {
                        "offset": resolved_offset,
                        "limit": resolved_limit,
                        "totalItems": 0,
                        "items": [],
                    }

                cur.execute(list_sql, (*params, resolved_limit, resolved_offset))
                rows = cur.fetchall()

            items = [_build_customer_aliases(dict(row)) for row in rows]
            return {
                "offset": resolved_offset,
                "limit": resolved_limit,
                "totalItems": total,
                "items": items,
            }

    except RuntimeError:
        return _error(
            status_code=503,
            code="DATABASE_UNAVAILABLE",
            detail="Database is unavailable.",
        )
    except psycopg2.Error as exc:
        message = "Failed to list customers."
        if getattr(exc, "pgerror", None):
            message = str(exc.pgerror).strip().splitlines()[0]
        return _error(
            status_code=500,
            code="CUSTOMER_QUERY_FAILED",
            detail=message,
        )


@router.get("/{customer_id}")
def get_customer_detail(
    customer_id: str,
    _user: dict = Depends(require_auth),
):
    customer_uuid = _parse_uuid(customer_id)
    if customer_uuid is None:
        return _customer_error_invalid_uuid()

    try:
        with get_conn() as conn:
            snapshot = _load_schema_snapshot(conn)
            customer_meta = _resolve_table(snapshot, CUSTOMER_TABLE_CANDIDATES)
            company_meta = _resolve_table(snapshot, COMPANY_TABLE_CANDIDATES)
            if customer_meta is None:
                return _error(
                    status_code=503,
                    code="CUSTOMER_TABLE_NOT_FOUND",
                    detail="Customer table is not available in the current database.",
                )

            row = _fetch_customer_by_id(
                conn=conn,
                customer_meta=customer_meta,
                company_meta=company_meta,
                customer_uuid=customer_uuid,
                include_inactive=False,
            )
            if row is None:
                return _error(
                    status_code=404,
                    code="CUSTOMER_NOT_FOUND",
                    detail=f"Customer {customer_id} was not found.",
                )
            return _build_customer_aliases(row)

    except RuntimeError:
        return _error(
            status_code=503,
            code="DATABASE_UNAVAILABLE",
            detail="Database is unavailable.",
        )
    except psycopg2.Error as exc:
        message = "Failed to fetch customer detail."
        if getattr(exc, "pgerror", None):
            message = str(exc.pgerror).strip().splitlines()[0]
        return _error(
            status_code=500,
            code="CUSTOMER_QUERY_FAILED",
            detail=message,
        )


@router.get("/{customer_id}/appointments")
def get_customer_appointments(
    customer_id: str,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=200),
    offset: int | None = Query(default=None, ge=0),
    limit: int | None = Query(default=None, ge=1, le=200),
    _user: dict = Depends(require_auth),
):
    customer_uuid = _parse_uuid(customer_id)
    if customer_uuid is None:
        return _customer_error_invalid_uuid()

    resolved_offset, resolved_limit = _resolve_paging(page, per_page, offset, limit)

    try:
        with get_conn() as conn:
            snapshot = _load_schema_snapshot(conn)
            customer_meta = _resolve_table(snapshot, CUSTOMER_TABLE_CANDIDATES)
            appointment_meta = _resolve_table(snapshot, APPOINTMENT_TABLE_CANDIDATES)
            if customer_meta is None or appointment_meta is None:
                return _error(
                    status_code=503,
                    code="APPOINTMENT_SCHEMA_UNAVAILABLE",
                    detail="Customer/appointment tables are not available.",
                )

            appointment_customer_col = _find_column(
                appointment_meta,
                "partnerid",
                "partner_id",
                "customerid",
                "customer_id",
                "patientid",
                "patient_id",
            )
            if appointment_customer_col is None:
                return _error(
                    status_code=503,
                    code="APPOINTMENT_SCHEMA_INVALID",
                    detail="Appointment table is missing customer reference column.",
                )

            active_col = _find_column(appointment_meta, "active", "isactive")
            date_col = _find_column(
                appointment_meta,
                "appointmentdate",
                "date",
                "startdate",
                "start_date",
                "created_at",
            ) or _find_column(appointment_meta, "id")

            where = [f"a.{_q(appointment_customer_col)} = %s"]
            params: list[Any] = [str(customer_uuid)]
            if active_col:
                where.append(f"COALESCE(a.{_q(active_col)}, TRUE) = TRUE")
            where_sql = " WHERE " + " AND ".join(where)

            count_sql = f"SELECT COUNT(*) AS total FROM {_qt(appointment_meta)} a{where_sql}"
            list_sql = (
                f"SELECT a.* FROM {_qt(appointment_meta)} a"
                f"{where_sql} "
                f"ORDER BY a.{_q(date_col)} DESC "
                f"LIMIT %s OFFSET %s"
            )

            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(count_sql, tuple(params))
                total = int(cur.fetchone()["total"])

                if total == 0:
                    return {
                        "offset": resolved_offset,
                        "limit": resolved_limit,
                        "totalItems": 0,
                        "items": [],
                    }

                cur.execute(list_sql, (*params, resolved_limit, resolved_offset))
                rows = cur.fetchall()

            items: list[dict[str, Any]] = []
            for row in rows:
                item = dict(row)
                item["customerId"] = _first_non_empty(item, appointment_customer_col)
                item["appointmentDate"] = _first_non_empty(
                    item, "appointmentdate", "date", "startdate", "start_date"
                )
                item["doctorName"] = _first_non_empty(
                    item,
                    "doctorname",
                    "doctor_name",
                    "doctor",
                    "salename",
                    "employee_name",
                )
                item["state"] = _first_non_empty(item, "state", "status", "appointmentstate")
                item["notes"] = _first_non_empty(item, "note", "notes", "comment")
                items.append(item)

            return {
                "offset": resolved_offset,
                "limit": resolved_limit,
                "totalItems": total,
                "items": items,
            }

    except RuntimeError:
        return _error(
            status_code=503,
            code="DATABASE_UNAVAILABLE",
            detail="Database is unavailable.",
        )
    except psycopg2.Error as exc:
        message = "Failed to fetch customer appointments."
        if getattr(exc, "pgerror", None):
            message = str(exc.pgerror).strip().splitlines()[0]
        return _error(
            status_code=500,
            code="APPOINTMENT_QUERY_FAILED",
            detail=message,
        )


@router.get("/{customer_id}/treatments")
def get_customer_treatments(
    customer_id: str,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=200),
    offset: int | None = Query(default=None, ge=0),
    limit: int | None = Query(default=None, ge=1, le=200),
    _user: dict = Depends(require_auth),
):
    customer_uuid = _parse_uuid(customer_id)
    if customer_uuid is None:
        return _customer_error_invalid_uuid()

    resolved_offset, resolved_limit = _resolve_paging(page, per_page, offset, limit)

    try:
        with get_conn() as conn:
            snapshot = _load_schema_snapshot(conn)
            order_meta = _resolve_table(snapshot, TREATMENT_TABLE_CANDIDATES)
            line_meta = _resolve_table(snapshot, TREATMENT_LINE_TABLE_CANDIDATES)
            if order_meta is None:
                return _error(
                    status_code=503,
                    code="TREATMENT_TABLE_NOT_FOUND",
                    detail="Sale-order table is not available.",
                )

            order_customer_col = _find_column(
                order_meta,
                "partnerid",
                "partner_id",
                "customerid",
                "customer_id",
                "patientid",
                "patient_id",
            )
            order_id_col = _find_column(order_meta, "id", "saleorderid", "sale_order_id")
            if order_customer_col is None or order_id_col is None:
                return _error(
                    status_code=503,
                    code="TREATMENT_SCHEMA_INVALID",
                    detail="Sale-order table is missing required relationship columns.",
                )

            active_col = _find_column(order_meta, "active", "isactive")
            date_col = _find_column(
                order_meta,
                "date",
                "orderdate",
                "saleorderdate",
                "created_at",
            ) or order_id_col

            where = [f"o.{_q(order_customer_col)} = %s"]
            params: list[Any] = [str(customer_uuid)]
            if active_col:
                where.append(f"COALESCE(o.{_q(active_col)}, TRUE) = TRUE")
            where_sql = " WHERE " + " AND ".join(where)

            count_sql = f"SELECT COUNT(*) AS total FROM {_qt(order_meta)} o{where_sql}"
            list_sql = (
                f"SELECT o.* FROM {_qt(order_meta)} o"
                f"{where_sql} "
                f"ORDER BY o.{_q(date_col)} DESC "
                f"LIMIT %s OFFSET %s"
            )

            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(count_sql, tuple(params))
                total = int(cur.fetchone()["total"])

                if total == 0:
                    return {
                        "offset": resolved_offset,
                        "limit": resolved_limit,
                        "totalItems": 0,
                        "items": [],
                    }

                cur.execute(list_sql, (*params, resolved_limit, resolved_offset))
                order_rows = [dict(r) for r in cur.fetchall()]

                # Pull nested line-items in one query.
                lines_by_order: dict[str, list[dict[str, Any]]] = defaultdict(list)
                if line_meta is not None:
                    line_order_col = _find_column(
                        line_meta,
                        "saleorderid",
                        "sale_order_id",
                        "orderid",
                        "order_id",
                    )
                    if line_order_col:
                        order_ids = [str(order[order_id_col]) for order in order_rows]
                        placeholders = ", ".join(["%s"] * len(order_ids))
                        line_active_col = _find_column(line_meta, "active", "isactive")
                        line_where = f"l.{_q(line_order_col)} IN ({placeholders})"
                        if line_active_col:
                            line_where += f" AND COALESCE(l.{_q(line_active_col)}, TRUE) = TRUE"
                        line_sql = (
                            f"SELECT l.* FROM {_qt(line_meta)} l "
                            f"WHERE {line_where} "
                            f"ORDER BY l.{_q(line_order_col)}"
                        )
                        cur.execute(line_sql, tuple(order_ids))
                        for line in cur.fetchall():
                            line_item = dict(line)
                            line_item["productName"] = _first_non_empty(
                                line_item, "productname", "product_name", "name"
                            )
                            line_item["quantity"] = _first_non_empty(
                                line_item, "quantity", "qty", "product_uom_qty"
                            )
                            line_item["priceUnit"] = _first_non_empty(
                                line_item, "priceunit", "price_unit", "unitprice"
                            )
                            line_item["teeth"] = _first_non_empty(
                                line_item, "teeth", "tooth", "toothposition", "tooth_position"
                            )
                            lines_by_order[str(line_item.get(line_order_col))].append(line_item)

            items: list[dict[str, Any]] = []
            for order_row in order_rows:
                order_item = dict(order_row)
                order_key = str(order_item.get(order_id_col))
                line_items = lines_by_order.get(order_key, [])
                order_item["customerId"] = _first_non_empty(order_item, order_customer_col)
                order_item["lineItems"] = line_items
                order_item["lines"] = line_items
                order_item["totalAmount"] = _first_non_empty(
                    order_item,
                    "amounttotal",
                    "amount_total",
                    "totalamount",
                    "total",
                )
                order_item["state"] = _first_non_empty(order_item, "state", "status", "orderstate")
                items.append(order_item)

            return {
                "offset": resolved_offset,
                "limit": resolved_limit,
                "totalItems": total,
                "items": items,
            }

    except RuntimeError:
        return _error(
            status_code=503,
            code="DATABASE_UNAVAILABLE",
            detail="Database is unavailable.",
        )
    except psycopg2.Error as exc:
        message = "Failed to fetch customer treatments."
        if getattr(exc, "pgerror", None):
            message = str(exc.pgerror).strip().splitlines()[0]
        return _error(
            status_code=500,
            code="TREATMENT_QUERY_FAILED",
            detail=message,
        )


@router.post("", status_code=201)
def create_customer(
    payload: dict[str, Any],
    _user: dict = Depends(require_auth),
):
    if not isinstance(payload, dict):
        return _validation_error([{"field": "body", "message": "Request body must be a JSON object"}])

    normalized, errors = _parse_create_or_update_payload(
        payload=payload,
        require_name_and_company=True,
    )
    if errors:
        return _validation_error(errors)

    try:
        with get_conn() as conn:
            snapshot = _load_schema_snapshot(conn)
            customer_meta = _resolve_table(snapshot, CUSTOMER_TABLE_CANDIDATES)
            company_meta = _resolve_table(snapshot, COMPANY_TABLE_CANDIDATES)
            if customer_meta is None:
                return _error(
                    status_code=503,
                    code="CUSTOMER_TABLE_NOT_FOUND",
                    detail="Customer table is not available in the current database.",
                )

            name_col = _find_column(customer_meta, "name")
            company_col = _find_column(customer_meta, "companyid", "company_id")
            if name_col is None or company_col is None:
                return _error(
                    status_code=503,
                    code="CUSTOMER_SCHEMA_INVALID",
                    detail="Customer table is missing required name/company columns.",
                )

            values = _build_customer_column_values(
                customer_meta=customer_meta,
                normalized_payload=normalized,
                raw_payload=payload,
                include_defaults=True,
            )

            if name_col not in values:
                values[name_col] = normalized["name"]
            if company_col not in values:
                values[company_col] = normalized["company_id"]

            if not values:
                return _error(
                    status_code=422,
                    code="INVALID_CUSTOMER_PAYLOAD",
                    detail="No valid fields were provided to create customer.",
                )

            insert_cols = list(values.keys())
            placeholders = ", ".join(["%s"] * len(insert_cols))
            insert_sql = (
                f"INSERT INTO {_qt(customer_meta)} ({', '.join(_q(col) for col in insert_cols)}) "
                f"VALUES ({placeholders})"
            )

            id_col = _find_column(customer_meta, "id")
            returning_col = id_col if id_col else insert_cols[0]
            insert_sql += f" RETURNING {_q(returning_col)}"

            with conn.cursor() as cur:
                cur.execute(insert_sql, tuple(values[col] for col in insert_cols))
                created_id = cur.fetchone()[0]

            created_uuid = _parse_uuid(created_id)
            if created_uuid is None:
                # If id isn't UUID in schema, still return created identifier.
                return {"id": str(created_id)}

            created = _fetch_customer_by_id(
                conn=conn,
                customer_meta=customer_meta,
                company_meta=company_meta,
                customer_uuid=created_uuid,
                include_inactive=True,
            )
            if created is None:
                return {"id": str(created_uuid)}

            return _build_customer_aliases(created)

    except RuntimeError:
        return _error(
            status_code=503,
            code="DATABASE_UNAVAILABLE",
            detail="Database is unavailable.",
        )
    except psycopg2.Error as exc:
        message = "Failed to create customer."
        if getattr(exc, "pgerror", None):
            message = str(exc.pgerror).strip().splitlines()[0]
        return _error(
            status_code=422,
            code="CREATE_CUSTOMER_FAILED",
            detail=message,
        )


@router.put("/{customer_id}")
def update_customer(
    customer_id: str,
    payload: dict[str, Any],
    _user: dict = Depends(require_auth),
):
    customer_uuid = _parse_uuid(customer_id)
    if customer_uuid is None:
        return _customer_error_invalid_uuid()

    if not isinstance(payload, dict):
        return _validation_error([{"field": "body", "message": "Request body must be a JSON object"}])

    normalized, errors = _parse_create_or_update_payload(
        payload=payload,
        require_name_and_company=False,
    )
    if errors:
        return _validation_error(errors)

    if not payload:
        return _validation_error([{"field": "body", "message": "At least one field is required"}])

    try:
        with get_conn() as conn:
            snapshot = _load_schema_snapshot(conn)
            customer_meta = _resolve_table(snapshot, CUSTOMER_TABLE_CANDIDATES)
            company_meta = _resolve_table(snapshot, COMPANY_TABLE_CANDIDATES)
            if customer_meta is None:
                return _error(
                    status_code=503,
                    code="CUSTOMER_TABLE_NOT_FOUND",
                    detail="Customer table is not available in the current database.",
                )

            id_col = _find_column(customer_meta, "id")
            if id_col is None:
                return _error(
                    status_code=503,
                    code="CUSTOMER_SCHEMA_INVALID",
                    detail="Customer table is missing id column.",
                )

            existing = _fetch_customer_by_id(
                conn=conn,
                customer_meta=customer_meta,
                company_meta=company_meta,
                customer_uuid=customer_uuid,
                include_inactive=True,
            )
            if existing is None:
                return _error(
                    status_code=404,
                    code="CUSTOMER_NOT_FOUND",
                    detail=f"Customer {customer_id} was not found.",
                )

            values = _build_customer_column_values(
                customer_meta=customer_meta,
                normalized_payload=normalized,
                raw_payload=payload,
                include_defaults=False,
            )

            # Never update immutable id via payload.
            values.pop(id_col, None)

            updated_at_col = _find_column(customer_meta, "updated_at", "updatedat")
            if updated_at_col and updated_at_col not in values:
                values[updated_at_col] = datetime.now(timezone.utc)

            if not values:
                return _validation_error(
                    [{"field": "body", "message": "No updatable fields were provided"}]
                )

            assignments = ", ".join(f"{_q(col)} = %s" for col in values.keys())
            update_sql = (
                f"UPDATE {_qt(customer_meta)} "
                f"SET {assignments} "
                f"WHERE {_q(id_col)} = %s "
                f"RETURNING {_q(id_col)}"
            )
            with conn.cursor() as cur:
                cur.execute(update_sql, (*values.values(), str(customer_uuid)))
                updated = cur.fetchone()
                if updated is None:
                    return _error(
                        status_code=404,
                        code="CUSTOMER_NOT_FOUND",
                        detail=f"Customer {customer_id} was not found.",
                    )

            refreshed = _fetch_customer_by_id(
                conn=conn,
                customer_meta=customer_meta,
                company_meta=company_meta,
                customer_uuid=customer_uuid,
                include_inactive=True,
            )
            if refreshed is None:
                return {"id": str(customer_uuid)}
            return _build_customer_aliases(refreshed)

    except RuntimeError:
        return _error(
            status_code=503,
            code="DATABASE_UNAVAILABLE",
            detail="Database is unavailable.",
        )
    except psycopg2.Error as exc:
        message = "Failed to update customer."
        if getattr(exc, "pgerror", None):
            message = str(exc.pgerror).strip().splitlines()[0]
        return _error(
            status_code=422,
            code="UPDATE_CUSTOMER_FAILED",
            detail=message,
        )


@router.delete("/{customer_id}")
def delete_customer(
    customer_id: str,
    _user: dict = Depends(require_auth),
):
    customer_uuid = _parse_uuid(customer_id)
    if customer_uuid is None:
        return _customer_error_invalid_uuid()

    try:
        with get_conn() as conn:
            snapshot = _load_schema_snapshot(conn)
            customer_meta = _resolve_table(snapshot, CUSTOMER_TABLE_CANDIDATES)
            if customer_meta is None:
                return _error(
                    status_code=503,
                    code="CUSTOMER_TABLE_NOT_FOUND",
                    detail="Customer table is not available in the current database.",
                )

            id_col = _find_column(customer_meta, "id")
            active_col = _find_column(customer_meta, "active", "isactive")
            if id_col is None or active_col is None:
                return _error(
                    status_code=503,
                    code="CUSTOMER_SCHEMA_INVALID",
                    detail="Customer table is missing id/active columns for soft delete.",
                )

            updates: list[str] = [f"{_q(active_col)} = FALSE"]
            params: list[Any] = []

            updated_at_col = _find_column(customer_meta, "updated_at", "updatedat")
            if updated_at_col:
                updates.append(f"{_q(updated_at_col)} = %s")
                params.append(datetime.now(timezone.utc))

            unactive_date_col = _find_column(customer_meta, "unactivedate", "unactive_date")
            if unactive_date_col:
                updates.append(f"{_q(unactive_date_col)} = %s")
                params.append(datetime.now(timezone.utc))

            sql = (
                f"UPDATE {_qt(customer_meta)} "
                f"SET {', '.join(updates)} "
                f"WHERE {_q(id_col)} = %s "
                f"RETURNING {_q(id_col)}"
            )
            params.append(str(customer_uuid))

            with conn.cursor() as cur:
                cur.execute(sql, tuple(params))
                row = cur.fetchone()
                if row is None:
                    return _error(
                        status_code=404,
                        code="CUSTOMER_NOT_FOUND",
                        detail=f"Customer {customer_id} was not found.",
                    )

            return {
                "id": str(row[0]),
                "active": False,
                "deleted": True,
            }

    except RuntimeError:
        return _error(
            status_code=503,
            code="DATABASE_UNAVAILABLE",
            detail="Database is unavailable.",
        )
    except psycopg2.Error as exc:
        message = "Failed to delete customer."
        if getattr(exc, "pgerror", None):
            message = str(exc.pgerror).strip().splitlines()[0]
        return _error(
            status_code=422,
            code="DELETE_CUSTOMER_FAILED",
            detail=message,
        )
