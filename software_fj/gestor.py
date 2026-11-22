"""
Módulo: gestor.py
Proyecto: Sistema Integral de Gestión de Clientes, Servicios y Reservas - Software FJ
Curso: Programación (213023) - UNAD - Fase 4

Contiene la clase GestorSoftwareFJ, que administra clientes, servicios y
reservas guardándolos en listas en memoria.
"""

from typing import Any, Callable, Dict, List, Optional, Tuple, Type

from .cliente import Cliente
from .excepciones import (
    EntidadNoEncontradaError,
    ParametroFaltanteError,
    RegistroDuplicadoError,
    ServicioInvalidoError,
    SoftwareFJError,
)
from .logger import registrar_error, registrar_evento
from .reserva import EstadoReserva, Reserva
from .servicios import (
    AlquilerEquipo,
    AsesoriaEspecializada,
    SalaReuniones,
    Servicio,
    formatear_moneda,
)


class GestorSoftwareFJ:
    """Administra clientes, servicios y reservas de Software FJ usando listas en memoria."""

    TIPOS_SERVICIO: Dict[str, Type[Servicio]] = {
        "sala": SalaReuniones,
        "equipo": AlquilerEquipo,
        "asesoria": AsesoriaEspecializada,
    }

    def __init__(self) -> None:
        self._clientes: List[Cliente] = []
        self._servicios: List[Servicio] = []
        self._reservas: List[Reserva] = []
        self._operaciones_intentadas = 0
        self._operaciones_fallidas = 0
        registrar_evento("Gestor Software FJ iniciado (sin base de datos: listas en memoria).")

    def registrar_cliente(self, nombre: Any, documento: Any, correo: Any, telefono: Any) -> Cliente:
        """Crea y registra un cliente nuevo."""
        try:
            documento_limpio = Cliente.normalizar_documento(documento)
            if self._buscar_por_documento(documento_limpio) is not None:
                raise RegistroDuplicadoError(
                    f"Ya existe un cliente con el documento terminado en {documento_limpio[-4:]}."
                )
            cliente = Cliente(nombre, documento_limpio, correo, telefono)
        except SoftwareFJError as error:
            self._operaciones_fallidas += 1
            registrar_error("Registro de cliente rechazado", error)
            raise
        else:
            self._clientes.append(cliente)
            registrar_evento(f"Cliente registrado: {cliente.describir()}")
            return cliente
        finally:
            self._operaciones_intentadas += 1

    def actualizar_contacto_cliente(
        self, identificador: str, correo: Optional[Any] = None, telefono: Optional[Any] = None
    ) -> Cliente:
        """Actualiza el correo y/o el teléfono de un cliente registrado."""
        try:
            cliente = self.buscar_cliente(identificador)
            cliente.actualizar_contacto(correo=correo, telefono=telefono)
        except SoftwareFJError as error:
            self._operaciones_fallidas += 1
            registrar_error(f"Actualización de contacto rechazada ({identificador})", error)
            raise
        else:
            registrar_evento(f"Contacto actualizado: {cliente.describir()}")
            return cliente
        finally:
            self._operaciones_intentadas += 1

    def buscar_cliente(self, identificador: str) -> Cliente:
        """Busca un cliente por su identificador o por su documento."""
        for cliente in self._clientes:
            if identificador in (cliente.identificador, cliente.documento):
                return cliente
        raise EntidadNoEncontradaError(f"No existe un cliente con identificador '{identificador}'.")

    def listar_clientes(self) -> Tuple[Cliente, ...]:
        return tuple(self._clientes)

    def _buscar_por_documento(self, documento: str) -> Optional[Cliente]:
        return next((c for c in self._clientes if c.documento == documento), None)

    def registrar_servicio(self, tipo: Any, **datos: Any) -> Servicio:
        """Crea y registra un servicio del tipo indicado: sala, equipo o asesoría."""
        try:
            clase = self._resolver_tipo_servicio(tipo)
            try:
                servicio = clase(**datos)
            except TypeError as error:  # Si faltan o sobran datos para crear el servicio
                raise ParametroFaltanteError(
                    f"Faltan o sobran parámetros para crear un servicio '{tipo}'."
                ) from error
        except SoftwareFJError as error:
            self._operaciones_fallidas += 1
            registrar_error(f"Creación de servicio '{tipo}' rechazada", error)
            raise
        else:
            self._servicios.append(servicio)
            registrar_evento(f"Servicio registrado: {servicio.describir()}")
            return servicio
        finally:
            self._operaciones_intentadas += 1

    def _resolver_tipo_servicio(self, tipo: Any) -> Type[Servicio]:
        try:
            return self.TIPOS_SERVICIO[tipo.strip().lower()]
        except (KeyError, AttributeError) as error:  # Si el tipo no existe o no es texto
            raise ServicioInvalidoError(
                f"El tipo de servicio '{tipo}' no existe. Opciones: {', '.join(self.TIPOS_SERVICIO)}."
            ) from error

    def buscar_servicio(self, identificador: str) -> Servicio:
        """Busca un servicio por su identificador."""
        for servicio in self._servicios:
            if servicio.identificador == identificador:
                return servicio
        raise EntidadNoEncontradaError(f"No existe un servicio con identificador '{identificador}'.")

    def listar_servicios(self, solo_disponibles: bool = False) -> Tuple[Servicio, ...]:
        if solo_disponibles:
            return tuple(s for s in self._servicios if s.disponible)
        return tuple(self._servicios)

    def cambiar_disponibilidad_servicio(self, identificador: str, disponible: bool) -> Servicio:
        """Habilita o deshabilita un servicio."""
        try:
            servicio = self.buscar_servicio(identificador)
            if disponible:
                servicio.activar()
            else:
                servicio.desactivar()
        except SoftwareFJError as error:
            self._operaciones_fallidas += 1
            registrar_error(f"Cambio de disponibilidad rechazado ({identificador})", error)
            raise
        else:
            estado = "habilitado" if disponible else "deshabilitado"
            registrar_evento(f"Servicio {identificador} {estado}.")
            return servicio
        finally:
            self._operaciones_intentadas += 1

    def cotizar_servicio(
        self,
        identificador: str,
        duracion: Any,
        *,
        impuesto: Optional[Any] = None,
        descuento: Optional[Any] = None,
        **detalles: Any,
    ) -> float:
        """Calcula cuánto cuesta un servicio, con impuesto y descuento opcionales."""
        try:
            servicio = self.buscar_servicio(identificador)
            costo = servicio.calcular_costo_total(
                duracion, impuesto=impuesto, descuento=descuento, **detalles
            )
        except SoftwareFJError as error:
            self._operaciones_fallidas += 1
            registrar_error(f"Cotización rechazada ({identificador})", error)
            raise
        else:
            registrar_evento(
                f"Cotización {identificador}: duración={duracion}, impuesto={impuesto}, "
                f"descuento={descuento}, detalles={detalles} -> {formatear_moneda(costo)}"
            )
            return costo
        finally:
            self._operaciones_intentadas += 1

    def crear_reserva(self, id_cliente: str, id_servicio: str, duracion: Any, **detalles: Any) -> Reserva:
        """Crea una reserva pendiente para un cliente y un servicio registrados."""
        try:
            cliente = self.buscar_cliente(id_cliente)
            servicio = self.buscar_servicio(id_servicio)
            reserva = Reserva(cliente, servicio, duracion, **detalles)
        except SoftwareFJError as error:
            self._operaciones_fallidas += 1
            registrar_error(f"Creación de reserva rechazada ({id_cliente} -> {id_servicio})", error)
            raise
        else:
            self._reservas.append(reserva)
            registrar_evento(f"Reserva creada: {reserva.describir()}")
            return reserva
        finally:
            self._operaciones_intentadas += 1

    def confirmar_reserva(self, identificador: str) -> Reserva:
        return self._operar_reserva(identificador, "Confirmación", lambda reserva: reserva.confirmar())

    def cancelar_reserva(self, identificador: str, motivo: Any = "sin motivo indicado") -> Reserva:
        return self._operar_reserva(identificador, "Cancelación", lambda reserva: reserva.cancelar(motivo))

    def procesar_reserva(
        self, identificador: str, *, impuesto: Optional[Any] = None, descuento: Optional[Any] = None
    ) -> Reserva:
        return self._operar_reserva(
            identificador, "Procesamiento",
            lambda reserva: reserva.procesar(impuesto=impuesto, descuento=descuento),
        )

    def _operar_reserva(
        self, identificador: str, operacion: str, accion: Callable[[Reserva], Any]
    ) -> Reserva:
        """Busca la reserva, le aplica la acción indicada y registra el resultado."""
        try:
            reserva = self.buscar_reserva(identificador)
            accion(reserva)
        except SoftwareFJError as error:
            self._operaciones_fallidas += 1
            registrar_error(f"{operacion} de reserva rechazada ({identificador})", error)
            raise
        else:
            registrar_evento(f"{operacion} de reserva exitosa: {reserva.describir()}")
            return reserva
        finally:
            self._operaciones_intentadas += 1

    def buscar_reserva(self, identificador: str) -> Reserva:
        """Busca una reserva por su identificador."""
        for reserva in self._reservas:
            if reserva.identificador == identificador:
                return reserva
        raise EntidadNoEncontradaError(f"No existe una reserva con identificador '{identificador}'.")

    def listar_reservas(self, estado: Optional[EstadoReserva] = None) -> Tuple[Reserva, ...]:
        if estado is None:
            return tuple(self._reservas)
        return tuple(r for r in self._reservas if r.estado is estado)

    def resumen(self) -> Dict[str, Any]:
        """Devuelve un resumen con los totales del sistema."""
        procesadas = self.listar_reservas(EstadoReserva.PROCESADA)
        return {
            "clientes": len(self._clientes),
            "servicios": len(self._servicios),
            "servicios_disponibles": len(self.listar_servicios(solo_disponibles=True)),
            "reservas": len(self._reservas),
            "reservas_por_estado": {
                estado.value: len(self.listar_reservas(estado)) for estado in EstadoReserva
            },
            "total_cobrado": round(sum(r.costo_final or 0 for r in procesadas), 2),
            "operaciones_intentadas": self._operaciones_intentadas,
            "operaciones_fallidas": self._operaciones_fallidas,
        }
