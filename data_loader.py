import streamlit as st
import pandas as pd

#FUNCIÓN PARA CARGAR Y ALMACENAR UN ARCHIVO CSV
@st.cache_data
def load_data(file_path):
    df = pd.read_csv(file_path)
    return df



players = load_data('/Users/evacarbajo/data/players.csv')
competitions = load_data('/Users/evacarbajo/data/competitions.csv')
clubs = load_data('/Users/evacarbajo/data/clubs.csv')
appearances = load_data('/Users/evacarbajo/data/appearances.csv')
club_games = load_data('/Users/evacarbajo/data/club_games.csv')
game_events = load_data('/Users/evacarbajo/data/game_events.csv')
game_lineups = load_data('/Users/evacarbajo/data/game_lineups.csv')
player_valuations = load_data('/Users/evacarbajo/data/player_valuations.csv')
transfers = load_data('/Users/evacarbajo/data/transfers.csv')
games = load_data('/Users/evacarbajo/data/games.csv')