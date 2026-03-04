# data_loader.py

from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
import pandas as pd
from nba_api.stats.library.http import NBAStatsHTTP

NBAStatsHTTP.headers = {
    "Host": "stats.nba.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Referer": "https://www.nba.com/",
    "Origin": "https://www.nba.com",
}


def load_player_games(player_name: str) -> pd.DataFrame:
    player = players.find_players_by_full_name(player_name)[0]
    player_id = player["id"]

    logs = playergamelog.PlayerGameLog(player_id=player_id)
    df = logs.get_data_frames()[0]

    df["GAME_DATE"] = pd.to_datetime(df["GAME_DATE"])

    return df