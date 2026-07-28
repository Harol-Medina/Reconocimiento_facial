# Reconocimiento Facial en Tiempo Real

Un sistema que abre tu cámara y reconoce caras automáticamente. Si hay 2 personas frente a la cámara, las diferencia. Si alguien se va y vuelve, lo reconoce. Puedes asignarle nombres y la próxima vez que aparezcan, los llama por su nombre.

No necesitas tomarle fotos antes, no necesitas entrenar nada. Solo abres la app y funciona.

---

## Qué puede hacer

- Detectar todas las caras que aparezcan frente a la cámara
- Diferenciar personas automáticamente (Persona 1, Persona 2, etc.)
- Reconocer si alguien sale del cuadro y vuelve a entrar
- Estimar edad y género de cada persona
- Guardar capturas de rostros con fecha y hora
- Asignar nombres que se guardan para siempre (la próxima sesión los recuerda)
- Llevar un historial en CSV de quién estuvo, cuándo llegó y cuándo se fue
- Grabar video
- Panel lateral con miniaturas de cada persona en vivo

---

## Cómo se ve cuando corre

Cuando ejecutas la app se abre una ventana con la cámara. Cada persona tiene:
- Un recuadro de color único con esquinas estilizadas
- Su nombre o ID arriba del recuadro
- Edad y género estimados
- Una barra que indica cuánto tiempo lleva en pantalla
- Un panel a la derecha con miniaturas de todos

Arriba hay un HUD con: personas activas, total vistas, cuadros por segundo y un reloj.

---

## Requisitos para que funcione

- **Python 3.9 o superior** (probado con 3.14)
- **Una cámara web** conectada
- **Internet** solo la primera vez (descarga el modelo de IA, pesa ~280MB)
- **Windows, Linux o Mac**

---

## Instalación paso a paso

### 1. Instalar las dependencias

Abre una terminal en la carpeta del proyecto y ejecuta:

```
pip install -r requirements.txt
```

Eso instala 4 paquetes:

| Paquete | Qué hace |
|---------|----------|
| `opencv-python` | Abre la cámara y dibuja la interfaz |
| `insightface` | El cerebro: detecta caras y genera la "huella facial" de cada persona |
| `onnxruntime` | Ejecuta los modelos de inteligencia artificial de forma rápida |
| `numpy` | Hace los cálculos matemáticos de comparación de rostros |

> No necesitas CMake, no necesitas compilar nada, no necesitas Visual Studio. Se instala directo.

### 2. Ejecutar

```
python src/main.py
```

La primera vez tarda unos segundos extra porque descarga el modelo de IA (~280MB). Se guarda en tu carpeta de usuario y no se vuelve a descargar.

---

## Controles

Todo se controla con teclas mientras la ventana de la cámara está abierta:

| Tecla | Qué hace |
|:-----:|----------|
| `C` | Captura el rostro de cada persona visible y lo guarda como imagen con fecha/hora |
| `S` | Toma un screenshot de toda la pantalla tal como se ve |
| `N` | Te pide un nombre en la terminal y se lo asigna a la persona (se guarda para siempre) |
| `G` | Empieza o detiene la grabación de video |
| `T` | Cambia entre tema oscuro y tema claro |
| `R` | Resetea: olvida a todas las personas de esta sesión |
| `Q` | Cierra la app |

---

## Opciones avanzadas (línea de comandos)

Si quieres personalizar algo al ejecutar:

```
python src/main.py --camera 1          # Usar otra cámara
python src/main.py --tema claro        # Empezar con tema claro
python src/main.py --no-panel          # Sin el panel lateral
python src/main.py --ancho 1280 --alto 720   # Resolución HD
python src/main.py --threshold 0.5     # Más estricto al diferenciar personas
```

Para ver todas las opciones:

```
python src/main.py --help
```

---

## Dónde se guardan las cosas

Todo se guarda automáticamente en una carpeta `datos/` que se crea sola:

```
datos/
├── capturas/       ← Fotos de rostros cuando presionas C
├── registro/       ← Los nombres que asignas (se mantienen entre sesiones)
├── historial/      ← CSV con hora de entrada, salida y duración de cada persona
└── grabaciones/    ← Videos cuando presionas G
```

---

