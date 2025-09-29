import streamlit as st
import data_loader as dl
import pandas as pd
from datetime import date

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

  

    players = dl.players.copy()

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
    players_filtered = players.copy()
    col1, col2 = st.columns(2)
    #Position
    with col1: 
        position_options = ["Todas"] + players_filtered["position_translate"].unique().tolist()
        position_sel = st.selectbox("Selecciona posición principal:", position_options)
    if position_sel != "Todas":
        players_filtered = players_filtered[players_filtered["position_translate"] == position_sel]
    #Sub-position
    with col2:
        sub_position_options = ["Todas"] + players_filtered["sub_position_translate"].unique().tolist()
        sub_position_sel = st.selectbox("Selecciona posición secundaria", sub_position_options)
    if sub_position_sel != "Todas":
        players_filtered = players_filtered[players_filtered["sub_position_translate"] == sub_position_sel]


    #FILTRAR POR EDAD
    min_age, max_age = st.slider("Selecciona rango de edad", min_value=int(players_filtered["age"].min()), max_value= int(players_filtered["age"].max()), value=(20,25))
    players_filtered = players_filtered[(players_filtered["age"] >= min_age) & (players_filtered["age"] <= max_age)  ]
    
    #FILTRAR POR COMPETICIÓN
    players_filtered = pd.merge (
        players_filtered,
        dl.competitions[["competition_id", "name"]],
        left_on= "current_club_domestic_competition_id",
        right_on="competition_id"
    ).rename(columns={"name_x":"name_player", "name_y": "name_competition"})
    comp_options = ["Todas"] + players_filtered["name_competition"].unique().tolist()
    comp_sel = st.selectbox("Selecciona competición:", comp_options, key="transfers_comp")
    if comp_sel != "Todas":
        players_filtered = players_filtered[players_filtered["name_competition"]== comp_sel]
    
    st.dataframe(players_filtered[["name_player", "current_club_name", "market_value_in_eur", "age"]])


     
