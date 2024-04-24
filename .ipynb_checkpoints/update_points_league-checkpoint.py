from __future__ import print_function

# basic imports
import numpy as np
import pandas as pd

# nba-api imports
from nba_api.stats.endpoints import leaguedashplayerstats

# google sheets api imports
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# specifying which sheet to use
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
spreadsheet_id = '1KHFofiupqYTIbuT8xL8atOuUjOOUM7mTbZzqOVtV2nw'

# taken from Google Sheets API instructions
creds = None
# The file token.pickle stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)
        
service = build('sheets', 'v4', credentials=creds)
sheet = service.spreadsheets()

player_stats = leaguedashplayerstats.LeagueDashPlayerStats().get_data_frames()[0]

# grab player names from the sheet 
# then update the total points each player has scored
# then push updated scores to the sheet
def update_player_points(sheet_name):
    sheet_range = sheet_name + '!' + 'A2:A17'
    new_sheet_range = sheet_name + '!' + 'B2:B17'
    
    player_result = sheet.values().get(spreadsheetId=spreadsheet_id,
                            range=sheet_range).execute()
    
    player_names = player_result.get('values',[])
    
    player_names = np.asarray(player_names)
    
    player_names = player_names.flatten()
    
    new_points = []
    
    
    for p in player_names:
        try:
            new_points.append([str(player_stats.query(f'PLAYER_NAME == "{p}"')['PTS'].iloc[0])])
        except IndexError:
            f'No points scored by {p}, adding a 0.'
            new_points.append([str(0)])

    values = new_points
    data = [
        {
            'range': new_sheet_range,
            'values': values
        },
        # Additional ranges to update ...
    ]
    body = {
        'valueInputOption': 'USER_ENTERED',
        'data': data
    }
    result = service.spreadsheets().values().batchUpdate(
        spreadsheetId=spreadsheet_id, body=body).execute()

def update_games_played(sheet_name):
    sheet_range = sheet_name + '!' + 'A2:A17'
    new_sheet_range = sheet_name + '!' + 'C2:C17'
    
    player_result = sheet.values().get(spreadsheetId=spreadsheet_id,
                            range=sheet_range).execute()
    
    player_names = player_result.get('values',[])
    
    player_names = np.asarray(player_names)
    
    player_names = player_names.flatten()
    
    games_played = []
    
    
    for p in player_names:
        try:
            games_played.append([str(player_stats.query(f'PLAYER_NAME == "{p}"')['GP'].iloc[0])])
        except IndexError:
            f'No points scored by {p}, adding a 0.'
            games_played.append([str(0)])

    values = games_played
    data = [
        {
            'range': new_sheet_range,
            'values': values
        },
        # Additional ranges to update ...
    ]
    body = {
        'valueInputOption': 'USER_ENTERED',
        'data': data
    }
    result = service.spreadsheets().values().batchUpdate(
        spreadsheetId=spreadsheet_id, body=body).execute()



# Update each sheet iteratively
sheet_names = ['Julian','Drew','Jono','Sam','Joe','Con']

for s in sheet_names:
    update_player_points(s)
    update_games_played(s)

