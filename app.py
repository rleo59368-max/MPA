import streamlit as st
import pandas as pd
import plotly.graph_objects as go
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
st.title("🎈 Seguimiento de Progreso por Categorías")

# -----------------------------
# Barra lateral
# -----------------------------
st.sidebar.header("➕ Agregar persona")
with st.sidebar.form("form_persona"):
    nombre = st.text_input("Nombre de la persona")
    categoria = st.selectbox("Categoría", CATEGORIAS)
    votos = st.number_input("Votos iniciales", min_value=0, step=1)
    imagen = st.text_input("URL de la imagen (opcional)")
    submit = st.form_submit_button("Agregar")

    if submit and nombre:
        df = cargar_datos()
        nueva = pd.DataFrame([[nombre, categoria, votos, imagen]], columns=["Persona","Categoria","Votos","Imagen"])
        df = pd.concat([df, nueva], ignore_index=True)
        guardar_datos(df)
        st.sidebar.success(f"✅ {nombre} agregado a {categoria}")

st.sidebar.header("🔄 Actualizar votos")
df = cargar_datos()
if not df.empty:
    with st.sidebar.form("form_votos"):
        persona_sel = st.selectbox("Selecciona la persona", df["Persona"].unique())
        nuevos_votos = st.number_input("Nuevos votos", min_value=0, step=1)
        submit_votos = st.form_submit_button("Actualizar")
        if submit_votos:
            df.loc[df["Persona"] == persona_sel, "Votos"] = nuevos_votos
            guardar_datos(df)
            st.sidebar.success(f"✅ Votos actualizados para {persona_sel}")

# Botón de reset
if st.sidebar.button("🔄 Resetear todos los valores"):
    df = resetear_datos()
    st.sidebar.success("✅ Todos los valores reseteados a 0")

# -----------------------------
# Selector de categoría
# -----------------------------
st.subheader("🔽 Selecciona una categoría para ver sus globos")
cat_sel = st.selectbox("Categoría", CATEGORIAS)
filtro = df[df["Categoria"] == cat_sel]

# -----------------------------
# Gráfica de globos con imágenes
# -----------------------------
if not filtro.empty:
    np.random.seed(42)
    filtro["x"] = np.random.rand(len(filtro))
    filtro["y"] = np.random.rand(len(filtro))

    fig = go.Figure()

    for _, row in filtro.iterrows():
        size = 20 + row["Votos"]*2  # tamaño proporcional a los votos
        # Círculo principal
        fig.add_trace(go.Scatter(
            x=[row["x"]],
            y=[row["y"]],
            mode="markers+text",
            marker=dict(size=size, color="lightblue", line=dict(width=2, color='DarkSlateGrey')),
            text=[row["Votos"]],
            textposition="middle center",
            hovertext=row["Persona"],
            hoverinfo="text"
        ))
        # Imagen dentro del globo
        if pd.notna(row["Imagen"]) and row["Imagen"]:
            fig.add_layout_image(
                dict(
                    source=row["Imagen"],
                    x=row["x"] - 0.025,
                    y=row["y"] + 0.025,
                    xref="x",
                    yref="y",
                    sizex=0.05,
                    sizey=0.05,
                    xanchor="left",
                    yanchor="bottom",
                    layer="above"
                )
            )

    fig.update_layout(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        plot_bgcolor='white',
        showlegend=False,
        height=600
    )

    st.plotly_chart(fig)
else:
    st.info("No hay personas en esta categoría todavía.")
