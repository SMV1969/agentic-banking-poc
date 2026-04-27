# db.py
import os
import psycopg2
from contextlib import contextmanager
from dotenv import load_dotenv


import os
import psycopg2
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("PG_HOST", "localhost")
DB_PORT = os.getenv("PG_PORT", "5432")
DB_NAME = os.getenv("PG_DB", "postgres")
DB_USER = os.getenv("PG_USER", "postgres")
DB_PASS = os.getenv("PG_PASS", "")

@contextmanager
def get_pg_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
    )
    try:
        yield conn
    finally:
        conn.close()