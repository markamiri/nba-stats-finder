# app.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy import text
import os

from query_logger import log_query
from player_parser import extract_player_name
from team_parser import extract_team
from database import create_connection, execute_query
from llm import generate_sql
from validator import validate_sql
import numpy as np
import pandas as pd

SUPABASE_URL = os.getenv("SUPABASE_URL")




app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    query: str


@app.get("/")
def root():
    return {"status": "API is running"}


@app.post("/query")
def handle_query(request: QueryRequest):

    user_query = request.query

    player_name = None
    team_abbr = None
    sql_query = None
    result_df = None
    stage = "start"

    try:

        # -------- entity extraction --------
        stage = "entity_extraction"

        player_name = extract_player_name(user_query)
        team_abbr = extract_team(user_query)

        if not player_name:
            raise HTTPException(status_code=400, detail="Player could not be extracted")

        # -------- database connection --------
        stage = "database_connection"

        conn = create_connection()

        try:
            # -------- find player_id --------
            stage = "player_lookup"

            player_lookup_sql = """
            SELECT player_id
            FROM players
            WHERE LOWER(player_name) = LOWER(:player_name)
            LIMIT 1
            """

            result = conn.execute(
                text(player_lookup_sql),
                {"player_name": player_name}
            ).fetchone()

            if not result:
                raise HTTPException(status_code=404, detail="Player not found")

            player_id = result[0]

            # -------- SQL generation --------
            stage = "sql_generation"

            DEFAULT_COLUMNS = """
            "TEAM_ABBREVIATION",
            "GAME_DATE","MATCHUP","WL",
            "MIN","FGM","FGA","FG_PCT","FG3M","FG3A","FG3_PCT",
            "FTM","FTA","FT_PCT","OREB","DREB","REB",
            "AST","STL","BLK","TOV","PF","PTS","PLUS_MINUS"
            """

            sql_query = generate_sql(user_query, player_id, team_abbr)

            sql_query = f"""
            SELECT {DEFAULT_COLUMNS}
            FROM player_game_logs
            WHERE "PLAYER_ID" = {player_id}
            {sql_query}
            """

            # -------- SQL validation --------
            stage = "sql_validation"

            validate_sql(sql_query)

            # -------- SQL execution --------
            stage = "sql_execution"

            result_df = execute_query(conn, sql_query)

        finally:
            conn.close()

        # -------- success logging --------
        log_query(
            query_text=user_query,
            extracted_player=player_name,
            parsed_intent="auto",
            sql_generated=sql_query,
            result_df=result_df,
            success=True
        )

        for col in ["FG_PCT", "FG3_PCT", "FT_PCT"]:
            if col in result_df.columns:
                result_df[col] = result_df[col].apply(
                    lambda x: f"{round(x * 100, 1)}%" if pd.notna(x) else None
                )

        result_df = result_df.replace({np.nan: None})

        headshot_url = f"{SUPABASE_URL}/storage/v1/object/public/NBA%20headshots/{player_id}.png"

        return {
            "player": player_name,
            "headshot": headshot_url,
            "sql": sql_query,
            "results": result_df.to_dict(orient="records")
        }

    except Exception as e:

        log_query(
            query_text=user_query,
            extracted_player=player_name,
            parsed_intent="auto",
            sql_generated=sql_query,
            success=False,
            error_message=f"{stage}: {str(e)}"
        )

        raise e