import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# --------------------------------------------------
# CONFIGURACIÓN
# --------------------------------------------------

st.set_page_config(
    page_title="StreamView Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# UBICACIÓN DEL EXCEL
# --------------------------------------------------

DATA = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "StreamView_Analytics_Dataset.xlsx"
)

# --------------------------------------------------
# CARGAR DATOS
# --------------------------------------------------

@st.cache_data
def load_data():

    sheets = [
        "usuarios",
        "contenidos",
        "dispositivos",
        "suscripciones",
        "reproducciones",
        "calificaciones",
        "interacciones"
    ]

    return {
        sheet: pd.read_excel(DATA, sheet_name=sheet)
        for sheet in sheets
    }


data = load_data()

usuarios = data["usuarios"].copy()
contenidos = data["contenidos"].copy()
dispositivos = data["dispositivos"].copy()
suscripciones = data["suscripciones"].copy()
reproducciones = data["reproducciones"].copy()
calificaciones = data["calificaciones"].copy()
interacciones = data["interacciones"].copy()

# --------------------------------------------------
# CONVERTIR FECHAS
# --------------------------------------------------

usuarios["fecha_registro"] = pd.to_datetime(
    usuarios["fecha_registro"],
    errors="coerce"
)

dispositivos["fecha_vinculado"] = pd.to_datetime(
    dispositivos["fecha_vinculado"],
    errors="coerce"
)

suscripciones["fecha_inicio"] = pd.to_datetime(
    suscripciones["fecha_inicio"],
    errors="coerce"
)

suscripciones["fecha_fin"] = pd.to_datetime(
    suscripciones["fecha_fin"],
    errors="coerce"
)

reproducciones["fecha"] = pd.to_datetime(
    reproducciones["fecha"],
    errors="coerce"
)

calificaciones["fecha"] = pd.to_datetime(
    calificaciones["fecha"],
    errors="coerce"
)

interacciones["fecha"] = pd.to_datetime(
    interacciones["fecha"],
    errors="coerce"
)

# --------------------------------------------------
# ESTILO
# --------------------------------------------------

