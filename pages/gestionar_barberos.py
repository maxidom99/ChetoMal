import streamlit as st
import pandas as pd
from datetime import datetime
from modules.nav import Navbar
import mysql.connector
from dotenv import load_dotenv
import os

# Cargar las variables de entorno
load_dotenv(dotenv_path='env/.env')

# Configuración de la página
st.set_page_config(page_title="Gestión de Barberos", page_icon="✂️", layout="wide")

def get_db_connection():
    """Establecer la conexión a la base de datos."""
    host = os.getenv("DB_HOST")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    database = os.getenv("DB_DATABASE")
    port = int(os.getenv("DB_PORT"))

    return mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        port=port
    )

def load_barbers():
    """Cargar la lista de barberos de la base de datos."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT Nombre, Rol, Activo, `fecha_alta`, `fecha_baja`, Baja FROM barberos")
    barbers_data = cursor.fetchall()

    barbers_df = pd.DataFrame(barbers_data, columns=["Nombre", "Rol", "Activo", "fecha_alta", "fecha_baja", "Baja"])
    
    cursor.close()
    conn.close()
    return barbers_df

def add_barber(nombre, rol, fecha_alta):
    """Agregar un nuevo barbero a la base de datos."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Estado por defecto "S" (activo) y "N" para "Baja"
    estado_inicial = "S"
    baja_inicial = "N"
    
    query = """
    INSERT INTO barberos (Nombre, Rol, Activo, Fecha_Alta, Fecha_Baja)
    VALUES (%s, %s, %s, %s, NULL)
    """
    cursor.execute(query, (nombre, rol, estado_inicial, fecha_alta))
    conn.commit()

    cursor.close()
    conn.close()

def update_barber_status(nombre, activo, baja):
    """Actualizar el estado de un barbero en la base de datos."""
    conn = get_db_connection()
    cursor = conn.cursor()

    if activo == "N":
        query = """
        UPDATE barberos
        SET Activo = %s, Baja = %s, `fecha_baja` = %s
        WHERE Nombre = %s
        """
        cursor.execute(query, (activo, baja, datetime.now().strftime("%Y-%m-%d"), nombre))
    else:
        query = """
        UPDATE barberos
        SET Activo = %s, Baja = %s, `fecha_baja` = NULL
        WHERE Nombre = %s
        """
        cursor.execute(query, (activo, baja, nombre))
    
    conn.commit()
    cursor.close()
    conn.close()

def main():
    # Construye el menú lateral
    Navbar()

    # Cargar la tabla de barberos desde la base de datos
    barberos_df = load_barbers()

    # Mostrar la tabla actual
    st.title("Gestión de Barberos")
    st.subheader("Tabla de Barberos")
    st.dataframe(barberos_df)

    # Formulario para agregar un nuevo barbero
    st.subheader("Agregar un Nuevo Barbero")
    with st.form(key="add_barbero_form"):
        nuevo_nombre = st.text_input("Nombre del Barbero")
        nuevo_rol = st.selectbox("Rol", options=["Barbero", "Socio"])
        fecha_alta = st.date_input("Fecha de Alta", datetime.now())
        
        # Botón para enviar el formulario
        submit_button = st.form_submit_button(label="Agregar")

        # Si se envía el formulario, agregar el nuevo barbero
        if submit_button:
            add_barber(nuevo_nombre, nuevo_rol, fecha_alta)
            st.success(f"Barbero '{nuevo_nombre}' agregado exitosamente.")
            # Recargar la lista de barberos
            barberos_df = load_barbers()
            st.dataframe(barberos_df)

    # Función para dar de baja a los barberos
    st.subheader("Activar/Dar de baja Barberos")

    # Loop por cada barbero en la tabla
    for index, row in barberos_df.iterrows():
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.write(f"Barbero: {row['Nombre']} | Estado: {row['Activo']} | Baja: {row['Baja']}")

        with col2:
            if row["Baja"] == "N":
                if st.button(f"Dar de baja {row['Nombre']}", key=f"baja_{index}"):
                    update_barber_status(row['Nombre'], "N", "S")
                    st.success(f"Barbero {row['Nombre']} dado de baja.")
                    # Recargar la lista de barberos
                    barberos_df = load_barbers()
            else:
                if st.button(f"Reactivar {row['Nombre']}", key=f"alta_{index}"):
                    update_barber_status(row['Nombre'], "S", "N")
                    st.success(f"Barbero {row['Nombre']} reactivado.")
                    # Recargar la lista de barberos
                    barberos_df = load_barbers()

if __name__ == '__main__':
    main()
