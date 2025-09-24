import streamlit as st
import players
import games
import rankings 
import clubs


#USAR TODO ANCHO DE PANTALLA
st.set_page_config(page_title="App Fútbol", layout="wide")

#CREAR PESTAÑAS
tab1, tab2, tab3, tab4 = st.tabs(["Jugadores", "Partidos", "Rankings", "Equipos"])


with tab1:
    st.subheader("Jugadores")
    players.main()
    

with tab2:
    st.subheader("Partidos")
    games.main()
    

with tab3:
    st.subheader("Rankings")
    rankings.main()

with tab4:
    st.subheader("Clubs")
    clubs.main()
