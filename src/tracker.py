"""
Módulo de Tracking y Re-identificación
=========================================
Combina tracking espacial con re-identificación por embeddings.
Integra registro de nombres y alertas de personas nuevas.
"""
import time
import numpy as np
from config import (
    UMBRAL_RECONOCIMIENTO,
    DISTANCIA_MAX_TRACKING,
    FRAMES_PARA_PERDER,
    FRAMES_PARA_CONFIRMAR,
    ALERTA_PERSONA_NUEVA,
    DURACION_ALERTA
)


def similitud_coseno(emb1, emb2):
    """Similitud coseno entre dos embeddings."""
    norma1 = np.linalg.norm(emb1)
    norma2 = np.linalg.norm(emb2)
    if norma1 < 1e-6 or norma2 < 1e-6:
        return 0.0
    return float(np.dot(emb1, emb2) / (norma1 * norma2))


def distancia_euclidiana(p1, p2):
    """Distancia entre dos puntos."""
    return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)


class Track:
    """Representa el tracking de una persona."""

    _next_id = 0

    def __init__(self, deteccion):
        self.id = Track._next_id
        Track._next_id += 1

        self.embedding = deteccion.embedding.copy()
        self.embeddings_hist = [deteccion.embedding.copy()]
        self.bbox = deteccion.bbox
        self.centro = deteccion.centro
        self.confianza = deteccion.confianza
        self.edad = deteccion.edad
        self.genero = deteccion.genero

        self.nombre = None  # Se asigna desde el registro
        self.frames_visto = 1
        self.frames_perdido = 0
        self.activo = True
        self.confirmado = False

        # Timing
        self.tiempo_primera_vez = time.time()
        self.tiempo_ultima_vez = time.time()

        # Miniatura del rostro
        self.miniatura = None

    def actualizar(self, deteccion):
        """Actualiza el track con una nueva detección."""
        self.bbox = deteccion.bbox
        self.centro = deteccion.centro
        self.confianza = deteccion.confianza
        self.frames_visto += 1
        self.frames_perdido = 0
        self.activo = True
        self.tiempo_ultima_vez = time.time()

        if deteccion.edad is not None:
            self.edad = deteccion.edad
        if deteccion.genero is not None:
            self.genero = deteccion.genero

        # Promedio móvil del embedding
        self.embeddings_hist.append(deteccion.embedding.copy())
        if len(self.embeddings_hist) > 20:
            self.embeddings_hist = self.embeddings_hist[-20:]
        self.embedding = np.mean(self.embeddings_hist, axis=0)
        norma = np.linalg.norm(self.embedding)
        if norma > 0:
            self.embedding = self.embedding / norma

        if self.frames_visto >= FRAMES_PARA_CONFIRMAR:
            self.confirmado = True

    def marcar_perdido(self):
        """Marca un frame sin detección. Retorna False si el track muere."""
        self.frames_perdido += 1
        self.activo = False
        return self.frames_perdido <= FRAMES_PARA_PERDER

    @property
    def tiempo_en_pantalla(self):
        """Segundos que lleva visible."""
        return time.time() - self.tiempo_primera_vez

    @staticmethod
    def reset_ids():
        Track._next_id = 0


class Alerta:
    """Representa una alerta visual temporal."""

    def __init__(self, mensaje, duracion=DURACION_ALERTA):
        self.mensaje = mensaje
        self.tiempo_inicio = time.time()
        self.duracion = duracion

    @property
    def activa(self):
        return (time.time() - self.tiempo_inicio) < self.duracion


