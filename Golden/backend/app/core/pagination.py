"""Reusable pagination helper for SQL queries."""

from psycopg2.extras import RealDictCursor


def paginate(
    query: str,
    params: tuple | list | None,
    conn,
    page: int = 1,
    per_page: int = 20,
    *,
    offset: int | None = None,
    limit: int | None = None,
) -> dict:
    """Execute *query* with pagination and return a standard envelope.

    Supports both:
    - ``page``/``per_page`` style (legacy)
    - ``offset``/``limit`` style (preferred for API parity)

    ``per_page=0`` or ``limit=0`` means "return all rows".
    """
    resolved_offset, resolved_limit = _resolve_window(
        page=page,
        per_page=per_page,
        offset=offset,
        limit=limit,
    )

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        count_sql = f"SELECT COUNT(*) AS total FROM ({query}) AS _counted"
        cur.execute(count_sql, params)
        total_items = int(cur.fetchone()["total"])

        if total_items == 0:
            return {
                "offset": resolved_offset,
                "limit": resolved_limit,
                "totalItems": 0,
                "items": [],
            }

        bound_params = _as_tuple(params)
        if resolved_limit == 0 and resolved_offset > 0:
            page_sql = f"{query} OFFSET %s"
            page_params = (*bound_params, resolved_offset)
        elif resolved_limit == 0:
            page_sql = query
            page_params = bound_params
        else:
            page_sql = f"{query} LIMIT %s OFFSET %s"
            page_params = (*bound_params, resolved_limit, resolved_offset)

        cur.execute(page_sql, page_params)
        rows = cur.fetchall()

    return {
        "offset": resolved_offset,
        "limit": resolved_limit,
        "totalItems": total_items,
        "items": [dict(row) for row in rows],
    }


def _normalise_page(page: int) -> int:
    try:
        value = int(page)
    except (TypeError, ValueError):
        return 1
    return value if value > 0 else 1


def _normalise_per_page(per_page: int) -> int:
    try:
        value = int(per_page)
    except (TypeError, ValueError):
        return 20
    if value < 0:
        return 20
    return value


def _normalise_offset(offset: int | None) -> int:
    try:
        value = int(offset) if offset is not None else 0
    except (TypeError, ValueError):
        return 0
    return value if value >= 0 else 0


def _resolve_window(
    *,
    page: int,
    per_page: int,
    offset: int | None,
    limit: int | None,
) -> tuple[int, int]:
    if offset is not None or limit is not None:
        resolved_offset = _normalise_offset(offset)
        resolved_limit = (
            _normalise_per_page(limit)
            if limit is not None
            else _normalise_per_page(per_page)
        )
        return resolved_offset, resolved_limit

    resolved_page = _normalise_page(page)
    resolved_limit = _normalise_per_page(per_page)
    resolved_offset = 0 if resolved_limit == 0 else (resolved_page - 1) * resolved_limit
    return resolved_offset, resolved_limit


def _as_tuple(params: tuple | list | None) -> tuple:
    if params is None:
        return ()
    return tuple(params)
