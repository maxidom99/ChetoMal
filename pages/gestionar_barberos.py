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
st.set_page_config(page_title="Panel de Gestión", page_icon="✂️", layout="wide")

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

def load_services():
    """Cargar la lista de servicios de la base de datos."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, nombre, precio, baja FROM servicios")
    servicios_data = cursor.fetchall()

    servicios_df = pd.DataFrame(servicios_data, columns=["id", "nombre", "precio", "baja"])
    
    cursor.close()
    conn.close()
    return servicios_df

def add_service(nombre, precio):
    """Agregar un nuevo servicio a la base de datos."""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """INSERT INTO servicios (nombre, precio) VALUES (%s, %s)"""
    cursor.execute(query, (nombre, precio))
    conn.commit()

    cursor.close()
    conn.close()

def load_employers():
    """Cargar la lista de barberos de la base de datos."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT Nombre, Rol, Activo, `fecha_alta`, `fecha_baja`, Baja FROM barberos")
    barbers_data = cursor.fetchall()

    barbers_df = pd.DataFrame(barbers_data, columns=["Nombre", "Rol", "Activo", "fecha_alta", "fecha_baja", "Baja"])
    
    cursor.execute("SELECT id, Nombre FROM socios")
    socios_data = cursor.fetchall()

    socios_df = pd.DataFrame(socios_data, columns=["id", "Nombre"])
    
    cursor.close()
    conn.close()
    return socios_df, barbers_df

def add_barber(nombre, rol, fecha_alta):
    """Agregar un nuevo barbero a la base de datos."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Estado por defecto "S" (activo) y "N" para "Baja"
    estado_inicial = "S"
    
    query = """
    INSERT INTO barberos (Nombre, Rol, Activo, Fecha_Alta, Fecha_Baja)
    VALUES (%s, %s, %s, %s, NULL)
    """
    cursor.execute(query, (nombre, rol, estado_inicial, fecha_alta))
    conn.commit()

    cursor.close()
    conn.close()
    
def add_socio(nombre):
    """Agregar un nuevo socio a la base de datos."""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO socios (Nombre)
    VALUES (%s)
    """
    cursor.execute(query, (nombre,))
    conn.commit()

    cursor.close()
    conn.close()

def update_employer_status(nombre, activo, baja):
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
    
def update_service_status(nombre, baja):
    """Actualizar el estado de un servicio en la base de datos."""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """UPDATE servicios SET baja = %s WHERE nombre = %s"""
    cursor.execute(query, (baja, nombre))
    
    conn.commit()
    cursor.close()
    conn.close()

def main():
    # Construye el menú lateral
    Navbar()

col1, col2 = st.columns(2)

with col1:
    bar = st.toggle("Gestionar Barberos")
    
with col2:
    ser = st.toggle("Gestionar Servicios")

# Mostrar la tabla actual
st.title("Panel de Gestión")
st.subheader('', divider='red')

if bar:
    #ser = True
    # Cargar la tabla de barberos y socios desde la base de datos
    socios_df, barberos_df = load_employers()
    # Formulario para agregar un nuevo empleado
    st.subheader("Agregar un Nuevo Empleado")
    with st.form(key="add_employer_form"):
        nuevo_nombre = st.text_input("Nombre del Empleado")
        nuevo_rol = st.selectbox("Rol", options=["Barbero", "Socio"])
        fecha_alta = st.date_input("Fecha de Alta", datetime.now())
        
        # Botón para enviar el formulario
        submit_button = st.form_submit_button(label="Agregar")

        # Si se envía el formulario, agregar el nuevo barbero o socio
        if submit_button:
            # Validar que el nombre no esté vacío
            if nuevo_nombre:
                if nuevo_rol == "Barbero":
                    add_barber(nuevo_nombre, nuevo_rol, fecha_alta)
                    st.success(f"Barbero '{nuevo_nombre}' agregado exitosamente.")
                else:
                    add_socio(nuevo_nombre)
                    st.success(f"Socio '{nuevo_nombre}' agregado exitosamente.")
                
                # Recargar los DataFrames después de agregar
                socios_df, barberos_df = load_employers()
            else:
                st.error("Por favor, ingresa un nombre válido para el empleado.")

    # Función para dar de baja a los barberos
    st.subheader("Activar/Dar de baja")

    # Loop por cada barbero en la tabla
    for index, row in barberos_df.iterrows():
        col1, col2 = st.columns([1.2, 1])
        
        with col1:
            st.write(f"Barbero: {row['Nombre']} | Activo: {row['Activo']} | Baja: {row['Baja']}")

        with col2:
            if row["Baja"] == "N":
                if st.button(f"Dar de baja {row['Nombre']}", key=f"baja_{index}"):
                    update_employer_status(row['Nombre'], "N", "S")
                    st.success(f"Barbero {row['Nombre']} dado de baja.")
                    # Recargar la lista de barberos
                    socios_df, barberos_df = load_employers()
            else:
                if st.button(f"Reactivar {row['Nombre']}", key=f"alta_{index}"):
                    update_employer_status(row['Nombre'], "S", "N")
                    st.success(f"Barbero {row['Nombre']} reactivado.")
                    # Recargar la lista de barberos
                    socios_df, barberos_df = load_employers()

    # Mostrar tablas actualizadas
    st.subheader("Lista de Barberos")
    st.dataframe(barberos_df, hide_index=True)

    st.subheader("Lista de Socios")
    st.dataframe(socios_df['Nombre'], hide_index=True)
        
if ser:
    st.subheader("Gestión de Servicios")
    
    servicios = load_services()
    
    with st.form(key="add_service_form"):
            nuevo_nombre = st.text_input("Nombre del Servicio")
            precio = st.number_input("Precio", min_value=0)
            
            # Botón para enviar el formulario
            submit_button = st.form_submit_button(label="Agregar")

            # Si se envía el formulario, agregar el nuevo barbero o socio
            if submit_button:
                # Validar que el nombre no esté vacío
                if nuevo_nombre:
                    add_service(nuevo_nombre, precio)
                    st.success(f"Servicio '{nuevo_nombre}' agregado exitosamente.")
                    
    
    # Función para dar de baja a los servicios
    st.subheader("Activar/Dar de baja")

    # Loop por cada servicio en la tabla
    for index, row in servicios.iterrows():
        col1, col2 = st.columns([0.6, 1.8])
        
        with col1:
            st.write(f"Servicio: {row['nombre']} ---------->")

        with col2:
            if row["baja"] == "N":
                if st.button(f"Dar de baja {row['nombre']}", key=f"baja_{index}_{row['nombre']}"):
                    baja = 'S'
                    update_service_status(row['nombre'], baja)
                    st.success(f"Servicio {row['nombre']} dado de baja.")
                    # Recargar la lista de barberos
                    servicios = load_services()
            else:
                if st.button(f"Reactivar {row['nombre']}", key=f"alta_{index}_{row['nombre']}"):
                    update_service_status(row['nombre'], "N")
                    st.success(f"Servicio {row['nombre']} reactivado.")
                    # Recargar la lista de barberos
                    servicios = load_services()
    
    st.divider()
    df = st.checkbox("Mostrar Listado")

    if df:
        st.dataframe(servicios, hide_index=True)

if __name__ == '__main__':
    main()