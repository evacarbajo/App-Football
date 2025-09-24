import streamlit as st
import pandas as pd
import data_loader as dl
from googletrans import Translator

def main():
    appearances_filtered = dl.appearances.copy()
    game_events_filtered = dl.game_events.copy()

    player_valuations_year = dl.player_valuations.copy()
    player_valuations_year["date"] = pd.to_datetime(player_valuations_year["date"])
    
    #AÑADE COLUMNA SEASON SOLO CON EL PRIMER AÑO DE LA TEMPORADA
    player_valuations_year["season"] = player_valuations_year["date"].apply(
        lambda x: f"{x.year}" if x.month >= 8 else f"{x.year-1}"
    )

    #AÑADE COLUMNA SEASON AÑO1/AÑO2
    #-------------------------------
    #player_valuations_year["season"] = player_valuations_year["date"].apply(
    #    lambda x: f"{x.year}-{x.year+1}" if x.month >= 8 else f"{x.year-1}-{x.year}")
    #-------------------------------

    col1,col2 = st.columns(2)

    with col1: 
        #SELECCIONAR MÉTRICA DEL RANKING
        metric_option = st.selectbox(
            "Selecciona la métrica para el ranking:",
            ["Goles", "Asistencias", "Minutos jugados","Valor de mercado", "Jugadores jóvenes"]
        )

    # DICCIONARIO DE COLUMNAS Y TÍTULOS 
    metric_map = {
        "Goles": ("goals", "Top 10 goleadores"),
        "Asistencias": ("assists", "Top 10 asistentes"),
        "Minutos jugados": ("minutes_played", "Top 10 minutos jugados"),
        "Valor de mercado": ("market_value", "Top 10 jugadores con mayor valor de mercado"),
        "Jugadores jóvenes": ("players_age", "Top 10 jugadores mas jovenes" )
    }

    ranking_sel, title = metric_map[metric_option]



    if ranking_sel == "players_age":
       
     #RANKING JUGADORES MÁS JOVENES
        players_age = dl.players.copy()
        players_age["date_of_birth"] = pd.to_datetime(players_age["date_of_birth"], errors="coerce")
        # Fecha actual
        today = pd.to_datetime("today")
        # Calcular edad
        players_age["age"] = players_age["date_of_birth"].apply(
            lambda x: today.year - x.year - ((today.month, today.day) < (x.month, x.day))
        )
        players_age["date_of_birth"] = players_age["date_of_birth"].dt.date
        ranking_age = (
            players_age
            .reset_index(drop=True)
            .sort_values(by="date_of_birth", ascending=False)
            .head(10)         
        )
        st.subheader(title)
        st.dataframe(ranking_age[["name", "age"]], hide_index=True )
        
    
    else:

        #FILTRO DE TEMPORADA
        season_options = ["Todas"] + sorted(set(map(str, dl.games["season"].dropna().tolist() +
                                                player_valuations_year["season"].dropna().tolist())))

        with col2:
            season_sel = st.selectbox("Selecciona temporada:", season_options, key="ranking_season")
        
        if season_sel == "Todas":
            
            games_filtered = dl.games.copy()
            
            valuations_filtered = player_valuations_year.copy()
            valuations_filtered = pd.merge(
                valuations_filtered[["player_id", "market_value_in_eur"]],
                dl.players[["player_id", "name"]],
                left_on="player_id",
                right_on="player_id",
            )
            
        else:
            
            games_filtered = dl.games[dl.games["season"] == int(season_sel)]
            appearances_filtered = pd.merge(
                games_filtered,
                dl.appearances,
                left_on="game_id",
                right_on="game_id",
            )
            
            

            #Valor de mercado
            valuations_filtered = player_valuations_year[player_valuations_year["season"] == season_sel]
            valuations_filtered = pd.merge(
                valuations_filtered[["player_id", "market_value_in_eur"]],
                dl.players[["player_id", "name"]],
                left_on="player_id",
                right_on="player_id",
            )
            
        #RESTO DE RANKINGS 
        if ranking_sel == "market_value":
            
            #RANKING VALOR DE MERCADO
            ranking_marketvalue = (
            valuations_filtered[["name", "market_value_in_eur"]]
            .groupby("name", as_index=False)  # agrupa por jugador
            .max()  
            .reset_index(drop=True)
            .sort_values(by="market_value_in_eur", ascending=False)
            .head(10)   
            )
            st.subheader(title)
            st.dataframe(ranking_marketvalue, hide_index=True)
        else:
            #RANKINGS GOLES, ASISTENCIAS, MINUTOS
            ranking = (
                appearances_filtered.groupby("player_name")[ranking_sel].sum()
                .reset_index()
                .sort_values(by=ranking_sel, ascending=False)
                .head(10)
            )

            st.subheader(title)
            st.dataframe(ranking, hide_index=True)


        

    
        

        

    
        


    
   




    """
    #RANKINGS GOLES 
    goals_ranking = (
        appearances_filtered.groupby("player_name")["goals"].sum()
        .reset_index()
        .sort_values(by="goals", ascending=False)
        .head(10)
    )

    st.subheader("Top 10 goleadores")
    st.dataframe(goals_ranking)


    #RANKINGS ASISTENCIAS
    assists_ranking = (
        appearances_filtered.groupby("player_name")["assists"].sum()
        .reset_index()
        .sort_values(by="assists", ascending=False)
        .head(10)
    )

    st.subheader("Top 10 asistencias")
    st.dataframe(assists_ranking)

    #RANKINGS MINUTOS
    minutes_ranking = (
        appearances_filtered.groupby("player_name")["minutes_played"].sum()
        .reset_index()
        .sort_values(by="minutes_played", ascending=False)
        .head(10)
    )

    st.subheader(title)
    st.dataframe(minutes_ranking)
    """






