import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import data_loader as dl

def graph_transfers(transfers: pd.DataFrame):

    
    # DATOS DEL JUGADOR
    transfers = transfers.sort_values("transfer_date")    
   
    #CONSTRUIR SECUENCIA DE NODOS 
    nodes_sequence = []
    for _, row in transfers.iterrows():
        # Agregar el club de origen si la secuencia está vacía
        if not nodes_sequence:
            nodes_sequence.append(row["from_club_name"])
            # Agregar el club de destino
        nodes_sequence.append(row["to_club_name"])

   
    n_nodes = len(nodes_sequence)
    #NÚMERO DE NODOS POR FILA
    nodes_per_row = 4  
     
    #CALCULAR POSICIÓN x, y DE CADA NODO
    x_positions = {}
    y_positions = {}
    for idx, node in enumerate(nodes_sequence):
        row_num = idx // nodes_per_row
        col_num = idx % nodes_per_row
        #Separación horizontal
        x_positions[idx] = col_num * 2
        #Separación vertical    
        y_positions[idx] = -row_num * 1.5    

    # CONSTRUIR ARISTAS Y TEXTOS
    edge_color = 'blue'
    edge_traces = []

    for i, row in enumerate(transfers.itertuples(index=False)):
        x0, y0 = x_positions[i], y_positions[i]
        x1, y1 = x_positions[i+1], y_positions[i+1]

        # Línea recta
        edge_traces.append(go.Scatter(
            x=[x0, x1],
            y=[y0, y1],
            mode='lines',
            line=dict(width=2, color=edge_color),
            text=f"{row.from_club_name} → {row.to_club_name}<br>Temporada: {row.transfer_season}<br>Precio: €{row.transfer_fee:,.0f}",
            hoverinfo='none'
        ))

        # Marcador invisible para mostrar texto de trasnferencia
        xm, ym = (x0 + x1)/2, (y0 + y1)/2
        edge_traces.append(go.Scatter(
            x=[xm],
            y=[ym],
            mode='markers',
            marker=dict(size=20, color=edge_color, opacity=0),
            hoverinfo='text',
            text=f"{row.from_club_name} → {row.to_club_name}<br>Temporada: {row.transfer_season}<br>Precio: €{row.transfer_fee:,.0f}"
        ))

        # Texto de temporada encima de la arista
        edge_traces.append(go.Scatter(
            x=[xm],
            y=[ym], 
            mode='text',
            text=[row.transfer_season],
            textposition="top center", 
             hoverinfo='skip'
        ))

 
    # DIBUJAR NODOS
    node_trace = go.Scatter(
        x=[x_positions[i] for i in range(n_nodes)],
        y=[y_positions[i] for i in range(n_nodes)],
        mode='markers+text',
        text=nodes_sequence,
        textposition="bottom center",
        marker=dict(size=30, color='orange'),
        hoverinfo='text'
    )

  
    # FIGURA FINAL
    fig = go.Figure(data=edge_traces + [node_trace])
    fig.update_layout(
        showlegend=False,
        hovermode='closest',
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=300 + (n_nodes // nodes_per_row) * 100 
    )

    st.plotly_chart(fig, use_container_width=True)
