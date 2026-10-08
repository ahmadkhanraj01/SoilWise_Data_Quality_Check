"""Database connection built from DB_* environment variables (loaded from .env)."""
import os

import psycopg
from dotenv import load_dotenv


def get_schema() -> str:
    load_dotenv()
    return os.environ.get("DB_SCHEMA", "public")


def connect(readonly: bool = True) -> psycopg.Connection:
    load_dotenv()
    try:
        conn = psycopg.connect(
            host=os.environ["DB_HOST"],
            port=int(os.environ.get("DB_PORT", "5432")),
            dbname=os.environ["DB_NAME"],
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            sslmode=os.environ.get("DB_SSLMODE", "prefer"),
            connect_timeout=int(os.environ.get("DB_CONNECT_TIMEOUT", "10")),
        )
    except KeyError as e:
        raise SystemExit(f"Missing environment variable: {e.args[0]} (check .env)")
    conn.read_only = readonly
    return conn
