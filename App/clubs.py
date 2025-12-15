import streamlit as st
import pandas as pd
import data_loader as dl
import plotly.express as px


def main():
    

    col1, col2 = st.columns(2)

    with col1:
        #FILTRAR CLUBS CON TEXTO
        search_club = st.text_input("Escribe letras para filtrar equipos")

    # FILTRAR LA LISTA DE CLUBS SEGÚN EL TEXTO INTRODUCIDO
    clubs_filtered = dl.load_data(
        f"""
        SELECT name, club_id FROM football.`gold-football-data`.clubs_gold
        WHERE LOWER(name) LIKE LOWER('%{search_club}%')
        ORDER BY name
        """
    )

    if clubs_filtered.empty:
        with col2: 
            club_sel = st.selectbox("Selecciona un club", ["No hay resultados"])

    else:

        clubs_filtered = clubs_filtered["name"].unique()

        with col2:
            #SELECTBOX CON CLUBS FILTRADOS
            club_sel = st.selectbox("Selecciona un club", clubs_filtered)
        
        clubs_filtered = dl.load_data(f""" 
                SELECT club_id, name, domestic_competition_id,stadium_name, stadium_seats, squad_size, average_age
                FROM football.`gold-football-data`.clubs_gold
                WHERE name = '{club_sel}'
                """)

        st.subheader(f"Ficha del {club_sel}:")

        container = st.container(width=450, height="stretch", border= True)

        #COMPETICIÓN DOMÉSTICA
        domestic_comp_club = clubs_filtered["domestic_competition_id"].iloc[0]
        competition_filtered = dl.load_data(F"""
                    SELECT competition_id, name
                    FROM football.`gold-football-data`.competitions_gold
                    WHERE competition_id = '{domestic_comp_club}'
                    """)
        competition_name = competition_filtered['name'].iloc[0]
        container.write(f"**Competición doméstica:** {competition_name}")

        #NOMBRE DEL ESTADIO Y ASIENTOS
        stadium_name = clubs_filtered["stadium_name"].iloc[0]
        stadium_seats = clubs_filtered["stadium_seats"].iloc[0]
        container.write(f"**Estadio:** {stadium_name} ({stadium_seats} asientos)")
        
        #TAMAÑO DE LA PLANTILLA
        squad_size = clubs_filtered["squad_size"].iloc[0]
        container.write(f"**Tamaño de la plantilla:** {squad_size}")

        #EDAD MEDIA DE LA PLANTILLA
        avrg_age = clubs_filtered["average_age"].iloc[0]
        container.write(f"**Edad media de la plantilla:** {avrg_age}")

        col3, col4 =  st.columns(2)

        #FILTRAR PARTIDOS DEL CLUB
        club_id = clubs_filtered["club_id"].iloc[0]
        games_filtered =  dl.load_data(f"""
                SELECT game_id, club_id, is_win, hosting, season, competition_id, date
                FROM football.`gold-football-data`.club_games_gold 
                WHERE club_id = {club_id}
                        """)            
        
        
        
        #FILTRAR POR TEMPORADA
        season_options = ["Todas"] + games_filtered["season"].unique().tolist()
        with col3:
            season_sel =  st.selectbox("Selecciona una temporada:", season_options , key="clubs_season")
        if season_sel != "Todas":
            games_filtered = games_filtered[games_filtered["season"] == season_sel]

        
        #FILTRAR POR COMPETICIÓN 
        comp_filtered = dl.load_data(f"""
            SELECT DISTINCT c.competition_id, c.name
            FROM football.`gold-football-data`.competitions_gold c
            JOIN (
                SELECT competition_id
                FROM football.`gold-football-data`.club_games_gold
                WHERE club_id = {club_id}                             
            ) AS fg
            ON c.competition_id = fg.competition_id
        """)
        comp_options = ["Todas"] + comp_filtered["name"].unique().tolist()
        with col4:
            comp_sel = st.selectbox("Selecciona una competición:", comp_options , key="clubs_comp")
        if comp_sel != "Todas":
            comp = comp_filtered[comp_filtered["name"] == comp_sel]
            games_filtered = games_filtered[games_filtered["competition_id"] == comp["competition_id"].iloc[0]]


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
    
        st.subheader("Análisis de los partidos:")
        
    
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
    


    


        

        
        
        


                        

    