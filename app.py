import numpy as np
import pandas as pd
import streamlit as st



def get_data():
    path = r'./pointsleague_2024.csv'
    return pd.read_csv(path,index_col=0)

def get_full_data():
    path = r'./full_points_table_2024.csv'
    return pd.read_csv(path,index_col=0)

df = get_data()

big_df = get_full_data()

# st.write(df)

st.table(df.sort_values('Points',ascending=False))

teams = big_df['Team'].drop_duplicates()
option = st.selectbox(
   "Select team for details",
   ("Andrew","Jono","Connor","Joe","Julian","Sam")
#    index=None,
#    placeholder="Select team...",
)

team_data = big_df.query(f'Team=="{option}"')[['Player','Total Points', 'Games Played']]

st.table(team_data)

# season_choice = st.multiselect('Select team:',seasons, seasons)
# team_choice = st.multiselect('Select team:', teams, teams)
# # team_data = df[team_choice]
# team_data = df[df['Season'].str.contains('|'.join(season_choice), na=False)][team_choice]

# option = st.selectbox(
#    "How would you like to be contacted?",
#    ("Email", "Home phone", "Mobile phone"),
#    index=None,
#    placeholder="Select contact method...",
# )