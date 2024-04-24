import numpy as np
import pandas as pd
import streamlit as st



def get_data():
    path = r'./pointsleague_2024.csv'
    return pd.read_csv(path,index_col=0)

df = get_data()

# st.write(df)

st.table(df.sort_values('Points',ascending=False))