## Estructura del proyecto

```
Reconocimiento_facial/
│
├── 📁 src/                        ← Código fuente
│   ├── 🚀 main.py                ← Punto de entrada (ejecuta esto)
│   ├── 🧠 detector.py            ← Motor de IA: detecta caras + huella facial
│   ├── 🔍 tracker.py             ← Seguimiento: sabe quién es quién entre frames
│   ├── 🎨 ui.py                  ← Interfaz: dibuja todo lo visual
│   ├── 📷 capturas.py            ← Guarda fotos de rostros con fecha/hora
│   ├── 📝 registro.py            ← Base de datos de nombres (persistente)
│   ├── 📊 historial.py           ← Log CSV de presencia
│   └── ⚙️  config.py              ← Configuración en un solo lugar
│
├── 📁 datos/                      ← Se crea automáticamente
│   ├── 📷 capturas/              ← Fotos de rostros (tecla C)
│   ├── 📝 registro/              ← Nombres guardados (.pkl)
│   ├── 📊 historial/             ← CSV de presencia
│   └── 🎬 grabaciones/           ← Videos grabados (tecla G)
│
├── 📋 requirements.txt            ← Dependencias (pip install -r)
├── 🚫 .gitignore                  ← Archivos que git ignora
└── 📖 README.md                   ← Este archivo
```

---

## Cómo funciona por dentro

### Arquitectura general

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              APLICACIÓN (main.py)                            │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                         PIPELINE DE PROCESAMIENTO                      │  │
│  │                                                                       │  │
│  │  ┌──────────┐    ┌──────────────┐    ┌────────────┐    ┌──────────┐  │  │
│  │  │          │    │              │    │            │    │          │  │  │
│  │  │  CÁMARA  │───►│  DETECTOR    │───►│  TRACKER   │───►│    UI    │  │  │
│  │  │          │    │              │    │            │    │          │  │  │
│  │  │ Captura  │    │ InsightFace  │    │ Asociación │    │ Dibujar  │  │  │
│  │  │ frames   │    │ RetinaFace + │    │ espacial + │    │ interfaz │  │  │
│  │  │ en vivo  │    │ ArcFace 512D │    │ embedding  │    │ completa │  │  │
│  │  │          │    │ + edad/género│    │            │    │          │  │  │
│  │  └──────────┘    └──────────────┘    └─────┬──────┘    └──────────┘  │  │
│  │                                            │                          │  │
│  └────────────────────────────────────────────┼──────────────────────────┘  │
│                                               │                             │
│  ┌────────────────────────────────────────────┼──────────────────────────┐  │
│  │                        SERVICIOS DE DATOS  │                           │  │
│  │                                            │                           │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────┴─────────┐                │  │
│  │  │              │  │              │  │              │                │  │
│  │  │   REGISTRO   │  │  HISTORIAL   │  │   CAPTURAS   │                │  │
│  │  │              │  │              │  │              │                │  │
│  │  │ Nombres de   │  │ CSV con hora │  │ Fotos con    │                │  │
│  │  │ personas     │  │ de entrada,  │  │ fecha y hora │                │  │
│  │  │ guardados    │  │ salida y     │  │ de cada      │                │  │
│  │  │ en disco     │  │ duración     │  │ rostro       │                │  │
│  │  │ (.pkl)       │  │ (.csv)       │  │ (.jpg)       │                │  │
│  │  │              │  │              │  │              │                │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘                │  │
│  │                                                                       │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Flujo de reconocimiento (lo que pasa en cada frame)

