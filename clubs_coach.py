import streamlit as st
import pandas as pd
import data_loader as dl
import plotly.express as px


def main():

     
    if "myclub_id" in st.session_state and st.session_state.myclub_id:
        my_club = st.session_state.myclub_id

        st.subheader("Temporada 24/25")
    

        col1, col2 = st.columns(2)

        #with col1:
        #    #FILTRAR CLUBS CON TEXTO
        #    search_club = st.text_input("Escribe letras para filtrar equipos")

        # FILTRAR LA LISTA DE CLUBS SEGÚN EL TEXTO INTRODUCIDO
        #clubs_filtered = dl.load_data(
        #    f"""
        #    SELECT name, club_id FROM clubs
        #    WHERE name LIKE '%{search_club}%'
        #    ORDER BY name
        #    """
        #)["name"].unique()   
        # 

        

    

        competition_filtered = dl.load_data(
            f"""
                        SELECT competition_id, competition_name
                        FROM football.`gold-football-data`.games_gold
                        WHERE (home_club_id = {my_club} OR away_club_id = {my_club})
                        AND season = 2024
                        """
            )

        comp_names = competition_filtered["competition_name"].unique().tolist()
      

        with col1:
            #FILTRAR COMPETICION
            comp_sel = st.selectbox("Selecciona una competición", comp_names, key="clubs_comp1")
            competition_id = competition_filtered.loc[
                            competition_filtered["competition_name"] == comp_sel, "competition_id"].iloc[0]

    
       


        clubs_filtered = dl.load_data(
                        f"""
                        SELECT DISTINCT
                            CASE
                                WHEN home_club_id = {my_club} THEN away_club_id
                                WHEN away_club_id = {my_club} THEN home_club_id
                            END AS rival_id,
                            CASE
                                WHEN home_club_id = {my_club} THEN away_club_name
                                WHEN away_club_id = {my_club} THEN home_club_name
                            END AS rival_name
                        FROM football.`gold-football-data`.games_gold
                        WHERE (home_club_id = {my_club} OR away_club_id = {my_club})
                        AND season = 2024
                        AND competition_id = '{competition_id}'
                        """
            )
        
        rival_names = sorted(clubs_filtered["rival_name"].dropna().unique().tolist())
        

        with col2:
            #SELECTBOX CON CLUBS FILTRADOS
            club_sel = st.selectbox("Selecciona un club", rival_names)
        
        clubs_filtered = dl.load_data(f""" 
                SELECT club_id, name, domestic_competition_id,stadium_name, stadium_seats, squad_size, average_age
                FROM football.`gold-football-data`.clubs_gold
                WHERE name = '{club_sel}'
                """)    

        col3, col4 =  st.columns(2)

        #FILTRAR PARTIDOS DEL CLUB
        club_id = clubs_filtered["club_id"].iloc[0]
        games_filtered =  dl.load_data(f"""
                SELECT game_id, club_id, is_win, hosting, season, competition_id, date
                FROM football.`gold-football-data`.club_games_gold
                WHERE club_id = {club_id}
                        """)            
        
        
        
        #FILTRAR POR TEMPORADA
        games_filtered = games_filtered[games_filtered["season"] == 2024]

        
        #FILTRAR POR COMPETICIÓN 
        comp_filtered = dl.load_data(f"""
            SELECT DISTINCT competition_id, competition_name
            FROM football.`gold-football-data`.club_games_gold
            WHERE club_id = {club_id}                             
        """)
        comp_options = ["Todas"] + comp_filtered["competition_name"].unique().tolist()
        

    
    
        st.subheader(f"Análisis de los partidos del {club_sel}:")
        
        #Selección competición
        comp_sel = st.selectbox("Selecciona una competición:", comp_options , key="clubs_comp2")
        if comp_sel != "Todas":
            comp = comp_filtered[comp_filtered["competition_name"] == comp_sel]
            games_filtered = games_filtered[games_filtered["competition_id"] == comp["competition_id"].iloc[0]]
        
        if not games_filtered.empty:

            #FILTRAR POR RANGO DE FECHAS **Por defecto rango de temporada completa
            min_date = games_filtered["date"].min()
            max_date = games_filtered["date"].max()

            date_range = st.date_input(
                "Selecciona rango de fechas",
                (min_date, max_date),
                min_value= min_date,
                max_value= max_date,
                format="DD.MM.YYYY"
                )

            start_date, end_date = date_range


            games_filtered = games_filtered[
            (games_filtered["date"] >= start_date) &
            (games_filtered["date"] <= end_date)
            ]

        
            st.write("**Victorias-Derrotas**")
            container1= st.container(border = True)    
            col1_c1, col2_c1 = container1.columns([1,3])

            #PARTIDOS JUGADOS
            total_games = len(games_filtered)
            
            
            #PARTIDOS TOTALES GANADOS
            win_games = games_filtered["is_win"].sum()
            

            #PARTIDOS TOTALES PERDIDOS
            lost_games = total_games - win_games

            #GRÁFICO PIE

            # Datos gráfico 
            data = pd.DataFrame({
                "Categoría": ["Victorias", "Derrotas"],
                "Valor": [win_games, lost_games]
            })

            #Crear gráfico
            pie_v_d = px.pie(data, values="Valor", names="Categoría")
            pie_v_d.update_layout(
                width=250,   
                height=250,  
                margin=dict(l=10, r=10, t=10, b=10)
            )

            #MOSTRAR MÉTRICAS PARTIDOS
            with col1_c1:
                st.metric(f"Partidos jugados:" ,total_games)
                st.metric(f"Victorias:", win_games)
                st.metric(f"Derrotas:", lost_games)
                
            #MOSTRAR GRÁFICO
            with col2_c1:
                st.plotly_chart(pie_v_d)

            st.write("**Victorias Local-Visitante**")

            container2 = st.container(border = True)

            col1_c2, col2_c2 = container2.columns([1,3]) 

            #PARTIDOS GANADOS - LOCAL
            games_home = games_filtered[games_filtered["hosting"] == "Home"]
            win_games_home = games_home["is_win"].sum()
            
            
            #PARTIDOS GANADOS - VISITANTE
            games_away = games_filtered[games_filtered["hosting"] == "Away"]
            win_games_away = games_away["is_win"].sum()
            

            #GRÁFICO PIE

            # Datos gráfico 
            data = pd.DataFrame({
                "Categoría": ["Local", "Visitante"],
                "Valor": [win_games_home, win_games_away]
            })

            #Crear gráfico
            pie_l_v = px.pie(data, values="Valor", names="Categoría")
            pie_l_v.update_layout(
                width=250,   # ancho en píxeles
                height=250,  # alto en píxeles
                margin=dict(l=10, r=10, t=10, b=10)
            )

            with col1_c2:
                st.metric(f"Victorias como local:", win_games_home)
                st.metric(f"Victorias como visitante:",  win_games_away)

            with col2_c2:
                st.plotly_chart(pie_l_v)


            
            #MINUTOS EN LOS QUE RECIBEN MÁS GOLES
            games_events_filtered = dl.load_data(f"""
                        SELECT game_id, type, minute
                        FROM football.`gold-football-data`.game_events_gold
                        WHERE club_id = {club_id}
                        AND type = 'Goals'
                        """)
            
            games_events_filtered = pd.merge(
                        games_events_filtered,
                        games_filtered,
                        left_on="game_id",
                        right_on="game_id",
                    )
            
            goals_minutes = games_events_filtered["minute"].value_counts()
            st.subheader(f"Minutos en los que anota mas goles el {club_sel}")
            st.bar_chart(goals_minutes, x_label = "Minutos", y_label = "Goles")
        
        else: 
            st.warning("No hay información sobre la competitión seleccionada")

    else:
        st.warning("No has seleccionado ningún club todavía. Elige tu club y pulsa sobre el botón de 'Guardar equipo'")


    


    


        

        
        
        


                        

    