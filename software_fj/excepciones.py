"""
Módulo: excepciones.py
Proyecto: Sistema Integral de Gestión de Clientes, Servicios y Reservas - Software FJ
Curso: Programación (213023) - UNAD - Fase 4

Define las excepciones propias del sistema. Todas heredan de SoftwareFJError.
"""


class SoftwareFJError(Exception):
    """Excepción base de todos los errores controlados del sistema."""

    codigo = "SFJ-000"

    def __init__(self, mensaje: str) -> None:
        super().__init__(mensaje)
        self.mensaje = mensaje

    def __str__(self) -> str:
        return f"[{self.codigo}] {self.mensaje}"


class ValidacionError(SoftwareFJError):
    """Un dato no cumple las reglas de validación del sistema."""

    codigo = "SFJ-100"


class ClienteInvalidoError(ValidacionError):
    """Los datos de un cliente son inválidos."""

    codigo = "SFJ-101"


class ServicioInvalidoError(ValidacionError):
    """Los datos para crear un servicio son inválidos."""

    codigo = "SFJ-102"


class ParametroFaltanteError(ValidacionError):
    """Falta un dato obligatorio para completar la operación."""

    codigo = "SFJ-103"


class ParametroInvalidoError(ValidacionError):
    """Un parámetro de la operación, como la duración o la cantidad, es inválido."""

    codigo = "SFJ-104"


class OperacionNoPermitidaError(SoftwareFJError):
    """Se intenta hacer una operación que las reglas del negocio no permiten."""

    codigo = "SFJ-200"


class RegistroDuplicadoError(OperacionNoPermitidaError):
    """Se intenta registrar algo que ya existe, como un documento repetido."""

    codigo = "SFJ-201"


class EntidadNoEncontradaError(SoftwareFJError):
    """No existe un cliente, servicio o reserva con el identificador buscado."""

    codigo = "SFJ-300"


class ServicioNoDisponibleError(SoftwareFJError):
    """El servicio existe pero no se puede usar en este momento."""

    codigo = "SFJ-400"


class CalculoInconsistenteError(SoftwareFJError):
    """El cálculo de un costo da un valor imposible, por ejemplo negativo."""

    codigo = "SFJ-500"


class ReservaInvalidaError(SoftwareFJError):
    """No se pudo crear una reserva con los datos indicados."""

    codigo = "SFJ-600"
