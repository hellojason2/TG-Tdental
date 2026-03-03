from app.core import lookup_sql


class _Cursor:
    def __init__(self, row):
        self._row = row
        self.sql = ""
        self.params = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, sql, params=None):
        self.sql = sql
        self.params = params

    def fetchone(self):
        return self._row


class _Conn:
    def __init__(self, row):
        self.cursor_obj = _Cursor(row)
        self.cursor_calls = 0

    def cursor(self):
        self.cursor_calls += 1
        return self.cursor_obj


def test_resolve_table_prefers_dbo_over_public():
    lookup_sql._TABLE_CACHE.clear()
    conn = _Conn(("dbo", "companies"))

    table = lookup_sql.resolve_table(conn, "Companies", "company", "companies")

    assert table is not None
    assert table.schema == "dbo"
    assert table.table == "companies"
    assert "WHEN 'dbo' THEN 0" in conn.cursor_obj.sql
    assert "WHEN 'public' THEN 1" in conn.cursor_obj.sql
    assert conn.cursor_obj.sql.index("WHEN 'dbo' THEN 0") < conn.cursor_obj.sql.index(
        "WHEN 'public' THEN 1"
    )
    assert conn.cursor_obj.params == (["companies", "company"],)


def test_resolve_table_uses_cache_without_second_query():
    lookup_sql._TABLE_CACHE.clear()
    first_conn = _Conn(("dbo", "companies"))
    second_conn = _Conn(("public", "companies"))

    first = lookup_sql.resolve_table(first_conn, "companies")
    second = lookup_sql.resolve_table(second_conn, "companies")

    assert first is not None
    assert second is not None
    assert first == second
    assert first_conn.cursor_calls == 1
    assert second_conn.cursor_calls == 0
