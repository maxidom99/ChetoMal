import streamlit as st
import pandas as pd
from datetime import datetime
from modules.nav import Navbar
import mysql.connector
from dotenv import load_dotenv
import os


# Configuración de la página
st.set_page_config(page_title="Barbería", page_icon="💈", layout="wide")

# Cargar las variables de entorno solo si no están en producción
if 'STREAMLIT_ENV' not in os.environ:
    load_dotenv(dotenv_path='env/.env')

def get_db_connection():
    host = os.getenv("DB_HOST")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    database = os.getenv("DB_DATABASE")
    port = os.getenv("DB_PORT")

    if port is None:
        raise ValueError("DB_PORT no está definido en el archivo .env.")

    return mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        port=int(port)
    )

def main():


    # Construye el menú lateral
    Navbar()

    # Resto de tu lógica de aplicación...
    precios = {
        "Corte de Pelo": 300,
        "Barba": 150,
        "Corte y Barba": 400,
        "Cejas": 100,
        "Mechitas (C/Corte)": 1190,
        "Platinado (C/Corte)": 1500,
        "Baño de Color": 300,
        "Piercing": 800,
        "Tatuaje": 0  # El precio de los tatuajes es variable
    }

    # Resto del código para manejar el registro de ventas...
    st.title("😎 CHETO :blue[MAL] :sunglasses:")
    st.subheader("Registro de Ventas", divider="rainbow")

if __name__ == '__main__':
    main()
