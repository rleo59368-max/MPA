import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import os
import base64
from PIL import Image, ImageDraw
from io import BytesIO

# -----------------------------
# Configuración
# -----------------------------
DATA_FILE = "progreso.csv"
CATEGORIAS = {
    "Impactante": "green",
    "Valiente": "yellow",
    "Enfocado": "red",
    "Adaptable": "cyan",
    "Influyente": "navy"
}

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

def imagen_circular(imagen_file):
    """Recorta la imagen en círculo y devuelve base64 PNG."""
    image = Image.open(imagen_file).convert("RGBA")
    size = min(image.size)
    mask = Image.new('L', (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size, size), fill=255)
    output = Image.new('RGBA', (size, size))
    output.paste(image.crop((0,0,size,size)), (0,0), mask=mask)
    buffered = BytesIO()
    output.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode()
    return "data:image/png;base64," + img_base64

# -----------------------------
# App
# -----------------------------
st.title("🎈 Dashboard de Progreso por Categorías")

# -----------------------------
# Barra lateral: agregar persona y reset
# -----------------------------
st.sidebar.header("➕ Agregar persona")
with st.sidebar.form("form_persona"):
    nombre = st.text_input("Nombre de la persona")
    categoria = st.selectbox("Categoría", list(CATEGORIAS.keys()))
    votos = st.number_input("Votos iniciales", min_value=0, step=1)
    imagen_url = st.text_input("URL de la imagen (opcional)")
    imagen_file = st.file_uploader("O subir imagen desde tu PC", type=["png","jpg","jpeg"])
    submit = st.form_submit_button("Agregar")
    if submit and nombre:
        df = cargar_datos()
        if imagen_file:
            img_uri = imagen_circular(imagen_file)
        elif imagen_url:
            img_uri = imagen_url
        else:
            img_uri = ""
        nueva = pd.DataFrame([[nombre, categoria, votos, img_uri]], columns=["Persona","Categoria","Votos","Imagen"])
        df = pd.concat([df, nueva], ignore_index=True)
        guardar_datos(df)
        st.sidebar.success(f"✅ {nombre} agregado a {categoria}")

st.sidebar.header("🔄 Actualizar votos")
df = cargar_datos()
if not df.empty:
    with st.sidebar.form("form_votos"):
        persona_sel = st.selectbox("Selecciona la persona", df["Persona"].unique())
        categoria_sel = st.selectbox("Selecciona la categoría", df["Categoria"].unique())
        nuevos_votos = st.number_input("Nuevos votos", min_value=0, step=1)
        submit_votos = st.form_submit_button("Actualizar")
        if submit_votos:
            df.loc[(df["Persona"] == persona_sel) & (df["Categoria"] == categoria_sel), "Votos"] = nuevos_votos
            guardar_datos(df)
            st.sidebar.success(f"✅ Votos actualizados para {persona_sel} en {categoria_sel}")

if st.sidebar.button("🔄 Resetear todos los valores"):
    df = resetear_datos()
    st.sidebar.success("✅ Todos los valores reseteados a 0")

# -----------------------------
# Botones de categorías
# -----------------------------
st.subheader("Selecciona una categoría")
col1, col2, col3, col4, col5 = st.columns(5)
botones = []
cols = [col1, col2, col3, col4, col5]

for i, (cat, color) in enumerate(CATEGORIAS.items()):
    botones.append(cols[i].button(cat, key=cat))

# Detectar cuál botón se presionó
categoria_seleccionada = None
for i, pressed in enumerate(botones):
    if pressed:
        categoria_seleccionada = list(CATEGORIAS.keys())[i]

# -----------------------------
# Mostrar gráfica de personas
# -----------------------------
if categoria_seleccionada:
    st.subheader(f"🎈 Globos de la categoría: {categoria_seleccionada}")
    filtro = df[df["Categoria"] == categoria_seleccionada]
    if not filtro.empty:
        np.random.seed(42)
        filtro["x"] = np.random.rand(len(filtro))
        filtro["y"] = np.random.rand(len(filtro))

        fig = go.Figure()
        for _, row in filtro.iterrows():
            size = 20 + row["Votos"]*2
            color = CATEGORIAS[row["Categoria"]]
            # Círculo base con color
            fig.add_trace(go.Scatter(
                x=[row["x"]],
                y=[row["y"]],
                mode="markers+text",
                marker=dict(size=size, color=color, line=dict(width=2, color='DarkSlateGrey')),
                text=[row["Votos"]],
                textposition="middle center",
                hovertext=f"{row['Persona']} - {row['Votos']} votos",
                hoverinfo="text"
            ))
            # Imagen circular dentro del círculo
            if pd.notna(row["Imagen"]) and row["Imagen"]:
                scale = size / 100  # ajustar tamaño relativo
                fig.add_layout_image(
                    dict(
                        source=row["Imagen"],
                        x=row["x"] - 0.03*scale,
                        y=row["y"] - 0.03*scale,
                        xref="x",
                        yref="y",
                        sizex=0.06*scale,
                        sizey=0.06*scale,
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
