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
    port = os.getenv("DB_PORT")  # Esto podría ser None si no está definido correctamente

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

st.set_page_config(page_title="Barbería", page_icon="💈")

def main():
    # Construye el menú lateral
    Navbar()

# Definir precios fijos de los servicios
precios = {
    "Corte de Pelo": 300,
    "Corte de Barba": 200,
    "Pelo y Barba": 350,
    "Tatuaje": 0  # El precio de los tatuajes es variable
}

# Formulario de registro
#st.logo("img/ChetoMal.jpg")
st.title("😎 CHETO :blue[MAL] :sunglasses:")


st.subheader("Registro de Ventas", divider="rainbow")

fecha_actual = datetime.now()
año_actual = fecha_actual.year

# # Cargar barberos para asignar el rol
# try:
#     barberos_df = pd.read_csv('data/barberos.csv')
# except FileNotFoundError:
#     st.error("El archivo de barberos no se encontró.")
#     barberos_df = pd.DataFrame(columns=["nombre", "rol", "Estado", "Fecha Alta", "Fecha Baja"])

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
        servicio = st.selectbox("Selecciona el servicio", ["Corte de Pelo", "Corte de Barba", "Pelo y Barba", "Tatuaje", "Otro"])

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

        if servicio == "Otro":
            descripcion = st.text_input("Descripción del servicio")
            precio = st.number_input("Ingresa el costo del servicio 'Otro'", min_value=0)

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
        if rol_barbero:
            if servicio == "Tatuaje" or servicio == "Otro":
                barbero_ingreso = 0  # Estos servicios no generan ingresos para los barberos
                socios_ingreso = precio  # Todo para los socios
            else:
                if rol_barbero == "Barbero":
                    barbero_ingreso = 0.50 * precio  # 50% para el barbero
                    socios_ingreso = 0.50 * precio  # 50% para los socios
                else:  # Si es Socio
                    barbero_ingreso = 0.00  # No recibe comisión
                    socios_ingreso = precio  # Todo para los socios

            # Registrar Venta en MySQL
            if st.button("Registrar Venta"):
                nueva_venta = {
                    "fecha": fecha,
                    "barbero": barbero,
                    "servicio": servicio,
                    "monto": monto,
                    "barbero_ingreso": barbero_ingreso,
                    "socios_ingreso": socios_ingreso,
                    "descripcion": descripcion if servicio == "Otro" else None  # Descripción solo para "Otro"
                }

                # Conectar a la base de datos
                conn = get_db_connection()
                cursor = conn.cursor()

                # Insertar los datos de la venta en la tabla 'ventas'
                query = """
                INSERT INTO ventas (fecha, barbero, servicio, monto, barbero_ingreso, socios_ingreso, descripcion)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (nueva_venta['fecha'], nueva_venta['barbero'], nueva_venta['servicio'],
                                    nueva_venta['monto'], nueva_venta['barbero_ingreso'], nueva_venta['socios_ingreso'],
                                    nueva_venta['descripcion']))

                # Guardar cambios y cerrar conexión
                conn.commit()
                cursor.close()
                conn.close()

                st.success("Venta registrada correctamente")
                
    else:
        st.warning("No hay barberos activos disponibles.")
else:
    st.warning("No hay datos de barberos disponibles.")

if __name__ == '__main__':
    main()
