import streamlit as st
import players
import games
import rankings 
import clubs
import transfers

st.logo("footballs.jpg")

#USAR TODO ANCHO DE PANTALLA
st.set_page_config(page_title="App Fútbol", layout="wide")

# Botón fijo para volver al inicio
col1, _ = st.columns([1, 5])
with col1:
    if st.button("Inicio"):
        st.switch_page("principal_page.py")


#CREAR PESTAÑAS
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Jugadores", "Partidos", "Rankings", "Equipos", "Fichajes"])


with tab1:
    st.title("Jugadores")
    players.main()
    

with tab2:
    st.title("Partidos")
    games.main()
    

with tab3:
    st.title("Rankings")
    rankings.main()

with tab4:
    st.title("Equipos")
    clubs.main()

with tab5:
    st.title("Fichajes")
    transfers.main()
