import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from app import get_db_connection
from datetime import datetime
from modules.nav import Navbar

st.set_page_config(page_title="Dashboard", layout="wide")
# Configurar la página y el título del dashboard

def main():
    Navbar()
    
# Obtener año, mes y día actuales
fecha_actual = datetime.now()
año_actual = fecha_actual.year
mes_actual = fecha_actual.month
día_actual = fecha_actual.day

# Cargar las ventas registradas
try:
# Leer ventas desde MySQL
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM ventas")
    ventas_sql = cursor.fetchall()

    # Convertir los resultados a un DataFrame de pandas
    ventas = pd.DataFrame(ventas_sql)
    try:
        ventas['fecha'] = pd.to_datetime(ventas['fecha'])
    except:
        pass
    
    # Cerrar conexión
    cursor.close()
    conn.close()
except FileNotFoundError:
    st.warning("No se han registrado ventas todavía.")
    try:
        ventas = pd.DataFrame(columns=["fecha", "barbero", "servicio", "monto", "barbero_ingreso", "socios_ingreso"])
        ventas['fecha'] = ventas['fecha'].dt.date
    except:
        pass

# Título del dashboard
st.title("Dashboard de Barbería")
#st.markdown("### Visualización de ingresos y ventas")

# Calcular las métricas de ingresos
if not ventas.empty:
    # Suma de ingresos totales
    ingresos_totales = ventas['monto'].sum()

    # Suma de ingresos de tatuajes
    ingresos_tatuajes = ventas[ventas['servicio'] == 'Tatuaje']['monto'].sum()

    # Suma de ingresos de socios
    ingresos_socios = ventas['socios_ingreso'].astype(int).sum()

    # Suma de ingresos por barbero (sólo los ingresos de los barberos)
    ingresos_barberos = ventas.groupby('barbero')['barbero_ingreso'].sum()

    # Mostrar métricas en el dashboard
    st.markdown("### Métricas de Ingresos")

 # Configuración de las columnas para las métricas
    col1, col2, col3 = st.columns(3)

    # Mostrar las métricas
    col1.metric(label="Ingresos Totales", value=f"${int(ingresos_totales)}")
    col2.metric(label="Ingresos por Tatuajes", value=f"${int(ingresos_tatuajes)}")
    col3.metric(label="Ingresos de Socios", value=f"${int(ingresos_socios)}")

    # Calcular ingresos filtrados por el año actual, mes actual y día actual
    ingresos_año_actual = ventas[ventas['fecha'].dt.year == año_actual]['monto'].sum()
    ingresos_mes_actual = ventas[(ventas['fecha'].dt.year == año_actual) & 
                                (ventas['fecha'].dt.month == mes_actual)]['monto'].sum()
    ingresos_día_actual = ventas[(ventas['fecha'].dt.year == año_actual) & 
                                (ventas['fecha'].dt.month == mes_actual) & 
                                (ventas['fecha'].dt.day == día_actual)]['monto'].sum()

    # Mostrar sumas filtradas
    st.markdown("### Ingresos Filtrados")
    col4, col5, col6 = st.columns(3)
    col4.metric(label="Ingresos Año Actual", value=f"${int(ingresos_año_actual)}")
    col5.metric(label="Ingresos Mes Actual", value=f"${int(ingresos_mes_actual)}")
    col6.metric(label="Ingresos Día Actual", value=f"${int(ingresos_día_actual)}")

    st.divider()
    # Crear tres columnas: barberos, divisor y socios
    col_barberos, col_divider, col_socios = st.columns([1, 0.1, 1])  # Ajustar tamaño de divisor
    st.divider()
    with col_barberos:
        st.subheader("Ingresos de Barberos")
        for barbero, ingreso in ingresos_barberos.items():
            if ingreso > 0:  # Mostrar solo aquellos que tengan ingresos
                st.metric(label=f"Ingreso de {barbero}", value=f"${int(ingreso)}")

    # Divisor vertical
    with col_divider:
        st.markdown("<div style='border-left: 10px solid white; height: 100%;'></div>", unsafe_allow_html=True)

    with col_socios:
        st.subheader("Ingresos de Socios")
        # Filtrar solo los empleados que son socios
        socios = barberos[barberos['Rol'] == 'Socio']['Nombre']
        ingresos_socios = ventas.groupby('barbero')['socios_ingreso'].sum()
        
        # Mostrar solo ingresos de aquellos que son socios
        for socio, ingreso in ingresos_socios.items():
            if ingreso > 0 and socio in socios.values:  # Mostrar solo ingresos de los socios
                st.metric(label=f"Ingreso de {socio}", value=f"${int(ingreso)}")

# Gráficos
col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

