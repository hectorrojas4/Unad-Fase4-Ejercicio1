"""
Módulo: excepciones.py
Proyecto: Sistema Integral de Gestión de Clientes, Servicios y Reservas - Software FJ
Curso: Programación (213023) - UNAD - Fase 4

Define la jerarquía de excepciones personalizadas del sistema.

Todas las excepciones propias heredan de SoftwareFJError. Gracias a esto, el
programa puede capturar cualquier error controlado del dominio con un único
bloque `except SoftwareFJError`, sin confundirlo con errores imprevistos de
Python (por ejemplo IndexError o ZeroDivisionError), que se tratan aparte.

Jerarquía:
    SoftwareFJError
    ├── ValidacionError
    │   ├── ClienteInvalidoError
    │   ├── ServicioInvalidoError
    │   ├── ParametroFaltanteError
    │   └── ParametroInvalidoError
    ├── OperacionNoPermitidaError
    │   └── RegistroDuplicadoError
    ├── EntidadNoEncontradaError
    ├── ServicioNoDisponibleError
    ├── CalculoInconsistenteError
    └── ReservaInvalidaError        (se usará en la Parte 2: reservas)
"""


class SoftwareFJError(Exception):
    """Excepción base de todos los errores controlados del sistema Software FJ."""

    codigo = "SFJ-000"  # Código genérico; cada subclase define su propio código

    def __init__(self, mensaje: str) -> None:
        """Guarda el mensaje del error y lo entrega a la clase Exception."""
        super().__init__(mensaje)  # Inicializa la clase padre Exception con el mensaje
        self.mensaje = mensaje  # Conserva el mensaje para consultarlo o registrarlo después

    def __str__(self) -> str:
        """Devuelve el error con su código, por ejemplo: [SFJ-101] Correo inválido."""
        return f"[{self.codigo}] {self.mensaje}"  # Formato uniforme para consola y logs


# ---------------------------------------------------------------------------
# Errores de validación de datos
# ---------------------------------------------------------------------------
class ValidacionError(SoftwareFJError):
    """Un dato no cumple las reglas de validación del sistema."""

    codigo = "SFJ-100"  # Familia de códigos 1xx: validaciones


class ClienteInvalidoError(ValidacionError):
    """Los datos personales de un cliente son inválidos (nombre, documento, correo...)."""

    codigo = "SFJ-101"  # Error específico de datos de cliente


class ServicioInvalidoError(ValidacionError):
    """Los datos con los que se intenta crear un servicio son inválidos."""

    codigo = "SFJ-102"  # Error específico de creación de servicios


class ParametroFaltanteError(ValidacionError):
    """Falta un parámetro obligatorio para completar la operación."""

    codigo = "SFJ-103"  # Error por dato obligatorio ausente o vacío


class ParametroInvalidoError(ValidacionError):
    """Un parámetro de operación (duración, cantidad, modalidad...) es inválido."""

    codigo = "SFJ-104"  # Error en parámetros de uso de un servicio


# ---------------------------------------------------------------------------
# Errores de reglas de negocio y operación
# ---------------------------------------------------------------------------
class OperacionNoPermitidaError(SoftwareFJError):
    """Se intenta realizar una operación que las reglas del negocio no permiten."""

    codigo = "SFJ-200"  # Familia de códigos 2xx: operaciones


class RegistroDuplicadoError(OperacionNoPermitidaError):
    """Se intenta registrar una entidad que ya existe (por ejemplo, un documento repetido)."""

    codigo = "SFJ-201"  # Error específico de duplicados


class EntidadNoEncontradaError(SoftwareFJError):
    """No existe un cliente o servicio con el identificador buscado."""

    codigo = "SFJ-300"  # Familia de códigos 3xx: búsquedas


class ServicioNoDisponibleError(SoftwareFJError):
    """El servicio existe pero no puede usarse (deshabilitado, sin unidades o sin cupo)."""

    codigo = "SFJ-400"  # Familia de códigos 4xx: disponibilidad


class CalculoInconsistenteError(SoftwareFJError):
    """El cálculo de un costo produce un valor imposible (negativo, infinito, tasas absurdas)."""

    codigo = "SFJ-500"  # Familia de códigos 5xx: cálculos


class ReservaInvalidaError(SoftwareFJError):
    """Intento de reserva incorrecto. Se implementará su uso en la Parte 2 (clase Reserva)."""

    codigo = "SFJ-600"  # Familia de códigos 6xx: reservas (Parte 2)
