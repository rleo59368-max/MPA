import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os

# -----------------------------
# Configuración
# -----------------------------
DATA_FILE = "progreso.csv"
CATEGORIAS = ["Categoria 1", "Categoria 2", "Categoria 3", "Categoria 4", "Categoria 5"]

# -----------------------------
# Funciones
# -----------------------------
def cargar_datos():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=["Persona","Categoria","Votos","Imagen"])

def guardar_datos(df):
    df.to_csv(DATA_FILE, index=False)

def resetear_datos():
    df = pd.DataFrame(columns=["Persona","Categoria","Votos","Imagen"])
    guardar_datos(df)
    return df

# -----------------------------
# App
# -----------------------------
st.title("🎈 Seguimiento de Progreso - Globos")

# Botón de reset
if st.sidebar.button("🔄 Resetear todos los valores"):
    df = resetear_datos()
    st.sidebar.success("✅ Todos los valores reseteados a 0")
else:
    df = cargar_datos()

# -----------------------------
# Agregar persona
# -----------------------------
st.sidebar.header("➕ Agregar persona")
with st.sidebar.form("form_persona"):
    nombre = st.text_input("Nombre de la persona")
    categoria = st.selectbox("Categoría", CATEGORIAS)
    votos = st.number_input("Votos iniciales", min_value=0, step=1)
    imagen = st.text_input("URL de la imagen (opcional)")
    submit = st.form_submit_button("Agregar")

    if submit and nombre:
        nueva = pd.DataFrame([[nombre, categoria, votos, imagen]], columns=["Persona","Categoria","Votos","Imagen"])
        df = pd.concat([df, nueva], ignore_index=True)
        guardar_datos(df)
        st.sidebar.success(f"✅ {nombre} agregado a {categoria}")

# -----------------------------
# Actualizar votos
# -----------------------------
st.sidebar.header("🔄 Actualizar votos")
if not df.empty:
    with st.sidebar.form("form_votos"):
        persona_sel = st.selectbox("Selecciona la persona", df["Persona"].unique())
        nuevos_votos = st.number_input("Nuevos votos", min_value=0, step=1)
        submit_votos = st.form_submit_button("Actualizar")
        if submit_votos:
            df.loc[df["Persona"] == persona_sel, "Votos"] = nuevos_votos
            guardar_datos(df)
            st.sidebar.success(f"✅ Votos actualizados para {persona_sel}")

# -----------------------------
# Nivel 1: Globos de categorías
# -----------------------------
st.subheader("🎈 Categorías (Globos)")
suma_categorias = df.groupby("Categoria")["Votos"].sum().reset_index()

# Posiciones aleatorias para globos
np.random.seed(42)
suma_categorias["x"] = np.random.rand(len(suma_categorias))
suma_categorias["y"] = np.random.rand(len(suma_categorias))

fig_cat = px.scatter(
    suma_categorias,
    x="x",
    y="y",
    size="Votos",
    color="Categoria",
    text="Categoria",
    size_max=100
)
fig_cat.update_layout(
    xaxis=dict(visible=False),
    yaxis=dict(visible=False),
    plot_bgcolor='white',
    showlegend=False
)
fig_cat.update_traces(marker=dict(opacity=0.7, line=dict(width=2, color='DarkSlateGrey')))
st.plotly_chart(fig_cat)

# -----------------------------
# Drill-down: selección categoría
# -----------------------------
cat_sel = st.selectbox("🔽 Selecciona una categoría para ver personas", CATEGORIAS)
filtro = df[df["Categoria"] == cat_sel]

if not filtro.empty:
    st.subheader(f"👥 Personas en {cat_sel} (Globos)")
    np.random.seed(42)
    filtro["x"] = np.random.rand(len(filtro))
    filtro["y"] = np.random.rand(len(filtro))

    fig = px.scatter(
        filtro,
        x="x",
        y="y",
        size="Votos",
        color="Persona",
        text="Votos",
        size_max=60
    )
    fig.update_layout(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        plot_bgcolor='white',
        showlegend=False
    )
    fig.update_traces(marker=dict(opacity=0.7, line=dict(width=1, color='DarkSlateGrey')))
    st.plotly_chart(fig)

    # Mostrar fotos
    for _, row in filtro.iterrows():
        col1, col2 = st.columns([1,3])
        with col1:
            if pd.notna(row["Imagen"]) and row["Imagen"]:
                st.image(row["Imagen"], width=80)
        with col2:
            st.write(f"**{row['Persona']}** - {row['Votos']} votos")
else:
    st.info("No hay personas en esta categoría todavía.")
