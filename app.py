# app.py

from fastapi import FastAPI
from pydantic import BaseModel
from query_logger import log_query
from player_parser import extract_player_name
from team_parser import extract_team
from data_loader import load_player_games
from database import create_connection, load_dataframe_to_db, execute_query
from llm import generate_sql
from validator import validate_sql
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException
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

        # -------- extraction stage --------
        stage = "entity_extraction"

        player_name = extract_player_name(user_query)
        team_abbr = extract_team(user_query)

        if not player_name:
            raise HTTPException(status_code=400, detail="Player could not be extracted")

        # -------- data loading --------
        stage = "load_player_games"

        df = load_player_games(player_name)

        conn = create_connection()
        load_dataframe_to_db(df, conn)

        # -------- SQL generation --------
        stage = "sql_generation"

        sql_query = generate_sql(user_query, team_abbr)

        # -------- SQL validation --------
        stage = "sql_validation"

        validate_sql(sql_query)

        # -------- SQL execution --------
        stage = "sql_execution"

        result_df = execute_query(conn, sql_query)

        # -------- success logging --------
        log_query(
            query_text=user_query,
            extracted_player=player_name,
            parsed_intent="auto",
            sql_generated=sql_query,
            result_df=result_df,
            success=True
        )

        return {
            "player": player_name,
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