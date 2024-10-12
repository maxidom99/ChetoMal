import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from modules.nav import Navbar
from app import get_db_connection

def main():
    Navbar()

# Obtener año, mes y día actuales
fecha_actual = datetime.now()
año_actual = fecha_actual.year
mes_actual = fecha_actual.month
día_actual = fecha_actual.day

def cargar_ventas():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
        SELECT v.*, so.nombre AS socio, b.nombre AS barbero, s.nombre AS servicio, ing.monto AS socios_ingreso
        FROM ventas v
        LEFT JOIN socios so ON so.id = v.socio_id
        LEFT JOIN barberos b ON b.id = v.barbero_id
        LEFT JOIN servicios s ON v.servicio_id = s.id
        LEFT JOIN ingresos_socios ing ON v.id = ing.venta_id AND ing.socio_id = so.id
        """
        cursor.execute(query)
        ventas_sql = cursor.fetchall()
        cursor.close()
        conn.close()

        # Convertir el resultado en un DataFrame de pandas
        ventas = pd.DataFrame(ventas_sql)

        if 'fecha' in ventas.columns:
            ventas['fecha'] = pd.to_datetime(ventas['fecha'], errors='coerce')
            ventas['socio_id'] = ventas['socio_id'].fillna(0).astype(int)
            return ventas
        else:
            st.error("No hay ventas.")
            return pd.DataFrame()
        
    except Exception as e:
        st.error(f"Error cargando ventas: {e}")
        return pd.DataFrame(columns=["fecha", "barbero", "servicio", "monto", "socios_ingreso"])

def cargar_socios():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM socios")
        socios_sql = cursor.fetchall()
        cursor.close()
        conn.close()
        socios = pd.DataFrame(socios_sql)
        return socios
    except Exception as e:
        st.error(f"Error cargando socios: {e}")
        return pd.DataFrame(columns=["id", "nombre"])
    
def cargar_barbero():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM barberos")
        socios_sql = cursor.fetchall()
        cursor.close()
        conn.close()
        socios = pd.DataFrame(socios_sql)
        return socios
    except Exception as e:
        st.error(f"Error cargando socios: {e}")
        return pd.DataFrame(columns=["id", "nombre","rol", "activo"])

# Cargar los datos
ventas = cargar_ventas()
socios = cargar_socios()
barberos = cargar_barbero()

# Mostrar título
st.title("Dashboard de Barbería")

# Calcular métricas de ingresos si hay datos de ventas
if not ventas.empty and 'fecha' in ventas.columns:
    ventas['monto'] = pd.to_numeric(ventas['monto'], errors='coerce')

    # Crear columnas para los ingresos de los socios según el servicio
    ventas['ingreso_juanma'] = 0
    ventas['ingreso_sebastian'] = 0
    ventas['ingreso_boyka'] = 0
    ventas['ingreso_barbero'] = 0

    servicios_barberos = ["Corte de Pelo","Barba", "Corte y Barba", "Cejas", "Mechitas (C/Corte)", "Platinado (C/Corte)", "Baño de Color"]
    
    # Asignar ingresos de acuerdo a las reglas establecidas
    for idx, venta in ventas.iterrows():
        servicio = venta['servicio']
        monto = venta['monto']
        barbero = venta['barbero']
        socio = venta['socio']

        if servicio == 'Piercing':
            # 50% para Sebastián y 50% para Juanma
            ventas.at[idx, 'ingreso_juanma'] = float(monto * 0.5)
            ventas.at[idx, 'ingreso_sebastian'] = float(monto * 0.5)
        elif servicio in servicios_barberos:
            # 50% para el barbero, 25% para Sebastián, 25% para Juanma
            ventas.at[idx, 'ingreso_juanma'] = float(monto * 0.5)
            ventas.at[idx, 'ingreso_sebastian'] = float(monto * 0.5)
            ventas.at[idx, 'ingreso_barbero'] = float(monto * 0.5)
        elif servicio == 'Tatuaje':
            # 100% para Juanma
            ventas.at[idx, 'ingreso_juanma'] = float(monto)
        else:
            # Si es un servicio realizado por Boyka
            if socio == 'Boyka':
                ventas.at[idx, 'ingreso_boyka'] = float(monto)
            else:
                # Ingreso normal para el barbero
                ventas.at[idx, 'ingreso_barbero'] = float(monto)

    # Mostrar métricas de ingresos
    st.markdown("### Métricas de Ingresos")
    col1, col2, col3, col4 = st.columns(4)

    ingresos_totales = ventas['monto'].sum()
    # Calcular ingresos del día
    ingresos_dia = ventas[ventas['fecha'].dt.date == fecha_actual.date()]['monto'].sum()
    # Calcular ingresos de la semana
    ingresos_semana = ventas[ventas['fecha'] >= (fecha_actual - pd.Timedelta(days=7))]['monto'].sum()
    # Calcular ingresos del mes
    ingresos_mes = ventas[ventas['fecha'].dt.month == mes_actual]['monto'].sum()
    # Mostrar ingresos totales
    col1.metric("Ingresos Totales", f"${int(ingresos_totales)}")
    # Mostrar ingresos del día
    col2.metric("Ingresos del Día", f"${int(ingresos_dia)}")
    # Mostrar ingresos de la semana
    col3.metric("Ingresos Semanales", f"${int(ingresos_semana)}")
    # Mostrar ingresos del mes
    col4.metric("Ingresos Mensuales", f"${int(ingresos_mes)}")

    st.divider()

    # Mostrar ingresos de socios
    col_socios = st.columns(3)
    with col_socios[0]:
        st.subheader("Ingresos de Juanma")
        st.metric("Total", f"${int(ventas['ingreso_juanma'].sum())}")

    with col_socios[1]:
        st.subheader("Ingresos de Sebastián")
        st.metric("Total", f"${int(ventas['ingreso_sebastian'].sum())}")
    
    with col_socios[2]:
        st.subheader("Ingresos por Boyka")
        st.metric("Ingresos de Boyka", f"${int(ventas['ingreso_boyka'].sum())}")
    

    st.divider()
    
    # Ingresos por barbero
    st.subheader("Ingresos por Barbero")
    ingresos_barberos = ventas.groupby('barbero')['ingreso_barbero'].sum()
    for barbero, ingreso in ingresos_barberos.items():
        st.metric(f"Ingreso de {barbero}", f"${int(ingreso)}")

    # Graficos
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)

    # Gráfico 1: Ventas por Mes
    with col1:
        st.subheader("Ventas por Mes")
        ventas['Mes'] = ventas['fecha'].dt.to_period('M')
        ventas_mes = ventas.groupby('Mes')['monto'].sum()
        fig, ax = plt.subplots()
        ventas_mes.plot(kind='bar', ax=ax, color='blue')
        ax.set_title("Ventas Totales por Mes")
        plt.xticks(rotation=45)
        ax.set_xlabel("Mes")
        ax.set_ylabel("Total Ventas")
        st.pyplot(fig)


    # Gráfico 2: Ventas por Barbero
    with col2:
        st.subheader("Ventas por Barbero")
        ventas_barbero = ventas.groupby('barbero')['monto'].sum()
        fig, ax = plt.subplots()
        ventas_barbero.plot(kind='bar', ax=ax, color='green')
        ax.set_title("Ventas Totales por Barbero")
        ax.set_xlabel("Barbero")
        ax.set_ylabel("Total Ventas")
        plt.xticks(rotation=45)
        st.pyplot(fig)

    # Gráfico 3: Ventas por Servicio
    with col3:
        st.subheader("Ventas por Servicio")
        ventas_servicio = ventas.groupby('servicio')['monto'].sum()
        fig, ax = plt.subplots()
        ventas_servicio.plot(kind='bar', ax=ax, color='orange')
        ax.set_title("Ventas Totales por Servicio")
        ax.set_xlabel("Servicio")
        ax.set_ylabel("Total Ventas")
        plt.xticks(rotation=45)
        st.pyplot(fig)

    # Gráfico 4: Distribución de Ingresos por Persona Activa
    with col4:
        st.subheader("Distribución de Ingresos por Persona Activa")
        # Calcular ingresos totales para barberos
        ingresos_barberos = ventas.groupby('barbero')['ingreso_barbero'].sum().reindex(barberos['nombre'].tolist(), fill_value=0)
        # Calcular ingresos para socios
        ingresos_socios = ventas.groupby('socio_id').agg({'socios_ingreso': 'sum'}).reindex(socios['id'], fill_value=0)
        # Asignar nombres a los ingresos de socios
        ingresos_socios.index = socios['nombre'].tolist()
        # Crear un nuevo DataFrame con ambos ingresos
        ingresos_combinados = pd.concat([ingresos_barberos, ingresos_socios['socios_ingreso']]).dropna()

        if not ingresos_combinados.empty and ingresos_combinados.ndim == 1:
            # Crear el gráfico
            fig, ax = plt.subplots()
            ax.pie(ingresos_combinados, labels=ingresos_combinados.index, autopct='%1.1f%%', startangle=90, colors=plt.cm.tab20.colors)
            ax.axis('equal')  # Para que el gráfico sea un círculo
            ax.set_title("Distribución de Ingresos por Persona Activa")
            st.pyplot(fig)
        else:
            st.warning("No hay ingresos para mostrar en el gráfico.")

    st.divider()

    # Filtrado de datos
    st.subheader("Filtros y Exportación")
    filtro_rango_fecha = st.date_input("Filtrar por rango de fechas", [])
    if len(filtro_rango_fecha) == 2:
        fecha_inicio, fecha_fin = filtro_rango_fecha
        ventas = ventas[(ventas['fecha'] >= pd.to_datetime(fecha_inicio)) & (ventas['fecha'] <= pd.to_datetime(fecha_fin))]

    filtro_barbero = st.multiselect("Filtrar por barbero", options=ventas['barbero'].unique())
    filtro_socio = st.multiselect("Filtrar por socio", options=ventas['socio'].unique())
    filtro_servicio = st.multiselect("Filtrar por servicio", options=ventas['servicio'].unique())

    if filtro_barbero:
        ventas = ventas[ventas['barbero'].isin(filtro_barbero)]
    if filtro_socio:
        ventas = ventas[ventas['socio'].isin(filtro_socio)]
    if filtro_servicio:
        ventas = ventas[ventas['servicio'].isin(filtro_servicio)]

    mostrar_datos = st.checkbox("Mostrar tabla de datos", value=False)
    if mostrar_datos:
        ventas['fecha'] = pd.to_datetime(ventas['fecha']).dt.date
        st.dataframe(ventas[['fecha', 'monto','socio','barbero','servicio','socios_ingreso','ingreso_juanma','ingreso_sebastian','ingreso_boyka','ingreso_barbero','Mes']], hide_index=True)

    if st.button("Exportar a CSV"):
        fecha_hoy = datetime.now().strftime("%d-%m-%Y")
        ventas.to_csv(f"Facturacion_Filtrada_{fecha_hoy}.csv", index=False)
        st.success(f"Archivo exportado como Facturacion_Filtrada_{fecha_hoy}.csv")
        
else:
    st.warning("No se encontraron datos de ventas.")

if __name__ == '__main__':
    main()