# Gráfico 1: Ventas por Mes
with col1:
    st.subheader("Ventas por Mes")
    if not ventas.empty:
        ventas['monto'] = pd.to_numeric(ventas['monto'], errors='coerce')
        ventas['Mes'] = ventas['fecha'].dt.to_period('M')  # Extraer el mes
        ventas_mes = ventas.groupby('Mes')['monto'].sum()
        fig, ax = plt.subplots()
        ventas_mes.plot(kind='bar', ax=ax, color='blue')
        ax.set_title("Ventas Totales por Mes")
        ax.set_xlabel("Mes")
        ax.set_ylabel("Total Ventas")
        plt.xticks(rotation=45)
        st.pyplot(fig)
    else:
        st.warning("No hay datos para mostrar las ventas por mes.")

# Gráfico 2: Ventas por Barbero
with col2:
    st.subheader("Ventas por Barbero")
    if not ventas.empty:
        ventas_barbero = ventas.groupby('barbero')['monto'].sum()
        fig, ax = plt.subplots()
        ventas_barbero.plot(kind='bar', ax=ax, color='green')
        ax.set_title("Ventas Totales por Barbero")
        ax.set_xlabel("Barbero")
        ax.set_ylabel("Total Ventas")
        plt.xticks(rotation=45)
        st.pyplot(fig)
    else:
        st.warning("No hay datos para mostrar las ventas por barbero.")

# Gráfico 3: Ventas por servicio
with col3:
    st.subheader("Ventas por servicio")
    if not ventas.empty:
        ventas_servicio = ventas.groupby('servicio')['monto'].sum()
        fig, ax = plt.subplots()
        ventas_servicio.plot(kind='bar', ax=ax, color='orange')
        ax.set_title("Ventas Totales por servicio")
        ax.set_xlabel("servicio")
        ax.set_ylabel("Total Ventas")
        plt.xticks(rotation=45)
        st.pyplot(fig)
    else:
        st.warning("No hay datos para mostrar las ventas por servicio.")

# Gráfico 4: Distribución de Ingresos por Persona Activa
with col4:
    st.subheader("Distribución de Ingresos por Persona Activa")
    if not ventas.empty:
        # Sumar ingresos totales por cada persona, considerando todos los ingresos
        ingresos_totales = ventas.groupby('barbero')['barbero_ingreso'].sum() + ventas.groupby('barbero')['socios_ingreso'].sum()
        
        # Asegurarse de que la información de barberos esté actualizada
        ingresos_totales = ingresos_totales.fillna(0)  # Reemplaza NaN por 0
        ingresos_totales = ingresos_totales[ingresos_totales > 0]  # Mantener solo ingresos positivos
        
        # Verificar que no haya valores NaN
        if ingresos_totales.empty:
            st.warning("No hay ingresos para mostrar en el gráfico.")
        else:
            fig, ax = plt.subplots()
            ax.pie(ingresos_totales, labels=ingresos_totales.index, autopct='%1.1f%%', startangle=90, colors=plt.cm.tab20.colors)
            ax.axis('equal')  # Para mantener la relación de aspecto
            ax.set_title("Distribución de Ingresos por Persona Activa")
            st.pyplot(fig)
    else:
        st.warning("No hay datos suficientes para mostrar la distribución de ingresos.")


st.divider()
if not ventas.empty:
    st.subheader("Filtrado y Extracción")
    # Filtrar por rango de fechas
    filtro_rango_fecha = st.date_input("Filtrar por rango de fechas", [])
    if len(filtro_rango_fecha) == 2:
        fecha_inicio, fecha_fin = filtro_rango_fecha
        ventas = ventas[(ventas['fecha'] >= pd.to_datetime(fecha_inicio)) & (ventas['fecha'] <= pd.to_datetime(fecha_fin))]

    # Filtrado de datos
    st.subheader("Filtros")
    filtro_barbero = st.multiselect("Filtrar por barbero", options=ventas['barbero'].unique())
    filtro_servicio = st.multiselect("Filtrar por servicio", options=ventas['servicio'].unique())

    # Aplicar filtros
    if filtro_barbero:
        ventas = ventas[ventas['barbero'].isin(filtro_barbero)]
    if filtro_servicio:
        ventas = ventas[ventas['servicio'].isin(filtro_servicio)]

    # Mostrar los datos filtrados
    st.markdown("### Datos Filtrados")
    mostrar_datos = st.checkbox("Mostrar tabla de datos", value=False)
    if mostrar_datos:
        if not ventas.empty:
            ventas['fecha'] = ventas['fecha'].dt.date
            st.dataframe(ventas, hide_index=True)
        else:
            st.warning("No hay datos para mostrar con los filtros aplicados.")

    # Exportar a CSV
    if st.button("Exportar a CSV"):
        if not ventas.empty:
            fecha_hoy = datetime.now().strftime("%d-%m-%Y")
            ventas.to_csv(f"Facturacion_Filtrada_{fecha_hoy}.csv", index=False)
            st.success(f"Archivo exportado como Factura_{fecha_hoy}.csv")
        else:
            st.warning("No hay datos para exportar con los filtros aplicados.")
else:
        st.warning("No hay datos suficientes para filtrar.")


if __name__ == '__main__':
    main()
