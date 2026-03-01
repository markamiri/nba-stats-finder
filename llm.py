# llm.py

from openai import OpenAI
from dotenv import load_dotenv
import os


load_dotenv()
client = OpenAI()

SYSTEM_PROMPT = """
You generate SQLite SELECT queries for a table called 'games'.

Table columns:
SEASON_ID, Player_ID, Game_ID, GAME_DATE, MATCHUP, WL,
MIN, FGM, FGA, FG_PCT, FG3M, FG3A, FG3_PCT,
FTM, FTA, FT_PCT, OREB, DREB, REB,
AST, STL, BLK, TOV, PF, PTS, PLUS_MINUS, VIDEO_AVAILABLE

Rules:
- Only generate SELECT statements.
- Do NOT use INSERT, UPDATE, DELETE, DROP.
- Do NOT use multiple statements.
- Always include ORDER BY when using LIMIT.
- ALWAYS include GAME_DATE and MATCHUP in the SELECT clause.
- The table contains only one player's games.
- Do NOT filter by Player_ID.
- The table games contains ONLY the detected player’s games. Do NOT filter by Player_ID.
- Use MIN as minutes played (integer).
- Use MATCHUP LIKE '%TEAM_ABBR%' when filtering opponent.
- If query includes "last", use ORDER BY GAME_DATE DESC.

Return ONLY the SQL query.
"""


def generate_sql(user_query: str, team_abbr: str | None = None) -> str:
    # Make a local copy

    
    system_prompt = SYSTEM_PROMPT

    # Inject team abbreviation dynamically
    if team_abbr:
        system_prompt += f"\nThe opponent team abbreviation is {team_abbr}."

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query},
        ],
    )

    sql_query = response.choices[0].message.content.strip()
    sql_query = sql_query.replace("```sql", "").replace("```", "").strip()

    return sql_query