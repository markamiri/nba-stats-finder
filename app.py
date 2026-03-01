# app.py

from fastapi import FastAPI
from pydantic import BaseModel

from player_parser import extract_player_name
from team_parser import extract_team
from data_loader import load_player_games
from database import create_connection, load_dataframe_to_db, execute_query
from llm import generate_sql
from validator import validate_sql
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "https://nba-frontend-beta.vercel.app",
        "https://nba-frontend-phihjxjkm-markamiris-projects.vercel.app",

    ],
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

    player_name = extract_player_name(user_query)
    team_abbr = extract_team(user_query)

    df = load_player_games(player_name)

    conn = create_connection()
    load_dataframe_to_db(df, conn)

    sql_query = generate_sql(user_query, team_abbr)

    validate_sql(sql_query)

    result_df = execute_query(conn, sql_query)

    return {
        "player": player_name,
        "sql": sql_query,
        "results": result_df.to_dict(orient="records")
    }