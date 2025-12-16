import streamlit as st
import data_loader as dl
import field as fd

def main():


    if "myclub_id" in st.session_state and st.session_state.myclub_id:
        my_club = st.session_state.myclub_id
   
        col1, col2 = st.columns(2)

        #FILTRAR POR TEMPORADA

        season_options =dl.load_data(f"""SELECT DISTINCT season FROM football.`gold-football-data`.games_gold 
                                            WHERE (home_club_id = '{my_club}' OR away_club_id = '{my_club}')
                                            ORDER BY season DESC""")
        with col1:
            season_sel = st.selectbox("Selecciona temporada", season_options, key="game_season")
        #games_filtered = games_filtered[games_filtered["season"] == season_sel]
        

        # SELECTOR DE COMPETICIÓN FILTRADO POR MAJOR COMPETITIONS
        major_competitions = dl.load_data(f"""SELECT competition_id, competition_name FROM football.`gold-football-data`.games_gold 
                                            WHERE (home_club_id = '{my_club}' OR away_club_id = '{my_club}')
                                            AND season = {season_sel}""")

        with col2:
            comp_sel = st.selectbox("Selecciona una competición", major_competitions["competition_name"].unique())
        comp_id = major_competitions.loc[major_competitions["competition_name"] == comp_sel, "competition_id"].values[0]

        
        games_filtered = dl.load_data(f"""SELECT * FROM football.`gold-football-data`.games_gold 
                                            WHERE competition_id = '{comp_id}'
                                            AND (home_club_id = '{my_club}' OR away_club_id = '{my_club}')
                                            AND season = {season_sel}""")

        
        #NUMERO DE PARTIDOS POR COMPETICIÓN 
        st.write(f"**Número de partidos totales en {comp_sel} en {season_sel}:** {len(games_filtered)}")

        #FILTRAR POR JORNADA
        #round_option = games_filtered["round"].dropna().unique().tolist()
        #round_sorted = sorted(round_option, key=lambda x: int(x.split(".")[0]))
        #round_sel = st.selectbox("**Selecciona jornada**", round_sorted)
        #games_filtered = games_filtered[games_filtered["round"] == round_sel]
        #games_filtered["round"] = ( games_filtered["round"].str.extract(r"(\d+)").astype(int))


        games_filtered = games_filtered.sort_values(by="date").reset_index(drop=True)


        #Mostrar partidos 
        selected_game = st.dataframe(
            games_filtered[["round", "date", "home_club_name", "away_club_name" ,"aggregate"]],
            use_container_width=True,
            hide_index=True,
            on_select="rerun",  # para seleccionar fila
            selection_mode="single-row",    
            column_config={
                "round": "Jornada",
                "date": "Fecha",
                "home_club_name": "Equipo local",
                "away_club_name": "Equipo visitante",
                "aggregate": "Resultado"
            },
        )
        


        #ALINEACIÓN
        if selected_game["selection"]["rows"]:
            row_idx = selected_game["selection"]["rows"][0]
            game_id = games_filtered.iloc[row_idx]["game_id"]
        
            

            

            #FILTRAR POR EQUIPO
            games_lineup_filtered = dl.load_data(f"""
                    SELECT player_name, type, position, number, club_id, club_name
                    FROM football.`gold-football-data`.game_lineups_gold
                    WHERE game_id = {game_id}        
                    """)
            if not games_lineup_filtered.empty:
                clubs_names = games_lineup_filtered["club_name"].unique().tolist()
                team_sel = st.selectbox("Selecciona un equipo para mostrar alineación", clubs_names)
                games_lineup_filtered = games_lineup_filtered[games_lineup_filtered["club_name"] == team_sel]
                
                #Alineación
                st.subheader("Alineación del partido:")
                st.dataframe(games_lineup_filtered[["player_name", "type", "position", "number"]],
                    hide_index=True,
                    column_config={
                        "player_name": "Nombre",
                        "type": "Titularidad", 
                        "position": "Posición", 
                        "number": "Dorsal"
                    }
                    )

                #Estructura alineación
                game = games_filtered.iloc[row_idx] 
                if team_sel == game["home_club_name"]:       
                    st.write(f"**Estructura alineación:** {game['home_club_formation']}")
                else:
                    st.write(f"**Estructura alineación:** {game['away_club_formation']}")

                #Dibujar campo con jugadores
                fd.draw_field(games_lineup_filtered)
            else:
                
                st.subheader("Alineación del partido:")
                st.write("No hay información de la alineación de este partido")

            
    else:
        st.warning("No has seleccionado ningún club todavía. Elige tu club y pulsa sobre el botón de 'Guardar equipo'")

            
            