import streamlit as st
import players
import games
import rankings 
import clubs
import transfers


#USAR TODO ANCHO DE PANTALLA
st.set_page_config(page_title="App Fútbol", layout="wide")



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
