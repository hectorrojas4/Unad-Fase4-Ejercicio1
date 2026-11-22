"""
Módulo: gestor.py
Proyecto: Sistema Integral de Gestión de Clientes, Servicios y Reservas - Software FJ
Curso: Programación (213023) - UNAD - Fase 4

Contiene GestorSoftwareFJ, la clase que administra el sistema SIN base de
datos: toda la información vive en listas internas en memoria.

Cada operación usa bloques try/except/else/finally:
    - try:     se intenta la operación.
    - except:  se registra el error en el log y se vuelve a lanzar para que
               quien llamó decida cómo continuar (el programa no se detiene).
    - else:    solo si no hubo error: se guarda el resultado y se registra el evento.
    - finally: siempre se ejecuta: cuenta la operación como intentada.
"""

from typing import Any, Dict, List, Optional, Tuple, Type  # Anotaciones de tipo

from .cliente import Cliente  # Entidad cliente
from .excepciones import (  # Errores propios usados por el gestor
    EntidadNoEncontradaError,
    ParametroFaltanteError,
    RegistroDuplicadoError,
    ServicioInvalidoError,
    SoftwareFJError,
)
from .logger import registrar_error, registrar_evento  # Registro en logs/sistema.log
from .servicios import (  # Servicios disponibles
    AlquilerEquipo,
    AsesoriaEspecializada,
    SalaReuniones,
    Servicio,
    formatear_moneda,
)


