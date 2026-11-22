"""
Módulo: entidad.py
Proyecto: Sistema Integral de Gestión de Clientes, Servicios y Reservas - Software FJ
Curso: Programación (213023) - UNAD - Fase 4

Contiene la clase abstracta Entidad, de la que heredan clientes, servicios y reservas.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict

from .excepciones import ValidacionError


class Entidad(ABC):
    """Clase abstracta base de todas las entidades del sistema."""

    _contadores: Dict[str, int] = {}

    def __init__(self, prefijo: str) -> None:
        """Asigna el identificador único (por ejemplo CLI-001) y la fecha de creación."""
        if not isinstance(prefijo, str) or not prefijo.strip():
            raise ValidacionError("El prefijo del identificador es obligatorio.")
        prefijo = prefijo.strip().upper()
        consecutivo = Entidad._contadores.get(prefijo, 0) + 1
        Entidad._contadores[prefijo] = consecutivo
        self._identificador = f"{prefijo}-{consecutivo:03d}"
        self._fecha_creacion = datetime.now()

    @property
    def identificador(self) -> str:
        return self._identificador

    @property
    def fecha_creacion(self) -> datetime:
        return self._fecha_creacion

    @abstractmethod
    def validar(self) -> None:
        """Verifica que los datos de la entidad sean válidos."""

    @abstractmethod
    def describir(self) -> str:
        """Devuelve una descripción de la entidad."""

    def __str__(self) -> str:
        return self.describir()

    def __repr__(self) -> str:
        return f"<{type(self).__name__} {getattr(self, '_identificador', 'sin-id')}>"

    def __eq__(self, otro: object) -> bool:
        if not isinstance(otro, Entidad):
            return NotImplemented
        return self._identificador == otro._identificador

    def __hash__(self) -> int:
        return hash(self._identificador)
