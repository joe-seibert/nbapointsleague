import json
import os

import pandas as pd
import yaml
from nba_api.stats.endpoints import leaguedashplayerstats, leaguegamelog

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

game_log = leaguegamelog.LeagueGameLog(
    season=api_season,
    season_type_all_star="Playoffs",
    player_or_team_abbreviation="P",
    proxy=PROXY,
    timeout=30,
).get_data_frames()[0]

# Player → NBA team mapping. Frozen once playoffs start (no mid-playoff trades),
# so we cache it on first run and reuse it on every subsequent run.
player_teams_cache = f"seasons/{SEASON}/player_teams_{SEASON}.json"
if os.path.exists(player_teams_cache):
    with open(player_teams_cache) as f:
        player_to_nba_team = json.load(f)
else:
    regular_season_stats = leaguedashplayerstats.LeagueDashPlayerStats(
        season=api_season,
        season_type_all_star="Regular Season",
        proxy=PROXY,
        timeout=30,
    ).get_data_frames()[0]
    player_to_nba_team = dict(
        zip(regular_season_stats["PLAYER_NAME"], regular_season_stats["TEAM_ABBREVIATION"])
    )
    with open(player_teams_cache, "w") as f:
        json.dump(player_to_nba_team, f, indent=2, sort_keys=True)

# Eliminated teams = (any NBA team that didn't make the playoffs) +
# (playoff teams with 4 losses to a single opponent, i.e. lost their series).
all_nba_teams = set(player_to_nba_team.values()) - {""}
playoff_teams = set(game_log["TEAM_ABBREVIATION"].unique())
non_playoff_teams = all_nba_teams - playoff_teams

team_games = game_log[["TEAM_ABBREVIATION", "GAME_ID", "MATCHUP", "WL"]].drop_duplicates()
team_games = team_games.assign(OPPONENT=team_games["MATCHUP"].str.split().str[-1])
loss_counts = (
    team_games[team_games["WL"] == "L"]
    .groupby(["TEAM_ABBREVIATION", "OPPONENT"])
    .size()
)
series_eliminated = {team for (team, _), n in loss_counts.items() if n >= 4}
eliminated_teams = sorted(non_playoff_teams | series_eliminated)

# Build per-player game-by-game breakdown sorted by date. WL is NaN for
# games still in progress; emit it as null so the JSON stays valid.
games_by_player = {}
for player_name, group in game_log.sort_values("GAME_DATE").groupby("PLAYER_NAME"):
    games_by_player[player_name] = [
        {
            "Date": row["GAME_DATE"],
            "Matchup": row["MATCHUP"],
            "WL": row["WL"] if pd.notna(row["WL"]) else None,
            "Points": int(row["PTS"]),
        }
        for _, row in group.iterrows()
    ]

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
            nba_team = row["TEAM_ABBREVIATION"]
        except (IndexError, KeyError):
            pts = 0
            gp = 0
            nba_team = player_to_nba_team.get(player_name, "")
        team_pts += pts
        team_gp += gp
        player_details.append(
            {
                "Player": player_name,
                "Total Points": pts,
                "Games Played": gp,
                "Team": team_name,
                "NBA Team": nba_team,
                "Eliminated": nba_team in eliminated_teams,
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
        "Eliminated": row["TEAM_ABBREVIATION"] in eliminated_teams,
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

with open(f"{output_dir}/player_games_{SEASON}.json", "w") as f:
    json.dump(games_by_player, f, indent=2, allow_nan=False)

# Write CSV
summary_df = pd.DataFrame(team_summaries).set_index("Team")
summary_df.to_csv(f"{output_dir}/pointsleague_{SEASON}.csv")

detail_df = pd.DataFrame(player_details)
detail_df.to_csv(f"{output_dir}/full_points_table_{SEASON}.csv", index=False)

print(
    f"Wrote {len(team_summaries)} teams, {len(player_details)} players, "
    f"{len(all_players)} all-players, and game logs for {len(games_by_player)} players to {output_dir}/"
)
print(f"Eliminated teams: {eliminated_teams}")
