"""
Módulo de Capturas
====================
Gestiona capturas de rostros individuales y screenshots completos.
Cada captura incluye timestamp en el nombre y opcionalmente en la imagen.
"""
import cv2
import os
import numpy as np
from datetime import datetime
from config import (
    RUTA_CAPTURAS, FORMATO_TIMESTAMP, CALIDAD_JPEG,
    COLOR_BLANCO, COLOR_NEGRO
)


def asegurar_carpeta():
    """Crea la carpeta de capturas si no existe."""
    os.makedirs(RUTA_CAPTURAS, exist_ok=True)


def capturar_rostro(frame, track, guardar=True):
    """
    Captura el rostro de un track específico.

    Args:
        frame: Frame BGR completo
        track: Objeto Track con bbox
        guardar: Si True, guarda en disco

    Returns:
        Imagen del rostro recortado con timestamp, o None si falla
    """
    asegurar_carpeta()

    x1, y1, x2, y2 = track.bbox
    h, w = frame.shape[:2]

    # Validar coordenadas
    x1 = max(0, x1)
    y1 = max(0, y1)
    x2 = min(w, x2)
    y2 = min(h, y2)

    if x2 <= x1 or y2 <= y1:
        return None

    # Recortar rostro con margen
    margen = 20
    x1m = max(0, x1 - margen)
    y1m = max(0, y1 - margen)
    x2m = min(w, x2 + margen)
    y2m = min(h, y2 + margen)

    rostro = frame[y1m:y2m, x1m:x2m].copy()

    if rostro.size == 0:
        return None

    # Agregar timestamp al rostro
    ahora = datetime.now()
    timestamp_texto = ahora.strftime("%Y-%m-%d %H:%M:%S")

    # Barra inferior con timestamp
    alto_barra = 25
    rostro_con_info = np.zeros(
        (rostro.shape[0] + alto_barra, rostro.shape[1], 3), dtype=np.uint8
    )
    rostro_con_info[:rostro.shape[0], :] = rostro
    rostro_con_info[rostro.shape[0]:, :] = (30, 30, 30)

    # Texto del timestamp
    nombre = track.nombre if hasattr(track, 'nombre') and track.nombre else f"Persona_{track.id + 1}"
    texto = f"{nombre} | {timestamp_texto}"
    cv2.putText(rostro_con_info, texto,
                (5, rostro.shape[0] + 17),
                cv2.FONT_HERSHEY_SIMPLEX, 0.35, COLOR_BLANCO, 1, cv2.LINE_AA)

    if guardar:
        # Nombre de archivo
        timestamp_archivo = ahora.strftime(FORMATO_TIMESTAMP)
        archivo = os.path.join(RUTA_CAPTURAS, f"{nombre}_{timestamp_archivo}.jpg")

        cv2.imwrite(archivo, rostro_con_info,
                    [cv2.IMWRITE_JPEG_QUALITY, CALIDAD_JPEG])
        print(f"  [Captura] Rostro guardado: {archivo}")

    return rostro_con_info


def capturar_todos(frame, tracks):
    """
    Captura todos los rostros visibles en el frame.

    Args:
        frame: Frame BGR completo
        tracks: Lista de tracks activos

    Returns:
        Lista de imágenes de rostros capturados
    """
    capturas = []
    for track in tracks:
        rostro = capturar_rostro(frame, track, guardar=True)
        if rostro is not None:
            capturas.append(rostro)
    return capturas


def screenshot(frame):
    """
    Guarda un screenshot del frame completo con anotaciones.

    Args:
        frame: Frame con la interfaz dibujada
    """
    asegurar_carpeta()

    ahora = datetime.now()
    timestamp = ahora.strftime(FORMATO_TIMESTAMP)
    archivo = os.path.join(RUTA_CAPTURAS, f"screenshot_{timestamp}.jpg")

    cv2.imwrite(archivo, frame, [cv2.IMWRITE_JPEG_QUALITY, CALIDAD_JPEG])
    print(f"  [Screenshot] Guardado: {archivo}")
