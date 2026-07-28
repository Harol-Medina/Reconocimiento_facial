"""
Reconocimiento Facial en Tiempo Real
======================================
Aplicación completa con todas las funcionalidades:
- Detección y diferenciación de múltiples personas (InsightFace)
- Tracking espacial + re-identificación
- Captura de rostros con timestamp
- Registro de nombres persistente
- Historial de presencia (CSV)
- Grabación de video
- Panel lateral con miniaturas
- Reloj en vivo
- Alertas de personas nuevas
- Temas oscuro/claro
- Argumentos CLI

Controles:
  C - Capturar rostros visibles
  S - Screenshot completo
  N - Asignar nombre a persona visible
  G - Iniciar/detener grabación
  T - Cambiar tema (oscuro/claro)
  R - Resetear (olvidar personas)
  Q - Salir
"""
import sys
import os
import time
import argparse
import warnings

# Silenciar warnings internos de dependencias
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)
os.environ["PYTHONWARNINGS"] = "ignore"

# Path setup
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import cv2
import numpy as np

from config import (
    CAMARA_ID, ANCHO_FRAME, ALTO_FRAME,
    RUTA_GRABACIONES, CODEC_VIDEO, FPS_GRABACION,
    USAR_THREADING, TAMANO_MINIATURA
)
from detector import DetectorRostros
from tracker import TrackerPersonas
from registro import RegistroPersonas
from historial import HistorialPresencia
from capturas import capturar_todos, screenshot
from ui import InterfazUI


