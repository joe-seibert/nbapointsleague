import numpy as np
import pandas as pd
import yaml
import os

from nba_api.stats.endpoints.commonallplayers import CommonAllPlayers
from nba_api.stats.endpoints import leaguedashplayerstats

all_players = CommonAllPlayers().common_all_players.get_data_frame()
player_stats = leaguedashplayerstats.LeagueDashPlayerStats(season_type_all_star='Playoffs').get_data_frames()[0]

dp_fn = './drafted_players_2024.yml'

with open(dp_fn) as file:
    league = yaml.load(file, Loader=yaml.FullLoader)


data = []
pts = 0
gps = 0
for n in league:
    pts = 0
    gps = 0
#     print(n)
    for p in league[n]:
        try:
            pname, pt, gp = player_stats[['PLAYER_NAME','PTS', 'GP']].query(f'PLAYER_NAME=="{p}"').to_numpy()[0]
        except IndexError:
            pname = p
            pt = 0
            gp = 0
#         print(pname, pt, gp)
        pts+=pt
        gps+=gp
    
    data.append(np.array([pts,gps,pts/gps]))
#     print(f'points: {pts}')
#     print(f'gps: {gps}')
#     print('\n')
data = np.array(data)

cols = np.array(['Points', 'Games Played', 'PPG'])

team_key = np.array([n for n in league])

df = pd.DataFrame(data=data,columns=cols,index=team_key)

df.to_csv('./pointsleague_2024.csv')