st.markdown("""
<style>

.block-container {
    padding-top: 1.2rem;
    padding-bottom: 2rem;
}

[data-testid="stMetric"] {
    background-color: #111827;
    border: 1px solid #263244;
    padding: 14px;
    border-radius: 12px;
}

</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# TÍTULO
# --------------------------------------------------

st.title("📊 StreamView Analytics")

st.caption(
    "Dashboard de comportamiento, consumo, suscripciones y engagement"
)

# --------------------------------------------------
# FILTROS
# --------------------------------------------------

st.sidebar.header("🎛️ Filtros")

countries = sorted(
    usuarios["pais"].dropna().unique().tolist()
)

genres = sorted(
    contenidos["genero"].dropna().unique().tolist()
)

types = sorted(
    contenidos["tipo"].dropna().unique().tolist()
)

plans = sorted(
    usuarios["plan_actual"].dropna().unique().tolist()
)

device_types = sorted(
    dispositivos["tipo_dispositivo"].dropna().unique().tolist()
)

sel_country = st.sidebar.multiselect(
    "País",
    countries
)

sel_genre = st.sidebar.multiselect(
    "Género",
    genres
)

sel_type = st.sidebar.multiselect(
    "Tipo de contenido",
    types
)

sel_plan = st.sidebar.multiselect(
    "Plan actual",
    plans
)

sel_device = st.sidebar.multiselect(
    "Dispositivo",
    device_types
)

# --------------------------------------------------
# FILTRO DE FECHAS
# --------------------------------------------------

min_date = reproducciones["fecha"].min()
max_date = reproducciones["fecha"].max()

date_range = st.sidebar.date_input(
    "Periodo de reproducciones",
    value=(
        min_date.date(),
        max_date.date()
    ),
    min_value=min_date.date(),
    max_value=max_date.date()
)

if isinstance(date_range, tuple) and len(date_range) == 2:

    start_date = pd.Timestamp(
        date_range[0]
    )

    end_date = (
        pd.Timestamp(date_range[1])
        + pd.Timedelta(days=1)
    )

else:

    start_date = min_date

    end_date = (
        max_date
        + pd.Timedelta(days=1)
    )

# --------------------------------------------------
# FILTRAR USUARIOS
# --------------------------------------------------

u = usuarios.copy()

if sel_country:

    u = u[
        u["pais"].isin(sel_country)
    ]

if sel_plan:

    u = u[
        u["plan_actual"].isin(sel_plan)
    ]

# --------------------------------------------------
# FILTRAR CONTENIDOS
# --------------------------------------------------

c = contenidos.copy()

if sel_genre:

    c = c[
        c["genero"].isin(sel_genre)
    ]

if sel_type:

    c = c[
        c["tipo"].isin(sel_type)
    ]

# --------------------------------------------------
# FILTRAR DISPOSITIVOS
# --------------------------------------------------

d = dispositivos.copy()

if sel_device:

    d = d[
        d["tipo_dispositivo"].isin(sel_device)
    ]

# --------------------------------------------------
# IDS
# --------------------------------------------------

user_ids = set(
    u["user_id"]
)

content_ids = set(
    c["content_id"]
)

device_ids = set(
    d["device_id"]
)

# --------------------------------------------------
# REPRODUCCIONES
# --------------------------------------------------

r = reproducciones[
    reproducciones["fecha"].between(
        start_date,
        end_date - pd.Timedelta(days=1)
    )
].copy()

r = r[
    r["user_id"].isin(user_ids)
    &
    r["content_id"].isin(content_ids)
    &
    r["device_id"].isin(device_ids)
]

# --------------------------------------------------
# SUSCRIPCIONES
# --------------------------------------------------

s = suscripciones[
    suscripciones["user_id"].isin(user_ids)
].copy()

# --------------------------------------------------
# CALIFICACIONES
# --------------------------------------------------

ratings = calificaciones[
    calificaciones["user_id"].isin(user_ids)
    &
    calificaciones["content_id"].isin(content_ids)
].copy()

# --------------------------------------------------
# INTERACCIONES
# --------------------------------------------------

ints = interacciones[
    interacciones["user_id"].isin(user_ids)
    &
    interacciones["content_id"].isin(content_ids)
].copy()

# --------------------------------------------------
# MENÚ PRINCIPAL
# --------------------------------------------------

page = st.sidebar.radio(
    "📂 Sección",

    [
        "🏠 Resumen ejecutivo",
        "👥 Usuarios",
        "🎬 Contenidos",
        "▶️ Consumo",
        "💳 Suscripciones & Engagement"
    ]
)

# ==================================================
# PÁGINA 1
# RESUMEN EJECUTIVO
# ==================================================

if page == "🏠 Resumen ejecutivo":

    st.header("Resumen ejecutivo")

    st.write(
        "Vista general del comportamiento "
        "de los usuarios y del consumo de contenido."
    )

    # KPI

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        "Usuarios",
        f"{u['user_id'].nunique():,}"
    )

    col2.metric(
        "Reproducciones",
        f"{len(r):,}"
    )

    col3.metric(
        "Minutos vistos",
        f"{r['minutos_vistos'].sum():,.0f}"
    )

    if not ratings.empty:

        avg_rating = ratings["calificacion"].mean()

        rating_text = f"{avg_rating:.2f}"

    else:

        rating_text = "N/D"

    col4.metric(
        "Calificación promedio",
        rating_text
    )

    col5.metric(
        "Suscripciones",
        f"{len(s):,}"
    )

    # GRÁFICO 1

    col1, col2 = st.columns(2)

    with col1:

        if not r.empty:

            monthly = (
                r.assign(
                    mes=r["fecha"]
                    .dt.to_period("M")
                    .astype(str)
                )
                .groupby("mes")
                .size()
                .reset_index(
                    name="reproducciones"
                )
            )

            fig = px.line(
                monthly,
                x="mes",
                y="reproducciones",
                markers=True,
                title="Evolución de reproducciones"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    # GRÁFICO 2

    with col2:

        if not r.empty:

            top = (
                r.groupby("content_id")
                .size()
                .reset_index(
                    name="reproducciones"
                )
                .sort_values(
                    "reproducciones",
                    ascending=False
                )
                .head(10)
            )

            top = top.merge(
                c[
                    [
                        "content_id",
                        "titulo"
                    ]
                ],
                on="content_id",
                how="left"
            )

            fig = px.bar(
                top.sort_values(
                    "reproducciones"
                ),
                x="reproducciones",
                y="titulo",
                orientation="h",
                title="Top 10 contenidos más reproducidos"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    # CONSUMO POR GÉNERO

    if not r.empty:

        by_genre = (
            r.merge(
                c[
                    [
                        "content_id",
                        "genero"
                    ]
                ],
                on="content_id",
                how="left"
            )
            .groupby("genero")
            .size()
            .reset_index(
                name="reproducciones"
            )
            .sort_values(
                "reproducciones",
                ascending=False
            )
        )

        fig = px.bar(
            by_genre,
            x="genero",
            y="reproducciones",
            title="Consumo por género"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

# ==================================================
# PÁGINA 2
# USUARIOS
# ==================================================

elif page == "👥 Usuarios":

    st.header("Análisis de usuarios")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Usuarios",
        f"{u['user_id'].nunique():,}"
    )

    col2.metric(
        "Edad promedio",
        f"{u['edad'].mean():.1f}"
    )

    col3.metric(
        "Países",
        f"{u['pais'].nunique():,}"
    )

    col1, col2 = st.columns(2)

    # PAÍS

    with col1:

        country = (
            u.groupby("pais")["user_id"]
            .nunique()
            .reset_index(
                name="usuarios"
            )
            .sort_values(
                "usuarios",
                ascending=False
            )
        )

        fig = px.bar(
            country,
            x="usuarios",
            y="pais",
            orientation="h",
            title="Usuarios por país"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # PLAN

    with col2:

        plan = (
            u.groupby("plan_actual")["user_id"]
            .nunique()
            .reset_index(
                name="usuarios"
            )
        )

        fig = px.pie(
            plan,
            names="plan_actual",
            values="usuarios",
            hole=.45,
            title="Usuarios por plan"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # EDAD

    col3, col4 = st.columns(2)

    with col3:

        bins = [
            0,
            17,
            24,
            34,
            44,
            54,
            64,
            120
        ]

        labels = [
            "<18",
            "18–24",
            "25–34",
            "35–44",
            "45–54",
            "55–64",
            "65+"
        ]

        ages = u.copy()

        ages["grupo_edad"] = pd.cut(
            ages["edad"],
            bins=bins,
            labels=labels,
            include_lowest=True
        )

        age = (
            ages
            .groupby(
                "grupo_edad",
                observed=False
            )["user_id"]
            .nunique()
            .reset_index(
                name="usuarios"
            )
        )

        fig = px.bar(
            age,
            x="grupo_edad",
            y="usuarios",
            title="Distribución por edad"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # ESTADO

    with col4:

        status = (
            u.groupby("estado_cuenta")["user_id"]
            .nunique()
            .reset_index(
                name="usuarios"
            )
        )

        fig = px.pie(
            status,
            names="estado_cuenta",
            values="usuarios",
            hole=.45,
            title="Estado de las cuentas"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

# ==================================================
# PÁGINA 3
# CONTENIDOS
# ==================================================

elif page == "🎬 Contenidos":

    st.header("Análisis de contenidos")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Contenidos",
        f"{c['content_id'].nunique():,}"
    )

    col2.metric(
        "Géneros",
        f"{c['genero'].nunique():,}"
    )

    col3.metric(
        "Tipos",
        f"{c['tipo'].nunique():,}"
    )

    col1, col2 = st.columns(2)

    # TIPO

    with col1:

        typ = (
            c.groupby("tipo")["content_id"]
            .nunique()
            .reset_index(
                name="contenidos"
            )
        )

        fig = px.pie(
            typ,
            names="tipo",
            values="contenidos",
            hole=.45,
            title="Películas vs. series"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # GÉNERO

    with col2:

        gen = (
            c.groupby("genero")["content_id"]
            .nunique()
            .reset_index(
                name="contenidos"
            )
            .sort_values(
                "contenidos",
                ascending=False
            )
        )

        fig = px.bar(
            gen,
            x="contenidos",
            y="genero",
            orientation="h",
            title="Contenidos por género"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # REPRODUCCIONES POR GÉNERO

    if not r.empty:

        rg = (
            r.merge(
                c[
                    [
                        "content_id",
                        "genero"
                    ]
                ],
                on="content_id",
                how="left"
            )
            .groupby("genero")
            .size()
            .reset_index(
                name="reproducciones"
            )
            .sort_values(
                "reproducciones",
                ascending=False
            )
        )

        fig = px.bar(
            rg,
            x="genero",
            y="reproducciones",
            title="Reproducciones por género"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

# ==================================================
# PÁGINA 4
# CONSUMO
# ==================================================

elif page == "▶️ Consumo":

    st.header("Análisis de consumo")

    if not r.empty:

        avg_completion = (
            r["porcentaje_completado"].mean()
        )

        avg_duration = (
            r["duracion_total_min"].mean()
        )

    else:

        avg_completion = None
        avg_duration = None

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Reproducciones",
        f"{len(r):,}"
    )

    col2.metric(
        "Minutos vistos",
        f"{r['minutos_vistos'].sum():,.0f}"
    )

    col3.metric(
        "Completitud promedio",
        f"{avg_completion:.1f}%"
        if avg_completion is not None
        else "N/D"
    )

    col4.metric(
        "Duración promedio",
        f"{avg_duration:.1f} min"
        if avg_duration is not None
        else "N/D"
    )

    if not r.empty:

        col1, col2 = st.columns(2)

        # MINUTOS POR MES

        with col1:

            monthly = (
                r.assign(
                    mes=r["fecha"]
                    .dt.to_period("M")
                    .astype(str)
                )
                .groupby("mes")["minutos_vistos"]
                .sum()
                .reset_index()
            )

            fig = px.line(
                monthly,
                x="mes",
                y="minutos_vistos",
                markers=True,
                title="Minutos vistos por mes"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        # COMPLETADOS

        with col2:

            comp = (
                r.groupby("completado")
                .size()
                .reset_index(
                    name="reproducciones"
                )
            )

            fig = px.pie(
                comp,
                names="completado",
                values="reproducciones",
                hole=.45,
                title="Reproducciones completadas vs. no completadas"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

# ==================================================
# PÁGINA 5
# SUSCRIPCIONES & ENGAGEMENT
# ==================================================

else:

    st.header(
        "Suscripciones & Engagement"
    )

    active = (
        s["estado"]
        .astype(str)
        .str.lower()
        .eq("activa")
        .sum()
    )

    cancelled = (
        s["estado"]
        .astype(str)
        .str.lower()
        .eq("cancelada")
        .sum()
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Suscripciones",
        f"{len(s):,}"
    )

    col2.metric(
        "Activas",
        f"{active:,}"
    )

    col3.metric(
        "Canceladas",
        f"{cancelled:,}"
    )

    col4.metric(
        "Precio mensual total",
        f"${s['precio_mensual_clp'].sum():,.0f}"
    )

    col1, col2 = st.columns(2)

    # PLANES

    with col1:

        by_plan = (
            s.groupby("plan")["suscripcion_id"]
            .count()
            .reset_index(
                name="suscripciones"
            )
            .sort_values(
                "suscripciones",
                ascending=False
            )
        )

        fig = px.bar(
            by_plan,
            x="plan",
            y="suscripciones",
            title="Suscripciones por plan"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # ESTADO

    with col2:

        by_status = (
            s.groupby("estado")["suscripcion_id"]
            .count()
            .reset_index(
                name="suscripciones"
            )
        )

        fig = px.pie(
            by_status,
            names="estado",
            values="suscripciones",
            hole=.45,
            title="Estado de suscripciones"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # INTERACCIONES

    if not ints.empty:

        interaction = (
            ints.groupby("tipo_interaccion")[
                "interaccion_id"
            ]
            .count()
            .reset_index(
                name="interacciones"
            )
            .sort_values(
                "interacciones",
                ascending=False
            )
        )

        fig = px.bar(
            interaction,
            x="tipo_interaccion",
            y="interacciones",
            title="Interacciones por tipo"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

# --------------------------------------------------
# PIE
# --------------------------------------------------

st.markdown("---")

st.caption(
    "StreamView Analytics | Proyecto académico de Visualización de Datos"
)