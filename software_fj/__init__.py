"""
Paquete software_fj
Sistema Integral de Gestión de Clientes, Servicios y Reservas - Software FJ
Curso: Programación (213023) - UNAD - Fase 4

Reúne las clases principales del sistema para importarlas desde el paquete.
"""

from .cliente import Cliente
from .entidad import Entidad
from .excepciones import (
    CalculoInconsistenteError,
    ClienteInvalidoError,
    EntidadNoEncontradaError,
    OperacionNoPermitidaError,
    ParametroFaltanteError,
    ParametroInvalidoError,
    RegistroDuplicadoError,
    ReservaInvalidaError,
    ServicioInvalidoError,
    ServicioNoDisponibleError,
    SoftwareFJError,
    ValidacionError,
)
from .gestor import GestorSoftwareFJ
from .reserva import EstadoReserva, Reserva
from .servicios import (
    IVA_COLOMBIA,
    AlquilerEquipo,
    AsesoriaEspecializada,
    SalaReuniones,
    Servicio,
    formatear_moneda,
)

__all__ = [
    "Entidad",
    "Cliente",
    "Servicio",
    "SalaReuniones",
    "AlquilerEquipo",
    "AsesoriaEspecializada",
    "Reserva",
    "EstadoReserva",
    "GestorSoftwareFJ",
    "formatear_moneda",
    "IVA_COLOMBIA",
    "SoftwareFJError",
    "ValidacionError",
    "ClienteInvalidoError",
    "ServicioInvalidoError",
    "ParametroFaltanteError",
    "ParametroInvalidoError",
    "OperacionNoPermitidaError",
    "RegistroDuplicadoError",
    "EntidadNoEncontradaError",
    "ServicioNoDisponibleError",
    "CalculoInconsistenteError",
    "ReservaInvalidaError",
]
