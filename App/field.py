import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import pandas as pd



def draw_field(game_lineup: pd.DataFrame):
    
    #ALINEACIÓN INICIAL
    starting_lineup = game_lineup[game_lineup["type"] == "starting_lineup"]
    
    #DATOS DE JUGADORES - POSICIONES 
    players = starting_lineup[["player_name", "position"]]



    # COORDENADAS VERTICALES SEGÚN POSICIÓN
    position_coords = {
        "Goalkeeper": [(50, 5)],
        "Left-Back": [(15, 25),(35, 25)],
        "Centre-Back": [(35, 25), (65, 25),(85, 25)],
        "Right-Back": [(85, 25)],
        "Attacking Midfield": [(50, 65), (60, 55)],
        "Central Midfield": [(40, 55), (60, 55)],
        "Right Midfield": [(80, 55)],
        "Left Midfield": [(20,55)],
        "Defensive Midfield": [(50, 45),(50,35)],
        "Centre-Forward": [(50, 85),(25, 85) ,(75, 85)],
        "Second Striker": [(50,75)],
        "Right Winger": [(15, 85)],
        "Left Winger": [(85, 85)]
    }

    #MAPEAR COORDENADAS AL DATAFRAME
    coords_x = []
    coords_y = []

    for _, row in players.iterrows():
        pos = row["position"]
        if pos == "Goalkeeper":
            x, y = position_coords["Goalkeeper"].pop(0)
        elif pos == "Left-Back":
            x, y = position_coords["Left-Back"].pop(0)
        elif pos == "Centre-Back":
            x, y = position_coords["Centre-Back"].pop(0)
        elif pos == "Right-Back":
            x, y = position_coords["Right-Back"].pop(0)
        elif pos == "Attacking Midfield":
            x, y = position_coords["Attacking Midfield"].pop(0)
        elif pos == "Central Midfield":
            x, y = position_coords["Central Midfield"].pop(0)
        elif pos == "Defensive Midfield":
            x, y = position_coords["Defensive Midfield"].pop(0)
        elif pos == "Right Midfield":
            x, y = position_coords["Right Midfield"].pop(0)
        elif pos == "Left Midfield":
            x, y = position_coords["Left Midfield"].pop(0)
        elif pos == "Centre-Forward":
            x, y = position_coords["Centre-Forward"].pop(0)
        elif pos == "Right Winger":
            x, y = position_coords["Right Winger"].pop(0)
        elif pos == "Left Winger":
            x, y = position_coords["Left Winger"].pop(0)
        elif pos == "Second Striker":
            x, y = position_coords["Second Striker"].pop(0)
        coords_x.append(x)
        coords_y.append(y)

    players["x"] = coords_x
    players["y"] = coords_y



    #CREAR EL CAMPO
    fig = go.Figure()

    # Campo
    fig.add_shape(type="rect", x0=0, y0=0, x1=100, y1=100,
                line=dict(color="white", width=3))

    # Medio campo
    fig.add_shape(type="line", x0=0, y0=50, x1=100, y1=50,
                line=dict(color="white", width=2))

    # Círculo central
    fig.add_shape(type="circle", x0=40, y0=40, x1=60, y1=60,
                line=dict(color="white", width=2))

    # Área de penalti superior
    fig.add_shape(type="rect", x0=35, y0=0, x1=65, y1=15,
                line=dict(color="white", width=2))

    # Área de penalti inferior
    fig.add_shape(type="rect", x0=35, y0=85, x1=65, y1=100,
                line=dict(color="white", width=2))

    # Porterías
    fig.add_shape(type="rect", x0=45, y0=-2, x1=55, y1=0,
                line=dict(color="white", width=3), fillcolor="white")
    fig.add_shape(type="rect", x0=45, y0=100, x1=55, y1=102,
                line=dict(color="white", width=3), fillcolor="white")

    # Añadir jugadores como puntos
    fig.add_trace(go.Scatter(
        x=players["x"],
        y=players["y"],
        mode="markers+text",
        text=players["player_name"],
        textposition="top center",
        marker=dict(size=20, color="black"),
        textfont=dict(
        color="black"
        )
    ))

    # Ajustes de layout
    fig.update_layout(
        width=600, height=625,
        xaxis=dict(showgrid=False, zeroline=False, visible=False, range=[0, 100]),
        yaxis=dict(showgrid=False, zeroline=False, visible=False, range=[0, 100]),
        plot_bgcolor="green",
        margin=dict(l=10, r=10, t=10, b=10),
        yaxis_scaleanchor="x"
    )

    #PINTAR EL CAMPO
    st.plotly_chart(fig, use_container_width=False)





