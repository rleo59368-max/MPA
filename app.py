import streamlit as st
import pandas as pd
import plotly.express as px
import os

# -----------------------------
# Configuración inicial
# -----------------------------
DATA_FILE = "progreso.csv"
CATEGORIAS = ["Categoria 1", "Categoria 2", "Categoria 3", "Categoria 4", "Categoria 5"]

# -----------------------------
# Funciones auxiliares
# -----------------------------
def cargar_datos():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=["Persona", "Categoria", "Votos", "Imagen"])

def guardar_datos(df):
    df.to_csv(DATA_FILE, index=False)

# -----------------------------
# Interfaz con Streamlit
# -----------------------------
st.title("📊 Seguimiento de Progreso por Categorías")

# Cargar datos
df = cargar_datos()

# -----------------------------
# Agregar nueva persona
# -----------------------------
st.sidebar.header("➕ Agregar persona")
with st.sidebar.form("form_persona"):
    nombre = st.text_input("Nombre de la persona")
    categoria = st.selectbox("Categoría", CATEGORIAS)
    votos = st.number_input("Votos iniciales", min_value=0, step=1)
    imagen = st.text_input("URL de la imagen (opcional)")
    submit = st.form_submit_button("Agregar")

    if submit and nombre:
        nueva = pd.DataFrame([[nombre, categoria, votos, imagen]],
                             columns=["Persona", "Categoria", "Votos", "Imagen"])
        df = pd.concat([df, nueva], ignore_index=True)
        guardar_datos(df)
        st.sidebar.success(f"✅ {nombre} agregado a {categoria}")

# -----------------------------
# Mostrar datos y progreso
# -----------------------------
st.subheader("📈 Progreso por Categoría")
cat = st.selectbox("Selecciona una categoría", CATEGORIAS)

filtro = df[df["Categoria"] == cat]
if not filtro.empty:
    # Tabla
    st.dataframe(filtro)

    # Gráfica de barras
    fig = px.bar(filtro, x="Persona", y="Votos", color="Persona", text="Votos",
                 title=f"Progreso en {cat}")
    st.plotly_chart(fig)

    # Mostrar fotos
    st.subheader("👥 Personas en esta categoría")
    for _, row in filtro.iterrows():
        col1, col2 = st.columns([1,3])
        with col1:
            if pd.notna(row["Imagen"]) and row["Imagen"]:
                st.image(row["Imagen"], width=100)
        with col2:
            st.write(f"**{row['Persona']}** - {row['Votos']} votos")
else:
    st.info("No hay personas en esta categoría todavía.")

# -----------------------------
# Actualizar votos
# -----------------------------
st.subheader("🔄 Actualizar votos")
with st.form("form_votos"):
    persona_sel = st.selectbox("Selecciona la persona", df["Persona"].unique() if not df.empty else [])
    nuevos_votos = st.number_input("Nuevos votos a asignar", min_value=0, step=1)
    submit_votos = st.form_submit_button("Actualizar")

    if submit_votos and persona_sel:
        df.loc[df["Persona"] == persona_sel, "Votos"] = nuevos_votos
        guardar_datos(df)
        st.success(f"✅ Votos actualizados para {persona_sel}")
