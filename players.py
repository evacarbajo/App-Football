import streamlit as st
import pandas as pd
import data_loader as dl
from googletrans import Translator
import graph as gp


def main():
    
    col1, col2 = st.columns(2)
    

    with col1: 
        #FILTRAR JUGADORES CON TEXTO
        search_player = st.text_input("Escribe letras para filtrar jugadores")

    # FILTRAR LA LISTA DE JUGADORES SEGÚN EL TEXTO INTRODUCIDO
    players_filtered = dl.players[
        dl.players["name"].str.contains(search_player, case=False, na=False)
    ]["name"].sort_values().unique()

    with col2:
        #SELECTBOX CON JUGADORES FILTRADOS
        player_sel = st.selectbox("Selecciona un jugador", players_filtered)

    #FILTRAR JUGADOR
    players_filtered = dl.players[dl.players["name"] == player_sel]

    
    #JUGADOR
    player = players_filtered.iloc[0]

    #FICHA PERSONAL DEL JUGADOR
    st.write("**Ficha personal del jugador:**")

    col3, col4 = st.columns(2)

    with col3:
        #Foto
        st.image(player["image_url"],width=175)

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

    

    player_id = players_filtered["player_id"]

    #VALOR DE MERCADO
    st.write("**Evolución del valor de mercado:**")
    players_valuation_filtered = dl.player_valuations[dl.player_valuations["player_id"].isin(player_id)]
    players_valuation_filtered["date"] = pd.to_datetime(players_valuation_filtered["date"]).dt.date
    #st.dataframe(players_valuation_filtered[["date", "market_value_in_eur"]])
    st.line_chart(players_valuation_filtered, x= "date", y="market_value_in_eur")

    #FILTRAR TRASPASOS DE ESE JUGADOR
    st.write("**Trayectoria:**")
    transfers_filtered = dl.transfers[dl.transfers["player_id"].isin(player_id)]
    if transfers_filtered.empty :
        st.write("No hay datos sobre la trayectoria del jugador")
    else:
        st.dataframe(transfers_filtered[["transfer_season","from_club_name", "to_club_name", "transfer_fee"]])
        gp.graph_transfers(transfers_filtered)
        



    appearances_filtered = dl.appearances[dl.appearances["player_id"].isin(player_id)]
    game_events_filtered = dl.game_events[dl.game_events["player_id"].isin(player_id)]

    #FILTRAR POR AÑOS
    season_options = sorted(dl.games["season"].dropna().unique().tolist())
    season_options = ["Todas"] + season_options
    season_sel = st.selectbox("Selecciona temporada", season_options, key="player_season")
    if season_sel == "Todas":
        games_filtered = dl.games.copy()
        
    else:
        games_filtered = dl.games[dl.games["season"] == season_sel]
        appearances_filtered = pd.merge(
            games_filtered,
            appearances_filtered,
            left_on="game_id",
            right_on="game_id",
        )
        game_events_filtered = pd.merge(
            games_filtered,
            game_events_filtered,
            left_on="game_id",
            right_on="game_id",
        )
        

    col1, col2, col3 = st.columns(3)

    #GOLES
    #Opcion 1
    total_goals = appearances_filtered["goals"].sum()
    #st.write(f"Goles totales: {total_goals}")
    with col1:
        st.metric(f"Goles totales:", total_goals)

    #Opción 2
    #game_goals = game_events_filtered[game_events_filtered["type"]== "Goals"]
    #total_goals = len(game_goals)
    #st.write(f"Goles totales: {total_goals}")

    #ASISTENCIAS
    total_assists = appearances_filtered["assists"].sum()
    #st.write(f"Asistencias totales: {total_assists}")
    with col2:
        st.metric(f"Asistencias totales:", total_assists)

    #GOLES POR MINUTO
    total_minutes = appearances_filtered["minutes_played"].sum()
    #st.write(f"Minutos totales: {total_minutes}")
    with col3: 
        st.metric(f"Minutos totales:", total_minutes)
    goals_minutes = total_goals/total_minutes
    #st.write(f"Goles por minuto: {round(goals_minutes, 4)}")

   

   
   
   












