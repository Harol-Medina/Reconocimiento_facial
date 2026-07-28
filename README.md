<div align="center">

# 🎯 Reconocimiento Facial en Tiempo Real

**Sistema inteligente que detecta, diferencia y reconoce múltiples personas en vivo usando inteligencia artificial.**

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.10%2B-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)](https://opencv.org)
[![InsightFace](https://img.shields.io/badge/InsightFace-ArcFace_512D-FF6F00?style=for-the-badge)](https://insightface.ai)
[![ONNX](https://img.shields.io/badge/ONNX_Runtime-1.17%2B-7B1FA2?style=for-the-badge)](https://onnxruntime.ai)

<br>

*Abre la cámara → detecta caras → las diferencia automáticamente → sin registro previo*

---

</div>

## 📌 ¿Qué es esto?

Un programa que al abrirlo enciende tu cámara web y automáticamente:

1. **Detecta** todas las caras que aparezcan
2. **Diferencia** quién es quién (Persona 1, Persona 2, etc.)
3. **Recuerda** — si alguien se va y vuelve, lo reconoce
4. **Aprende nombres** — le asignas un nombre y lo recuerda para siempre

No necesitas tomarle fotos antes. No necesitas entrenar nada. Solo ejecutas y funciona.

---

## ⚡ Inicio rápido

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Ejecutar
python src/main.py
```

> 💡 La primera ejecución descarga el modelo de IA (~280MB). Solo pasa una vez.

---

## 🎮 Controles

<div align="center">

| Tecla | Acción | Detalle |
|:-----:|--------|---------|
| `C` | 📷 Capturar | Guarda foto recortada de cada rostro con fecha y hora |
| `S` | 🖼️ Screenshot | Guarda la pantalla completa tal como se ve |
| `N` | ✏️ Nombrar | Asigna un nombre a la persona (se guarda permanentemente) |
| `G` | 🎬 Grabar | Inicia o detiene grabación de video |
| `T` | 🎨 Tema | Alterna entre interfaz oscura y clara |
| `R` | 🔄 Reset | Olvida a todas las personas de esta sesión |
| `Q` | ❌ Salir | Cierra la aplicación |

</div>

---

## 🧠 ¿Cómo funciona?

<div align="center">

```
┌─────────────┐       ┌──────────────────┐       ┌─────────────────┐       ┌────────────┐
│             │       │                  │       │                 │       │            │
│   CÁMARA    │──────►│    DETECTOR      │──────►│    TRACKER      │──────►│     UI     │
│             │       │                  │       │                 │       │            │
│  Captura    │       │  Encuentra las   │       │  Decide quién   │       │  Dibuja    │
│  imagen     │       │  caras y genera  │       │  es quién       │       │  todo en   │
│  30 veces   │       │  una "huella"    │       │  comparando     │       │  pantalla  │
│  por segundo│       │  única de 512    │       │  huellas y      │       │            │
│             │       │  números por     │       │  posiciones     │       │            │
│             │       │  cada rostro     │       │                 │       │            │
└─────────────┘       └──────────────────┘       └────────┬────────┘       └────────────┘
                                                          │
                                                          │
                              ┌────────────────────────────┼────────────────────────────┐
                              │                            │                            │
                              ▼                            ▼                            ▼
                    ┌──────────────────┐       ┌──────────────────┐       ┌──────────────────┐
                    │                  │       │                  │       │                  │
                    │    REGISTRO      │       │    HISTORIAL     │       │    CAPTURAS      │
                    │                  │       │                  │       │                  │
                    │  ¿Tiene nombre?  │       │  Anota a qué     │       │  Guarda fotos    │
                    │  Si ya lo vi     │       │  hora llegó y    │       │  cuando el       │
                    │  antes, lo       │       │  a qué hora se   │       │  usuario lo      │
                    │  llamo por       │       │  fue cada        │       │  pide            │
                    │  su nombre       │       │  persona         │       │                  │
                    │                  │       │                  │       │                  │
                    └──────────────────┘       └──────────────────┘       └──────────────────┘
```

</div>

### La "huella facial" explicada simple

Cada rostro se convierte en **512 números**. Es como un código de barras de tu cara:

```
Tu cara:           [0.12, -0.45, 0.78, 0.33, -0.91, ...]  → 512 valores
Tu cara (otra foto): [0.11, -0.44, 0.77, 0.34, -0.90, ...]  → Casi iguales ✓

Otra persona:      [0.89, 0.23, -0.56, 0.11, 0.67, ...]  → Muy diferente ✗
```

Dos fotos tuyas siempre dan números parecidos. Otra persona siempre da números diferentes. Así el sistema sabe quién es quién.

---

## 📁 Estructura del proyecto

```
Reconocimiento_facial/
│
├── src/                           CÓDIGO FUENTE
│   ├── main.py                    → Punto de entrada (esto es lo que ejecutas)
│   ├── detector.py                → Motor de IA: encuentra caras + genera huella
│   ├── tracker.py                 → Seguimiento: sabe quién es quién entre frames
│   ├── ui.py                      → Interfaz: dibuja recuadros, panel, reloj, HUD
│   ├── capturas.py                → Guarda fotos de rostros con fecha/hora
│   ├── registro.py                → Base de datos de nombres (persiste en disco)
│   ├── historial.py               → Log CSV de quién estuvo y cuándo
│   └── config.py                  → Toda la configuración en un solo lugar
│
├── datos/                         SE CREA AUTOMÁTICAMENTE
│   ├── capturas/                  → Fotos guardadas con tecla C
│   ├── registro/                  → Nombres que asignas (tecla N)
│   ├── historial/                 → CSV: persona, entrada, salida, duración
│   └── grabaciones/               → Videos con tecla G
│
├── requirements.txt               → Las 4 dependencias del proyecto
├── .gitignore                     → Lo que git no sube
└── README.md                      → Este archivo
```

---

## 🔧 Instalación detallada

### Requisitos previos

| Necesitas | Por qué |
|-----------|---------|
| Python 3.9+ | El lenguaje. Probado con 3.11, 3.12, 3.14 |
| Cámara web | Para capturar video en vivo |
| Internet | Solo la primera vez (descarga modelo de 280MB) |

### Paso 1: Instalar dependencias

```bash
pip install -r requirements.txt
```

<details>
<summary><b>¿Qué instala exactamente?</b> (clic para expandir)</summary>
<br>

| Paquete | Versión | Función | Tamaño aprox |
|---------|---------|---------|:------------:|
| `opencv-python` | ≥4.10 | Cámara, video, dibujar interfaz | ~40MB |
| `insightface` | ≥1.0 | Detectar caras, generar huellas faciales, edad/género | ~1MB (+ modelo 280MB la 1ra vez) |
| `onnxruntime` | ≥1.17 | Ejecutar modelos de IA eficientemente en CPU | ~15MB |
| `numpy` | ≥1.26 | Cálculos numéricos (comparar vectores) | ~20MB |

No necesita CMake. No necesita compilar. No necesita Visual Studio. Se instala directo.
</details>

### Paso 2: Ejecutar

```bash
python src/main.py
```

### Opciones de ejecución

```bash
python src/main.py --camera 1              # Usar segunda cámara
python src/main.py --tema claro            # Interfaz clara
python src/main.py --no-panel              # Sin panel lateral
python src/main.py --ancho 1280 --alto 720 # Resolución HD
python src/main.py --threshold 0.5         # Más exigente al diferenciar
python src/main.py --help                  # Ver todas las opciones
```

---

## ⚙️ Configuración

Todo se ajusta editando `src/config.py`:

<div align="center">

| Qué quieres cambiar | Variable | Valor actual | Qué hace |
|:---------------------|:---------|:------------:|:---------|
| Sensibilidad de detección | `CONFIANZA_DETECCION` | `0.5` | Más bajo = detecta más (pero puede haber falsos) |
| Exigencia para reconocer | `UMBRAL_RECONOCIMIENTO` | `0.4` | Más alto = necesita más parecido para decir "es la misma persona" |
| Tiempo antes de olvidar | `FRAMES_PARA_PERDER` | `15` | Si no ve a alguien por 15 frames, lo da por ido |
| Panel lateral | `MOSTRAR_PANEL` | `True` | Muestra miniaturas de cada persona a la derecha |
| Edad y género | `MOSTRAR_GENERO_EDAD` | `True` | Muestra estimación debajo del nombre |
| Alerta persona nueva | `ALERTA_PERSONA_NUEVA` | `True` | Aviso rojo cuando aparece alguien que no conoce |
| Detección en paralelo | `USAR_THREADING` | `True` | Detecta en un hilo separado para más fluidez |

</div>

---

## 📊 Datos que genera

### Historial de presencia (`datos/historial/historial_presencia.csv`)

Cada vez que alguien aparece y desaparece de la cámara, se registra:

```csv
persona,entrada,salida,duracion_segundos,fecha
Franklin,14:23:05,14:25:30,145.0,2026-07-27
Persona_2,14:24:10,14:24:55,45.0,2026-07-27
```

### Capturas (`datos/capturas/`)

Cuando presionas `C`, guarda la cara recortada con nombre + fecha + hora en el nombre del archivo:

```
Franklin_2026-07-27_14-23-15.jpg
Persona_2_2026-07-27_14-24-30.jpg
```

### Registro (`datos/registro/`)

Cuando presionas `N` y le das un nombre a alguien, se guarda su huella facial en disco. La próxima vez que abras la app y esa persona aparezca, la reconoce sin que hagas nada.

---

## 🛠️ Tecnología

<div align="center">

| Capa | Tecnología | Modelo | Qué resuelve |
|:----:|:-----------|:------:|:-------------|
| Detección | InsightFace | RetinaFace | ¿Dónde están las caras en la imagen? |
| Reconocimiento | InsightFace | ArcFace (512D) | ¿De quién es esta cara? |
| Demografía | InsightFace | GenderAge | ¿Qué edad tiene? ¿Hombre o mujer? |
| Inferencia | ONNX Runtime | CPU | Ejecutar los 3 modelos rápido sin GPU |
| Video | OpenCV | — | Leer cámara, dibujar interfaz, grabar |
| Tracking | Propio | — | Seguir personas entre frames |

</div>

> 📝 Todo corre en CPU. No necesitas tarjeta gráfica dedicada.

---

## ❓ Preguntas frecuentes

<details>
<summary><b>¿Necesito crear un entorno virtual (venv)?</b></summary>
<br>
No es obligatorio. Pero si quieres aislar las dependencias:

```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
</details>

<details>
<summary><b>¿Funciona sin internet?</b></summary>
<br>
Sí, después de la primera ejecución. El modelo se descarga una sola vez y queda en <code>~/.insightface/models/</code>.
</details>

<details>
<summary><b>¿Qué tan preciso es?</b></summary>
<br>
ArcFace tiene ~99.5% de precisión en el benchmark LFW. En la práctica diferencia bien entre personas distintas.
</details>

<details>
<summary><b>¿Puede reconocer a alguien solo con una foto?</b></summary>
<br>
No directamente. Está diseñado para cámara en vivo. Pero si registras a alguien con la tecla N, la próxima sesión lo reconoce automáticamente.
</details>

<details>
<summary><b>¿Qué pasa si la cámara se desconecta?</b></summary>
<br>
La app intenta reconectar automáticamente hasta 3 veces antes de cerrarse.
</details>

---

## 🚀 Posibles mejoras futuras

- [ ] Interfaz web (ver desde el navegador o celular)
- [ ] Soporte GPU con `onnxruntime-gpu`
- [ ] Múltiples cámaras simultáneas
- [ ] Notificaciones por Telegram/Discord cuando aparece alguien
- [ ] Exportar historial a Excel
- [ ] Modo de solo detección (sin reconocimiento, más rápido)

---

<div align="center">

**Hecho con Python, OpenCV e InsightFace**

</div>