class TrackerPersonas:
    """Tracker multi-persona con tracking espacial + re-identificación."""

    def __init__(self, registro=None):
        self.tracks = []
        self.tracks_totales = 0
        self.registro = registro  # RegistroPersonas (opcional)
        self.alertas = []

    def actualizar(self, detecciones):
        """Actualiza con nuevas detecciones. Retorna tracks visibles."""
        if not detecciones:
            self._marcar_todos_perdidos()
            return self._tracks_visibles()

        if not self.tracks:
            for det in detecciones:
                self._crear_track(det)
            return self._tracks_visibles()

        # Matrices de asociación
        n_tracks = len(self.tracks)
        n_dets = len(detecciones)

        matriz_score = np.full((n_tracks, n_dets), -np.inf)

        for i, track in enumerate(self.tracks):
            for j, det in enumerate(detecciones):
                dist = distancia_euclidiana(track.centro, det.centro)
                sim = similitud_coseno(track.embedding, det.embedding)

                if dist < DISTANCIA_MAX_TRACKING and sim > UMBRAL_RECONOCIMIENTO:
                    matriz_score[i, j] = sim - (dist / DISTANCIA_MAX_TRACKING) * 0.3

        # Asociación greedy
        tracks_matcheados = set()
        dets_matcheadas = set()

        while True:
            if matriz_score.max() == -np.inf:
                break
            i, j = np.unravel_index(np.argmax(matriz_score), matriz_score.shape)
            if i in tracks_matcheados or j in dets_matcheadas:
                matriz_score[i, j] = -np.inf
                continue
            tracks_matcheados.add(i)
            dets_matcheadas.add(j)
            self.tracks[i].actualizar(detecciones[j])
            matriz_score[i, :] = -np.inf
            matriz_score[:, j] = -np.inf

        # Re-identificación por embedding puro (persona que reapareció)
        for j in range(n_dets):
            if j in dets_matcheadas:
                continue
            mejor_sim = UMBRAL_RECONOCIMIENTO
            mejor_track = -1
            for i in range(n_tracks):
                if i in tracks_matcheados:
                    continue
                sim = similitud_coseno(self.tracks[i].embedding, detecciones[j].embedding)
                if sim > mejor_sim:
                    mejor_sim = sim
                    mejor_track = i
            if mejor_track >= 0:
                tracks_matcheados.add(mejor_track)
                dets_matcheadas.add(j)
                self.tracks[mejor_track].actualizar(detecciones[j])

        # Nuevos tracks
        for j in range(n_dets):
            if j not in dets_matcheadas:
                self._crear_track(detecciones[j])

        # Marcar perdidos
        tracks_vivos = []
        for i, track in enumerate(self.tracks):
            if i in tracks_matcheados:
                tracks_vivos.append(track)
            else:
                if track.marcar_perdido():
                    tracks_vivos.append(track)
        self.tracks = tracks_vivos

        # Limpiar alertas expiradas
        self.alertas = [a for a in self.alertas if a.activa]

        return self._tracks_visibles()

    def _crear_track(self, deteccion):
        """Crea un nuevo track y busca en el registro."""
        track = Track(deteccion)

        # Buscar en registro de nombres
        if self.registro:
            nombre, sim = self.registro.buscar(deteccion.embedding)
            if nombre:
                track.nombre = nombre

        # Alerta de persona nueva
        if ALERTA_PERSONA_NUEVA and not track.nombre:
            self.alertas.append(Alerta(f"Nueva persona detectada (ID: {track.id + 1})"))

        self.tracks.append(track)
        self.tracks_totales += 1

    def _marcar_todos_perdidos(self):
        tracks_vivos = []
        for track in self.tracks:
            if track.marcar_perdido():
                tracks_vivos.append(track)
        self.tracks = tracks_vivos

    def _tracks_visibles(self):
        return [t for t in self.tracks if t.activo and t.confirmado]

    def obtener_track_por_id(self, track_id):
        """Busca un track por su ID."""
        for track in self.tracks:
            if track.id == track_id:
                return track
        return None

    def reset(self):
        self.tracks = []
        self.tracks_totales = 0
        self.alertas = []
        Track.reset_ids()

    @property
    def personas_activas(self):
        return len(self._tracks_visibles())

    @property
    def total_vistas(self):
        return self.tracks_totales
