import json
import os

import pandas as pd
import yaml
from nba_api.stats.endpoints import leaguedashplayerstats

SEASON = os.environ.get("SEASON", "2026")
PROXY = os.environ.get("WEBSHARE_PROXY")

# Season format for the API is "YYYY-YY" where SEASON env var is the ending year
api_season = f"{int(SEASON) - 1}-{SEASON[2:]}"

player_stats = leaguedashplayerstats.LeagueDashPlayerStats(
    season=api_season,
    season_type_all_star="Playoffs",
    proxy=PROXY,
    timeout=30,
).get_data_frames()[0]

with open(f"seasons/{SEASON}/drafted_players_{SEASON}.yml") as file:
    league = yaml.load(file, Loader=yaml.FullLoader)

output_dir = f"seasons/{SEASON}/data"
os.makedirs(output_dir, exist_ok=True)

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

drafted_names = {name for roster in league.values() for name in roster}
player_to_owner = {name: owner for owner, roster in league.items() for name in roster}

all_players = [
    {
        "Player": row["PLAYER_NAME"],
        "NBA Team": row["TEAM_ABBREVIATION"],
        "Coach": player_to_owner.get(row["PLAYER_NAME"], "Undrafted"),
        "Total Points": int(row["PTS"]),
        "Games Played": int(row["GP"]),
        "PPG": round(row["PTS"] / row["GP"], 2) if row["GP"] > 0 else 0,
    }
    for _, row in player_stats.sort_values("PTS", ascending=False).head(128).iterrows()
]

# Write JSON
with open(f"{output_dir}/pointsleague_{SEASON}.json", "w") as f:
    json.dump(team_summaries, f, indent=2)

with open(f"{output_dir}/full_points_table_{SEASON}.json", "w") as f:
    json.dump(player_details, f, indent=2)

with open(f"{output_dir}/all_players_{SEASON}.json", "w") as f:
    json.dump(all_players, f, indent=2)

# Write CSV
summary_df = pd.DataFrame(team_summaries).set_index("Team")
summary_df.to_csv(f"{output_dir}/pointsleague_{SEASON}.csv")

detail_df = pd.DataFrame(player_details)
detail_df.to_csv(f"{output_dir}/full_points_table_{SEASON}.csv", index=False)

print(f"Wrote {len(team_summaries)} teams, {len(player_details)} players, and {len(all_players)} all-players to {output_dir}/")
