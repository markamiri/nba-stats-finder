from sqlalchemy import create_engine, text
from nba_api.stats.endpoints import leaguegamelog
import pandas as pd
import os
from dotenv import load_dotenv


load_dotenv()

DATABASE_URL = os.getenv("NEON_PLAYER_DATABASE")

engine = create_engine(DATABASE_URL)

# Fetch season data
logs = leaguegamelog.LeagueGameLog(
    player_or_team_abbreviation="P",
    season="2025-26",
    season_type_all_star="Regular Season"
)

df = logs.get_data_frames()[0]

# -------------------------
# UPSERT PLAYERS
# -------------------------

players_df = df[[
    "PLAYER_ID",
    "PLAYER_NAME",
    "TEAM_ID",
    "TEAM_NAME"
]].drop_duplicates()

with engine.begin() as conn:
    for _, row in players_df.iterrows():
        conn.execute(text("""
            INSERT INTO players (
                player_id,
                player_name,
                team_id,
                team_name
            )
            VALUES (
                :PLAYER_ID,
                :PLAYER_NAME,
                :TEAM_ID,
                :TEAM_NAME
            )
            ON CONFLICT (player_id)
            DO UPDATE SET
                team_id = EXCLUDED.team_id,
                team_name = EXCLUDED.team_name
        """), row.to_dict())

# -------------------------
# GAME LOGS TABLE
# -------------------------

game_logs_df = df.drop(columns=["PLAYER_NAME", "TEAM_NAME"])

game_logs_df.to_sql(
    "player_game_logs",
    engine,
    if_exists="replace",
    index=False
)

print("Database updated successfully.")