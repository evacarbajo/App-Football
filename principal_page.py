import streamlit as st



_,col2= st.columns([0.3, 0.7])

with col2:
    st.title("APP FOOTBALL")
    st.image("/Users/evacarbajo/footballs.jpg", width=270)

    
   
#st.write("**Selecciona tipo de usuario:**")
st.write("")

# Configuración de la app 
st.set_page_config(
    page_title="App Football",
    page_icon="⚽",
    layout="centered",  # También puedes usar "wide"
)

# Botones que llevan a páginas secundarias
col1, col2 = st.columns(2)
with col1:
    if st.button("AFICIONADOS", width=400, type="primary"):
        st.switch_page("pages/app.py")
with col2:
    if st.button("ENTRENADORES", width=400, type="primary"):
        st.switch_page("pages/app_coach.py")



