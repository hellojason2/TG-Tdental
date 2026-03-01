"""Database connection pool using psycopg2 ThreadedConnectionPool."""

import logging
from contextlib import contextmanager
from typing import Generator, Optional

import psycopg2
from psycopg2 import pool as pg_pool

logger = logging.getLogger(__name__)

_pool: Optional[pg_pool.ThreadedConnectionPool] = None


def init_pool(database_url: str) -> None:
    """Initialise the global connection pool.

    Logs success on creation. On failure (bad URL, unreachable host, etc.)
    the error is logged and the pool remains ``None`` so the app can still
    start and serve non-DB routes.
    """
    global _pool
    if _pool is not None:
        _pool.closeall()
        _pool = None

    try:
        _pool = pg_pool.ThreadedConnectionPool(
            minconn=2,
            maxconn=10,
            dsn=database_url,
        )
        logger.info("[BOOT] Database pool ready (2-10 connections)")
    except psycopg2.OperationalError as exc:
        logger.error("[BOOT] Failed to create database pool: %s", exc)
        _pool = None
    except Exception as exc:
        logger.error("[BOOT] Unexpected error creating database pool: %s", exc)
        _pool = None


def close_pool() -> None:
    """Close all connections in the pool."""
    global _pool
    if _pool is not None:
        _pool.closeall()
        logger.info("[SHUTDOWN] Database pool closed")
        _pool = None


@contextmanager
def get_conn() -> Generator:
    """Yield a connection from the pool and return it when done.

    Usage::

        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")

    The connection is returned to the pool after the block exits.
    If the block raises, the transaction is rolled back before returning.
    """
    if _pool is None:
        raise RuntimeError("Database pool is not initialised")

    conn = _pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        _pool.putconn(conn)
