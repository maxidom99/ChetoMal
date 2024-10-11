import streamlit as st
import mysql.connector
from dotenv import load_dotenv
from modules.nav import Navbar
import os

load_dotenv()  

st.set_page_config(page_title="Inicio de Sesión", page_icon="✂️", layout="wide")

# Obtener la conexión a la base de datos
def get_db_connection():
    try:
        return mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_DATABASE"),
            port=int(os.getenv("DB_PORT"))
        )
    except mysql.connector.Error as err:
        st.error(f"Error al conectar a la base de datos: {err}")
        return None

# Verificar las credenciales
def check_credentials(username, password):
    conn = get_db_connection()
    if conn is None:
        return None  # Si no se puede conectar, retornar None

    cursor = conn.cursor()
    query = "SELECT * FROM usuarios WHERE username = %s AND password = %s"
    cursor.execute(query, (username, password))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    return user  # Retorna el usuario si existe, None si no

# Mostrar el dashboard una vez logueado
def show_dashboard():
    st.title("Dashboard")
    
    if 'username' in st.session_state:
        st.write(f"Bienvenido, **{st.session_state['username']}**")
    else:
        st.write("Bienvenido al dashboard")

# Manejar la lógica de inicio de sesión
def main():
    Navbar()

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        show_dashboard()  # Mostrar el dashboard si ya está logueado
    else:
        st.title("Inicio de Sesión")  
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")

        if st.button("Iniciar Sesión"):
            user = check_credentials(username, password)
            if user:
                st.success("Inicio de sesión exitoso!")
                st.balloons()
                
                # Guardar estado de sesión
                st.session_state.logged_in = True
                st.session_state.username = user[1]  # Asume que el nombre está en el índice 1
                st.experimental_rerun()  # Redirigir al dashboard
            else:
                st.error("Usuario o contraseña incorrectos. Inténtalo de nuevo.")

if __name__ == '__main__':
    main()
