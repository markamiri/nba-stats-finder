import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

DATABASE_URL = os.getenv("NEON_CONNECTION_STRING")

if not DATABASE_URL:
    raise ValueError("NEON_CONNECTION_STRING not set")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,     # checks if connection is alive
    pool_recycle=300        # refresh connection every 5 min
)