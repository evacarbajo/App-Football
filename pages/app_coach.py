import streamlit as st
import players_coach
import games_coach
import rankings 
import clubs_coach
import transfers
import data_loader as dl

st.logo("/Users/evacarbajo/footballs.jpg")

#USAR TODO ANCHO DE PANTALLA
st.set_page_config(page_title="App Fútbol", layout="wide")

if st.button("Inicio"):
    st.session_state.myclub = ""
    st.switch_page("principal_page.py")

# Botón fijo para volver al inicio
col_c1, col_c2, col_c3= st.columns([0.4, 0.4, 0.2])


        
    

#Inicializar session_state
if "myclub_id" not in st.session_state:
    st.session_state.myclub_id = ""
    
    
if not st.session_state.myclub_id:

    with col_c1:
    # Input para escribir el nombre del equipo
        clubs_filter = st.text_input("Nombre de tu equipo:")

    # FILTRAR LA LISTA DE CLUBS SEGÚN EL TEXTO INTRODUCIDO
    clubs_filtered = dl.load_data(
        f"""
        SELECT name, club_id FROM football.`gold-football-data`.clubs_gold
        WHERE LOWER(name) LIKE LOWER('%{clubs_filter}%')
        ORDER BY name
        """
        )
    
    if clubs_filtered.empty:
        with col_c2:
            myclub_name_sel = st.selectbox("Selecciona un club", ["No hay resultados"])
            myclub_sel_id = None
    else:
        with col_c2:
            #SELECTBOX CON CLUBS FILTRADOS
            myclub_name_sel = st.selectbox("Selecciona un club", clubs_filtered["name"].unique(), key= "global_club")

        myclub_sel_id = clubs_filtered[clubs_filtered["name"] == myclub_name_sel]["club_id"].iloc[0]

        with col_c3:
            #Botón para guardar la selección
            if st.button("Guardar equipo"):
                st.session_state.myclub_id = myclub_sel_id
                #st.success(f"Equipo guardado: {st.session_state.myclub}")
                st.success(f"Equipo guardado: {myclub_name_sel}")
                st.rerun()
        

else:

    col_s1, col_s2 = st.columns([0.8, 0.2])
    
    with col_s1:
        # Si ya hay un equipo guardado → mostrar solo el nombre
        #st.subheader(f"Tu equipo: **{st.session_state.myclub}**")
        myclub_name_sel = dl.load_data(f"""
        SELECT name FROM football.`gold-football-data`.clubs_gold
        WHERE club_id == {st.session_state.myclub_id}
        """
        )["name"].iloc[0]
        st.subheader(f"Tu equipo: **{myclub_name_sel}**")
    with col_s2:
        # Botón para cambiar de equipo
        if st.button("Cambiar equipo"):
            st.session_state.myclub_id = ""
            st.rerun()



#CREAR PESTAÑAS
tab1, tab2, tab3, tab4 = st.tabs(["Plantilla", "Partidos", "Rivales", "Fichajes"])


with tab1:
    st.title("Plantilla")
    players_coach.main()
    
with tab2:
    st.title("Partidos")
    games_coach.main()
    
with tab3:
    st.title("Proximo rival:")
    clubs_coach.main()

with tab4:
    st.title("Fichajes")
    transfers.main()
