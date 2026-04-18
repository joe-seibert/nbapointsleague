import json
import os

import numpy as np
import pandas as pd
import yaml
from nba_api.stats.endpoints import leaguedashplayerstats
from nba_api.stats.endpoints.commonallplayers import CommonAllPlayers

all_players = CommonAllPlayers().common_all_players.get_data_frame()
player_stats = leaguedashplayerstats.LeagueDashPlayerStats(
    season_type_all_star="Playoffs"
).get_data_frames()[0]

with open("./drafted_players_2024.yml") as file:
    league = yaml.load(file, Loader=yaml.FullLoader)

os.makedirs("data", exist_ok=True)

team_summaries = []
player_details = []

for team_name, roster in league.items():
    team_pts = 0
    team_gp = 0
    for player_name in roster:
        try:
            row = player_stats[player_stats["PLAYER_NAME"] == player_name].iloc[0]
            pts = int(row["PTS"])
            gp = int(row["GP"])
        except (IndexError, KeyError):
            pts = 0
            gp = 0
        team_pts += pts
        team_gp += gp
        player_details.append(
            {
                "Player": player_name,
                "Total Points": pts,
                "Games Played": gp,
                "Team": team_name,
            }
        )

    team_summaries.append(
        {
            "Team": team_name,
            "Points": team_pts,
            "Games Played": team_gp,
            "PPG": round(team_pts / team_gp, 2) if team_gp > 0 else 0,
        }
    )

# Write JSON
with open("data/pointsleague_2024.json", "w") as f:
    json.dump(team_summaries, f, indent=2)

with open("data/full_points_table_2024.json", "w") as f:
    json.dump(player_details, f, indent=2)

# Write CSV
summary_df = pd.DataFrame(team_summaries).set_index("Team")
summary_df.to_csv("data/pointsleague_2024.csv")

detail_df = pd.DataFrame(player_details)
detail_df.to_csv("data/full_points_table_2024.csv", index=False)

print(f"Wrote {len(team_summaries)} teams and {len(player_details)} players to data/")
