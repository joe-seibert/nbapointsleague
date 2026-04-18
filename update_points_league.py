import json
import os
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = "1KHFofiupqYTIbuT8xL8atOuUjOOUM7mTbZzqOVtV2nw"
DATA_FILE = "data/full_points_table_2024.json"

SHEET_NAME_MAP = {
    "Andrew": "Drew",
    "Connor": "Con",
    "Jono": "Jono",
    "Joe": "Joe",
    "Julian": "Julian",
    "Sam": "Sam",
}


def get_sheets_service():
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
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
