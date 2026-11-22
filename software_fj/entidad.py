"""
Módulo: entidad.py
Proyecto: Sistema Integral de Gestión de Clientes, Servicios y Reservas - Software FJ
Curso: Programación (213023) - UNAD - Fase 4

Contiene la clase abstracta Entidad, que representa a cualquier elemento
general del sistema (clientes, servicios y, en la Parte 2, reservas).

Aplica el principio de ABSTRACCIÓN: define qué debe saber hacer toda entidad
(validarse y describirse) sin decir cómo; cada clase hija lo implementa.
"""

from abc import ABC, abstractmethod  # ABC permite crear clases abstractas en Python
from datetime import datetime  # Para registrar la fecha y hora de creación
from typing import Dict  # Anotación de tipo para el diccionario de contadores

from .excepciones import ValidacionError  # Error a lanzar si el prefijo es inválido


class Entidad(ABC):
    """Clase abstracta base de todas las entidades del sistema.

    Cada entidad recibe un identificador único y legible con la forma
    PREFIJO-NNN (por ejemplo CLI-001 o SAL-002) y guarda su fecha de creación.
    No puede instanciarse directamente: Entidad() lanza TypeError.
    """

    _contadores: Dict[str, int] = {}  # Consecutivo por prefijo, compartido por todas las entidades

    def __init__(self, prefijo: str) -> None:
        """Asigna el identificador único y la fecha de creación de la entidad."""
        if not isinstance(prefijo, str) or not prefijo.strip():  # El prefijo debe ser texto no vacío
            raise ValidacionError("El prefijo del identificador es obligatorio.")  # Error controlado
        prefijo = prefijo.strip().upper()  # Normaliza: sin espacios y en mayúsculas
        consecutivo = Entidad._contadores.get(prefijo, 0) + 1  # Siguiente número para este prefijo
        Entidad._contadores[prefijo] = consecutivo  # Guarda el nuevo valor del contador
        self._identificador = f"{prefijo}-{consecutivo:03d}"  # Ej.: CLI-001 (3 dígitos con ceros)
        self._fecha_creacion = datetime.now()  # Momento exacto en que se creó la entidad

    # ------------------------------------------------------------------
    # Propiedades de solo lectura (ENCAPSULACIÓN: no tienen setter)
    # ------------------------------------------------------------------
    @property
    def identificador(self) -> str:
        """Identificador único de la entidad (no se puede modificar)."""
        return self._identificador  # Se expone solo para lectura

    @property
    def fecha_creacion(self) -> datetime:
        """Fecha y hora de creación de la entidad (no se puede modificar)."""
        return self._fecha_creacion  # Se expone solo para lectura

    # ------------------------------------------------------------------
    # Métodos abstractos: toda clase hija está obligada a implementarlos
    # ------------------------------------------------------------------
    @abstractmethod
    def validar(self) -> None:
        """Verifica que el estado completo de la entidad siga siendo válido."""

    @abstractmethod
    def describir(self) -> str:
        """Devuelve una descripción legible de la entidad."""

    # ------------------------------------------------------------------
    # Métodos especiales comunes a todas las entidades
    # ------------------------------------------------------------------
    def __str__(self) -> str:
        """Al imprimir una entidad se muestra su descripción (polimorfismo)."""
        return self.describir()  # Cada clase hija decide qué devuelve describir()

    def __repr__(self) -> str:
        """Representación técnica, útil al depurar: <Cliente CLI-001>."""
        return f"<{type(self).__name__} {getattr(self, '_identificador', 'sin-id')}>"  # Tolera objetos a medio crear

    def __eq__(self, otro: object) -> bool:
        """Dos entidades son iguales si tienen el mismo identificador."""
        if not isinstance(otro, Entidad):  # Solo se compara contra otras entidades
            return NotImplemented  # Le indica a Python que no sabe comparar con otro tipo
        return self._identificador == otro._identificador  # Compara por identificador

    def __hash__(self) -> int:
        """Permite usar entidades en conjuntos y como claves de diccionario."""
        return hash(self._identificador)  # El hash se basa en el identificador único
