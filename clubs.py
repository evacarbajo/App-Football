import streamlit as st
import pandas as pd
import data_loader as dl


def main():
    
    col1, col2 = st.columns(2)

    with col1:
        #FILTRAR CLUBS CON TEXTO
        search_player = st.text_input("Escribe letras para filtrar equipos")

    # FILTRAR LA LISTA DE CLUBS SEGÚN EL TEXTO INTRODUCIDO
    clubs_filtered = dl.clubs[
        dl.clubs["name"].str.contains(search_player, case=False, na=False)
    ]["name"].sort_values().unique()

    with col2:
        #SELECTBOX CON CLUBS FILTRADOS
        club_sel = st.selectbox("Selecciona un jugador", clubs_filtered)
    
    clubs_filtered = dl.clubs[dl.clubs["name"] == club_sel]

    #COMPETICIÓN DOMÉSTICA
    competition_filtered = dl.competitions[dl.competitions["competition_id"] == clubs_filtered["domestic_competition_id"].iloc[0]]
    competition_name = competition_filtered['name'].iloc[0]
    st.write(f"**Competición doméstica:** {competition_name}")

    #NOMBRE DEL ESTADIO Y ASIENTOS
    stadium_name = clubs_filtered["stadium_name"].iloc[0]
    stadium_seats = clubs_filtered["stadium_seats"].iloc[0]
    st.write(f"**Estadio:** {stadium_name} ({stadium_seats} asientos)")
    
    #TAMAÑO DE LA PLANTILLA
    squad_size = clubs_filtered["squad_size"].iloc[0]
    st.write(f"**Tamaño de la plantilla:** {squad_size}")

    #FILTRAR PARTIDOS DEL CLUB
    club_id = clubs_filtered["club_id"].iloc[0]
    club_games_filtered = dl.club_games[dl.club_games["club_id"] == club_id]

    games_filtered = pd.merge(
                club_games_filtered,
                dl.games,
                left_on="game_id",
                right_on="game_id",
            )
    
    #FILTRAR POR TEMPORADA
    season_sel = st.selectbox("Selecciona una temporada:", games_filtered["season"].unique(), key="clubs_season")
    games_filtered = games_filtered[games_filtered["season"] == season_sel]

    #FILTRAR POR COMPETICIÓN 
    comp_filtered = dl.competitions[dl.competitions["competition_id"].isin(games_filtered["competition_id"])]
    comp_sel = st.selectbox("Selecciona una competición:", comp_filtered["name"].unique(), key="clubs_comp")

    comp = comp_filtered[comp_filtered["name"] == comp_sel]
    
    games_filtered = games_filtered[games_filtered["competition_id"] == comp["competition_id"].iloc[0]]


    #PARTIDOS JUGADOS
    total_games = len(games_filtered)
    st.write(f"Partidos jugados: {total_games}")
    
    #PARTIDOS TOTALES GANADOS
    win_games = games_filtered["is_win"].sum()
    st.write(f"Partidos ganados: {win_games}")

    #PARTIDOS GANADOS - LOCAL
    games_home = games_filtered[games_filtered["hosting"] == "Home"]
    win_games_home = games_home["is_win"].sum()
    st.write(f"Partidos ganados como local: {win_games_home}")
    
    #PARTIDOS GANADOS - VISITANTE
    games_away = games_filtered[games_filtered["hosting"] == "Away"]
    win_games_away = games_away["is_win"].sum()
    st.write(f"Partidos ganados como local: {win_games_away}")

    #MOSTRAR COMO GRAFO CIRCULAR

    #AÑADIR TODOS A SELECTBOX


    

    
    
    


                           
    st.dataframe(games_filtered)

   