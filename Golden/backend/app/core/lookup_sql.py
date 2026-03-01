"""Helpers for resilient lookup queries across evolving TDental schemas."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class TableRef:
    """Resolved table location in the database."""

    schema: str
    table: str

    @property
    def qualified_name(self) -> str:
        return f'{quote_ident(self.schema)}.{quote_ident(self.table)}'


_TABLE_CACHE: dict[tuple[str, ...], TableRef | None] = {}
_COLUMN_CACHE: dict[tuple[str, str], tuple[str, ...]] = {}


def resolve_table(conn, *candidates: str) -> TableRef | None:
    """Resolve the first existing table from *candidates* across non-system schemas."""
    key = tuple(_normalise_candidates(candidates))
    if not key:
        return None

    if key in _TABLE_CACHE:
        return _TABLE_CACHE[key]

    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT table_schema, table_name
            FROM information_schema.tables
            WHERE table_type = 'BASE TABLE'
              AND table_schema NOT IN ('pg_catalog', 'information_schema')
              AND lower(table_name) = ANY(%s)
            ORDER BY
              CASE table_schema
                WHEN 'public' THEN 0
                WHEN 'dbo' THEN 1
                ELSE 2
              END,
              table_schema,
              table_name
            LIMIT 1
            """,
            (list(key),),
        )
        row = cur.fetchone()

    table_ref = TableRef(schema=row[0], table=row[1]) if row else None
    _TABLE_CACHE[key] = table_ref
    return table_ref


def table_columns(conn, table_ref: TableRef) -> tuple[str, ...]:
    """Return all lowercased column names for *table_ref*."""
    key = (table_ref.schema, table_ref.table)
    if key in _COLUMN_CACHE:
        return _COLUMN_CACHE[key]

    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT lower(column_name)
            FROM information_schema.columns
            WHERE table_schema = %s
              AND table_name = %s
            ORDER BY ordinal_position
            """,
            (table_ref.schema, table_ref.table),
        )
        cols = tuple(row[0] for row in cur.fetchall())

    _COLUMN_CACHE[key] = cols
    return cols


def pick_column(columns: Iterable[str], *candidates: str) -> str | None:
    """Pick the first existing column from *candidates*.

    Supports tolerant matching for ``snake_case`` vs compact names
    (for example ``is_doctor`` and ``isdoctor``).
    """
    normalised = {col.lower(): col.lower() for col in columns}
    compact = {col.lower().replace("_", ""): col.lower() for col in columns}

    for candidate in candidates:
        key = candidate.strip().lower()
        if not key:
            continue
        if key in normalised:
            return normalised[key]
        key_compact = key.replace("_", "")
        if key_compact in compact:
            return compact[key_compact]
    return None


def page_window(
    *,
    page: int | None,
    per_page: int | None,
    offset: int | None,
    limit: int | None,
    default_limit: int,
) -> tuple[int, int]:
    """Resolve effective ``offset`` and ``limit`` from page or offset style params."""
    if offset is not None or limit is not None:
        return max(offset or 0, 0), max(default_limit if limit is None else limit, 0)

    resolved_page = max(page or 1, 1)
    resolved_limit = max(per_page if per_page is not None else default_limit, 0)
    if resolved_limit == 0:
        return 0, 0
    return (resolved_page - 1) * resolved_limit, resolved_limit


def empty_page(offset: int, limit: int) -> dict:
    """Standard empty paged envelope."""
    return {"offset": offset, "limit": limit, "totalItems": 0, "items": []}


def quote_ident(identifier: str) -> str:
    """Quote SQL identifier safely for dynamic query construction."""
    escaped = identifier.replace('"', '""')
    return f'"{escaped}"'


def _normalise_candidates(candidates: Iterable[str]) -> tuple[str, ...]:
    deduped: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        key = candidate.strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(key)
    return tuple(deduped)
