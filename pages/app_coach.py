import streamlit as st
import players
import games
import rankings 
import clubs
import transfers
import data_loader as dl

st.logo("footballs.jpg")

#USAR TODO ANCHO DE PANTALLA
st.set_page_config(page_title="App Fútbol", layout="wide")

if st.button("Inicio"):
    st.session_state.myclub = ""
    st.switch_page("principal_page.py")

# Botón fijo para volver al inicio
col_c1, col_c2, col_c3= st.columns([0.4, 0.4, 0.2])


        
    

#Inicializar session_state
if "myclub" not in st.session_state:
    st.session_state.myclub = ""


if not st.session_state.myclub:

    with col_c1:
    # Input para escribir el nombre del equipo
        clubs_filter = st.text_input("Nombre de tu equipo:", st.session_state.myclub)

    # FILTRAR LA LISTA DE CLUBS SEGÚN EL TEXTO INTRODUCIDO
    clubs_filtered = dl.clubs[
        dl.clubs["name"].str.contains(clubs_filter, case=False, na=False)
        ]["name"].sort_values().unique()
   

    with col_c2:
            #SELECTBOX CON CLUBS FILTRADOS
            myclub_sel = st.selectbox("Selecciona un club", clubs_filtered)

    with col_c3:
        #Botón para guardar la selección
        if st.button("Guardar equipo"):
            st.session_state.myclub = myclub_sel
            st.success(f"Equipo guardado: {st.session_state.myclub}")
            st.rerun()
        

else:

    col_s1, col_s2 = st.columns([0.8, 0.2])
    
    with col_s1:
        # Si ya hay un equipo guardado → mostrar solo el nombre
        st.subheader(f"Tu equipo: **{st.session_state.myclub}**")
    with col_s2:
        # Botón para cambiar de equipo
        if st.button("Cambiar equipo"):
            st.session_state.myclub = ""
            st.rerun()



#CREAR PESTAÑAS
tab1, tab2, tab3, tab4 = st.tabs(["Jugadores", "Partidos", "Equipos", "Fichajes"])


with tab1:
    st.title("Jugadores")
    players.main()
    
with tab2:
    st.title("Partidos")
    games.main()
    
with tab3:
    st.title("Equipos")
    clubs.main()

with tab4:
    st.title("Fichajes")
    transfers.main()
