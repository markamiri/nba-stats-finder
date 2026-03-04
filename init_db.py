from sqlalchemy import text
from db import engine

with engine.connect() as conn:

    conn.execute(text("""
    CREATE TABLE IF NOT EXISTS queries (
        id SERIAL PRIMARY KEY,
        query_text TEXT,
        extracted_player TEXT,
        parsed_intent TEXT,
        sql_generated TEXT,
        result_json JSONB,
        success BOOLEAN,
        error_message TEXT,
        created_at TIMESTAMP DEFAULT NOW()
    )
    """))

    conn.commit()

print("Database initialized")