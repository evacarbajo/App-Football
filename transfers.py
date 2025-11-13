import streamlit as st
import data_loader as dl
import pandas as pd
from datetime import date
from googletrans import Translator


def main():

    # Diccionario traduccion posiciones
    pos_translate = {
            "Goalkeeper": "Portero",
            "Defender" : "Defensa",
            "Left-Back": "Lateral izquierdo",
            "Centre-Back": "Defensa central",
            "Right-Back": "Lateral derecho",
            "Midfield" : "Centrocampista",
            "Attacking Midfield": "Mediapunta",
            "Central Midfield": "Mediocentro",
            "Right Midfield": "Centrocampista derecho",
            "Left Midfield": "Centrocampista izquierdo",
            "Defensive Midfield": "Mediocentro defensivo",
            "Attack": "Delantero",
            "Centre-Forward": "Delantero centro",
            "Second Striker": "Segundo delantero",
            "Right Winger": "Extremo derecho",
            "Left Winger": "Extremo izquierdo",
        }
    
    
    col1, col2 = st.columns(2)

    #FILTRAR POR EDAD
    min_age, max_age = st.slider("Selecciona rango de edad", min_value=15, max_value= int(60), value=(20,25))
    
    #FILTRAR POR VALOR DE MERCADO
    min_value, max_value = st.slider("Selecciona rango de valor de mercado", 
                                    
                                     max_value= 300000000, 
                                     value=(20000000, 50000000),
                                     step=1000000)
    # Mostrar los valores seleccionados con separador de miles
    st.write(f"Rango valor de mercado: {min_value:,}€  - {max_value:,}€".replace(",", "."))


    players = dl.load_data(f"""SELECT *
                                FROM football.`gold-football-data`.players_gold 
                                WHERE
                                age BETWEEN {min_age} AND {max_age} AND
                                market_value_in_eur BETWEEN {min_value} AND {max_value}
                           """)
    
    players_valuation = dl.load_data(f"""SELECT p.*, pv.date, pv.market_value_in_eur as market_value
                                FROM football.`gold-football-data`.players_gold p
                                JOIN football.`gold-football-data`.player_valuations_gold pv
                                ON p.player_id = pv.player_id
                                WHERE
                                age BETWEEN {min_age} AND {max_age} AND
                                p.market_value_in_eur BETWEEN {min_value} AND {max_value}
                           """)
    
    
    #AÑADIR COLUMNAS CON LAS POSICIONES EN ESPAÑOL
    players["position_translate"] = players["position"].map(pos_translate).fillna(players["position"])
    players["sub_position_translate"] = players["sub_position"].map(pos_translate).fillna(players["sub_position"])

    
    #FILTRAR POR POSITION Y SUB-POSITION
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

    

    #FILTRAR POR COMPETICIÓN
    comp_options = dl.load_data("""
                                SELECT DISTINCT competition_name 
                                FROM football.`gold-football-data`.players_gold
                                """)
    comp_options = comp_options["competition_name"].dropna().tolist()
    comp_options = ["Todas"] + comp_options
    comp_sel = st.selectbox("Selecciona competición:", comp_options, key="transfers_comp")
    if comp_sel != "Todas":
        players = players[players["competition_name"]== comp_sel]
    
    
   
    #CREAR LISTA ORDENADA CON LA EVOLUCIÓN DE LOS VALORES DE MERCADO
    player_valuations = (
        players_valuation.sort_values(["player_id", "date"])
        .groupby("player_id")["market_value"]
        .apply(list)
        .reset_index(name="market_value_history")
    )

    #MERGE DE JUGADORES CON SU EVOLUCIÓN DEL VALOR DE MERCADO
    players = pd.merge (
        players,
        player_valuations,
        on="player_id"
    )

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
            dl.load_data("SELECT player_id, goals, season FROM football.`gold-football-data`.appearances_gold"),
            on="player_id"               
        )
        season_options = sorted(goals["season"].unique().tolist())
        season_options = ["Todas"] + season_options
        with col_goals:
            st.subheader("Comparación goles:")
            season_sel = st.selectbox("Selecciona temporada", season_options, key="transfers_season")
        if season_sel != "Todas":
            goals = goals[goals["season"]== season_sel]

        total_goals = goals.groupby(
                ["player_id", "name"], as_index=False
                    )["goals"].sum()
        chart_goals = total_goals.set_index("name")[["goals"]]

        with col_goals:
            st.bar_chart(chart_goals)

