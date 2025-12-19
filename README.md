# 📊 EDA Panel - Exploratory Data Analysis

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white)
![CustomTkinter](https://img.shields.io/badge/CustomTkinter-5.2-green?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**Una aplicación de escritorio profesional para Análisis Exploratorio de Datos**

</div>

---

## ✨ Características

| Módulo | Funcionalidades |
|--------|-----------------|
| 📂 **Carga de Datos** | CSV, Excel, JSON • Detección automática de encoding • Barra de progreso |
| 📊 **Información del Dataset** | Resumen de filas/columnas • Uso de memoria • Indicador de calidad (semáforo) |
| 🔍 **Selector de Variables** | Tabs por tipo de dato • Búsqueda/filtrado • Barra de completitud |
| 📈 **Estadísticas Descriptivas** | Media, mediana, moda • Percentiles • Prueba de normalidad Shapiro-Wilk |
| 🎨 **Visualizaciones** | Histograma + KDE • Boxplot • Detección de outliers • Datos faltantes |
| 📄 **Reportes** | Generación de PDF • Copiar al portapapeles |

---

## 🖼️ Capturas de Pantalla

*La aplicación cuenta con tema oscuro profesional y diseño responsive.*

---

## 🚀 Instalación y Ejecución

### Opción 1: Script automático (Recomendado)

**Linux/Mac:**
```bash
chmod +x run_eda_panel.sh
./run_eda_panel.sh
```

**Windows:**
```
Doble clic en run_eda_panel.bat
```

### Opción 2: Manual

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/eda-panel.git
cd eda-panel

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
python main.py
```

---


## 🛠️ Tecnologías Utilizadas

- **GUI:** CustomTkinter
- **Datos:** pandas, numpy, openpyxl
- **Visualización:** matplotlib, seaborn
- **Estadística:** scipy, statsmodels
- **Reportes:** ReportLab

---

## 🛠️ Uso

Luego de clonar el repositorio puede usar el scrip ejecutable, se incluye un dataset "Simple_data" para hacer pruebas.

---

## 📋 Requisitos

- Python 3.10 o superior
- Sistema operativo: Windows, Linux, macOS

---


<div align="center">
Desarrollado con por Milton Tercero
</div>