def parsear_argumentos():
    """Parsea argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(
        description="Reconocimiento Facial en Tiempo Real"
    )
    parser.add_argument('-c', '--camera', type=int, default=CAMARA_ID,
                        help=f'ID de la cámara (default: {CAMARA_ID})')
    parser.add_argument('-t', '--threshold', type=float, default=None,
                        help='Umbral de reconocimiento (0.0-1.0)')
    parser.add_argument('--ancho', type=int, default=ANCHO_FRAME,
                        help=f'Ancho del frame (default: {ANCHO_FRAME})')
    parser.add_argument('--alto', type=int, default=ALTO_FRAME,
                        help=f'Alto del frame (default: {ALTO_FRAME})')
    parser.add_argument('--no-panel', action='store_true',
                        help='Desactivar panel lateral')
    parser.add_argument('--no-threading', action='store_true',
                        help='Desactivar detección en threading')
    parser.add_argument('--tema', choices=['oscuro', 'claro'], default='oscuro',
                        help='Tema de la interfaz')
    return parser.parse_args()


class App:
    """Aplicación principal de reconocimiento facial."""

    def __init__(self, args):
        self.args = args
        self.detector = None
        self.registro = RegistroPersonas()
        self.tracker = TrackerPersonas(registro=self.registro)
        self.historial = HistorialPresencia()
        self.ui = InterfazUI()
        self.camara = None
        self.grabador = None
        self.fps = 0
        self.frame_count = 0
        self.fps_timer = 0
        self.corriendo = False
        self.frame_actual = None

        # Aplicar args
        if args.tema:
            self.ui.tema_actual = args.tema
            self.ui.tema = self.ui.tema.__class__.__mro__  # reload
            from config import TEMAS
            self.ui.tema = TEMAS[args.tema]

        if args.no_panel:
            import config
            config.MOSTRAR_PANEL = False

        if args.no_threading:
            import config
            config.USAR_THREADING = False

    def inicializar(self):
        """Inicializa todos los componentes."""
        try:
            self.detector = DetectorRostros()
        except Exception as e:
            print(f"[ERROR] No se pudo cargar el modelo: {e}")
            print("        Verifica conexion a internet (primera vez descarga ~280MB).")
            return False

        if not self._abrir_camara():
            return False

        return True

    def _abrir_camara(self):
        """Abre la cámara con reintentos."""
        cam_id = self.args.camera
        for i in range(3):
            self.camara = cv2.VideoCapture(cam_id)
            self.camara.set(cv2.CAP_PROP_FRAME_WIDTH, self.args.ancho)
            self.camara.set(cv2.CAP_PROP_FRAME_HEIGHT, self.args.alto)
            self.camara.set(cv2.CAP_PROP_BUFFERSIZE, 1)

            if self.camara.isOpened():
                ret, _ = self.camara.read()
                if ret:
                    print(f"[Camara] Abierta (ID: {cam_id}, intento {i + 1}).")
                    return True
            self.camara.release()
            print(f"[Camara] Intento {i + 1}/3 fallido...")
            time.sleep(1)

        print("[ERROR] No se pudo abrir la camara.")
        return False

    def ejecutar(self):
        """Bucle principal."""
        if not self.inicializar():
            return

        self.corriendo = True
        self.fps_timer = time.time()

        print("\n[OK] Aplicacion activa.")
        print("     Controles: [C]aptura [S]creenshot [N]ombre [G]rabar [T]ema [R]eset [Q]Salir\n")

        # IDs de tracks activos en el frame anterior (para historial)
        tracks_previos = set()

        while self.corriendo:
            ret, frame = self.camara.read()
            if not ret:
                print("[!] Frame perdido. Reconectando...")
                self.camara.release()
                time.sleep(0.5)
                if not self._abrir_camara():
                    break
                continue

            frame = cv2.flip(frame, 1)
            self.frame_count += 1
            self.frame_actual = frame.copy()

            # Detección
            try:
                if USAR_THREADING:
                    detecciones = self.detector.detectar_async(frame)
                else:
                    detecciones = self.detector.detectar(frame)
            except Exception as e:
                print(f"[!] Error deteccion: {e}")
                detecciones = []

            # Tracking
            tracks_visibles = self.tracker.actualizar(detecciones)

            # Actualizar miniaturas
            for track in tracks_visibles:
                x1, y1, x2, y2 = track.bbox
                h, w = frame.shape[:2]
                x1c = max(0, x1)
                y1c = max(0, y1)
                x2c = min(w, x2)
                y2c = min(h, y2)
                if x2c > x1c and y2c > y1c:
                    rostro = frame[y1c:y2c, x1c:x2c]
                    if rostro.size > 0:
                        track.miniatura = cv2.resize(
                            rostro, (TAMANO_MINIATURA, TAMANO_MINIATURA)
                        )

            # Historial de presencia
            tracks_actuales = set(t.id for t in tracks_visibles)

            # Personas que aparecieron
            for t in tracks_visibles:
                if t.id not in tracks_previos:
                    nombre = t.nombre or f"Persona_{t.id + 1}"
                    self.historial.persona_aparece(t.id, nombre)

            # Personas que desaparecieron
            for tid in tracks_previos - tracks_actuales:
                self.historial.persona_desaparece(tid)

            tracks_previos = tracks_actuales

            # Renderizar UI
            frame_ui = self.ui.renderizar(frame, tracks_visibles, self.tracker, self.fps)

            # Grabación
            if self.grabador is not None:
                # Grabar solo el frame sin panel
                self.grabador.write(frame)

            # FPS
            if self.frame_count % 10 == 0:
                ahora = time.time()
                elapsed = ahora - self.fps_timer
                if elapsed > 0:
                    self.fps = 10 / elapsed
                self.fps_timer = ahora

            # Mostrar
            cv2.imshow("Reconocimiento Facial", frame_ui)

            # Input
            tecla = cv2.waitKey(1) & 0xFF
            self._procesar_tecla(tecla, tracks_visibles)

        # Limpieza
        self._cerrar()

    def _procesar_tecla(self, tecla, tracks):
        """Procesa input del teclado."""
        if tecla == ord('q') or tecla == ord('Q'):
            self.corriendo = False

        elif tecla == ord('r') or tecla == ord('R'):
            self.tracker.reset()
            print("  [!] Reset: personas olvidadas.")

        elif tecla == ord('c') or tecla == ord('C'):
            # Capturar todos los rostros
            if tracks and self.frame_actual is not None:
                capturar_todos(self.frame_actual, tracks)
            else:
                print("  [!] No hay rostros visibles para capturar.")

        elif tecla == ord('s') or tecla == ord('S'):
            # Screenshot
            if self.frame_actual is not None:
                screenshot(self.frame_actual)

        elif tecla == ord('n') or tecla == ord('N'):
            # Asignar nombre
            self._asignar_nombre(tracks)

        elif tecla == ord('g') or tecla == ord('G'):
            # Toggle grabación
            self._toggle_grabacion()

        elif tecla == ord('t') or tecla == ord('T'):
            # Cambiar tema
            self.ui.cambiar_tema()

    def _asignar_nombre(self, tracks):
        """Pide nombre por consola y lo asigna a la primera persona sin nombre."""
        if not tracks:
            print("  [!] No hay personas visibles.")
            return

        # Buscar la primera persona sin nombre
        track_sin_nombre = None
        for t in tracks:
            if not t.nombre:
                track_sin_nombre = t
                break

        if not track_sin_nombre:
            track_sin_nombre = tracks[0]

        print(f"\n  Asignar nombre a Persona {track_sin_nombre.id + 1}")
        nombre = input("  Nombre: ").strip()

        if nombre:
            track_sin_nombre.nombre = nombre
            # Registrar para persistencia
            self.registro.registrar(nombre, track_sin_nombre.embedding)
            # Actualizar historial
            self.historial.actualizar_nombre(track_sin_nombre.id, nombre)
            print(f"  [OK] '{nombre}' asignado y guardado.\n")
        else:
            print("  [!] Nombre vacío, cancelado.\n")

    def _toggle_grabacion(self):
        """Inicia o detiene la grabación de video."""
        if self.grabador is None:
            # Iniciar grabación
            os.makedirs(RUTA_GRABACIONES, exist_ok=True)
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            archivo = os.path.join(RUTA_GRABACIONES, f"grabacion_{timestamp}.avi")

            fourcc = cv2.VideoWriter_fourcc(*CODEC_VIDEO)
            self.grabador = cv2.VideoWriter(
                archivo, fourcc, FPS_GRABACION,
                (self.args.ancho, self.args.alto)
            )
            self.ui.grabando = True
            print(f"  [REC] Grabacion iniciada: {archivo}")
        else:
            # Detener grabación
            self.grabador.release()
            self.grabador = None
            self.ui.grabando = False
            print("  [REC] Grabacion detenida.")

    def _cerrar(self):
        """Limpia todos los recursos."""
        # Cerrar historial
        self.historial.cerrar_todas()

        # Cerrar grabación
        if self.grabador:
            self.grabador.release()

        # Cerrar cámara
        if self.camara:
            self.camara.release()

        cv2.destroyAllWindows()

        print(f"\nSesion finalizada.")
        print(f"  Personas vistas: {self.tracker.total_vistas}")
        print(f"  Personas registradas: {self.registro.total}")


def main():
    """Punto de entrada."""
    args = parsear_argumentos()

    print("\n" + "=" * 60)
    print("   RECONOCIMIENTO FACIAL EN TIEMPO REAL v2.0")
    print("=" * 60 + "\n")

    app = App(args)
    app.ejecutar()


if __name__ == "__main__":
    main()
