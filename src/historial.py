"""
Módulo de Historial de Presencia
==================================
Registra en CSV cada aparición de personas:
- Hora de entrada
- Hora de salida
- Duración en pantalla
- Nombre o ID de la persona
"""
import os
import csv
from datetime import datetime
from config import RUTA_HISTORIAL, ARCHIVO_HISTORIAL, INTERVALO_LOG


class HistorialPresencia:
    """
    Gestiona el log de presencia de personas.
    Cada persona tiene una sesión que se abre al aparecer y se cierra al desaparecer.
    """

    def __init__(self):
        self.sesiones_activas = {}  # track_id -> {"inicio": datetime, "nombre": str}
        self.archivo = os.path.join(RUTA_HISTORIAL, ARCHIVO_HISTORIAL)
        self._asegurar_archivo()

    def _asegurar_archivo(self):
        """Crea el archivo CSV con headers si no existe."""
        os.makedirs(RUTA_HISTORIAL, exist_ok=True)
        if not os.path.exists(self.archivo):
            with open(self.archivo, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "persona", "entrada", "salida", "duracion_segundos", "fecha"
                ])

    def persona_aparece(self, track_id, nombre=None):
        """Registra que una persona apareció en cámara."""
        if track_id in self.sesiones_activas:
            return  # Ya está activa

        self.sesiones_activas[track_id] = {
            "inicio": datetime.now(),
            "nombre": nombre or f"Persona_{track_id + 1}"
        }

    def persona_desaparece(self, track_id):
        """Registra que una persona salió de cámara y guarda en CSV."""
        if track_id not in self.sesiones_activas:
            return

        sesion = self.sesiones_activas.pop(track_id)
        fin = datetime.now()
        duracion = (fin - sesion["inicio"]).total_seconds()

        # Solo registrar si estuvo más de 1 segundo
        if duracion < INTERVALO_LOG:
            return

        self._escribir_log(sesion["nombre"], sesion["inicio"], fin, duracion)

    def _escribir_log(self, nombre, inicio, fin, duracion):
        """Escribe una entrada en el CSV."""
        try:
            with open(self.archivo, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    nombre,
                    inicio.strftime("%H:%M:%S"),
                    fin.strftime("%H:%M:%S"),
                    f"{duracion:.1f}",
                    inicio.strftime("%Y-%m-%d")
                ])
        except Exception as e:
            print(f"[Historial] Error escribiendo log: {e}")

    def cerrar_todas(self):
        """Cierra todas las sesiones activas (al salir de la app)."""
        ids = list(self.sesiones_activas.keys())
        for track_id in ids:
            self.persona_desaparece(track_id)

    def actualizar_nombre(self, track_id, nombre):
        """Actualiza el nombre de una sesión activa."""
        if track_id in self.sesiones_activas:
            self.sesiones_activas[track_id]["nombre"] = nombre

    @property
    def activas(self):
        """Número de sesiones activas."""
        return len(self.sesiones_activas)
