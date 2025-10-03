import streamlit as st
import data_loader as dl
import pandas as pd
from datetime import date
from googletrans import Translator


def main():

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
            "Left Winger": "Extremo izquierdo",
            "Attack": "Delantero",
            "Goalkeeper" : "Portero",
            "Defender" : "Defensa",
            "Midfield" : "Centrocampista"
        }

  

    #players = dl.players.copy()
    players = dl.load_data("SELECT * FROM players")

    #AÑADIR COLUMNAS CON LAS POSICIONES EN ESPAÑOL
    players["position_translate"] = players["position"].map(pos_translate).fillna(players["position"])
    players["sub_position_translate"] = players["sub_position"].map(pos_translate).fillna(players["sub_position"])
    
    #AÑADIR COLUMNA CON LA EDAD
    players["date_of_birth"] = pd.to_datetime(players["date_of_birth"])
    today = date.today()
    players["age"] = players["date_of_birth"].apply(   
    lambda x: today.year - x.year - ((today.month, today.day) < (x.month, x.day))
    )


    #FILTRAR POR POSITION Y SUB-POSITION
    col1, col2 = st.columns(2)
    #Position
    with col1: 
        position_options = ["Todas"] + players["position_translate"].unique().tolist()
        position_sel = st.selectbox("Selecciona posición principal:", position_options)
    if position_sel != "Todas":
        players = players[players["position_translate"] == position_sel]
    #Sub-position
    with col2:
        sub_position_options = ["Todas"] + players["sub_position_translate"].unique().tolist()
        sub_position_sel = st.selectbox("Selecciona posición secundaria", sub_position_options)
    if sub_position_sel != "Todas":
        players = players[players["sub_position_translate"] == sub_position_sel]


    #FILTRAR POR EDAD
    min_age, max_age = st.slider("Selecciona rango de edad", min_value=int(players["age"].min()), max_value= int(players["age"].max()), value=(20,25))
    players = players[(players["age"] >= min_age) & (players["age"] <= max_age)  ]
    
    #FILTRAR POR VALOR DE MERCADO
    min_value, max_value = st.slider("Selecciona rango de valor de mercado", 
                                     #min_value=int(players["market_value_in_eur"].min()), 
                                     max_value= int(players["market_value_in_eur"].max()), 
                                     value=(20000000, 50000000),
                                     step=1000000)
    players = players[(players["market_value_in_eur"] >= min_value) & (players["market_value_in_eur"] <= max_value)  ]
    # Mostrar los valores seleccionados con separador de miles
    st.write(f"Rango valor de mercado: {min_value:,}€  - {max_value:,}€".replace(",", "."))


    #FILTRAR POR COMPETICIÓN
    players = pd.merge (
        players,
        dl.load_data("SELECT competition_id, name FROM competitions"),
        left_on= "current_club_domestic_competition_id",
        right_on="competition_id"
    ).rename(columns={"name_x":"name", "name_y": "name_competition"})
    comp_options = ["Todas"] + players["name_competition"].unique().tolist()
    comp_sel = st.selectbox("Selecciona competición:", comp_options, key="transfers_comp")
    if comp_sel != "Todas":
        players = players[players["name_competition"]== comp_sel]
    
   
    #CREAR LISTA ORDENADA CON LA EVOLUCIÓN DE LOS VALORES DE MERCADO
    player_id = players["player_id"]
    player_valuations = dl.load_data("SELECT * FROM player_valuations")
    player_valuations = player_valuations[player_valuations["player_id"].isin(player_id)]
    player_valuations["date"] = pd.to_datetime(player_valuations["date"])
    player_valuations = (
        player_valuations.sort_values(["player_id", "date"])
        .groupby("player_id")["market_value_in_eur"]
        .apply(list)
        .reset_index(name="market_value_history")
    )

    
    #MERGE DE JUGADORES CON SU EVOLUCIÓN DEL VALOR DE MERCADO
    players = pd.merge (
        players,
        player_valuations,
        on="player_id"
    )

    players["contract_expiration_date"] = pd.to_datetime(players["contract_expiration_date"])

  

    #TABLA CON DATOS DE INTERES DE JUGADORES
    selected_players = st.dataframe(
        players[["image_url", "name", "current_club_name","age","market_value_in_eur", "position_translate", "sub_position_translate", "contract_expiration_date"
                         # "market_value_history"
                          ]],
        column_config= {
            "image_url": st.column_config.ImageColumn("Foto", width=50),
            "name": "Nombre",
            "current_club_name": "Club actual",
            "position_translate": "Posición principal",
            "sub_position_translate": "Posición secundaria",
            "age": "Edad",
            #"market_value_history": st.column_config.AreaChartColumn(
            #   "Evolución valor de mercado",
            #   width="medium",
            #    y_max = players["market_value_in_eur"].max()
            #    ),
            "market_value_in_eur": st.column_config.NumberColumn(
                "Valor de mercado(€)",
                format="euro"
            ),
            "contract_expiration_date": st.column_config.DatetimeColumn(
                "Fin contrato",
                format="calendar"
            )
            
            
           },
           hide_index=True,
           on_select="rerun",
           selection_mode="multi-row",
           
        )
    

    #CONTROLA SELECCIÓN DE JUGADORES MÍNIMO Y MÁXIMO
    players_index = selected_players["selection"]["rows"]
    num_sel= len(players_index)
    players_sel = players.iloc[players_index]
    if num_sel < 2:
        st.write("Selecciona entre 2 y 4 jugadores para compararlos")
    elif num_sel > 4:
        st.write("Demasiados jugadores seleccionados")
    else:
        #Muestra jugadores seleccionados
        st.subheader("Jugadores seleccionados:")
        selected_players = st.dataframe(
        players_sel[["image_url", "name", "current_club_name","age","market_value_in_eur","market_value_history", "position_translate", "sub_position_translate", "contract_expiration_date"]],
        column_config= {
            "image_url": st.column_config.ImageColumn("Foto", width=100),
            "name": "Nombre",
            "current_club_name": "Club actual",
            "position_translate": "Posición principal",
            "sub_position_translate": "Posición secundaria",
            "age": "Edad",
            "market_value_history": st.column_config.AreaChartColumn(
                "Evolución valor de mercado",
                y_max = players_sel["market_value_in_eur"].max()
                ),
            "market_value_in_eur": st.column_config.NumberColumn(
                "Valor de mercado(€)",
                format="euro"
            ),
            "contract_expiration_date": st.column_config.DatetimeColumn(
                "Fin contrato",
                format="calendar"
            )
           },
           hide_index=True,
           row_height=100   
        )

        col_val, col_goals = st.columns(2, border=True)

        #BAR CHAR DEL VALOR DE MERCADO 
        val_mercado = players_sel.set_index("name")[["market_value_in_eur"]]
        with col_val:
            st.subheader("**Comparación del valor de mercado:**")
            st.bar_chart(val_mercado)

       


        #BAR CHAR GOLES
        goals = pd.merge(
            players_sel[["player_id", "name"]],
            dl.load_data("SELECT player_id, goals, game_id FROM appearances"),
            on="player_id"               
        )
        season_options = pd.merge(
                    dl.load_data("SELECT season, game_id FROM games WHERE season IS NOT NULL ORDER BY season"),
                    goals[["game_id"]], 
                    on = "game_id"            
                    )["season"].unique().tolist()
        season_options = ["Todas"] + season_options
        with col_goals:
            st.subheader("Comparación goles:")
            season_sel = st.selectbox("Selecciona temporada", season_options, key="transfers_season")
        if season_sel != "Todas":
            goals = pd.merge(
                goals,
                dl.load_data(f"SELECT game_id, season FROM games WHERE season = {season_sel}"),
                on= "game_id"                
                )
        total_goals = goals.groupby(
                ["player_id", "name"], as_index=False
                    )["goals"].sum()
        chart_goals = total_goals.set_index("name")[["goals"]]

        with col_goals:
            st.bar_chart(chart_goals)

