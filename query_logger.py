import json
from sqlalchemy import text
from db import engine


def log_query(
    query_text,
    extracted_player=None,
    parsed_intent=None,
    sql_generated=None,
    result_df=None,
    success=False,
    error_message=None
):

    result_json = None

    if result_df is not None:
        result_json = result_df.to_dict(orient="records")

    with engine.connect() as conn:

        conn.execute(text("""
        INSERT INTO queries (
            query_text,
            extracted_player,
            parsed_intent,
            sql_generated,
            result_json,
            success,
            error_message
        )
        VALUES (
            :query_text,
            :extracted_player,
            :parsed_intent,
            :sql_generated,
            :result_json,
            :success,
            :error_message
        )
        """), {

            "query_text": query_text,
            "extracted_player": extracted_player,
            "parsed_intent": parsed_intent,
            "sql_generated": sql_generated,
            "result_json": json.dumps(result_json) if result_json else None,
            "success": success,
            "error_message": error_message

        })

        conn.commit()