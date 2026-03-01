# main.py
from player_parser import extract_player_name
from data_loader import load_player_games
from database import create_connection, load_dataframe_to_db, execute_query
from llm import generate_sql
from validator import validate_sql
from team_parser import extract_team



def main():
    print("=== NBA Stats Finder ===")

    # Only works for active player propts right now
    user_query = input("\nEnter your NBA query: ")

    # 🔥 Extract player first
    player_name = extract_player_name(user_query)
    print(f"\nDetected Player: {player_name}")

    team_abbr = extract_team(user_query)

    # Load that player's data
    df = load_player_games(player_name)

    conn = create_connection()
    load_dataframe_to_db(df, conn)

    # Generate SQL
    sql_query = generate_sql(user_query, team_abbr)

    print("\nGenerated SQL:")
    print(sql_query)

    validate_sql(sql_query)

    result = execute_query(conn, sql_query)

    print("\nQuery Result:")
    print(result)


if __name__ == "__main__":
    main()