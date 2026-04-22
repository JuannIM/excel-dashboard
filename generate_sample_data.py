"""
generate_sample_data.py — Genera archivos Excel de demostración
================================================================
Ejecutar una vez para crear datos de prueba:
    python generate_sample_data.py
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

np.random.seed(42)

EMPRESAS = [
    "TechNova Solutions", "Minera Patagonia S.A.", "AgroVerde Corp",
    "Energía Solar del Norte", "Constructora Andes", "BioFarma Argentina",
    "LogiTrans S.R.L.", "DataCore Analytics", "Metalúrgica Federal",
    "GreenPack Envases", "Alimentos del Sur", "CloudBridge IT",
    "Petroquímica Litoral", "Textil Noroeste", "Finanzas Plus S.A.",
    "Agua Viva Servicios", "ElectroPower S.A.", "Consultora Nexus",
    "RedPoint Marketing", "Salud Integral SRL", "AutoParts Nacional",
    "CerealMax Export", "Inmobiliaria Capital", "TeleCom Express",
    "Laboratorios Delta",
]

ESTADOS = ["Activo", "Pendiente", "En revisión", "Completado", "Cancelado"]
CATEGORIAS = ["Tecnología", "Minería", "Agro", "Energía", "Construcción",
              "Salud", "Logística", "Finanzas", "Servicio", "Industria"]

def generate_file(filename: str, n_rows: int, start_date: str):
    """Genera un archivo Excel con datos corporativos simulados."""
    base_date = datetime.strptime(start_date, "%Y-%m-%d")

    data = {
        "Nombre de la Empresa": np.random.choice(EMPRESAS, n_rows),
        "Monto": np.round(np.random.lognormal(mean=10, sigma=1.5, size=n_rows), 2),
        "Fecha": [base_date + timedelta(days=int(x)) for x in np.random.randint(0, 365, n_rows)],
        "Estado": np.random.choice(ESTADOS, n_rows, p=[0.35, 0.25, 0.15, 0.15, 0.10]),
        "Categoría": np.random.choice(CATEGORIAS, n_rows),
    }

    df = pd.DataFrame(data)

    # Introducir algunos nulos realistas (~5%)
    null_indices = np.random.choice(n_rows, size=max(1, n_rows // 20), replace=False)
    df.loc[null_indices[:len(null_indices)//2], "Estado"] = None
    df.loc[null_indices[len(null_indices)//2:], "Categoría"] = None

    os.makedirs("sample_data", exist_ok=True)
    filepath = os.path.join("sample_data", filename)
    df.to_excel(filepath, index=False, engine="openpyxl")
    print(f"[OK] Generado: {filepath} ({n_rows} filas)")

if __name__ == "__main__":
    generate_file("empresas_q1_2025.xlsx", 80, "2025-01-01")
    generate_file("empresas_q2_2025.xlsx", 65, "2025-04-01")
    generate_file("empresas_q3_2025.xlsx", 90, "2025-07-01")
    print("\nDatos de demostracion generados en ./sample_data/")
