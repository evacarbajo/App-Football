import streamlit as st
import data_loader as dl
import field as fd

def main():
   
    col1, col2 = st.columns(2)

    # SELECTOR DE COMPETICIÓN FILTRADO POR MAJOR COMPETITIONS
    major_competitions = dl.competitions[dl.competitions["is_major_national_league"] == True]
    with col1:
        comp_sel = st.selectbox("Selecciona una competición", major_competitions["name"].unique())
    comp_id = major_competitions.loc[major_competitions["name"] == comp_sel, "competition_id"].values[0]

    games_filtered = dl.games[dl.games["competition_id"] == comp_id]

    #FILTRAR POR AÑOS
    season_options = sorted(dl.games["season"].dropna().unique().tolist())
    with col2:
        season_sel = st.selectbox("Selecciona temporada", season_options, key="game_season")
    games_filtered = games_filtered[games_filtered["season"] == season_sel]
    

    #NUMERO DE PARTIDOS POR COMPETICIÓN 
    st.write(f"**Número de partidos totales en {comp_sel} en {season_sel}:** {len(games_filtered)}")

    #FILTRAR POR JORNADA
    round_option = games_filtered["round"].dropna().unique().tolist()
    round_sorted = sorted(round_option, key=lambda x: int(x.split(".")[0]))
    round_sel = st.selectbox("**Selecciona jornada**", round_sorted)
    games_filtered = games_filtered[games_filtered["round"] == round_sel]


   
    
    selected_game = st.dataframe(
        games_filtered[["date", "home_club_name", "away_club_name" ,"aggregate"]].rename(columns={
        "date": "Fecha",
        "home_club_name": "Equipo local",
        "away_club_name": "Equipo visitante",
        "aggregate": "Resultado"}),
        use_container_width=True,
        hide_index=True,
        on_select="rerun",  # para seleccionar fila
        selection_mode="single-row",    
    )
    
    

    


    #ALINEACIÓN
    if selected_game["selection"]["rows"]:
        row_idx = selected_game["selection"]["rows"][0]
        game_id = games_filtered.iloc[row_idx]["game_id"]
        

        #FILTRAR POR EQUIPO
        games_lineup_filtered = dl.game_lineups[dl.game_lineups["game_id"] == game_id]
        if not games_lineup_filtered.empty:
            teams_id = games_lineup_filtered["club_id"].unique()
            clubs_names = dl.clubs[dl.clubs["club_id"].isin(teams_id)]
            team_sel = st.selectbox("Selecciona un equipo para mostrar alineación", clubs_names["name"])
            team_sel = clubs_names[clubs_names["name"]== team_sel]
            games_lineup_filtered = games_lineup_filtered[games_lineup_filtered["club_id"].isin(team_sel["club_id"])]
            
            #Alineación
            st.subheader("Alineación del partido:")
            st.dataframe(games_lineup_filtered[["player_name", "type", "position", "number"]].rename(columns={
                "player_name": "Nombre",
                "type": "Titularidad", 
                "position": "Posición", 
                "number": "Dorsal"
            })
                , hide_index=True)

            #Estructura alineación
            game = games_filtered.iloc[row_idx] 
            team_sel_name = team_sel["name"].iloc[0] 
            if team_sel_name == game["home_club_name"]:       
                st.write(f"**Estructura alineación:** {game['home_club_formation']}")
            else:
                st.write(f"**Estructura alineación:** {game['away_club_formation']}")

            #Dibujar campo con jugadores
            fd.draw_field(games_lineup_filtered)
        else:
            
            st.subheader("Alineación del partido:")
            st.write("No hay información de la alineación de este partido")

        
       

        
        