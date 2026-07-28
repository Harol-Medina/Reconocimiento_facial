"""
Configuración centralizada del proyecto.
=========================================
Ajusta estos valores para calibrar el comportamiento de la aplicación.
"""
import os

# ============================================================
# RUTAS
# ============================================================
RUTA_PROYECTO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUTA_DATOS = os.path.join(RUTA_PROYECTO, 'datos')
RUTA_CAPTURAS = os.path.join(RUTA_DATOS, 'capturas')
RUTA_REGISTRO = os.path.join(RUTA_DATOS, 'registro')
RUTA_HISTORIAL = os.path.join(RUTA_DATOS, 'historial')
RUTA_GRABACIONES = os.path.join(RUTA_DATOS, 'grabaciones')

# ============================================================
# CÁMARA
# ============================================================
CAMARA_ID = 0               # ID de la cámara (0 = default)
ANCHO_FRAME = 640           # Resolución horizontal
ALTO_FRAME = 480            # Resolución vertical

# ============================================================
# DETECCIÓN (InsightFace)
# ============================================================
MODELO_NOMBRE = "buffalo_l"  # Modelo (buffalo_l = mejor precisión, buffalo_s = más rápido)
DET_SIZE = (640, 640)        # Tamaño de detección
CONFIANZA_DETECCION = 0.5    # Umbral mínimo de confianza

# ============================================================
# TRACKING Y RE-IDENTIFICACIÓN
# ============================================================
UMBRAL_RECONOCIMIENTO = 0.4   # Similitud coseno mínima (mayor = más estricto)
DISTANCIA_MAX_TRACKING = 150  # Píxeles máximos para asociar detección con track
FRAMES_PARA_PERDER = 15       # Frames sin ver antes de perder un track
FRAMES_PARA_CONFIRMAR = 3     # Frames mínimos para confirmar una persona

# ============================================================
# CAPTURAS
# ============================================================
FORMATO_TIMESTAMP = "%Y-%m-%d_%H-%M-%S"  # Formato para nombres de archivo
CALIDAD_JPEG = 95                         # Calidad de guardado (1-100)

# ============================================================
# HISTORIAL
# ============================================================
ARCHIVO_HISTORIAL = "historial_presencia.csv"
INTERVALO_LOG = 1.0  # Segundos mínimos entre logs de la misma persona

# ============================================================
# GRABACIÓN
# ============================================================
CODEC_VIDEO = "XVID"    # Codec para grabación (XVID, MJPG, mp4v)
FPS_GRABACION = 20.0    # FPS del video grabado

# ============================================================
# INTERFAZ
# ============================================================
# Panel lateral
ANCHO_PANEL = 200          # Ancho del panel lateral en píxeles
TAMANO_MINIATURA = 60      # Tamaño de miniatura de rostro

# Temas
TEMAS = {
    "oscuro": {
        "fondo_hud": (20, 20, 20),
        "texto_principal": (0, 230, 0),
        "texto_secundario": (160, 160, 160),
        "texto_info": (220, 220, 220),
        "fondo_panel": (30, 30, 30),
    },
    "claro": {
        "fondo_hud": (240, 240, 240),
        "texto_principal": (0, 150, 0),
        "texto_secundario": (80, 80, 80),
        "texto_info": (40, 40, 40),
        "fondo_panel": (230, 230, 230),
    }
}
TEMA_DEFAULT = "oscuro"

# Colores BGR para cada persona
COLORES = [
    (72, 255, 72),     # Verde
    (255, 150, 50),    # Azul
    (50, 220, 255),    # Amarillo
    (255, 100, 255),   # Magenta
    (80, 200, 255),    # Naranja
    (255, 255, 100),   # Cyan
    (200, 100, 255),   # Violeta
    (150, 255, 150),   # Verde claro
    (255, 180, 130),   # Azul claro
    (130, 130, 255),   # Rojo claro
]

COLOR_BLANCO = (255, 255, 255)
COLOR_NEGRO = (0, 0, 0)
COLOR_GRIS = (160, 160, 160)
COLOR_ALERTA = (0, 0, 255)

# Mostrar información extra
MOSTRAR_GENERO_EDAD = True
MOSTRAR_RELOJ = True
MOSTRAR_PANEL = True

# ============================================================
# ALERTAS
# ============================================================
ALERTA_PERSONA_NUEVA = True   # Alertar cuando aparece alguien nuevo
DURACION_ALERTA = 2.0         # Segundos que dura la alerta visual

# ============================================================
# THREADING
# ============================================================
USAR_THREADING = True  # Detección en hilo separado para más FPS
