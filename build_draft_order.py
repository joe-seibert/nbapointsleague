"""Build the snake-draft pick order for a season.

Reads the column order from the Sheet's `Draft` tab (row 1, one coach per column)
and the per-coach pick order from `seasons/<SEASON>/drafted_players_<SEASON>.yml`,
then writes `seasons/<SEASON>/draft_order_<SEASON>.json` as a flat list of
`{pick, round, coach, player}` records sorted by overall pick number.

Run once per season after the draft finishes:
    uv run build_draft_order.py
"""

import json
import os

import yaml
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
SPREADSHEET_ID = "17jVuUBaDOxkuVDSkqVx9UyVQ3_1y6IJv5stjgdzCT3E"
SEASON = os.environ.get("SEASON", "2026")


def get_sheets_service():
    creds_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT")
    if creds_json:
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write(creds_json)
            creds_path = f.name
        creds = service_account.Credentials.from_service_account_file(creds_path, scopes=SCOPES)
        os.unlink(creds_path)
    else:
        creds = service_account.Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
    return build("sheets", "v4", credentials=creds)


def main():
    svc = get_sheets_service()
    header = (
        svc.spreadsheets()
        .values()
        .get(spreadsheetId=SPREADSHEET_ID, range="Draft!1:1")
        .execute()
        .get("values", [[]])[0]
    )
    coach_order = [c.strip() for c in header if c.strip()]

    with open(f"seasons/{SEASON}/drafted_players_{SEASON}.yml") as f:
        league = yaml.safe_load(f)

    missing = [c for c in coach_order if c not in league]
    extra = [c for c in league if c not in coach_order]
    if missing or extra:
        raise SystemExit(
            f"Coach mismatch between Sheet and YAML. Missing in YAML: {missing}. Extra in YAML: {extra}"
        )

    n_coaches = len(coach_order)
    rounds = max(len(roster) for roster in league.values())
    picks = []
    for r in range(rounds):
        # Snake: round 1 (r=0) goes left-to-right, round 2 reverses, etc.
        ordered_coaches = coach_order if r % 2 == 0 else list(reversed(coach_order))
        for col_in_round, coach in enumerate(ordered_coaches):
            roster = league[coach]
            if r >= len(roster):
                continue
            picks.append(
                {
                    "pick": r * n_coaches + col_in_round + 1,
                    "round": r + 1,
                    "coach": coach,
                    "player": roster[r],
                }
            )

    out_path = f"seasons/{SEASON}/draft_order_{SEASON}.json"
    with open(out_path, "w") as f:
        json.dump(picks, f, indent=2)
    print(f"Wrote {len(picks)} picks to {out_path}")
    print(f"Coach order (round 1): {coach_order}")


if __name__ == "__main__":
    main()
