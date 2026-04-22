# DataVault — Dashboard Corporativo de Análisis de Datos Excel

Dashboard interactivo construido con **Streamlit + Pandas + Plotly** para la ingesta, consolidación y visualización de datos provenientes de múltiples archivos Excel.

## 🚀 Inicio Rápido

### 1. Crear entorno virtual e instalar dependencias

```bash
cd excel-dashboard
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
```

### 2. (Opcional) Generar datos de demostración

```bash
python generate_sample_data.py
```

Esto crea 3 archivos `.xlsx` de prueba en la carpeta `sample_data/`.

### 3. Ejecutar la aplicación

```bash
streamlit run app.py
```

La app se abrirá automáticamente en `http://localhost:8501`.

---

## 📋 Columnas Esperadas

| Columna      | Requerida | Aliases aceptados                                  |
| ------------ | --------- | -------------------------------------------------- |
| **Empresa**  | ✅ Sí     | empresa, nombre de la empresa, company, razon social |
| **Monto**    | ✅ Sí     | monto, importe, amount, valor, total                |
| Fecha        | ❌ No     | fecha, date, fecha_registro                         |
| Estado       | ❌ No     | estado, status, situación                           |
| Categoría    | ❌ No     | categoría, category, tipo, rubro, sector            |

> Las columnas se normalizan automáticamente (case-insensitive).

---

## 🏗️ Arquitectura

```
excel-dashboard/
├── .streamlit/
│   └── config.toml           # Tema corporativo dark
├── app.py                    # Aplicación principal (UI + layout)
├── data_loader.py            # Módulo de ingesta, validación y KPIs
├── charts.py                 # Módulo de visualización Plotly
├── generate_sample_data.py   # Generador de datos de prueba
├── requirements.txt          # Dependencias Python
└── README.md
```

---

## ✨ Funcionalidades

- **Carga múltiple** de archivos Excel con drag & drop
- **Normalización automática** de columnas vía aliases
- **KPIs** en tarjetas ejecutivas (monto total, empresas únicas, promedio, máximo)
- **Buscador avanzado** con autocompletado y texto libre
- **Tabla interactiva** con filtros por Estado y Categoría
- **4 tipos de gráficos** Plotly: barras horizontales (Top N), dona, línea temporal, barras por categoría
- **Estadísticas descriptivas** y matriz de correlación
- **Manejo de errores** con mensajes amigables
- **Diseño corporativo dark** con CSS personalizado
