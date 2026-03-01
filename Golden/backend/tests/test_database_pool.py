from concurrent.futures import ThreadPoolExecutor
from threading import Lock

import psycopg2
import pytest

import app.core.database as database


class DummyConn:
    def __init__(self):
        self.commit_calls = 0
        self.rollback_calls = 0

    def commit(self):
        self.commit_calls += 1

    def rollback(self):
        self.rollback_calls += 1


class FakePool:
    def __init__(self, minconn: int, maxconn: int, dsn: str):
        self.minconn = minconn
        self.maxconn = maxconn
        self.dsn = dsn
        self.in_use = 0
        self.max_in_use = 0
        self.get_calls = 0
        self.put_calls = 0
        self.closed = False
        self._lock = Lock()

    def getconn(self):
        with self._lock:
            self.get_calls += 1
            self.in_use += 1
            self.max_in_use = max(self.max_in_use, self.in_use)
        return DummyConn()

    def putconn(self, conn):
        del conn
        with self._lock:
            self.put_calls += 1
            self.in_use -= 1

    def closeall(self):
        self.closed = True


@pytest.fixture(autouse=True)
def reset_pool_state():
    database.close_pool()
    yield
    database.close_pool()


def test_init_pool_bad_database_url_is_graceful(monkeypatch):
    def _raise(*args, **kwargs):
        raise psycopg2.OperationalError("bad DATABASE_URL")

    monkeypatch.setattr(database.pg_pool, "ThreadedConnectionPool", _raise)
    database.init_pool("postgresql://bad-url")
    assert database._pool is None


def test_init_pool_good_database_url_and_get_conn(monkeypatch):
    monkeypatch.setattr(database.pg_pool, "ThreadedConnectionPool", FakePool)
    database.init_pool("postgresql://good-url")

    assert isinstance(database._pool, FakePool)
    assert database._pool.minconn == 2
    assert database._pool.maxconn == 10

    with database.get_conn() as _conn:
        pass

    assert database._pool.get_calls == 1
    assert database._pool.put_calls == 1
    assert database._pool.in_use == 0


def test_get_conn_concurrent_usage_has_no_leak(monkeypatch):
    monkeypatch.setattr(database.pg_pool, "ThreadedConnectionPool", FakePool)
    database.init_pool("postgresql://good-url")

    def _worker(_):
        with database.get_conn() as _conn:
            return True

    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(_worker, range(10)))

    assert all(results)
    assert database._pool.get_calls == 10
    assert database._pool.put_calls == 10
    assert database._pool.in_use == 0
    assert database._pool.max_in_use <= 10
