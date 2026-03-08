from sqlalchemy import create_engine, text
from nba_api.stats.endpoints import leaguegamefinder
import pandas as pd
from datetime import datetime, timedelta
import os
import logging
from dotenv import load_dotenv


import os
load_dotenv()

print(os.getenv("NEON_PLAYER_DATABASE"))
# ----------------------------
# Logging Setup
# ----------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger()

# ----------------------------
# Database
# ----------------------------
DATABASE_URL = os.getenv("NEON_PLAYER_DATABASE")
engine = create_engine(DATABASE_URL)

# ----------------------------
# Date Range
# ----------------------------
today = datetime.utcnow()
yesterday = (today - timedelta(days=1)).strftime("%m/%d/%Y")
two_days_ago = (today - timedelta(days=2)).strftime("%m/%d/%Y")

logger.info(f"Fetching games from {two_days_ago} to {yesterday}")

# ----------------------------
# Fetch Data
# ----------------------------
games = leaguegamefinder.LeagueGameFinder(
    date_from_nullable=two_days_ago,
    date_to_nullable=yesterday,
    player_or_team_abbreviation="P"
)

df = games.get_data_frames()[0]

if df.empty:
    logger.info("No games found in this date range.")
    exit()

logger.info(f"Fetched {len(df)} player game logs from NBA API")

# ----------------------------
# Insert Players
# ----------------------------
players_df = df[[
    "PLAYER_ID",
    "PLAYER_NAME",
    "TEAM_ID",
    "TEAM_NAME"
]].drop_duplicates()

new_players = 0

with engine.begin() as conn:
    for _, row in players_df.iterrows():
       result = conn.execute(text("""
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
            RETURNING xmax = 0 AS inserted
        """), row.to_dict())
    row_result = result.fetchone()

    if row_result.inserted:
        new_players += 1

logger.info(f"New players added: {new_players}")

# ----------------------------
# Insert Game Logs
# ----------------------------
game_logs_df = df.drop(columns=["PLAYER_NAME", "TEAM_NAME"])

inserted_logs = 0
duplicate_logs = 0

with engine.begin() as conn:
    for _, row in game_logs_df.iterrows():
        result = conn.execute(text("""
            INSERT INTO player_game_logs (
                   "SEASON_ID",
                    "PLAYER_ID",
                    "TEAM_ID",
                    "TEAM_ABBREVIATION",
                    "GAME_ID",
                    "GAME_DATE",
                    "MATCHUP",
                    "WL",
                    "MIN",
                    "PTS",
                    "FGM",
                    "FGA",
                    "FG_PCT",
                    "FG3M",
                    "FG3A",
                    "FG3_PCT",
                    "FTM",
                    "FTA",
                    "FT_PCT",
                    "OREB",
                    "DREB",
                    "REB",
                    "AST",
                    "STL",
                    "BLK",
                    "TOV",
                    "PF",
                    "PLUS_MINUS"
            )
            VALUES (
                :SEASON_ID,
                :PLAYER_ID,
                :TEAM_ID,
                :TEAM_ABBREVIATION,
                :GAME_ID,
                :GAME_DATE,
                :MATCHUP,
                :WL,
                :MIN,
                :PTS,
                :FGM,
                :FGA,
                :FG_PCT,
                :FG3M,
                :FG3A,
                :FG3_PCT,
                :FTM,
                :FTA,
                :FT_PCT,
                :OREB,
                :DREB,
                :REB,
                :AST,
                :STL,
                :BLK,
                :TOV,
                :PF,
                :PLUS_MINUS
            )
            ON CONFLICT ("PLAYER_ID", "GAME_ID") DO NOTHING
            RETURNING "PLAYER_ID"
        """), row.to_dict())

        if result.fetchone():
            inserted_logs += 1
        else:
            duplicate_logs += 1

logger.info(f"Game logs inserted: {inserted_logs}")
logger.info(f"Duplicate logs skipped: {duplicate_logs}")

logger.info("Daily sync complete.")