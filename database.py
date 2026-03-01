# database.py

import sqlite3
import pandas as pd


def create_connection():
    return sqlite3.connect(":memory:")


def load_dataframe_to_db(df: pd.DataFrame, conn):
    df.to_sql("games", conn, index=False, if_exists="replace")


def execute_query(conn, query: str) -> pd.DataFrame:
    return pd.read_sql(query, conn)