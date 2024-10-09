import streamlit as st
import pandas as pd
from datetime import datetime
from modules.nav import Navbar

st.set_page_config(page_title="Gestión de Barberos", page_icon="✂️")

def main():
    # Construye el menú lateral
    Navbar()

# Cargar o crear el archivo de barberos
try:
    barberos_df = pd.read_csv('data/barberos.csv')
    # Asegurarse de que las columnas "Activo" y "Baja" existan y estén en el formato correcto
    barberos_df['Activo'] = barberos_df['Activo'].astype(str)
    barberos_df['Baja'] = barberos_df['Baja'].astype(str)
except FileNotFoundError:
    # Si no hay archivo, crear un DataFrame vacío
    barberos_df = pd.DataFrame(columns=["Nombre", "Rol", "Activo", "Fecha Alta", "Fecha Baja", "Baja"])

# Mostrar la tabla de barberos con opción para editar
st.title("Gestión de Barberos")

# Mostrar la tabla actual
st.subheader("Tabla de Barberos")

# Mostrar la tabla editable
edited_df = st.data_editor(barberos_df, num_rows="dynamic")


# Guardar cambios en la tabla
if st.button("Guardar Cambios"):
    edited_df.to_csv('data/barberos.csv', index=False)
    st.success("Cambios guardados correctamente.")

# Formulario para agregar un nuevo barbero
st.subheader("Agregar un Nuevo Barbero")
with st.form(key="add_barbero_form"):
    nuevo_nombre = st.text_input("Nombre del Barbero")
    nuevo_rol = st.selectbox("Rol", options=["Barbero", "Socio"])
    fecha_alta = st.date_input("Fecha de Alta", datetime.now())
    
    # Estado por defecto "S" (activo) y "N" para "Baja"
    estado_inicial = "S"
    baja_inicial = "N"
    
    # Botón para enviar el formulario
    submit_button = st.form_submit_button(label="Agregar")

    # Si se envía el formulario, agregar el nuevo barbero
    if submit_button:
        nuevo_barbero = pd.DataFrame({
            "Nombre": [nuevo_nombre],
            "Rol": [nuevo_rol],
            "Activo": [estado_inicial],
            "Fecha Alta": [fecha_alta.strftime("%Y-%m-%d")],
            "Fecha Baja": [None],  # Cuando se agrega, no tiene fecha de baja
            "Baja": [baja_inicial]
        })
        
        # Concatenar el nuevo barbero al DataFrame existente
        barberos_df = pd.concat([barberos_df, nuevo_barbero], ignore_index=True)
        
        # Guardar los cambios en el archivo CSV
        barberos_df.to_csv('data/barberos.csv', index=False)
        st.success(f"Barbero '{nuevo_nombre}' agregado exitosamente.")

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
                barberos_df.at[index, "Activo"] = "N"
                barberos_df.at[index, "Baja"] = "S"
                barberos_df.at[index, "Fecha Baja"] = datetime.now().strftime("%Y-%m-%d")
                st.success(f"Barbero {row['Nombre']} dado de baja.")
        else:
            if st.button(f"Reactivar {row['Nombre']}", key=f"alta_{index}"):
                barberos_df.at[index, "Activo"] = "S"
                barberos_df.at[index, "Baja"] = "N"
                barberos_df.at[index, "Fecha Baja"] = None
                st.success(f"Barbero {row['Nombre']} reactivado.")
                
# Guardar automáticamente los cambios en el CSV
barberos_df.to_csv('data/barberos.csv', index=False)

if __name__ == '__main__':
    main()
