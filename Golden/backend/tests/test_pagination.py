from app.core.pagination import paginate


class FakePaginationCursor:
    def __init__(self, rows):
        self.rows = rows
        self._one = None
        self._all = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, sql, params):
        normalized = " ".join(sql.split()).lower()
        params = params or ()

        if normalized.startswith("select count(*) as total from"):
            self._one = {"total": len(self.rows)}
            self._all = []
            return

        if "limit %s offset %s" in normalized:
            limit = int(params[-2])
            offset = int(params[-1])
            self._all = self.rows[offset : offset + limit]
            return

        if normalized.endswith("offset %s"):
            offset = int(params[-1])
            self._all = self.rows[offset:]
            return

        self._all = list(self.rows)

    def fetchone(self):
        return self._one

    def fetchall(self):
        return self._all


class FakePaginationConn:
    def __init__(self, rows):
        self.rows = rows

    def cursor(self, **kwargs):
        del kwargs
        return FakePaginationCursor(self.rows)


def test_paginate_page_two_twenty_items():
    rows = [{"id": i} for i in range(1, 101)]
    conn = FakePaginationConn(rows)

    result = paginate(
        "SELECT id FROM sample ORDER BY id",
        params=[],
        conn=conn,
        page=2,
        per_page=20,
    )

    assert result["offset"] == 20
    assert result["limit"] == 20
    assert result["totalItems"] == 100
    assert len(result["items"]) == 20
    assert result["items"][0]["id"] == 21


def test_paginate_per_page_zero_returns_all_rows():
    rows = [{"id": i} for i in range(1, 101)]
    conn = FakePaginationConn(rows)

    result = paginate(
        "SELECT id FROM sample ORDER BY id",
        params=[],
        conn=conn,
        page=1,
        per_page=0,
    )

    assert result["offset"] == 0
    assert result["limit"] == 0
    assert result["totalItems"] == 100
    assert len(result["items"]) == 100


def test_paginate_empty_dataset_default_shape():
    conn = FakePaginationConn([])

    result = paginate(
        "SELECT id FROM sample ORDER BY id",
        params=[],
        conn=conn,
        page=1,
        per_page=20,
    )

    assert result == {
        "offset": 0,
        "limit": 20,
        "totalItems": 0,
        "items": [],
    }


def test_paginate_offset_limit_style_returns_expected_window():
    rows = [{"id": i} for i in range(1, 31)]
    conn = FakePaginationConn(rows)

    result = paginate(
        "SELECT id FROM sample ORDER BY id",
        params=[],
        conn=conn,
        offset=10,
        limit=5,
    )

    assert result["offset"] == 10
    assert result["limit"] == 5
    assert result["totalItems"] == 30
    assert [item["id"] for item in result["items"]] == [11, 12, 13, 14, 15]


def test_paginate_limit_zero_with_offset_returns_all_from_offset():
    rows = [{"id": i} for i in range(1, 21)]
    conn = FakePaginationConn(rows)

    result = paginate(
        "SELECT id FROM sample ORDER BY id",
        params=[],
        conn=conn,
        offset=15,
        limit=0,
    )

    assert result["offset"] == 15
    assert result["limit"] == 0
    assert result["totalItems"] == 20
    assert [item["id"] for item in result["items"]] == [16, 17, 18, 19, 20]
