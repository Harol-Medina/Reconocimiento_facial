"""
Módulo de Interfaz de Usuario
================================
Renderiza toda la interfaz visual:
- Recuadros estilizados por persona
- Panel lateral con miniaturas
- Reloj en vivo
- HUD con estadísticas
- Histograma de presencia
- Alertas visuales
- Soporte de temas (oscuro/claro)
"""
import cv2
import numpy as np
from datetime import datetime
from config import (
    COLORES, COLOR_BLANCO, COLOR_NEGRO, COLOR_GRIS, COLOR_ALERTA,
    MOSTRAR_GENERO_EDAD, MOSTRAR_RELOJ, MOSTRAR_PANEL,
    ANCHO_PANEL, TAMANO_MINIATURA, TEMAS, TEMA_DEFAULT
)


class InterfazUI:
    """Gestiona toda la interfaz visual."""

    def __init__(self):
        self.tema_actual = TEMA_DEFAULT
        self.tema = TEMAS[self.tema_actual]
        self.grabando = False

    def cambiar_tema(self):
        """Alterna entre tema oscuro y claro."""
        if self.tema_actual == "oscuro":
            self.tema_actual = "claro"
        else:
            self.tema_actual = "oscuro"
        self.tema = TEMAS[self.tema_actual]
        print(f"  [UI] Tema: {self.tema_actual}")

    def renderizar(self, frame, tracks, tracker, fps):
        """
        Renderiza toda la interfaz sobre el frame.

        Args:
            frame: Frame BGR de la cámara
            tracks: Lista de tracks visibles
            tracker: TrackerPersonas (para alertas y stats)
            fps: FPS actual

        Returns:
            Frame con interfaz dibujada (puede ser más ancho si hay panel)
        """
        # Dibujar rostros detectados
        for track in tracks:
            self._dibujar_track(frame, track)

        if not tracks:
            self._dibujar_sin_detecciones(frame)

        # HUD superior
        self._dibujar_hud(frame, tracker, fps)

        # Alertas
        self._dibujar_alertas(frame, tracker.alertas)

        # Indicador de grabación
        if self.grabando:
            self._dibujar_grabando(frame)

        # Panel lateral
        if MOSTRAR_PANEL and tracks:
            frame = self._dibujar_panel(frame, tracks)

        return frame

    def _dibujar_track(self, frame, track):
        """Dibuja recuadro y etiqueta de un track."""
        x1, y1, x2, y2 = track.bbox
        color = COLORES[track.id % len(COLORES)]
        w = x2 - x1
        h = y2 - y1

        # Esquinas estilizadas
        largo = min(25, w // 4, h // 4)
        grosor = 2

        cv2.line(frame, (x1, y1), (x1 + largo, y1), color, grosor + 1)
        cv2.line(frame, (x1, y1), (x1, y1 + largo), color, grosor + 1)
        cv2.line(frame, (x2, y1), (x2 - largo, y1), color, grosor + 1)
        cv2.line(frame, (x2, y1), (x2, y1 + largo), color, grosor + 1)
        cv2.line(frame, (x1, y2), (x1 + largo, y2), color, grosor + 1)
        cv2.line(frame, (x1, y2), (x1, y2 - largo), color, grosor + 1)
        cv2.line(frame, (x2, y2), (x2 - largo, y2), color, grosor + 1)
        cv2.line(frame, (x2, y2), (x2, y2 - largo), color, grosor + 1)

        # Línea fina
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 1)

        # Etiqueta
        nombre = track.nombre or f"Persona {track.id + 1}"
        info_extra = ""
        if MOSTRAR_GENERO_EDAD:
            partes = []
            if track.genero:
                partes.append(track.genero)
            if track.edad:
                partes.append(f"{track.edad}")
            if partes:
                info_extra = " | ".join(partes)

        # Fondo de etiqueta
        alto_etiqueta = 24 if not info_extra else 40
        overlay = frame.copy()
        cv2.rectangle(overlay,
                      (x1, y1 - alto_etiqueta - 4),
                      (x1 + max(len(nombre) * 11, 120), y1 - 2),
                      color, -1)
        cv2.addWeighted(overlay, 0.85, frame, 0.15, 0, frame)

        cv2.putText(frame, nombre, (x1 + 5, y1 - alto_etiqueta + 14),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOR_BLANCO, 1, cv2.LINE_AA)

        if info_extra:
            cv2.putText(frame, info_extra, (x1 + 5, y1 - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.35, (220, 220, 220), 1, cv2.LINE_AA)

        # Barra de tiempo en pantalla
        tiempo = track.tiempo_en_pantalla
        barra_max = x2 - x1
        barra_ancho = min(barra_max, int(tiempo * 5))  # 5px por segundo
        cv2.line(frame, (x1, y2 + 4), (x1 + barra_ancho, y2 + 4), color, 2)

    def _dibujar_hud(self, frame, tracker, fps):
        """HUD superior."""
        h, w = frame.shape[:2]

        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, 55), self.tema["fondo_hud"], -1)
        cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)

        # Título
        cv2.putText(frame, "RECONOCIMIENTO FACIAL",
                    (12, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.55,
                    self.tema["texto_principal"], 1, cv2.LINE_AA)

        # Stats
        stats = f"Activas: {tracker.personas_activas}  |  Total: {tracker.total_vistas}  |  Cuadros/s: {fps:.0f}"
        cv2.putText(frame, stats, (12, 45),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4,
                    self.tema["texto_secundario"], 1, cv2.LINE_AA)

        # Reloj
        if MOSTRAR_RELOJ:
            ahora = datetime.now().strftime("%H:%M:%S")
            cv2.putText(frame, ahora, (w - 100, 22),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        self.tema["texto_secundario"], 1, cv2.LINE_AA)

        # Controles
        controles = "[C]aptura [N]ombre [G]rabar [T]ema [R]eset [Q]Salir"
        cv2.putText(frame, controles, (w - 400, 45),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.32,
                    (100, 100, 100), 1, cv2.LINE_AA)

        # LIVE indicator
        cv2.circle(frame, (w - 110, 42), 4, (0, 0, 255), -1)
        cv2.putText(frame, "EN VIVO", (w - 102, 47),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1, cv2.LINE_AA)

    def _dibujar_panel(self, frame, tracks):
        """Panel lateral con miniaturas de personas."""
        h, w = frame.shape[:2]

        # Crear panel
        panel = np.full((h, ANCHO_PANEL, 3), self.tema["fondo_panel"], dtype=np.uint8)

        # Título del panel
        cv2.putText(panel, "PERSONAS", (10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    self.tema["texto_principal"], 1, cv2.LINE_AA)
        cv2.line(panel, (10, 35), (ANCHO_PANEL - 10, 35),
                 self.tema["texto_secundario"], 1)

        # Miniaturas
        y_offset = 50
        for i, track in enumerate(tracks[:6]):  # Máximo 6 en el panel
            color = COLORES[track.id % len(COLORES)]
            nombre = track.nombre or f"Persona {track.id + 1}"

            # Miniatura del rostro
            if track.miniatura is not None:
                mini = cv2.resize(track.miniatura, (TAMANO_MINIATURA, TAMANO_MINIATURA))
                y_end = y_offset + TAMANO_MINIATURA
                if y_end < h - 10:
                    panel[y_offset:y_end, 10:10 + TAMANO_MINIATURA] = mini

            # Borde de color
            cv2.rectangle(panel,
                          (8, y_offset - 2),
                          (12 + TAMANO_MINIATURA, y_offset + TAMANO_MINIATURA + 2),
                          color, 2)

            # Info
            x_texto = 10 + TAMANO_MINIATURA + 8
            cv2.putText(panel, nombre[:12], (x_texto, y_offset + 18),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.35, COLOR_BLANCO, 1, cv2.LINE_AA)

            tiempo = track.tiempo_en_pantalla
            if tiempo < 60:
                t_texto = f"{tiempo:.0f}s"
            else:
                t_texto = f"{tiempo / 60:.1f}m"
            cv2.putText(panel, t_texto, (x_texto, y_offset + 38),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.3, COLOR_GRIS, 1, cv2.LINE_AA)

            if track.genero and track.edad:
                cv2.putText(panel, f"{track.genero} {track.edad}",
                            (x_texto, y_offset + 55),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.3, COLOR_GRIS, 1, cv2.LINE_AA)

            y_offset += TAMANO_MINIATURA + 15

        # Unir frame + panel
        resultado = np.hstack([frame, panel])
        return resultado

    def _dibujar_alertas(self, frame, alertas):
        """Dibuja alertas visuales."""
        h, w = frame.shape[:2]
        y = h - 40

        for alerta in alertas:
            if alerta.activa:
                # Fondo de alerta
                overlay = frame.copy()
                cv2.rectangle(overlay, (10, y - 20), (w - 10, y + 5), COLOR_ALERTA, -1)
                cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)

                cv2.putText(frame, alerta.mensaje, (20, y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOR_BLANCO, 1, cv2.LINE_AA)
                y -= 35

    def _dibujar_grabando(self, frame):
        """Indicador de grabacion."""
        h, w = frame.shape[:2]
        cv2.circle(frame, (30, h - 30), 8, (0, 0, 255), -1)
        cv2.putText(frame, "GRABANDO", (45, h - 24),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)

    def _dibujar_sin_detecciones(self, frame):
        """Mensaje cuando no hay detecciones."""
        h, w = frame.shape[:2]
        texto = "Buscando rostros..."
        tam = cv2.getTextSize(texto, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)[0]
        x = (w - tam[0]) // 2
        cv2.putText(frame, texto, (x, h - 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLOR_GRIS, 1, cv2.LINE_AA)
