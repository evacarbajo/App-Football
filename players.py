import streamlit as st
import pandas as pd
import data_loader as dl
from googletrans import Translator
import graph as gp
import graph_st as gpst
import sqlite3


def main():
    
    col1, col2 = st.columns(2)
    

    with col1: 
        #FILTRAR JUGADORES CON TEXTO
        search_player = st.text_input("Escribe letras para filtrar jugadores")

    # FILTRAR LA LISTA DE JUGADORES SEGÚN EL TEXTO INTRODUCIDO
    players_filtered = dl.load_data(
        f"""
        SELECT name, player_id FROM football.`gold-football-data`.players_gold
        WHERE LOWER(name) LIKE LOWER('%{search_player}%')
        ORDER BY name
        """
    )

    if players_filtered.empty:
        with col2:
            player_sel = st.selectbox("Selecciona un jugador", ["No hay resultados"])
    else:
        players_filtered = players_filtered["name"].unique()

        with col2:
            #SELECTBOX CON JUGADORES FILTRADOS
            player_sel = st.selectbox("Selecciona un jugador", players_filtered)

        #JUGADOR
        player = dl.load_data(
            f"SELECT * FROM football.`gold-football-data`.players_gold WHERE name = '{player_sel}'"
        ).iloc[0]

        #FICHA PERSONAL DEL JUGADOR
        st.subheader("**Ficha personal del jugador:**")

        col3, col4 = st.columns([0.2,0.8], border=True)

        with col3:
            #Foto
            st.write("\n")
            st.image(player["image_url"])

        with col4:
            #Nombre
            st.write(f"**Nombre:**  {player['name']}")

            #Fecha de nacimiento y años 
            date = pd.to_datetime(player['date_of_birth'])
            today = pd.Timestamp('today')
            age = today.year - date.year - (
                (today.month, today.day) < (date.month, date.day)
            )
            date = date.strftime("%d/%m/%Y")
            st.write(f"**Fecha de nacimiento:**  {date} ({age} años)")

            #Pais de nacimiento
            translator = Translator()
            trad = translator.translate(player["country_of_birth"], src="en", dest="es")
            st.write("**Pais de nacimiento:**", trad.text)

            #Altura
            player["height_in_cm"] = pd.to_numeric(player["height_in_cm"], errors="coerce")
            st.write(f"**Altura:**  {player['height_in_cm']/100} m")
            st.write(f"**Club actual:**  {player['current_club_name']}")


            # Diccionario traduccion posiciones
            pos_translate = {
                "Goalkeeper": "Portero",
                "Left-Back": "Lateral izquierdo",
                "Centre-Back": "Defensa central",
                "Right-Back": "Lateral derecho",
                "Midfield": "Centrocampista",
                "Attacking Midfield": "Mediapunta",
                "Central Midfield": "Mediocentro",
                "Right Midfield": "Centrocampista derecho",
                "Left Midfield": "Centrocampista izquierdo",
                "Defensive Midfield": "Mediocentro defensivo",
                "Centre-Forward": "Delantero centro",
                "Second Striker": "Segundo delantero",
                "Right Winger": "Extremo derecho",
                "Left Winger": "Extremo izquierdo"

                }

            #Posicion
            pos_es = pos_translate.get(player['sub_position'], player['sub_position'])
            st.write(f"**Posición:**  {pos_es}")

        

        player_id = player["player_id"]


        #VALOR DE MERCADO
        st.subheader("Evolución del valor de mercado:")
        players_valuation_filtered = dl.load_data(
            f"SELECT date, market_value_in_eur FROM football.`gold-football-data`.player_valuations_gold WHERE player_id = {player_id}"
        )
        players_valuation_filtered["date"] = pd.to_datetime(players_valuation_filtered["date"]).dt.date
        container_market_value = st.container(border=True)
        container_market_value.line_chart(players_valuation_filtered, 
                                        x= "date", y="market_value_in_eur",
                                        x_label= "Fecha", y_label="Valor de mercado(€)")

        #FILTRAR TRASPASOS DE ESE JUGADOR
        st.subheader("Trayectoria:")
        transfers_filtered = dl.load_data(
            f"""
            SELECT *
            FROM football.`gold-football-data`.transfers_gold
            WHERE player_id = {player_id}
            """
        )
        if transfers_filtered.empty :
            st.write("No hay datos sobre la trayectoria del jugador")
        else:
            #st.dataframe(transfers_filtered[["transfer_season","from_club_name", "to_club_name", "transfer_fee"]])
            gp.graph_transfers(transfers_filtered)
            gpst.graph_transfers(transfers_filtered)
            

        #RENDIMIENTO 
        st.subheader("Rendimiento:")

        appearances_filtered = dl.load_data(f"SELECT * FROM football.`gold-football-data`.appearances_gold WHERE player_id = {player_id}")

        #FILTRAR POR AÑOS
        season_options = dl.load_data("SELECT DISTINCT season FROM football.`gold-football-data`.appearances_gold WHERE season IS NOT NULL ORDER BY season")["season"].tolist()
        season_options = ["Todas"] + season_options
        season_sel = st.selectbox("Selecciona temporada", season_options, key="player_season")
        if season_sel != "Todas":
            appearances_filtered = dl.load_data(
                f"""
                SELECT *
                FROM football.`gold-football-data`.appearances_gold 
                WHERE player_id = {player_id}
                AND season = '{season_sel}'
                """
            )
            

        col1, col2, col3, col4 = st.columns(4, border=True)
        

        #GOLES
        total_goals = appearances_filtered["goals"].sum()
        with col3:
            st.metric(f"**Goles totales:**", total_goals)

        #ASISTENCIAS
        total_assists = appearances_filtered["assists"].sum()
        with col4:
            st.metric(f"**Asistencias totales:**", total_assists)

        #PARTIDOS
        games = appearances_filtered["games_played"].sum()
        with col1:  
            st.metric(f"**Partidos jugados:**", games)

        #MEDIA DE MINUTOS POR PARTIDO
        games_minutes = appearances_filtered["minutes_played"].sum() // games
        with col2: 
                st.metric(f"**Media de minutos por partido:**", games_minutes)

