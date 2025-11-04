import streamlit as st
import pandas as pd
import data_loader as dl
from googletrans import Translator
import graph as gp
import graph_st as gpst
import sqlite3


def main():


    
    
    col1, col2 = st.columns(2)
    
    if "myclub_id" in st.session_state and st.session_state.myclub_id:
        my_club = st.session_state.myclub_id

        # FILTRAR LA LISTA DE JUGADORES SEGÚN SU EQUIPO 
        players_filtered = dl.load_data(
            f"""
            SELECT * FROM football.`gold-football-data`.players_gold
            WHERE current_club_id == {my_club}
            AND last_season == 2024
            ORDER BY name
            """
        )
        

        # Diccionario traduccion posiciones
        pos_translate = {
                "Goalkeeper": "Portero",
                "Defender": "Defensa",
                "Attack": "Delantero",
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

        positions = ["Goalkeeper", "Defender", "Midfield", "Attack"]
        
        cols = st.columns(len(positions))

        players_sel_list = []


        for i, pos in enumerate(positions):
            with cols[i]:
                pos_es = pos_translate.get(pos, pos)
                
                st.markdown(f"### {pos_es}s:")
                
                players_pos = players_filtered[players_filtered["position"] == pos]
                players_pos["sub_position_es"] = players_pos["sub_position"].map(pos_translate).fillna(players_pos["sub_position"])

                selected = st.dataframe(
                    players_pos[["image_url", "name"]],
                    column_config={
                        "image_url": st.column_config.ImageColumn("Foto", width=50),
                        "name": "Nombre",
                        "sub_position": "Posición secundaria",
                    },
                    hide_index=True,
                    use_container_width=True,
                    on_select="rerun",
                    selection_mode="multi-row"
                )

                # Capturar selección
                if selected["selection"]["rows"]:
                    for idx in selected["selection"]["rows"]:
                        players_sel_list.append(players_pos.iloc[idx])

        num_sel = len(players_sel_list)


        if num_sel== 1:
            #Mostrar ficha del jugador
            player = players_sel_list[0]
            st.markdown("---")

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

                #Posicion
                pos_es = pos_translate.get(player['sub_position'], player['sub_position'])
                st.write(f"**Posición:**  {pos_es}")

            

            player_id = player["player_id"]

            appearances_filtered = dl.load_data(f"""SELECT *
                                                FROM football.`gold-football-data`.appearances_gold
                                                WHERE player_id = {player_id}
                                                """)
            
            #RENDIMIENTO 
            st.subheader("Rendimiento:")

            #Filtrar por años
            season_options = appearances_filtered["season"].unique().tolist()
            #season_options = ["Todas"] + season_options
            season_sel = st.selectbox("Selecciona temporada", season_options, index=len(season_options) - 1, key="player_season")
            #if season_sel != "Todas":
            appearances_filtered = dl.load_data(
                    f"""
                    SELECT *
                    FROM football.`gold-football-data`.appearances_gold
                    WHERE player_id = {player_id}
                    AND season = '{season_sel}'
                    """
            )
            

            col1, col2, col3, col4 = st.columns(4, border=True)
            #Goles
            total_goals = appearances_filtered["goals"]
            with col3:
                st.metric(f"**Goles totales:**", total_goals)
            #Asistencias
            total_assists = appearances_filtered["assists"]
            with col4:
                st.metric(f"**Asistencias totales:**", total_assists)
            #Partidos 
            games = appearances_filtered["games_played"]
            with col1:  
                st.metric(f"**Partidos jugados:**", games)
            #Media de minutos por partido
            games_minutes = appearances_filtered["minutes_played"] // games
            with col2: 
                st.metric(f"**Media de minutos por partido:**", games_minutes)
            #goals_minutes = total_goals/total_minutes
        

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
                st.dataframe(
                            transfers_filtered[["transfer_season","from_club_name", "to_club_name", "transfer_fee"]],
                            column_config={
                                 "transfer_season": "Temporada de traspaso",
                                 "from_club_name": "Club origen",
                                 "to_club_name": "Club destino",
                                 "transfer_fee": "Valor del traspaso"
                            })
                



           
                

            
        elif 2 <= num_sel <= 4:
            st.markdown("---")
            st.markdown("##  Comparativa de jugadores")

            


            #FILTRAR POR AÑOS
            appearances_filtered = dl.load_data(f"""SELECT *
                                                FROM football.`gold-football-data`.appearances_gold
                                                """)
            season_options = sorted(appearances_filtered["season"].unique().tolist())
            season_options = ["Todas"] + season_options
            season_sel = st.selectbox("Selecciona temporada", season_options, index=len(season_options) - 1, key="player_season")
            
            cols_c = st.columns(num_sel, border=True)

            for i, player in enumerate(players_sel_list):
                with cols_c[i]:
                    
                    player_id = player["player_id"]
                    player_name = player["name"]

                    
                    
                    if season_sel != "Todas":
                        appearances_filtered = dl.load_data(
                            f"""
                            SELECT *
                            FROM football.`gold-football-data`.appearances_gold
                            WHERE player_id = {player_id}
                            AND season = '{season_sel}'
                            """
                        )
                    else:
                        appearances_filtered = dl.load_data(
                            f"""
                            SELECT *
                            FROM football.`gold-football-data`.appearances_gold
                            WHERE player_id = {player_id}

                            """
                        )
                    
                    #NOMBRE
                    st.subheader(f"{player_name}")
                    st.image(player["image_url"])

                    if not appearances_filtered.empty:

                        #GOLES
                        total_goals = appearances_filtered["goals"]
                        st.metric(f"**Goles totales:**", total_goals)

                        #ASISTENCIAS
                        total_assists = appearances_filtered["assists"]
                        st.metric(f"**Asistencias totales:**", total_assists)

                        #PARTIDOS 
                        games = appearances_filtered["games_played"]
                        st.metric(f"**Partidos jugados:**", games)
                        
                        

                        #MEDIA DE MINUTOS POR PARTIDO
                        games_minutes = appearances_filtered["minutes_played"] // games
                        st.metric(f"**Media de minutos por partido:**", games_minutes)
                        #goals_minutes = total_goals/total_minutes
                    
                    else:
                        st.warning("No hay datos sobre el jugador")



        
        elif num_sel > 4:
            st.warning("Demasiados jugadores seleccionados. Selecciona entre 1 y 4 jugadores.")
         
        else:
            st.info("Selecciona uno o varios jugadores para ver su información o compararlos.")
   
    else:
        st.warning("No has seleccionado ningún club todavía. Elige tu club y pulsa sobre el botón de 'Guardar equipo'")

