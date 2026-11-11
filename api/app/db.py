"""Database helpers.

Supports the local portable PostgreSQL instance (PG* environment variables)
and a hosted PostgreSQL (DATABASE_URL), which is what the deployed API uses.

All helpers degrade gracefully: if the database is unreachable the API still
serves the model-backed features and simply reports empty persistence.
"""
from __future__ import annotations

import os

import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()

DB_PARAMS = dict(
    host=os.environ.get("PGHOST", "localhost"),
    port=int(os.environ.get("PGPORT", "5433")),
    dbname=os.environ.get("PGDATABASE", "marine_conservation"),
    user=os.environ.get("PGUSER", "postgres"),
)

# Optional password for hosted instances that use one.
if os.environ.get("PGPASSWORD"):
    DB_PARAMS["password"] = os.environ["PGPASSWORD"]


def get_conn():
    if DATABASE_URL:
        return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return psycopg2.connect(**DB_PARAMS, cursor_factory=RealDictCursor)


def database_available() -> bool:
    """True when a database connection can be established."""
    try:
        conn = get_conn()
        conn.close()
        return True
    except Exception:
        return False


def fetch_all(sql, params=()):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()
    finally:
        conn.close()


def fetch_one(sql, params=()):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchone()
    finally:
        conn.close()


def execute(sql, params=()):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
        conn.commit()
        return True
    finally:
        conn.close()


# ---------------------------------------------------------------- resilient API
def safe_fetch_all(sql, params=()):
    """Like fetch_all but returns [] when the database is unavailable."""
    try:
        return fetch_all(sql, params)
    except Exception:
        return []


def safe_fetch_one(sql, params=()):
    try:
        return fetch_one(sql, params)
    except Exception:
        return None


def safe_execute(sql, params=()):
    """Like execute but returns False when persistence fails."""
    try:
        return execute(sql, params)
    except Exception:
        return False


def ensure_schema():
    """Create the application tables if they are missing (idempotent)."""
    schema_path = os.path.join(os.path.dirname(__file__), "..", "..", "database", "schema.sql")
    try:
        with open(schema_path, encoding="utf-8") as f:
            sql = f.read()
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(sql)
            conn.commit()
        finally:
            conn.close()
        return True
    except Exception:
        return False