```
 FRAME DE CÁMARA
       │
       ▼
 ┌─────────────────────────────────────────────────────────────┐
 │  1. DETECCIÓN                                                │
 │                                                              │
 │  El modelo RetinaFace busca rostros en la imagen.            │
 │  Por cada rostro encontrado genera:                          │
 │    • Coordenadas (dónde está la cara)                        │
 │    • Embedding de 512 dimensiones (la "huella facial")       │
 │    • Edad estimada                                           │
 │    • Género estimado                                         │
 │    • Nivel de confianza                                      │
 └──────────────────────────┬──────────────────────────────────┘
                            │
                            ▼
 ┌─────────────────────────────────────────────────────────────┐
 │  2. TRACKING (Asociación)                                    │
 │                                                              │
 │  Para cada rostro detectado, el tracker decide:              │
 │                                                              │
 │  ¿Está CERCA de donde estaba alguien en el frame anterior?   │
 │        │                                                     │
 │        ├── SÍ ──► ¿Su huella facial coincide? ──► MISMA      │
 │        │                                          PERSONA    │
 │        │                                                     │
 │        └── NO ──► ¿Su huella coincide con alguien            │
 │                    que se fue hace poco? ──► REAPARECIÓ       │
 │                                                              │
 │  Si no coincide con nadie ──► PERSONA NUEVA (nuevo ID)       │
 └──────────────────────────┬──────────────────────────────────┘
                            │
                            ▼
 ┌─────────────────────────────────────────────────────────────┐
 │  3. RENDERIZADO                                              │
 │                                                              │
 │  Se dibuja sobre el frame:                                   │
 │    • Recuadro con color único por persona                    │
 │    • Nombre o ID                                             │
 │    • Edad y género                                           │
 │    • Panel lateral con miniaturas                            │
 │    • HUD con estadísticas                                    │
 │    • Reloj                                                   │
 │    • Alertas si aparece alguien nuevo                        │
 └─────────────────────────────────────────────────────────────┘
```

### ¿Qué es la "huella facial"?

Es un vector de **512 números** que representa matemáticamente la cara de una persona. Funciona como un DNI numérico del rostro:

```
Persona A:  [0.12, -0.45, 0.78, 0.33, -0.91, ...]  (512 valores)
Persona B:  [0.89, 0.23, -0.56, 0.11, 0.67, ...]   (512 valores)

Similitud entre A y A (otra foto): 0.92  ← MUY parecidos = misma persona
Similitud entre A y B:             0.15  ← MUY diferentes = personas distintas
```

El modelo ArcFace genera estos vectores de manera que dos fotos de la misma persona siempre producen vectores cercanos, sin importar si cambió de ángulo, expresión o iluminación.

---

## Configuración

Si quieres ajustar el comportamiento, edita `src/config.py`. Los más importantes:

| Qué ajustar | Variable | Default | Explicación |
|---|---|---|---|
| Sensibilidad de detección | `CONFIANZA_DETECCION` | 0.5 | Más bajo detecta más caras pero puede tener falsos positivos |
| Diferenciación de personas | `UMBRAL_RECONOCIMIENTO` | 0.4 | Más alto = necesita más parecido para decir que es la misma persona |
| Cuánto espera antes de olvidar | `FRAMES_PARA_PERDER` | 15 | Si alguien desaparece por 15 frames, lo da por ido |
| Panel lateral | `MOSTRAR_PANEL` | True | Muestra/oculta el panel con miniaturas |
| Edad y género | `MOSTRAR_GENERO_EDAD` | True | Muestra/oculta la estimación de edad/género |
| Alertas | `ALERTA_PERSONA_NUEVA` | True | Aviso visual cuando aparece alguien nuevo |

---

## Preguntas frecuentes

**¿Necesito entorno virtual (venv)?**
No es obligatorio. Las dependencias se instalan sin conflictos. Pero si prefieres aislarlo:
```
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**¿El requirements.txt es necesario?**
Sí. Es la lista de dependencias del proyecto. Sin él tendrías que instalar cada paquete a mano.

**¿Funciona sin internet?**
Sí, después de la primera ejecución. El modelo se descarga una sola vez y queda guardado.

**¿Qué tan preciso es?**
Usa el modelo ArcFace que tiene ~99.5% de precisión en benchmarks estándar. En la práctica funciona muy bien para diferenciar personas.

**¿Puede reconocer a alguien de una foto?**
No directamente. Está diseñado para cámara en vivo. Pero puedes registrar a alguien (tecla N) y la próxima vez que aparezca lo reconoce.

---

## Tecnología que usa

El proyecto usa **InsightFace** con el modelo **buffalo_l**, que incluye:

- **RetinaFace** para detectar dónde están las caras
- **ArcFace** para generar la huella facial única de cada persona (512 dimensiones)
- **GenderAge** para estimar edad y género

Todo corre en CPU con ONNX Runtime. No necesitas GPU ni tarjeta gráfica especial.
