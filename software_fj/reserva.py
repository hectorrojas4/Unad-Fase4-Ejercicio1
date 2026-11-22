"""
Módulo: reserva.py
Proyecto: Sistema Integral de Gestión de Clientes, Servicios y Reservas - Software FJ
Curso: Programación (213023) - UNAD - Fase 4

Contiene la clase Reserva y los estados que puede tener una reserva:
pendiente, confirmada, procesada o cancelada.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from .cliente import Cliente
from .entidad import Entidad
from .excepciones import (
    CalculoInconsistenteError,
    OperacionNoPermitidaError,
    ReservaInvalidaError,
    SoftwareFJError,
)
from .servicios import Servicio, formatear_moneda


class EstadoReserva(Enum):
    """Estados posibles de una reserva."""

    PENDIENTE = "pendiente"
    CONFIRMADA = "confirmada"
    PROCESADA = "procesada"
    CANCELADA = "cancelada"


class Reserva(Entidad):
    """Reserva de un servicio por parte de un cliente durante un tiempo determinado."""

    PREFIJO = "RES"
    TRANSICIONES = {
        EstadoReserva.PENDIENTE: (EstadoReserva.CONFIRMADA, EstadoReserva.CANCELADA),
        EstadoReserva.CONFIRMADA: (EstadoReserva.PROCESADA, EstadoReserva.CANCELADA),
        EstadoReserva.PROCESADA: (),
        EstadoReserva.CANCELADA: (),
    }

    def __init__(self, cliente: Any, servicio: Any, duracion: Any, **detalles: Any) -> None:
        """Valida los datos y crea la reserva en estado pendiente."""
        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaError("La reserva necesita un cliente registrado.")
        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaError("La reserva necesita un servicio válido.")
        try:
            cliente.validar()
            servicio.verificar_disponibilidad()
            parametros = servicio.validar_parametros(duracion, **detalles)
            costo_estimado = servicio.calcular_costo(duracion, **detalles)
        except SoftwareFJError as error:  # Si falla alguna validación del cliente o del servicio
            raise ReservaInvalidaError(
                f"No se pudo crear la reserva de {servicio.identificador} para {cliente.identificador}: "
                f"{error.mensaje}"
            ) from error
        self._cliente = cliente
        self._servicio = servicio
        self._detalles = dict(detalles)
        self._parametros = parametros
        self._costo_estimado = round(costo_estimado, 2)
        self._costo_final: Optional[float] = None
        self._estado = EstadoReserva.PENDIENTE
        self._historial: List[Tuple[datetime, str, str]] = []
        self._intentos_procesamiento = 0
        super().__init__(self.PREFIJO)
        self._registrar_historial("Reserva creada")

    @property
    def cliente(self) -> Cliente:
        return self._cliente

    @property
    def servicio(self) -> Servicio:
        return self._servicio

    @property
    def duracion(self) -> float:
        return self._parametros["duracion"]

    @property
    def estado(self) -> EstadoReserva:
        return self._estado

    @property
    def costo_estimado(self) -> float:
        return self._costo_estimado

    @property
    def costo_final(self) -> Optional[float]:
        return self._costo_final

    @property
    def historial(self) -> Tuple[Tuple[datetime, str, str], ...]:
        return tuple(self._historial)

    @property
    def intentos_procesamiento(self) -> int:
        return self._intentos_procesamiento

    def _registrar_historial(self, nota: str) -> None:
        self._historial.append((datetime.now(), self._estado.value, nota))

    def _validar_transicion(self, nuevo: EstadoReserva) -> None:
        """Revisa si la reserva puede pasar al nuevo estado y, si no, lanza un error."""
        actual = self._estado
        if nuevo in self.TRANSICIONES[actual]:
            return
        if actual is nuevo:
            motivo = f"ya está {actual.value}"
        elif actual is EstadoReserva.PROCESADA:
            motivo = "el servicio ya se prestó y se cobró"
        elif actual is EstadoReserva.CANCELADA:
            motivo = "la reserva fue cancelada"
        else:
            motivo = "primero debe confirmarse"
        raise OperacionNoPermitidaError(
            f"La reserva {self.identificador} no puede pasar de '{actual.value}' a '{nuevo.value}': {motivo}."
        )

    def confirmar(self) -> None:
        """Confirma la reserva y aparta los recursos del servicio."""
        self._validar_transicion(EstadoReserva.CONFIRMADA)
        self._servicio.verificar_disponibilidad()
        self._servicio.apartar(self._parametros)
        self._estado = EstadoReserva.CONFIRMADA
        self._registrar_historial("Reserva confirmada")

    def cancelar(self, motivo: Any = "sin motivo indicado") -> None:
        """Cancela la reserva y, si estaba confirmada, libera los recursos apartados."""
        self._validar_transicion(EstadoReserva.CANCELADA)
        motivo_texto = str(motivo).strip() or "sin motivo indicado"
        if self._estado is EstadoReserva.CONFIRMADA:
            self._servicio.liberar(self._parametros)
        self._estado = EstadoReserva.CANCELADA
        self._registrar_historial(f"Reserva cancelada: {motivo_texto}")

    def procesar(self, impuesto: Optional[Any] = None, descuento: Optional[Any] = None) -> float:
        """Presta el servicio, cobra el costo final y devuelve el valor cobrado."""
        self._validar_transicion(EstadoReserva.PROCESADA)
        try:
            costo_final = self._servicio.aplicar_ajustes(
                self._costo_estimado, impuesto=impuesto, descuento=descuento
            )
        except CalculoInconsistenteError as error:  # Si el descuento o el impuesto no son válidos
            self._registrar_historial(f"Cobro rechazado: {error.mensaje}")
            raise
        else:
            self._servicio.liberar(self._parametros)
            self._costo_final = costo_final
            self._estado = EstadoReserva.PROCESADA
            self._registrar_historial(f"Servicio prestado y cobrado: {formatear_moneda(costo_final)}")
            return costo_final
        finally:
            self._intentos_procesamiento += 1

    def validar(self) -> None:
        """Revisa que los datos de la reserva sean coherentes."""
        self._cliente.validar()
        self._servicio.validar()
        if not isinstance(self._estado, EstadoReserva):
            raise ReservaInvalidaError(f"La reserva {self.identificador} tiene un estado desconocido.")
        if self._estado is EstadoReserva.PROCESADA and self._costo_final is None:
            raise CalculoInconsistenteError(f"La reserva {self.identificador} está procesada pero no tiene cobro.")

    def describir(self) -> str:
        duracion = self._parametros["duracion"]
        unidad = self._servicio.UNIDAD if duracion == 1 else self._servicio.UNIDAD_PLURAL
        extras = ", ".join(
            f"{clave}: {valor}" for clave, valor in self._parametros.items()
            if clave != "duracion" and valor is not None
        )
        detalle = f"{duracion:g} {unidad}" + (f" ({extras})" if extras else "")
        if self._costo_final is not None:
            costo = f"cobrado {formatear_moneda(self._costo_final)}"
        else:
            costo = f"estimado {formatear_moneda(self._costo_estimado)}"
        return (
            f"Reserva {self.identificador} | {self._cliente.nombre} ({self._cliente.identificador}) | "
            f"{self._servicio.nombre} ({self._servicio.identificador}) | {detalle} | "
            f"{self._estado.value} | {costo}"
        )
