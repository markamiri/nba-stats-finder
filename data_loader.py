# data_loader.py

from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
import pandas as pd


def load_player_games(player_name: str) -> pd.DataFrame:
    player = players.find_players_by_full_name(player_name)[0]
    player_id = player["id"]

    logs = playergamelog.PlayerGameLog(player_id=player_id)
    df = logs.get_data_frames()[0]

    df["GAME_DATE"] = pd.to_datetime(df["GAME_DATE"])

    return df