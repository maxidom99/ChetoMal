import streamlit as st
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()  

st.set_page_config(page_title="Iniciar sesion", page_icon="✂️", layout="wide")

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

def check_credentials(username, password):
    conn = get_db_connection()
    if conn is None:
        return False  # Si no se puede conectar, no se puede verificar

    cursor = conn.cursor()
    query = "SELECT * FROM usuarios WHERE username = %s AND password = %s"
    cursor.execute(query, (username, password))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    return user is not None

def main():
    st.title("Inicio de Sesión")  

    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("Iniciar Sesión"):
        if check_credentials(username, password):
            st.success("Inicio de sesión exitoso!")
            st.balloons()  
            return True  
        else:
            st.error("Usuario o contraseña incorrectos. Inténtalo de nuevo.")
    return False 

if __name__ == '__main__':
    main()