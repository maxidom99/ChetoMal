import streamlit as st

def Navbar():
    # builds the sidebar menu
    with st.sidebar:
        st.page_link('app.py', label='Inicio', icon='🔥')
        st.page_link('pages/gestionar_barberos.py', label='Gestion Barberos', icon='🔍')
        st.page_link('pages/dashboard.py', label='Dashboard', icon='📊')
        st.page_link('pages/login.py', label='Inicio sesion', icon='📊')
        st.divider()
        st.image("img/ChetoMal.jpg", width=230)