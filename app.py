import json
import streamlit as st
import pandas as pd
from datetime import datetime
from modules.nav import Navbar
import mysql.connector
from dotenv import load_dotenv
import os

# Cargar las variables de entorno solo si no están en producción
if 'STREAMLIT_ENV' not in os.environ:
    load_dotenv(dotenv_path='env/.env')

def get_db_connection():
    # Verificar que todas las variables necesarias estén disponibles
    host = os.getenv("DB_HOST")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    database = os.getenv("DB_DATABASE")
    port = os.getenv("DB_PORT")

    # Imprimir para depuración (opcional)
    #print(f"Host: {host}, User: {user}, Database: {database}, Port: {port}")

    if port is None:
        raise ValueError("DB_PORT no está definido en el archivo .env.")

    return mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        port=int(port)  # Convertir a entero
    )

st.set_page_config(page_title="Barbería", page_icon="💈", layout="wide")

def main():
    # Construye el menú lateral
    Navbar()

def calcular_ingresos(servicio, precio, rol_barbero, nombre_barbero, socios):
    barbero_ingreso = 0
    socios_ingreso = {socio: 0 for socio in socios}  # Inicializar ingresos en 0 para cada socio

    if servicio == "Boyka":
        # Si el servicio es "Boyka", el 100% va al barbero llamado "Boyka"
        if nombre_barbero == "Boyka":
            barbero_ingreso = precio  # Todo para el barbero Boyka
        else:
            barbero_ingreso = 0  # Ningún otro barbero recibe ingresos si no es Boyka
    elif servicio == "Tatuaje":
        # Si el servicio es "Tatuaje", el 100% va al socio llamado "Juanma"
        if "Juanma" in socios:
            socios_ingreso["Juanma"] = precio  # Todo para Juanma
    elif servicio == "Piercing" and nombre_barbero != "Boyka":
        # Si el servicio es "Piercing", el 50% se divide entre los socios
        for socio in socios:
            socios_ingreso[socio] = (0.50 * precio) / len(socios)  # 50% repartido entre los socios
    else:
        # Cualquier otro servicio
        if rol_barbero == "Barbero":
            barbero_ingreso = 0.50 * precio  # 50% para el barbero
            for socio in socios:
                socios_ingreso[socio] = (0.50 * precio) / len(socios)  # 50% repartido entre socios
        elif rol_barbero == "Socio" and nombre_barbero != "Boyka":
            # El socio no recibe comisión de barbero, todo va para los socios
            for socio in socios:
                socios_ingreso[socio] = precio / len(socios)  # Todo para los socios, dividido

    return barbero_ingreso, socios_ingreso

socios = ["Juanma", "Sebastian"]

# Definir precios fijos de los servicios
precios = {
    "Corte de Pelo": 300,
    "Barba": 150,
    "Corte y Barba": 400,
    "Cejas": 100,
    "Mechitas (C/Corte)": 1190,
    "Platinado (C/Corte)": 1500,
    "Baño de Color":300,
    "Piercing": 800,
    "Boyka" : 0,
    "Tatuaje": 0
}


st.title("😎 CHETO :blue[MAL] :sunglasses:")


st.subheader("Registro de Ventas", divider="rainbow")

fecha_actual = datetime.now()
año_actual = fecha_actual.year

# Conectar a la base de datos para obtener barberos
conn = get_db_connection()
cursor = conn.cursor()

# Consulta SQL para obtener barberos activos
query = "SELECT nombre, rol, activo FROM barberos WHERE activo = 'S' and baja = 'N'"
cursor.execute(query)

# Cargar los resultados en un DataFrame
barberos_data = cursor.fetchall()
barberos_df = pd.DataFrame(barberos_data, columns=["nombre", "rol", "activo"])

# Cerrar la conexión
cursor.close()
conn.close()

# Verifica si hay barberos en el archivo cargado
if not barberos_df.empty:
    barberos = barberos_df[barberos_df['activo'] == 'S']["nombre"].tolist()
    
    if len(barberos) > 0:
        barbero = st.selectbox("Selecciona el barbero", barberos)
        servicio = st.selectbox("Selecciona el servicio", ["Corte de Pelo", "Corte de Barba", "Corte y Barba", "Cejas","Mechitas (C/Corte)","Platinado (C/Corte)", "Baño de Color", "Tatuaje", "Boyka", "Piercing"])

        # Inicializar la variable de precio y descripción
        precio = None
        descripcion = ""

        # Mostrar el precio correspondiente al servicio seleccionado
        if servicio in precios:
            if servicio == "Tatuaje":
                precio = st.number_input("Ingresa el costo del tatuaje", min_value=0)
            else:
                precio = precios[servicio]

        # Mostrar precio del servicio
        if precio is not None:
            st.markdown(f"### Precio del servicio **{servicio}:** ${precio}")

        if servicio == "Boyka":
            descripcion = st.text_input("Descripción del servicio")
            precio = st.number_input("Ingresa el costo del servicio", min_value=0)

        fecha = st.date_input("Fecha de la venta", datetime.now())
        monto = precio

        # Cálculo de ingresos basado en el rol del barbero
        rol_barbero = barberos_df.loc[barberos_df['nombre'] == barbero, 'rol']

        # Verificar si existe el rol para el barbero seleccionado
        if not rol_barbero.empty:
            rol_barbero = rol_barbero.values[0]
        else:
            st.error("El barbero seleccionado no tiene un rol asignado.")
            rol_barbero = None
        
        # Lógica para calcular los ingresos según el rol
        
        barbero_ingreso, socios_ingreso = calcular_ingresos(servicio, precio, rol_barbero, barbero, socios)
        print(f"Ingreso para el barbero: {barbero_ingreso}")
        print(f"Ingresos para los socios: {socios_ingreso}")


        # Registrar Venta en MySQL
        if st.button("Registrar Venta"):
            nueva_venta = {
                "fecha": fecha,
                "barbero": barbero,
                "servicio": servicio,
                "monto": monto,
                "barbero_ingreso": barbero_ingreso,
                "socios_ingreso": socios_ingreso,
                "descripcion": descripcion if servicio == "Otro" or servicio == 'Boyka' else None  
            }

            # Convertir el diccionario 'socios_ingreso' a JSON
            socios_ingreso_json = json.dumps(nueva_venta['socios_ingreso'])

            # Conectar a la base de datos
            conn = get_db_connection()
            cursor = conn.cursor()

            # Insertar los datos de la venta en la tabla 'ventas'
            query = """
            INSERT INTO ventas (fecha, barbero, servicio, monto, barbero_ingreso, socios_ingreso, descripcion)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            valores = (
                nueva_venta['fecha'], 
                nueva_venta['barbero'], 
                nueva_venta['servicio'],
                nueva_venta['monto'], 
                nueva_venta['barbero_ingreso'], 
                socios_ingreso_json,  # Guardar como JSON
                nueva_venta['descripcion']
            )
            
            cursor.execute(query, valores)
            conn.commit()  # No olvides confirmar la transacción
            cursor.close()
            conn.close()


            st.success("Venta registrada correctamente")
                
    else:
        st.warning("No hay barberos activos disponibles.")
else:
    st.warning("No hay datos de barberos disponibles.")

if __name__ == '__main__':
    main()
