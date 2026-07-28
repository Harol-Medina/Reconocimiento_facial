"""
Módulo de Registro de Personas
================================
Permite asociar nombres a personas detectadas.
Persiste los embeddings con nombres en disco para reconocerlas en futuras sesiones.
"""
import os
import pickle
import numpy as np
from config import RUTA_REGISTRO, UMBRAL_RECONOCIMIENTO

ARCHIVO_REGISTRO = os.path.join(RUTA_REGISTRO, "personas_registradas.pkl")


class RegistroPersonas:
    """
    Gestiona el registro de personas conocidas.
    Guarda embeddings con nombres asociados para reconocimiento persistente.
    """

    def __init__(self):
        self.personas = []  # Lista de dicts: {"nombre": str, "embedding": np.array}
        self._cargar()

    def _cargar(self):
        """Carga el registro desde disco."""
        if os.path.exists(ARCHIVO_REGISTRO):
            try:
                with open(ARCHIVO_REGISTRO, 'rb') as f:
                    self.personas = pickle.load(f)
                print(f"[Registro] {len(self.personas)} personas cargadas.")
            except Exception as e:
                print(f"[Registro] Error al cargar: {e}. Iniciando vacio.")
                self.personas = []

    def _guardar(self):
        """Guarda el registro en disco."""
        os.makedirs(RUTA_REGISTRO, exist_ok=True)
        with open(ARCHIVO_REGISTRO, 'wb') as f:
            pickle.dump(self.personas, f)

    def registrar(self, nombre, embedding):
        """
        Registra una persona con nombre y embedding.

        Args:
            nombre: Nombre de la persona
            embedding: Embedding facial 512D (numpy array)
        """
        # Verificar si ya existe
        for persona in self.personas:
            if persona["nombre"].lower() == nombre.lower():
                # Actualizar embedding (promediar)
                persona["embedding"] = (persona["embedding"] + embedding) / 2
                norma = np.linalg.norm(persona["embedding"])
                if norma > 0:
                    persona["embedding"] = persona["embedding"] / norma
                self._guardar()
                print(f"  [Registro] '{nombre}' actualizado.")
                return

        # Nuevo registro
        self.personas.append({
            "nombre": nombre,
            "embedding": embedding.copy()
        })
        self._guardar()
        print(f"  [Registro] '{nombre}' registrado exitosamente.")

    def buscar(self, embedding):
        """
        Busca una persona por su embedding.

        Args:
            embedding: Embedding facial a buscar

        Returns:
            (nombre, similitud) si se encuentra, (None, 0.0) si no
        """
        if not self.personas:
            return None, 0.0

        mejor_nombre = None
        mejor_similitud = 0.0

        for persona in self.personas:
            # Similitud coseno
            sim = float(np.dot(embedding, persona["embedding"]) /
                       (np.linalg.norm(embedding) * np.linalg.norm(persona["embedding"]) + 1e-8))

            if sim > mejor_similitud:
                mejor_similitud = sim
                mejor_nombre = persona["nombre"]

        if mejor_similitud >= UMBRAL_RECONOCIMIENTO:
            return mejor_nombre, mejor_similitud

        return None, 0.0

    def eliminar(self, nombre):
        """Elimina una persona del registro."""
        self.personas = [p for p in self.personas if p["nombre"].lower() != nombre.lower()]
        self._guardar()
        print(f"  [Registro] '{nombre}' eliminado.")

    def listar(self):
        """Lista todas las personas registradas."""
        return [p["nombre"] for p in self.personas]

    @property
    def total(self):
        return len(self.personas)
