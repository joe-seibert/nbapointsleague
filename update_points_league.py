import json
import os

from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = "1KHFofiupqYTIbuT8xL8atOuUjOOUM7mTbZzqOVtV2nw"

SEASON = os.environ.get("SEASON", "2026")
DATA_FILE = f"seasons/{SEASON}/data/full_points_table_{SEASON}.json"

SHEET_NAME_MAP = {
    "Andrew": "Drew",
    "Connor": "Con",
    "Jono": "Jono",
    "Joe": "Joe",
    "Julian": "Julian",
    "Sam": "Sam",
}


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


def load_player_data():
    with open(DATA_FILE) as f:
        return json.load(f)


def update_sheet(service, sheet_name, players):
    names = [[p["Player"]] for p in players]
    points = [[p["Total Points"]] for p in players]
    games = [[p["Games Played"]] for p in players]

    row_end = len(players) + 1

    body = {
        "valueInputOption": "USER_ENTERED",
        "data": [
            {"range": f"{sheet_name}!A2:A{row_end}", "values": names},
            {"range": f"{sheet_name}!B2:B{row_end}", "values": points},
            {"range": f"{sheet_name}!C2:C{row_end}", "values": games},
        ],
    }
    service.spreadsheets().values().batchUpdate(
        spreadsheetId=SPREADSHEET_ID, body=body
    ).execute()
    print(f"Updated sheet: {sheet_name}")


def main():
    player_data = load_player_data()
    service = get_sheets_service()

    for team_name, sheet_name in SHEET_NAME_MAP.items():
        team_players = [p for p in player_data if p["Team"] == team_name]
        update_sheet(service, sheet_name, team_players)

    print("All sheets updated.")


if __name__ == "__main__":
    main()
