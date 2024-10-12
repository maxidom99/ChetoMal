import streamlit as st
import pandas as pd
from datetime import datetime
from modules.nav import Navbar
import mysql.connector
from dotenv import load_dotenv
import os

def main():
    Navbar()

# Cargar las variables de entorno
if 'STREAMLIT_ENV' not in os.environ:
    load_dotenv(dotenv_path='env/.env')

def get_db_connection():
    host = os.getenv("DB_HOST")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    database = os.getenv("DB_DATABASE")
    port = os.getenv("DB_PORT")
    return mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        port=int(port)
    )

st.set_page_config(page_title="Barbería", page_icon="💈", layout="wide")

def calcular_ingresos(servicio, precio, rol_barbero, nombre_barbero, socios):
    precio = float(precio) if isinstance(precio, (int, float)) else float(precio)
    barbero_ingreso = 0
    socios_ingreso = {socio['id']: 0 for socio in socios}  # Ingresos por socio ID

    if servicio == "Boyka":
        if nombre_barbero == "Boyka":
            barbero_ingreso = 0  # Todo para Boyka, pero no se le cuenta
            socios_ingreso[next(socio['id'] for socio in socios if socio['nombre'] == "Boyka")] = precio  # 100% para Boyka
    elif servicio == "Tatuaje":
        if "Juanma" in [socio['nombre'] for socio in socios]:
            for socio in socios:
                if socio['nombre'] == "Juanma":
                    socios_ingreso[socio['id']] = precio  # 100% para Juanma
    elif servicio == "Piercing":
        for socio in socios:
            socios_ingreso[socio['id']] = (0.50 * precio) / len(socios)  # 50% para cada socio
    else:  # Para los otros servicios
        if rol_barbero == "Barbero":
            barbero_ingreso = 0.50 * precio  # 50% para el barbero
            for socio in socios:
                socios_ingreso[socio['id']] = (0.25 * precio)  # 25% para cada socio
        elif rol_barbero == "Socio" and nombre_barbero != "Boyka":
            for socio in socios:
                socios_ingreso[socio['id']] = precio / len(socios)  # 100% dividido entre socios

    return barbero_ingreso, socios_ingreso

# Cargar los socios activos desde la base de datos
def obtener_socios():
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT id, nombre FROM socios"
    cursor.execute(query)
    socios = cursor.fetchall()
    conn.close()
    return [{"id": s[0], "nombre": s[1]} for s in socios]

# Obtener precios desde la base de datos
def obtener_precios():
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT nombre, precio FROM servicios"
    cursor.execute(query)
    servicios = cursor.fetchall()
    conn.close()
    return {s[0]: s[1] for s in servicios}

socios = obtener_socios()
precios = obtener_precios()

# Definir servicios permitidos por barbero y socio
servicios_por_barbero = {
    "Matias": ["Corte de Pelo", "Barba", "Corte y Barba", "Cejas", "Mechitas (C/Corte)", "Platinado (C/Corte)", "Baño de Color"],
    "Alejandro": ["Corte de Pelo", "Barba", "Corte y Barba", "Cejas", "Mechitas (C/Corte)", "Platinado (C/Corte)", "Baño de Color"]
}

servicios_por_socios = {
    "Boyka": ["Boyka"],
    "Sebastian": ["Piercing"],
    "Juanma": ["Tatuaje", "Piercing"]
}

st.title("😎 CHETO :blue[MAL] :sunglasses:")
st.subheader("Registro de Ventas", divider="rainbow")

# Conectar a la base de datos para obtener barberos
conn = get_db_connection()
cursor = conn.cursor()

# Obtener barberos activos
query = "SELECT id, nombre, rol FROM barberos WHERE activo = 'S' and baja = 'N'"
cursor.execute(query)
barberos_data = cursor.fetchall()
barberos_df = pd.DataFrame(barberos_data, columns=["id", "nombre", "rol"])

cursor.close()
conn.close()

# Verificar si hay barberos o socios disponibles
if not barberos_df.empty or socios:
    # Combinar los nombres de barberos y socios para la selección
    opciones = list(barberos_df['nombre']) + [s['nombre'] for s in socios]
    seleccion = st.selectbox("Selecciona el barbero o socio", opciones)

    # Determinar si la selección es un barbero o un socio
    if seleccion in barberos_df['nombre'].values:
        # El seleccionado es un barbero
        barbero_id = int(barberos_df.loc[barberos_df['nombre'] == seleccion, 'id'].values[0])
        rol_barbero = barberos_df.loc[barberos_df['nombre'] == seleccion, 'rol'].values[0]

        # Filtrar servicios según el barbero seleccionado
        servicios_permitidos = servicios_por_barbero.get(seleccion, [])
    else:
        # El seleccionado es un socio
        socio_id = next(s['id'] for s in socios if s['nombre'] == seleccion)
        rol_barbero = "Socio"

        # Filtrar servicios según el socio seleccionado
        servicios_permitidos = servicios_por_socios.get(seleccion, [])

    # Mostrar lista de servicios disponibles
    servicios_disponibles = [servicio for servicio in precios.keys() if servicio in servicios_permitidos]
    servicio_seleccionado = st.selectbox("Selecciona el servicio", servicios_disponibles)

    # Obtener el precio del servicio seleccionado
    precio = precios.get(servicio_seleccionado)
    if servicio_seleccionado in ["Tatuaje", "Boyka"]:
        precio = st.number_input(f"Ingresa el costo del servicio {servicio_seleccionado}", min_value=0)

    st.info(f"Precio del **{servicio_seleccionado}** ⮕ **${precio}**")

    # Capturar la fecha de la venta y el monto
    fecha = st.date_input("Fecha de la venta", datetime.now())
    monto = float(precio)

    # Calcular ingresos para el barbero o socio seleccionado
    barbero_ingreso, socios_ingreso = calcular_ingresos(servicio_seleccionado, precio, rol_barbero, seleccion, socios)

    if st.button("Registrar Venta"):
        # Conectar a la base de datos para registrar la venta
        conn = get_db_connection()
        cursor = conn.cursor()

        if rol_barbero == "Socio":
            # Si es un socio, se le pasa socio_id
            query_venta_socio = """
        INSERT INTO ventas (fecha, socio_id, servicio_id, monto)
        VALUES (%s, %s, (SELECT id FROM servicios WHERE nombre = %s), %s)
        """
            valores_venta = (fecha, socio_id, servicio_seleccionado, monto)
            cursor.execute(query_venta_socio, valores_venta)
            conn.commit()
        else:
            query_venta = """
        INSERT INTO ventas (fecha, barbero_id, servicio_id, monto)
        VALUES (%s, %s, (SELECT id FROM servicios WHERE nombre = %s), %s)
        """
            valores_venta = (fecha, barbero_id, servicio_seleccionado, monto)
            cursor.execute(query_venta, valores_venta)
            conn.commit()
        

        # Obtener el ID de la venta registrada
        venta_id = cursor.lastrowid

        # Registrar los ingresos de los socios
        for socio_id, ingreso in socios_ingreso.items():
            if ingreso > 0:
                query_ingreso_socio = """
                INSERT INTO ingresos_socios (venta_id, socio_id, monto)
                VALUES (%s, %s, %s)
                """
                valores_ingreso_socio = (venta_id, socio_id, ingreso)
                cursor.execute(query_ingreso_socio, valores_ingreso_socio)

        conn.commit()
        cursor.close()
        conn.close()

        st.success("Venta registrada correctamente")
else:
    st.warning("No hay barberos o socios activos disponibles.")

if __name__ == '__main__':
    main()
