from sqlalchemy import create_engine
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("NEON_PLAYER_DATABASE")

engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True
)
def create_connection():
    return engine.connect()


def execute_query(conn, sql_query):
    return pd.read_sql(sql_query, conn)