import streamlit as st
import pandas as pd
from st_link_analysis import st_link_analysis, NodeStyle, EdgeStyle

def graph_transfers(transfers: pd.DataFrame):
    # Ordenar por fecha de transferencia
    transfers = transfers.sort_values("transfer_date")

    # Crear nodos únicos 
    clubs = pd.unique(transfers[["from_club_name", "to_club_name"]].values.ravel())
    nodes = [{"data": {"id": club, "label": "CLUB", "name": club}} for club in clubs]

    # Crear edges de las transferencias
    edges = []
    for _, row in transfers.iterrows():
        edges.append({
            "data": {
                "id": f"{row.from_club_name}_{row.to_club_name}_{row.transfer_date}",
                "source": row.from_club_name,
                "target": row.to_club_name,
                "label": f"{row.transfer_season} - €{row.transfer_fee:,.0f}"
            }
        })

    elements = {"nodes": nodes, "edges": edges}

    # Definir estilos de nodo y arista
    node_styles = [NodeStyle("CLUB", "#FF7F3E", "name", "group")]
    edge_styles = [EdgeStyle("PLAYS_FOR", caption="label", directed=True)]  

    # Mostrar grafo en Streamlit
    st.markdown("## Grafo de Transferencias de Jugadores")
    st_link_analysis(elements, layout="cose", node_styles=node_styles, edge_styles=edge_styles)


