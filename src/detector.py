"""
Módulo de Detección de Rostros (con Threading)
================================================
Usa InsightFace (ArcFace/RetinaFace) para:
- Detectar rostros en un frame
- Generar embeddings de 512 dimensiones (deep learning)
- Extraer edad y género

Soporta detección en hilo separado para no bloquear el renderizado.
"""
import warnings
import os
warnings.filterwarnings("ignore")
os.environ["PYTHONWARNINGS"] = "ignore"

import threading
import numpy as np
from insightface.app import FaceAnalysis
from config import MODELO_NOMBRE, DET_SIZE, CONFIANZA_DETECCION, USAR_THREADING


class Deteccion:
    """Resultado de una detección facial."""

    __slots__ = ['bbox', 'embedding', 'confianza', 'edad', 'genero', 'landmarks']

    def __init__(self, bbox, embedding, confianza, edad=None, genero=None, landmarks=None):
        self.bbox = bbox            # (x1, y1, x2, y2)
        self.embedding = embedding  # numpy array 512D normalizado
        self.confianza = confianza  # float 0.0 - 1.0
        self.edad = edad            # int o None
        self.genero = genero        # 'M' o 'F' o None
        self.landmarks = landmarks  # puntos faciales

    @property
    def centro(self):
        """Centro del bounding box."""
        x1, y1, x2, y2 = self.bbox
        return ((x1 + x2) / 2, (y1 + y2) / 2)

    @property
    def area(self):
        """Área del bounding box."""
        x1, y1, x2, y2 = self.bbox
        return (x2 - x1) * (y2 - y1)


class DetectorRostros:
    """
    Detector de rostros con InsightFace.
    Puede correr en modo síncrono o asíncrono (threading).
    """

    def __init__(self):
        print("[Detector] Cargando modelo de reconocimiento facial...")

        # Suprimir mensajes internos de ONNX/InsightFace
        import io
        import contextlib
        with contextlib.redirect_stderr(io.StringIO()), \
             contextlib.redirect_stdout(io.StringIO()):
            self.app = FaceAnalysis(
                name=MODELO_NOMBRE,
                providers=['CPUExecutionProvider']
            )
            self.app.prepare(ctx_id=-1, det_size=DET_SIZE)

        print("[Detector] Modelo cargado correctamente.")

        # Threading
        self.usar_threading = USAR_THREADING
        self._lock = threading.Lock()
        self._frame_pendiente = None
        self._resultados = []
        self._procesando = False
        self._hilo = None

    def detectar(self, frame):
        """
        Detección síncrona. Bloquea hasta tener resultados.
        Usa esto si USAR_THREADING = False.
        """
        return self._procesar_frame(frame)

    def detectar_async(self, frame):
        """
        Envía un frame para detección asíncrona.
        No bloquea. Retorna los últimos resultados disponibles.
        """
        if not self.usar_threading:
            return self.detectar(frame)

        with self._lock:
            if not self._procesando:
                self._procesando = True
                self._hilo = threading.Thread(
                    target=self._worker, args=(frame.copy(),), daemon=True
                )
                self._hilo.start()

        with self._lock:
            return list(self._resultados)

    def _worker(self, frame):
        """Worker thread para detección."""
        resultados = self._procesar_frame(frame)
        with self._lock:
            self._resultados = resultados
            self._procesando = False

    def _procesar_frame(self, frame):
        """Procesa un frame y retorna lista de Detecciones."""
        faces = self.app.get(frame)

        detecciones = []
        for face in faces:
            if face.det_score < CONFIANZA_DETECCION:
                continue

            bbox = face.bbox.astype(int)
            x1, y1, x2, y2 = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])

            embedding = face.embedding

            edad = int(face.age) if hasattr(face, 'age') and face.age is not None else None
            genero = None
            if hasattr(face, 'gender') and face.gender is not None:
                genero = 'M' if face.gender == 1 else 'F'

            landmarks = face.landmark_2d_106 if hasattr(face, 'landmark_2d_106') else None

            deteccion = Deteccion(
                bbox=(x1, y1, x2, y2),
                embedding=embedding,
                confianza=float(face.det_score),
                edad=edad,
                genero=genero,
                landmarks=landmarks
            )
            detecciones.append(deteccion)

        return detecciones
