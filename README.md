# 🔍 ReconX 👁

**ReconX** es una herramienta gráfica de **reconocimiento y análisis de vulnerabilidades** en redes, diseñada para técnicos, estudiantes y entusiastas de la ciberseguridad.  
Combina el poder de **Nmap** para el escaneo de puertos y servicios con el análisis inteligente de **IA** para ofrecer informes detallados, visuales y fáciles de entender.

---

## ✨ Características

- **Interfaz moderna** con [`ttkbootstrap`](https://ttkbootstrap.readthedocs.io/en/latest/styleguide/button).
- **Escaneo configurable**: selección de cantidad de puertos, tipo de protocolo (TCP/UDP) y perfil de velocidad.
- **Detección de vulnerabilidades** con script [`vulners`](https://github.com/vulnersCom/nmap-vulners).
- **Análisis avanzado con IA**:
  - Top 3 riesgos críticos.
  - Mapa de vulnerabilidades por puerto.
  - Recomendaciones prácticas.
  - Análisis técnico profundo.
- **Exportación e importación** de resultados.
- **Intro multimedia** con VLC.
- Compatible con **Windows**.

---

## 📦 Instalación

### 1. Dependencias externas
ReconX necesita que tengas instalados:

- **[Nmap](https://nmap.org/download.html)**  
  Asegúrate de marcar **"Add to PATH"** durante la instalación.
- **[VLC Media Player](https://www.videolan.org/vlc/)**  
  También marca la opción de agregar VLC al PATH si existe.

> Si no están en el PATH, ReconX intentará localizarlos en las rutas comunes de instalación.

---

### 2. Uso desde código fuente (modo desarrollo)

Requisitos:
- Python 3.10 o superior
- pip actualizado

Clonar y configurar:
```bash
git clone https://github.com/whenigroup/ReconX.git
cd ReconX
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
