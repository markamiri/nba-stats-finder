# llm.py

from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI()

SYSTEM_PROMPT = """
You generate SQL filter clauses for PostgreSQL queries on table player_game_logs.

Available columns (use ONLY these exact names):
"PLAYER_ID", "TEAM_ABBREVIATION", "GAME_DATE", "MATCHUP", "WL",
"MIN", "FGM", "FGA", "FG_PCT", "FG3M", "FG3A", "FG3_PCT",
"FTM", "FTA", "FT_PCT", "OREB", "DREB", "REB",
"AST", "STL", "BLK", "TOV", "PF", "PTS", "PLUS_MINUS"

Rules:
- NEVER generate SELECT
- NEVER generate FROM
- NEVER generate WHERE "PLAYER_ID"
- The player filter is already applied by the backend
- Only generate additional filters, ORDER BY, and LIMIT
- NEVER use column names not listed above (e.g. use "PTS" not "POINTS", "REB" not "REBOUNDS")

Examples:

User: last 5 games
Output:
ORDER BY "GAME_DATE" DESC
LIMIT 5

User: last 5 games vs BOS
Output:
AND "MATCHUP" LIKE '%BOS%'
ORDER BY "GAME_DATE" DESC
LIMIT 5

Return only SQL.
"""


def generate_sql(user_query: str, player_id: int, team_abbr: str | None = None) -> str:

    system_prompt = SYSTEM_PROMPT
    system_prompt += f"\nAll queries MUST include: PLAYER_ID = {player_id}"

    if team_abbr:
        system_prompt += f"\nThe opponent team abbreviation is {team_abbr}."

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query},
        ],
    )

    sql_query = response.choices[0].message.content.strip()

    sql_query = sql_query.replace("```sql", "").replace("```", "").strip()

    if "SELECT" in sql_query:
        sql_query = sql_query[sql_query.index("SELECT"):]

    return sql_query
