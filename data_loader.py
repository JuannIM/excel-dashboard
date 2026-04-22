"""
data_loader.py — Módulo de Ingesta, Limpieza y Consolidación de Datos
=====================================================================
Responsabilidades:
  - Leer archivos Excel (.xlsx) subidos por el usuario.
  - Validar la existencia de columnas requeridas.
  - Limpieza de valores nulos y duplicados.
  - Concatenación segura de múltiples DataFrames.
  - Cálculo de métricas KPI agregadas.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st
from typing import List, Dict, Any, Optional, Tuple

# ---------------------------------------------------------------------------
# Configuración de columnas esperadas
# ---------------------------------------------------------------------------
# Mapeo canónico: nombre interno → posibles aliases en los archivos fuente.
# Esto permite normalizar headers con variaciones comunes.

COLUMN_ALIASES: Dict[str, List[str]] = {
    "Empresa":   ["empresa", "nombre de la empresa", "nombre_empresa", "company", "razon social", "razón social", "nombre"],
    "Monto":     ["monto", "importe", "amount", "valor", "total", "monto total"],
    "Fecha":     ["fecha", "date", "fecha_registro", "fecha registro"],
    "Estado":    ["estado", "status", "situación", "situacion", "state"],
    "Categoría": ["categoría", "categoria", "category", "tipo", "rubro", "sector"],
}

REQUIRED_COLUMNS = ["Empresa", "Monto"]  # Mínimo indispensable


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normaliza los nombres de columnas del DataFrame al esquema canónico.
    Busca coincidencias case-insensitive contra los aliases definidos.
    Las columnas que no coinciden con ningún alias se preservan tal cual.
    """
    rename_map: Dict[str, str] = {}
    original_cols_lower = {col: col.strip().lower() for col in df.columns}

    for canonical_name, aliases in COLUMN_ALIASES.items():
        for original_col, lower_col in original_cols_lower.items():
            if lower_col in aliases and original_col not in rename_map:
                rename_map[original_col] = canonical_name
                break  # Una sola coincidencia por nombre canónico

    return df.rename(columns=rename_map)


def _validate_required_columns(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """
    Verifica que el DataFrame contenga las columnas requeridas.
    Retorna (is_valid, lista_de_columnas_faltantes).
    """
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    return (len(missing) == 0, missing)


def _clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Pipeline de limpieza:
      1. Eliminar filas completamente vacías.
      2. Eliminar duplicados exactos.
      3. Coerción de tipos en columnas clave.
      4. Rellenar nulos en columnas categóricas.
    """
    # Paso 1: Filas vacías
    df = df.dropna(how="all").reset_index(drop=True)

    # Paso 2: Duplicados
    initial_count = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    duplicates_removed = initial_count - len(df)

    # Paso 3: Coerción de tipos
    if "Monto" in df.columns:
        df["Monto"] = pd.to_numeric(df["Monto"], errors="coerce")

    if "Fecha" in df.columns:
        df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce", dayfirst=True)

    # Paso 4: Relleno de nulos categóricos
    for col in ["Estado", "Categoría"]:
        if col in df.columns:
            df[col] = df[col].fillna("Sin especificar")

    if "Empresa" in df.columns:
        df["Empresa"] = df["Empresa"].astype(str).str.strip()
        # Eliminar filas donde Empresa quedó vacía o es 'nan'
        df = df[~df["Empresa"].isin(["", "nan"])].reset_index(drop=True)

    return df


@st.cache_data(show_spinner=False)
def load_and_consolidate(
    uploaded_files: List[Any],
) -> Tuple[Optional[pd.DataFrame], Dict[str, Any]]:
    """
    Función principal de ingesta.
    Lee, normaliza, valida, limpia y concatena todos los archivos subidos.

    Retorna:
        - DataFrame consolidado (o None si hubo error crítico).
        - Diccionario de metadatos del proceso de carga.
    """
    metadata: Dict[str, Any] = {
        "files_processed": 0,
        "files_skipped": [],
        "total_rows_raw": 0,
        "total_rows_clean": 0,
        "duplicates_removed": 0,
        "warnings": [],
    }

    frames: List[pd.DataFrame] = []

    for file in uploaded_files:
        try:
            df_raw = pd.read_excel(file, engine="openpyxl")
        except Exception as e:
            metadata["files_skipped"].append((file.name, f"Error de lectura: {e}"))
            continue

        if df_raw.empty:
            metadata["files_skipped"].append((file.name, "Archivo vacío"))
            continue

        df_normalized = _normalize_columns(df_raw)
        is_valid, missing_cols = _validate_required_columns(df_normalized)

        if not is_valid:
            metadata["files_skipped"].append(
                (file.name, f"Columnas requeridas faltantes: {', '.join(missing_cols)}")
            )
            continue

        raw_count = len(df_normalized)
        metadata["total_rows_raw"] += raw_count
        metadata["files_processed"] += 1
        frames.append(df_normalized)

    if not frames:
        return None, metadata

    # Concatenación segura
    consolidated = pd.concat(frames, ignore_index=True, sort=False)

    # Limpieza global post-concatenación
    pre_clean = len(consolidated)
    consolidated = _clean_dataframe(consolidated)
    metadata["duplicates_removed"] = pre_clean - len(consolidated)
    metadata["total_rows_clean"] = len(consolidated)

    return consolidated, metadata


def compute_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calcula métricas clave (KPIs) a partir del DataFrame consolidado.
    """
    kpis: Dict[str, Any] = {}

    kpis["total_registros"] = len(df)
    kpis["empresas_unicas"] = df["Empresa"].nunique() if "Empresa" in df.columns else 0

    if "Monto" in df.columns:
        monto_series = df["Monto"].dropna()
        kpis["monto_total"] = monto_series.sum()
        kpis["monto_promedio"] = monto_series.mean()
        kpis["monto_maximo"] = monto_series.max()
        kpis["monto_mediana"] = monto_series.median()
    else:
        kpis["monto_total"] = 0
        kpis["monto_promedio"] = 0
        kpis["monto_maximo"] = 0
        kpis["monto_mediana"] = 0

    if "Estado" in df.columns:
        kpis["distribucion_estado"] = df["Estado"].value_counts().to_dict()

    if "Categoría" in df.columns:
        kpis["distribucion_categoria"] = df["Categoría"].value_counts().to_dict()

    return kpis
