import streamlit as st
import pandas as pd
import data_loader as dl
from googletrans import Translator

def main():
    appearances_filtered = dl.load_data("SELECT * FROM football.`gold-football-data`.appearances_gold")
    

    #player_valuations_year = dl.load_data("SELECT player_id, market_value_in_eur, season FROM football.`gold-football-data`.player_valuations_gold")
    

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
        players_age = dl.load_data("SELECT player_id, name, date_of_birth, age FROM football.`gold-football-data`.players_gold")
        ranking_age = (
            players_age
            .reset_index(drop=True)
            .sort_values(by="date_of_birth", ascending=False)
            .head(10)    
            .rename(columns={
                "name": "Nombre",
                "age": "Edad"
            })     
        )
        st.subheader(title)
        st.dataframe(ranking_age[["Nombre", "Edad"]], hide_index=True )
        
    
    else:

        #FILTRO DE TEMPORADA
        
        if ranking_sel == "market_value":
            seasons = dl.load_data("""
                        SELECT DISTINCT season
                        FROM football.`gold-football-data`.player_valuations_gold
                        WHERE season IS NOT NULL
                        ORDER BY season
                        """)
            season_options = ["Todas"] + seasons["season"].astype(str).tolist()
        else:

    
            seasons = dl.load_data("""
                        SELECT DISTINCT season
                        FROM football.`gold-football-data`.games_gold
                        WHERE season IS NOT NULL
                        ORDER BY season
                        """)
            season_options = ["Todas"] + seasons["season"].astype(str).tolist()
        

        with col2:
            season_sel = st.selectbox("Selecciona temporada:", season_options, key="ranking_season")
        
        if season_sel == "Todas":
            
            valuations_filtered = dl.load_data("""
                                                SELECT player_name,
                                                MAX(market_value_in_eur) AS market_value_in_eur
                                                FROM football.`gold-football-data`.player_valuations_gold
                                                GROUP BY player_name
                                                ORDER BY market_value_in_eur DESC
                                                LIMIT 10
                                                """)
            #valuations_filtered = player_valuations_year[["player_id", "market_value_in_eur"]]
        
            
        else:

            appearances_filtered = dl.load_data(f""" 
                    SELECT player_name, goals, assists, minutes_played, season
                    FROM football.`gold-football-data`.appearances_gold
                    WHERE season == {season_sel} 
                    """)
            

            #Valor de mercado
            #valuations_filtered = player_valuations_year[player_valuations_year["season"] == season_sel][["player_id", "market_value_in_eur"]]
            valuations_filtered = dl.load_data(f"""
                                                SELECT player_name,
                                                MAX(market_value_in_eur) AS market_value_in_eur
                                                FROM football.`gold-football-data`.player_valuations_gold
                                                WHERE season == {season_sel}
                                                GROUP BY player_name
                                                ORDER BY market_value_in_eur DESC
                                                LIMIT 10
                                                """)
         
            
            
        #RESTO DE RANKINGS 
        if ranking_sel == "market_value":
            
            #RANKING VALOR DE MERCADO
            ranking_marketvalue = (
            valuations_filtered[["player_name", "market_value_in_eur"]] 
            .reset_index(drop=True)  
            .rename(columns= {"player_name": "Nombre", "market_value_in_eur":"Valor de mercado(€)"})
            )
            st.subheader(title)
            st.dataframe(ranking_marketvalue, hide_index=True)
        else:
            #RANKINGS GOLES, ASISTENCIAS, MINUTOS
            ranking = (
                appearances_filtered[["player_name", ranking_sel]]
                .groupby("player_name", as_index=False)[[ranking_sel]].sum()
                .sort_values(by=ranking_sel, ascending=False)
                .head(10)
            )

            st.subheader(title)
            st.dataframe(
                ranking,
                hide_index=True,
                column_config={
                    "player_name" : "Nombre", 
                    "goals": "Goles", 
                    "assists": "Asistencias", 
                    "minutes_played": "Minutos jugados"
                }
                )


        

    
        

        

    
        


    
   




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