class GestorSoftwareFJ:
    """Administra clientes y servicios de Software FJ usando listas en memoria.

    PARTE 2 (pendiente): gestión de reservas (crear, confirmar, cancelar y procesar).
    """

    # Relaciona el nombre corto de cada tipo con su clase (permite crear servicios por nombre)
    TIPOS_SERVICIO: Dict[str, Type[Servicio]] = {
        "sala": SalaReuniones,  # Reserva de salas
        "equipo": AlquilerEquipo,  # Alquiler de equipos
        "asesoria": AsesoriaEspecializada,  # Asesorías especializadas
    }

    def __init__(self) -> None:
        """Inicializa las listas internas vacías y los contadores."""
        self._clientes: List[Cliente] = []  # Lista interna de clientes registrados
        self._servicios: List[Servicio] = []  # Lista interna de servicios ofrecidos
        self._reservas: List[Any] = []  # PARTE 2: lista interna de reservas (aún sin uso)
        self._operaciones_intentadas = 0  # Cuántas operaciones se han intentado (exitosas o no)
        self._operaciones_fallidas = 0  # Cuántas terminaron en error controlado
        registrar_evento("Gestor Software FJ iniciado (sin base de datos: listas en memoria).")  # Evento inicial

    # ==================================================================
    # CLIENTES
    # ==================================================================
    def registrar_cliente(self, nombre: Any, documento: Any, correo: Any, telefono: Any) -> Cliente:
        """Crea y registra un cliente nuevo. Lanza SoftwareFJError si algo falla."""
        try:  # Se intenta el registro
            documento_limpio = Cliente.normalizar_documento(documento)  # Valida el documento primero
            if self._buscar_por_documento(documento_limpio) is not None:  # ¿Ya existe ese documento?
                raise RegistroDuplicadoError(  # No se permiten clientes repetidos
                    f"Ya existe un cliente con el documento terminado en {documento_limpio[-4:]}."
                )
            cliente = Cliente(nombre, documento_limpio, correo, telefono)  # Crea el objeto (valida el resto)
        except SoftwareFJError as error:  # Error controlado: datos inválidos, faltantes o duplicados
            self._operaciones_fallidas += 1  # Se contabiliza el fallo
            registrar_error("Registro de cliente rechazado", error)  # Queda en el log
            raise  # Se relanza el MISMO error para que el llamador lo maneje
        else:  # Solo si no hubo ningún error
            self._clientes.append(cliente)  # Se guarda en la lista interna
            registrar_evento(f"Cliente registrado: {cliente.describir()}")  # Queda en el log
            return cliente  # Se entrega el cliente creado
        finally:  # Se ejecuta siempre, haya o no error
            self._operaciones_intentadas += 1  # Se contabiliza el intento

    def actualizar_contacto_cliente(
        self, identificador: str, correo: Optional[Any] = None, telefono: Optional[Any] = None
    ) -> Cliente:
        """Actualiza el correo y/o teléfono de un cliente existente."""
        try:  # Se intenta la actualización
            cliente = self.buscar_cliente(identificador)  # Lanza EntidadNoEncontradaError si no existe
            cliente.actualizar_contacto(correo=correo, telefono=telefono)  # Valida en modo todo o nada
        except SoftwareFJError as error:  # Cliente inexistente o datos inválidos
            self._operaciones_fallidas += 1  # Se contabiliza el fallo
            registrar_error(f"Actualización de contacto rechazada ({identificador})", error)  # Log
            raise  # Se relanza para el llamador
        else:  # Actualización exitosa
            registrar_evento(f"Contacto actualizado: {cliente.describir()}")  # Log
            return cliente  # Se entrega el cliente actualizado
        finally:  # Siempre
            self._operaciones_intentadas += 1  # Se contabiliza el intento

    def buscar_cliente(self, identificador: str) -> Cliente:
        """Busca un cliente por su identificador (CLI-001) o por su documento."""
        for cliente in self._clientes:  # Recorre la lista interna
            if identificador in (cliente.identificador, cliente.documento):  # Coincide id o documento
                return cliente  # Lo encontró
        raise EntidadNoEncontradaError(f"No existe un cliente con identificador '{identificador}'.")  # No está

    def listar_clientes(self) -> Tuple[Cliente, ...]:
        """Devuelve una copia inmutable de los clientes (protege la lista interna)."""
        return tuple(self._clientes)  # Una tupla no se puede modificar desde afuera

    def _buscar_por_documento(self, documento: str) -> Optional[Cliente]:
        """Devuelve el cliente con ese documento o None si no existe."""
        return next((c for c in self._clientes if c.documento == documento), None)  # Primer coincidente

    # ==================================================================
    # SERVICIOS
    # ==================================================================
    def registrar_servicio(self, tipo: Any, **datos: Any) -> Servicio:
        """Crea y registra un servicio del tipo indicado ('sala', 'equipo' o 'asesoria')."""
        try:  # Se intenta crear el servicio
            clase = self._resolver_tipo_servicio(tipo)  # Clase correspondiente al tipo
            try:  # try anidado: captura errores de parámetros del constructor
                servicio = clase(**datos)  # Crea el objeto: el constructor valida todo
            except TypeError as error:  # Faltan o sobran argumentos en la llamada
                raise ParametroFaltanteError(  # ENCADENAMIENTO: TypeError -> error del dominio
                    f"Faltan o sobran parámetros para crear un servicio '{tipo}'."
                ) from error  # El detalle técnico queda en la causa original
        except SoftwareFJError as error:  # Cualquier error controlado
            self._operaciones_fallidas += 1  # Se contabiliza el fallo
            registrar_error(f"Creación de servicio '{tipo}' rechazada", error)  # Log con cadena de causas
            raise  # Se relanza para el llamador
        else:  # Servicio creado sin errores
            self._servicios.append(servicio)  # Se guarda en la lista interna
            registrar_evento(f"Servicio registrado: {servicio.describir()}")  # Log
            return servicio  # Se entrega el servicio creado
        finally:  # Siempre
            self._operaciones_intentadas += 1  # Se contabiliza el intento

    def _resolver_tipo_servicio(self, tipo: Any) -> Type[Servicio]:
        """Traduce el nombre corto del tipo a su clase; lanza error si no existe."""
        try:  # Intenta buscar el tipo en el diccionario
            return self.TIPOS_SERVICIO[tipo.strip().lower()]  # "Sala " -> SalaReuniones
        except (KeyError, AttributeError) as error:  # Tipo inexistente o no es texto
            raise ServicioInvalidoError(  # ENCADENAMIENTO con el error original
                f"El tipo de servicio '{tipo}' no existe. Opciones: {', '.join(self.TIPOS_SERVICIO)}."
            ) from error

    def buscar_servicio(self, identificador: str) -> Servicio:
        """Busca un servicio por su identificador (por ejemplo SAL-001)."""
        for servicio in self._servicios:  # Recorre la lista interna
            if servicio.identificador == identificador:  # Coincide el identificador
                return servicio  # Lo encontró
        raise EntidadNoEncontradaError(f"No existe un servicio con identificador '{identificador}'.")  # No está

    def listar_servicios(self, solo_disponibles: bool = False) -> Tuple[Servicio, ...]:
        """Devuelve los servicios; opcionalmente solo los disponibles."""
        if solo_disponibles:  # Filtro opcional
            return tuple(s for s in self._servicios if s.disponible)  # Solo habilitados
        return tuple(self._servicios)  # Copia inmutable de todos

    def cambiar_disponibilidad_servicio(self, identificador: str, disponible: bool) -> Servicio:
        """Habilita o deshabilita un servicio existente."""
        try:  # Se intenta el cambio
            servicio = self.buscar_servicio(identificador)  # Lanza error si no existe
            if disponible:  # Se quiere habilitar
                servicio.activar()  # Lanza OperacionNoPermitidaError si ya estaba activo
            else:  # Se quiere deshabilitar
                servicio.desactivar()  # Lanza OperacionNoPermitidaError si ya estaba inactivo
        except SoftwareFJError as error:  # Error controlado
            self._operaciones_fallidas += 1  # Se contabiliza el fallo
            registrar_error(f"Cambio de disponibilidad rechazado ({identificador})", error)  # Log
            raise  # Se relanza
        else:  # Cambio exitoso
            estado = "habilitado" if disponible else "deshabilitado"  # Texto del nuevo estado
            registrar_evento(f"Servicio {identificador} {estado}.")  # Log
            return servicio  # Se entrega el servicio
        finally:  # Siempre
            self._operaciones_intentadas += 1  # Se contabiliza el intento

    def cotizar_servicio(
        self,
        identificador: str,
        duracion: Any,
        *,
        impuesto: Optional[Any] = None,
        descuento: Optional[Any] = None,
        **detalles: Any,
    ) -> float:
        """Calcula el costo total de un servicio usando la variante de cálculo que corresponda."""
        try:  # Se intenta la cotización
            servicio = self.buscar_servicio(identificador)  # Lanza error si no existe
            costo = servicio.calcular_costo_total(  # SOBRECARGA + POLIMORFISMO
                duracion, impuesto=impuesto, descuento=descuento, **detalles
            )
        except SoftwareFJError as error:  # Error controlado (parámetros, disponibilidad, cálculo)
            self._operaciones_fallidas += 1  # Se contabiliza el fallo
            registrar_error(f"Cotización rechazada ({identificador})", error)  # Log
            raise  # Se relanza
        else:  # Cotización exitosa
            registrar_evento(  # Log con el detalle de la variante usada
                f"Cotización {identificador}: duración={duracion}, impuesto={impuesto}, "
                f"descuento={descuento}, detalles={detalles} -> {formatear_moneda(costo)}"
            )
            return costo  # Se entrega el valor calculado
        finally:  # Siempre
            self._operaciones_intentadas += 1  # Se contabiliza el intento

    # ==================================================================
    # RESERVAS - PARTE 2 (pendiente)
    # ==================================================================
    # Aquí se implementarán: crear_reserva, confirmar_reserva,
    # cancelar_reserva, procesar_reserva y listar_reservas, usando la
    # clase Reserva (software_fj/reserva.py) y la lista self._reservas.

    # ==================================================================
    # RESUMEN
    # ==================================================================
    def resumen(self) -> Dict[str, int]:
        """Devuelve un resumen numérico del estado del sistema."""
        return {  # Diccionario con los totales
            "clientes": len(self._clientes),  # Clientes registrados
            "servicios": len(self._servicios),  # Servicios creados
            "servicios_disponibles": len(self.listar_servicios(solo_disponibles=True)),  # Servicios habilitados
            "reservas": len(self._reservas),  # PARTE 2
            "operaciones_intentadas": self._operaciones_intentadas,  # Total de intentos en el gestor
            "operaciones_fallidas": self._operaciones_fallidas,  # Intentos que terminaron en error
        }
