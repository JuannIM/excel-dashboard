"""
app.py — Dashboard Corporativo de Análisis de Datos Excel
==========================================================
Aplicación Streamlit de grado producción para la ingesta, consolidación
y visualización interactiva de datos provenientes de múltiples archivos Excel.

Ejecutar con:
    streamlit run app.py
"""

from __future__ import annotations

import streamlit as st
import pandas as pd

from data_loader import load_and_consolidate, compute_kpis
from charts import (
    bar_chart_top_empresas,
    pie_chart_distribucion,
    line_chart_temporal,
    bar_chart_por_categoria,
)


# ---------------------------------------------------------------------------
# Configuración de página
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="DataVault · Dashboard Corporativo",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------------------------
# CSS personalizado para diseño corporativo premium
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
    /* ---------- Tipografía ---------- */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }

    /* ---------- Header branding ---------- */
    .brand-header {
        background: linear-gradient(135deg, #0066FF 0%, #00D4AA 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2.2rem;
        font-weight: 700;
        letter-spacing: -0.5px;
        margin-bottom: 0;
        line-height: 1.2;
    }
    .brand-subtitle {
        color: #8892A8;
        font-size: 0.95rem;
        font-weight: 400;
        margin-top: 2px;
        margin-bottom: 1.5rem;
    }

    /* ---------- KPI Cards ---------- */
    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, #1A1F2E 0%, #151926 100%);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px;
        padding: 18px 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.25);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0,102,255,0.15);
        border-color: rgba(0,102,255,0.3);
    }
    div[data-testid="stMetric"] label {
        color: #8892A8 !important;
        font-weight: 500;
        font-size: 0.82rem;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        font-weight: 700;
        font-size: 1.6rem;
        color: #FAFAFA;
    }

    /* ---------- Sidebar styling ---------- */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0E1117 0%, #131720 100%);
        border-right: 1px solid rgba(255,255,255,0.05);
    }
    section[data-testid="stSidebar"] .block-container {
        padding-top: 2rem;
    }

    /* ---------- Tabs ---------- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255,255,255,0.02);
        border-radius: 10px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        font-weight: 500;
        font-size: 0.9rem;
        padding: 8px 20px;
        color: #8892A8;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #0066FF, #0055DD) !important;
        color: #FFFFFF !important;
    }

    /* ---------- Dataframe ---------- */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
    }

    /* ---------- File uploader ---------- */
    div[data-testid="stFileUploader"] {
        border: 2px dashed rgba(0,102,255,0.3);
        border-radius: 12px;
        padding: 10px;
        transition: border-color 0.3s ease;
    }
    div[data-testid="stFileUploader"]:hover {
        border-color: rgba(0,102,255,0.6);
    }

    /* ---------- Search result card ---------- */
    .search-card {
        background: linear-gradient(145deg, #1A1F2E 0%, #151926 100%);
        border: 1px solid rgba(0,102,255,0.2);
        border-radius: 14px;
        padding: 24px 28px;
        margin: 12px 0;
        box-shadow: 0 4px 24px rgba(0,0,0,0.3);
    }
    .search-card h3 {
        color: #00D4AA;
        margin-bottom: 16px;
        font-size: 1.2rem;
    }
    .search-card .field {
        display: flex;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px solid rgba(255,255,255,0.04);
    }
    .search-card .field:last-child {
        border-bottom: none;
    }
    .search-card .label {
        color: #8892A8;
        font-weight: 500;
        font-size: 0.9rem;
    }
    .search-card .value {
        color: #FAFAFA;
        font-weight: 600;
        font-size: 0.95rem;
    }

    /* ---------- Divider ---------- */
    hr {
        border-color: rgba(255,255,255,0.06) !important;
        margin: 1.5rem 0;
    }

    /* ---------- General polish ---------- */
    .block-container {
        padding-top: 1.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Sidebar — Ingesta de datos
# ---------------------------------------------------------------------------

def render_sidebar() -> list:
    """Renderiza la barra lateral con el módulo de carga de archivos."""
    with st.sidebar:
        st.markdown("### 📂 Carga de Datos")
        st.caption("Arrastra o selecciona uno o varios archivos Excel (.xlsx).")

        uploaded_files = st.file_uploader(
            "Subir archivos Excel",
            type=["xlsx"],
            accept_multiple_files=True,
            key="excel_uploader",
            label_visibility="collapsed",
        )

        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} archivo(s) cargado(s)")
            with st.expander("📋 Archivos cargados", expanded=False):
                for f in uploaded_files:
                    size_kb = f.size / 1024
                    st.markdown(f"- **{f.name}** ({size_kb:.1f} KB)")

        st.divider()
        st.markdown("### ℹ️ Acerca de")
        st.caption(
            "**DataVault** consolida múltiples archivos Excel en un dashboard "
            "unificado. Las columnas se normalizan automáticamente.\n\n"
            "**Columnas requeridas:** *Empresa*, *Monto*\n\n"
            "**Columnas opcionales:** *Fecha*, *Estado*, *Categoría*"
        )

    return uploaded_files


# ---------------------------------------------------------------------------
# KPI Cards
# ---------------------------------------------------------------------------

def render_kpis(kpis: dict):
    """Renderiza las tarjetas de métricas ejecutivas en la parte superior."""
    st.markdown('<p class="brand-header">DataVault</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="brand-subtitle">Dashboard Corporativo de Análisis de Datos</p>',
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            label="📄 Total Registros",
            value=f"{kpis['total_registros']:,}",
        )
    with col2:
        st.metric(
            label="🏢 Empresas Únicas",
            value=f"{kpis['empresas_unicas']:,}",
        )
    with col3:
        st.metric(
            label="💰 Monto Total",
            value=f"${kpis['monto_total']:,.0f}",
        )
    with col4:
        st.metric(
            label="📊 Monto Promedio",
            value=f"${kpis['monto_promedio']:,.0f}",
        )
    with col5:
        st.metric(
            label="🔝 Monto Máximo",
            value=f"${kpis['monto_maximo']:,.0f}",
        )


# ---------------------------------------------------------------------------
# Buscador de empresa
# ---------------------------------------------------------------------------

def render_search(df: pd.DataFrame):
    """Buscador avanzado de empresa con visualización tipo ficha."""
    st.markdown("---")
    st.markdown("### 🔍 Buscador de Empresa")

    col_search, col_mode = st.columns([3, 1])

    with col_mode:
        search_mode = st.radio(
            "Modo",
            ["Autocompletado", "Texto libre"],
            horizontal=True,
            label_visibility="collapsed",
        )

    with col_search:
        if search_mode == "Autocompletado":
            empresas = sorted(df["Empresa"].unique().tolist())
            selected = st.selectbox(
                "Buscar empresa",
                options=[""] + empresas,
                index=0,
                placeholder="Selecciona o escribe el nombre de la empresa…",
                label_visibility="collapsed",
            )
            search_term = selected
        else:
            search_term = st.text_input(
                "Buscar empresa",
                placeholder="Escribe el nombre de la empresa…",
                label_visibility="collapsed",
            )

    if search_term:
        if search_mode == "Texto libre":
            # Búsqueda parcial case-insensitive
            mask = df["Empresa"].str.contains(search_term, case=False, na=False)
        else:
            mask = df["Empresa"] == search_term

        results = df[mask]

        if results.empty:
            st.warning(f"⚠️ No se encontraron resultados para **'{search_term}'**.")
        else:
            st.caption(f"Se encontraron **{len(results)}** registro(s).")
            for _, row in results.iterrows():
                fields_html = ""
                for col_name in results.columns:
                    val = row[col_name]
                    if pd.notna(val):
                        if isinstance(val, float):
                            display_val = f"${val:,.2f}" if "monto" in col_name.lower() else f"{val:,.2f}"
                        else:
                            display_val = str(val)
                        fields_html += (
                            f'<div class="field">'
                            f'  <span class="label">{col_name}</span>'
                            f'  <span class="value">{display_val}</span>'
                            f"</div>"
                        )

                empresa_name = row.get("Empresa", "—")
                st.markdown(
                    f'<div class="search-card">'
                    f"  <h3>🏢 {empresa_name}</h3>"
                    f"  {fields_html}"
                    f"</div>",
                    unsafe_allow_html=True,
                )


# ---------------------------------------------------------------------------
# Tabs con dataframe y gráficos
# ---------------------------------------------------------------------------

def render_analysis_tabs(df: pd.DataFrame, kpis: dict):
    """Renderiza las pestañas principales: Datos, Análisis Visual, Detalle."""

    tab_data, tab_charts, tab_detail = st.tabs([
        "📋 Datos Completos",
        "📊 Análisis Visual",
        "📈 Detalle Avanzado",
    ])

    # ── Tab 1: DataFrame interactivo ──
    with tab_data:
        st.markdown("#### Explorador de Datos")
        st.caption("Haz clic en los encabezados de columna para ordenar. Usa el buscador integrado.")

        # Filtros rápidos
        col_f1, col_f2 = st.columns(2)
        filtered_df = df.copy()

        with col_f1:
            if "Estado" in df.columns:
                estados = ["Todos"] + sorted(df["Estado"].unique().tolist())
                estado_filter = st.selectbox("Filtrar por Estado", estados, key="filter_estado")
                if estado_filter != "Todos":
                    filtered_df = filtered_df[filtered_df["Estado"] == estado_filter]

        with col_f2:
            if "Categoría" in df.columns:
                categorias = ["Todas"] + sorted(df["Categoría"].unique().tolist())
                cat_filter = st.selectbox("Filtrar por Categoría", categorias, key="filter_cat")
                if cat_filter != "Todas":
                    filtered_df = filtered_df[filtered_df["Categoría"] == cat_filter]

        st.dataframe(
            filtered_df,
            use_container_width=True,
            height=480,
            column_config={
                "Monto": st.column_config.NumberColumn(
                    "Monto",
                    format="$%.2f",
                ),
                "Fecha": st.column_config.DateColumn(
                    "Fecha",
                    format="DD/MM/YYYY",
                ),
            },
        )

        col_info1, col_info2, col_info3 = st.columns(3)
        with col_info1:
            st.caption(f"Mostrando **{len(filtered_df):,}** de **{len(df):,}** registros")
        with col_info2:
            if "Monto" in filtered_df.columns:
                st.caption(f"Monto filtrado: **${filtered_df['Monto'].sum():,.0f}**")
        with col_info3:
            st.caption(f"Columnas: **{len(filtered_df.columns)}**")

    # ── Tab 2: Gráficos ──
    with tab_charts:
        st.markdown("#### Panel de Análisis Visual")

        # Fila 1: Top empresas + Distribución
        chart_col1, chart_col2 = st.columns([1.3, 1])

        with chart_col1:
            top_n = st.slider("Top N empresas", 5, 25, 10, key="top_n_slider")
            fig_bar = bar_chart_top_empresas(df, top_n=top_n)
            if fig_bar:
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("ℹ️ Se requieren las columnas 'Empresa' y 'Monto' para este gráfico.")

        with chart_col2:
            # Selección dinámica de columna para el pie chart
            pie_options = []
            if "Estado" in df.columns:
                pie_options.append("Estado")
            if "Categoría" in df.columns:
                pie_options.append("Categoría")

            if pie_options:
                pie_col = st.selectbox("Distribuir por", pie_options, key="pie_selector")
                fig_pie = pie_chart_distribucion(df, column=pie_col, title_suffix=pie_col)
                if fig_pie:
                    st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("ℹ️ Se requiere una columna 'Estado' o 'Categoría' para el gráfico de distribución.")

        # Fila 2: Timeline + Categorías
        chart_col3, chart_col4 = st.columns(2)

        with chart_col3:
            fig_line = line_chart_temporal(df)
            if fig_line:
                st.plotly_chart(fig_line, use_container_width=True)
            else:
                st.info("ℹ️ Se requieren las columnas 'Fecha' y 'Monto' para la evolución temporal.")

        with chart_col4:
            fig_cat = bar_chart_por_categoria(df)
            if fig_cat:
                st.plotly_chart(fig_cat, use_container_width=True)
            else:
                st.info("ℹ️ Se requieren las columnas 'Categoría' y 'Monto' para este gráfico.")

    # ── Tab 3: Estadísticas descriptivas ──
    with tab_detail:
        st.markdown("#### Estadísticas Descriptivas")

        col_stats1, col_stats2 = st.columns(2)

        with col_stats1:
            st.markdown("##### 📊 Resumen Numérico")
            numeric_desc = df.describe(include="number")
            if not numeric_desc.empty:
                # Traducir índice al español
                index_translation = {
                    "count": "Cantidad",
                    "mean": "Media",
                    "std": "Desv. Estándar",
                    "min": "Mínimo",
                    "25%": "Percentil 25",
                    "50%": "Mediana",
                    "75%": "Percentil 75",
                    "max": "Máximo",
                }
                numeric_desc = numeric_desc.rename(index=index_translation)
                st.dataframe(numeric_desc, use_container_width=True)
            else:
                st.info("No hay columnas numéricas para describir.")

        with col_stats2:
            st.markdown("##### 🏷️ Resumen Categórico")
            cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
            if cat_cols:
                selected_cat = st.selectbox("Columna", cat_cols, key="cat_desc")
                value_counts = df[selected_cat].value_counts().head(15)
                st.bar_chart(value_counts)
                st.caption(f"Valores únicos: **{df[selected_cat].nunique()}**")
            else:
                st.info("No hay columnas categóricas para describir.")

        # Correlación (si hay al menos 2 columnas numéricas)
        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        if len(numeric_cols) >= 2:
            st.markdown("##### 🔗 Correlaciones")
            corr_matrix = df[numeric_cols].corr()
            import plotly.figure_factory as ff

            fig_corr = ff.create_annotated_heatmap(
                z=corr_matrix.values.round(2),
                x=numeric_cols,
                y=numeric_cols,
                colorscale=[[0, "#0E1117"], [0.5, "#0066FF"], [1, "#00D4AA"]],
                showscale=True,
            )
            fig_corr.update_layout(
                height=350,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#FAFAFA", size=12),
                margin=dict(l=20, r=20, t=30, b=20),
            )
            st.plotly_chart(fig_corr, use_container_width=True)


# ---------------------------------------------------------------------------
# Estado vacío (sin archivos cargados)
# ---------------------------------------------------------------------------

def render_empty_state():
    """Pantalla de bienvenida cuando no hay archivos cargados."""
    st.markdown('<p class="brand-header">DataVault</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="brand-subtitle">Dashboard Corporativo de Análisis de Datos</p>',
        unsafe_allow_html=True,
    )

    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            """
            <div style="
                text-align: center;
                padding: 60px 40px;
                border: 2px dashed rgba(0,102,255,0.25);
                border-radius: 20px;
                background: linear-gradient(145deg, rgba(26,31,46,0.5) 0%, rgba(14,17,23,0.5) 100%);
            ">
                <div style="font-size: 4rem; margin-bottom: 16px;">📊</div>
                <h2 style="color: #FAFAFA; font-weight: 600; font-size: 1.5rem; margin-bottom: 8px;">
                    Bienvenido a DataVault
                </h2>
                <p style="color: #8892A8; font-size: 1rem; max-width: 400px; margin: 0 auto 24px;">
                    Carga uno o varios archivos Excel (.xlsx) desde la barra lateral izquierda
                    para comenzar el análisis.
                </p>
                <div style="
                    display: inline-flex;
                    gap: 24px;
                    margin-top: 12px;
                ">
                    <div style="text-align: center;">
                        <div style="font-size: 1.5rem;">📂</div>
                        <div style="color: #8892A8; font-size: 0.8rem; margin-top: 4px;">Cargar</div>
                    </div>
                    <div style="color: #333; font-size: 1.5rem;">→</div>
                    <div style="text-align: center;">
                        <div style="font-size: 1.5rem;">🔄</div>
                        <div style="color: #8892A8; font-size: 0.8rem; margin-top: 4px;">Consolidar</div>
                    </div>
                    <div style="color: #333; font-size: 1.5rem;">→</div>
                    <div style="text-align: center;">
                        <div style="font-size: 1.5rem;">📊</div>
                        <div style="color: #8892A8; font-size: 0.8rem; margin-top: 4px;">Analizar</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Columnas requeridas
    st.markdown("#### 📋 Columnas Esperadas")
    col_req, col_opt = st.columns(2)
    with col_req:
        st.markdown(
            """
            **Requeridas:**
            - `Empresa` — Nombre de la empresa o razón social
            - `Monto` — Valor numérico asociado
            """
        )
    with col_opt:
        st.markdown(
            """
            **Opcionales (habilitan más visualizaciones):**
            - `Fecha` — Fecha del registro
            - `Estado` — Estado, situación o status del registro
            - `Categoría` — Rubro, tipo, sector o categoría
            """
        )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    """Punto de entrada principal de la aplicación."""
    uploaded_files = render_sidebar()

    if not uploaded_files:
        render_empty_state()
        return

    # Carga y consolidación
    with st.spinner("⚙️ Procesando archivos…"):
        df, metadata = load_and_consolidate(uploaded_files)

    # Reportar archivos con errores
    if metadata["files_skipped"]:
        for fname, reason in metadata["files_skipped"]:
            st.error(f"❌ **{fname}**: {reason}")

    if df is None or df.empty:
        st.error(
            "⚠️ No se pudo procesar ningún archivo. Verifica que al menos un archivo "
            "contenga las columnas requeridas (**Empresa**, **Monto**)."
        )
        render_empty_state()
        return

    # Notificación de limpieza
    if metadata["duplicates_removed"] > 0:
        st.toast(
            f"🧹 Se eliminaron {metadata['duplicates_removed']} fila(s) duplicadas.",
            icon="🧹",
        )

    # KPIs
    kpis = compute_kpis(df)
    render_kpis(kpis)

    # Buscador
    render_search(df)

    # Tabs principales
    st.markdown("---")
    render_analysis_tabs(df, kpis)

    # Footer
    st.markdown("---")
    st.caption(
        "DataVault v1.0 · Dashboard Corporativo · "
        f"Datos: {metadata['files_processed']} archivo(s) · "
        f"{metadata['total_rows_clean']:,} registros procesados"
    )


if __name__ == "__main__":
    main()
