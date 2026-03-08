from nba_api.stats.endpoints import leaguegamefinder
import pandas as pd

# gets all the team stats for the games

# Example: get games from March 1 to March 3
date_from = "03/01/2026"
date_to = "03/03/2026"

# Call the NBA API
gamefinder = leaguegamefinder.LeagueGameFinder(
    date_from_nullable=date_from,
    date_to_nullable=date_to,
    league_id_nullable="00"  # NBA
)

# Convert response to dataframe
games_df = gamefinder.get_data_frames()[0]

# Print results
print("Number of records:", len(games_df))
print(games_df.head())

# Print selected columns for readability
print("\nExample simplified output:\n")
print(games_df[[
    "PLAYER_ID",
    "PLAYER_NAME",
    "TEAM_NAME",
    "GAME_ID",
    "GAME_DATE",
    "MATCHUP",
    "PTS",
    "REB",
    "AST"
]].head(20))