import streamlit as st
import pandas as pd
from datetime import datetime
from modules.nav import Navbar

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
st.title("😎 CHETO :blue[MAL] :sunglasses:")

st.divider()

st.subheader("Registro de Ventas", divider="rainbow")

fecha_actual = datetime.now()
año_actual = fecha_actual.year

# Cargar barberos para asignar el rol
try:
    barberos_df = pd.read_csv('data/barberos.csv')
except FileNotFoundError:
    st.error("El archivo de barberos no se encontró.")
    barberos_df = pd.DataFrame(columns=["Nombre", "Rol", "Estado", "Fecha Alta", "Fecha Baja"])

# Verifica si hay barberos en el archivo cargado
if not barberos_df.empty:
    barberos = barberos_df[barberos_df['Activo'] == 'S']["Nombre"].tolist()
    
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
        rol_barbero = barberos_df.loc[barberos_df['Nombre'] == barbero, 'Rol']

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

            # Guardar la venta
            if st.button("Registrar Venta"):
                nueva_venta = pd.DataFrame({
                    "Fecha": [fecha],
                    "Barbero": [barbero],
                    "Servicio": [servicio],
                    "Monto": [monto],
                    "Barbero Ingreso": [barbero_ingreso],
                    "Socios Ingreso": [socios_ingreso],
                    "Descripción": [descripcion]  # Agregar la descripción aquí
                })

                try:
                    ventas = pd.read_csv(f'data/ventas_{año_actual}.csv')
                except FileNotFoundError:
                    ventas = pd.DataFrame(columns=["Fecha", "Barbero", "Servicio", "Monto", "Barbero Ingreso", "Socios Ingreso", "Descripción"])

                # Eliminar columnas vacías o completamente NA antes de concatenar
                nueva_venta = nueva_venta.dropna(axis=1, how='all')
                ventas = pd.concat([ventas, nueva_venta], ignore_index=True)
                ventas.to_csv(f'data/ventas_{año_actual}.csv', index=False)
                st.success("Venta registrada correctamente")
    else:
        st.warning("No hay barberos activos disponibles.")
else:
    st.warning("No hay datos de barberos disponibles.")

if __name__ == '__main__':
    main()
