import streamlit as st
import pandas as pd
import sqlite3

#FUNCIÓN PARA CARGAR Y ALMACENAR UN ARCHIVO CSV
#@st.cache_data
#def load_data_csv(file_path):
#   df = pd.read_csv(file_path)
#    return df

#CONEXION A a SQLite
@st.cache_resource
def get_connection():
    
    return sqlite3.connect('/Users/evacarbajo/football-data.db',check_same_thread=False) 

#EJECUTA CONSULTA SQL Y DEVUELVE DATAFRAME CACHEADO
@st.cache_data
def load_data(query):   
    conn = get_connection()
    return pd.read_sql_query(query, conn)



"""players = load_data_csv('/Users/evacarbajo/data/players.csv')
competitions = load_data_csv('/Users/evacarbajo/data/competitions.csv')
clubs = load_data_csv('/Users/evacarbajo/data/clubs.csv')
appearances = load_data_csv('/Users/evacarbajo/data/appearances.csv')
club_games = load_data_csv('/Users/evacarbajo/data/club_games.csv')
game_events = load_data_csv('/Users/evacarbajo/data/game_events.csv')
game_lineups = load_data_csv('/Users/evacarbajo/data/game_lineups.csv')
player_valuations = load_data_csv('/Users/evacarbajo/data/player_valuations.csv')
transfers = load_data_csv('/Users/evacarbajo/data/transfers.csv')
games = load_data_csv('/Users/evacarbajo/data/games.csv')"""