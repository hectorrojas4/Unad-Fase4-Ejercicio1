"""
Paquete software_fj
Sistema Integral de Gestión de Clientes, Servicios y Reservas - Software FJ
Curso: Programación (213023) - UNAD - Fase 4

Expone las clases principales para poder importarlas directamente:
    from software_fj import GestorSoftwareFJ, Cliente, SalaReuniones
"""

from .cliente import Cliente  # Clase Cliente
from .entidad import Entidad  # Clase abstracta base
from .excepciones import (  # Jerarquía de excepciones personalizadas
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
from .gestor import GestorSoftwareFJ  # Administrador del sistema
from .servicios import (  # Servicio abstracto y servicios especializados
    IVA_COLOMBIA,
    AlquilerEquipo,
    AsesoriaEspecializada,
    SalaReuniones,
    Servicio,
    formatear_moneda,
)

__all__ = [  # Nombres que se exportan con "from software_fj import *"
    "Entidad",
    "Cliente",
    "Servicio",
    "SalaReuniones",
    "AlquilerEquipo",
    "AsesoriaEspecializada",
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
