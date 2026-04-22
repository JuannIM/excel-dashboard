"""
charts.py — Módulo de Visualización con Plotly
===============================================
Responsabilidades:
  - Generar gráficos interactivos con diseño corporativo consistente.
  - Encapsular la lógica de creación de figuras Plotly.
  - Paleta de colores y layout unificados.
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional

# ---------------------------------------------------------------------------
# Paleta corporativa y configuración visual global
# ---------------------------------------------------------------------------

CORPORATE_PALETTE = [
    "#0066FF",  # Azul principal
    "#00D4AA",  # Verde-turquesa
    "#FF6B35",  # Naranja
    "#A855F7",  # Púrpura
    "#F43F5E",  # Rosa-rojo
    "#3B82F6",  # Azul medio
    "#10B981",  # Esmeralda
    "#F59E0B",  # Ámbar
    "#8B5CF6",  # Violeta
    "#EC4899",  # Fucsia
    "#06B6D4",  # Cian
    "#84CC16",  # Lima
]

LAYOUT_DEFAULTS = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, system-ui, sans-serif", color="#FAFAFA", size=13),
    margin=dict(l=20, r=20, t=50, b=20),
    hoverlabel=dict(
        bgcolor="#1A1F2E",
        font_size=13,
        font_family="Inter, system-ui, sans-serif",
        bordercolor="#333",
    ),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        borderwidth=0,
        font=dict(size=12),
    ),
)


def _apply_layout(fig: go.Figure, title: str, height: int = 450) -> go.Figure:
    """Aplica el diseño corporativo unificado a cualquier figura."""
    fig.update_layout(
        title=dict(text=title, font=dict(size=18, color="#FAFAFA"), x=0.0),
        height=height,
        **LAYOUT_DEFAULTS,
    )
    return fig


# ---------------------------------------------------------------------------
# Gráficos principales
# ---------------------------------------------------------------------------


def bar_chart_top_empresas(
    df: pd.DataFrame,
    top_n: int = 10,
    column_monto: str = "Monto",
    column_empresa: str = "Empresa",
) -> Optional[go.Figure]:
    """
    Gráfico de barras horizontales: Top N empresas por monto acumulado.
    Incluye etiquetas de valor y degradado de color.
    """
    if column_monto not in df.columns or column_empresa not in df.columns:
        return None

    top_data = (
        df.groupby(column_empresa, as_index=False)[column_monto]
        .sum()
        .nlargest(top_n, column_monto)
        .sort_values(column_monto, ascending=True)
    )

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            y=top_data[column_empresa],
            x=top_data[column_monto],
            orientation="h",
            marker=dict(
                color=top_data[column_monto],
                colorscale=[[0, "#1E3A5F"], [0.5, "#0066FF"], [1, "#00D4AA"]],
                line=dict(width=0),
                cornerradius=4,
            ),
            text=[f"${v:,.0f}" for v in top_data[column_monto]],
            textposition="outside",
            textfont=dict(color="#FAFAFA", size=12),
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Monto: $%{x:,.2f}<br>"
                "<extra></extra>"
            ),
        )
    )

    fig = _apply_layout(fig, f"🏆 Top {top_n} Empresas por Monto", height=max(350, top_n * 42))
    fig.update_xaxes(
        showgrid=True,
        gridcolor="rgba(255,255,255,0.06)",
        tickformat="$,.0f",
        zeroline=False,
    )
    fig.update_yaxes(showgrid=False, tickfont=dict(size=12))

    return fig


def pie_chart_distribucion(
    df: pd.DataFrame,
    column: str = "Estado",
    title_suffix: str = "Estado",
) -> Optional[go.Figure]:
    """
    Gráfico de dona (donut) con la distribución porcentual de una columna categórica.
    """
    if column not in df.columns:
        return None

    dist = df[column].value_counts().reset_index()
    dist.columns = [column, "Cantidad"]

    fig = go.Figure()
    fig.add_trace(
        go.Pie(
            labels=dist[column],
            values=dist["Cantidad"],
            hole=0.55,
            marker=dict(
                colors=CORPORATE_PALETTE[: len(dist)],
                line=dict(color="#0E1117", width=2),
            ),
            textinfo="label+percent",
            textfont=dict(size=12, color="#FAFAFA"),
            hovertemplate=(
                "<b>%{label}</b><br>"
                "Cantidad: %{value}<br>"
                "Porcentaje: %{percent}<br>"
                "<extra></extra>"
            ),
            sort=False,
        )
    )

    fig = _apply_layout(fig, f"📊 Distribución por {title_suffix}", height=420)
    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5,
        ),
    )

    return fig


def line_chart_temporal(
    df: pd.DataFrame,
    column_fecha: str = "Fecha",
    column_monto: str = "Monto",
    freq: str = "ME",
) -> Optional[go.Figure]:
    """
    Gráfico de línea/área temporal mostrando la evolución de montos en el tiempo.
    Agrupa por mes para visibilidad.
    """
    if column_fecha not in df.columns or column_monto not in df.columns:
        return None

    df_temp = df[[column_fecha, column_monto]].dropna()
    if df_temp.empty:
        return None

    # Asegurar tipo datetime
    df_temp[column_fecha] = pd.to_datetime(df_temp[column_fecha], errors="coerce")
    df_temp = df_temp.dropna(subset=[column_fecha])

    if df_temp.empty:
        return None

    monthly = (
        df_temp.set_index(column_fecha)
        .resample(freq)[column_monto]
        .sum()
        .reset_index()
    )

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=monthly[column_fecha],
            y=monthly[column_monto],
            mode="lines+markers",
            fill="tozeroy",
            fillcolor="rgba(0,102,255,0.12)",
            line=dict(color="#0066FF", width=2.5, shape="spline"),
            marker=dict(size=7, color="#00D4AA", line=dict(width=1.5, color="#0066FF")),
            hovertemplate=(
                "<b>%{x|%B %Y}</b><br>"
                "Monto: $%{y:,.2f}<br>"
                "<extra></extra>"
            ),
        )
    )

    fig = _apply_layout(fig, "📈 Evolución Temporal de Montos")
    fig.update_xaxes(
        showgrid=True,
        gridcolor="rgba(255,255,255,0.06)",
        dtick="M1",
        tickformat="%b %Y",
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="rgba(255,255,255,0.06)",
        tickformat="$,.0f",
        zeroline=False,
    )

    return fig


def bar_chart_por_categoria(
    df: pd.DataFrame,
    column_categoria: str = "Categoría",
    column_monto: str = "Monto",
) -> Optional[go.Figure]:
    """
    Gráfico de barras verticales agrupadas por categoría.
    """
    if column_categoria not in df.columns or column_monto not in df.columns:
        return None

    cat_data = (
        df.groupby(column_categoria, as_index=False)[column_monto]
        .sum()
        .sort_values(column_monto, ascending=False)
    )

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=cat_data[column_categoria],
            y=cat_data[column_monto],
            marker=dict(
                color=CORPORATE_PALETTE[: len(cat_data)],
                line=dict(width=0),
                cornerradius=6,
            ),
            text=[f"${v:,.0f}" for v in cat_data[column_monto]],
            textposition="outside",
            textfont=dict(color="#FAFAFA", size=11),
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Monto: $%{y:,.2f}<br>"
                "<extra></extra>"
            ),
        )
    )

    fig = _apply_layout(fig, "📦 Montos por Categoría")
    fig.update_xaxes(showgrid=False, tickangle=-30)
    fig.update_yaxes(
        showgrid=True,
        gridcolor="rgba(255,255,255,0.06)",
        tickformat="$,.0f",
        zeroline=False,
    )

    return fig
