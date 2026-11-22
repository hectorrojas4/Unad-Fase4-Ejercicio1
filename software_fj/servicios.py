"""
Módulo: servicios.py
Proyecto: Sistema Integral de Gestión de Clientes, Servicios y Reservas - Software FJ
Curso: Programación (213023) - UNAD - Fase 4

Contiene la clase abstracta Servicio y los tres servicios que ofrece Software FJ:
salas de reuniones, alquiler de equipos y asesorías especializadas.
"""

import math
from abc import abstractmethod
from typing import Any, Dict, FrozenSet, Optional, Type, overload

from .entidad import Entidad
from .excepciones import (
    CalculoInconsistenteError,
    OperacionNoPermitidaError,
    ParametroFaltanteError,
    ParametroInvalidoError,
    ServicioInvalidoError,
    ServicioNoDisponibleError,
    ValidacionError,
)

IVA_COLOMBIA = 0.19


def formatear_moneda(valor: float) -> str:
    return "$ " + f"{valor:,.0f}".replace(",", ".")


class Servicio(Entidad):
    """Clase abstracta base de los servicios que ofrece Software FJ."""

    PREFIJO = "SRV"
    UNIDAD = "unidad"
    UNIDAD_PLURAL = "unidades"
    DURACION_MINIMA = 1.0
    DURACION_MAXIMA = 1.0
    TARIFA_MAXIMA = 10_000_000
    TASA_MAXIMA = 0.5
    PARAMETROS_PERMITIDOS: FrozenSet[str] = frozenset()

    def __init__(self, nombre: Any, tarifa: Any, disponible: Any = True) -> None:
        self._nombre = self._validar_nombre(nombre)
        self._tarifa = self._validar_tarifa(tarifa)
        self._disponible = self._validar_bandera(disponible, "disponible")
        super().__init__(self.PREFIJO)

    @staticmethod
    def _validar_nombre(valor: Any) -> str:
        if valor is None or (isinstance(valor, str) and not valor.strip()):
            raise ParametroFaltanteError("El nombre del servicio es obligatorio.")
        if not isinstance(valor, str):
            raise ServicioInvalidoError("El nombre del servicio debe ser texto.")
        texto = " ".join(valor.split())
        if not 3 <= len(texto) <= 80:
            raise ServicioInvalidoError("El nombre del servicio debe tener entre 3 y 80 caracteres.")
        return texto

    @classmethod
    def _validar_tarifa(cls, valor: Any) -> float:
        if valor is None:
            raise ParametroFaltanteError("La tarifa del servicio es obligatoria.")
        if isinstance(valor, bool):
            raise ServicioInvalidoError("La tarifa debe ser un número, no un valor lógico.")
        try:
            tarifa = float(valor)
        except (TypeError, ValueError) as error:
            raise ServicioInvalidoError(
                f"La tarifa '{valor}' no es un número válido."
            ) from error
        if not math.isfinite(tarifa) or tarifa <= 0:
            raise ServicioInvalidoError(f"La tarifa debe ser mayor que cero (recibido: {valor}).")
        if tarifa > cls.TARIFA_MAXIMA:
            raise ServicioInvalidoError(f"La tarifa supera el máximo de {formatear_moneda(cls.TARIFA_MAXIMA)}.")
        return tarifa

    @staticmethod
    def _validar_bandera(valor: Any, campo: str) -> bool:
        if not isinstance(valor, bool):
            raise ServicioInvalidoError(f"El campo '{campo}' debe ser True o False.")
        return valor

    @staticmethod
    def _convertir_entero(
        valor: Any, campo: str, minimo: int, maximo: int, clase_error: Type[ValidacionError]
    ) -> int:
        if valor is None:
            raise ParametroFaltanteError(f"El campo '{campo}' es obligatorio.")
        if isinstance(valor, bool):
            raise clase_error(f"El campo '{campo}' debe ser un número entero.")
        try:
            numero = float(valor)
        except (TypeError, ValueError) as error:  # Si el valor no es numérico, por ejemplo "doce"
            raise clase_error(
                f"El campo '{campo}' debe ser un número entero (recibido: {valor!r})."
            ) from error
        if not numero.is_integer():
            raise clase_error(f"El campo '{campo}' debe ser un número entero (recibido: {valor!r}).")
        entero = int(numero)
        if not minimo <= entero <= maximo:
            raise clase_error(f"El campo '{campo}' debe estar entre {minimo} y {maximo}.")
        return entero

    def _validar_duracion(self, duracion: Any) -> float:
        if duracion is None:
            raise ParametroFaltanteError("La duración es obligatoria.")
        if isinstance(duracion, bool):
            raise ParametroInvalidoError("La duración debe ser un número.")
        try:
            valor = float(duracion)
        except (TypeError, ValueError) as error:
            raise ParametroInvalidoError(
                f"La duración '{duracion}' no es un número válido."
            ) from error
        if not math.isfinite(valor):
            raise ParametroInvalidoError("La duración debe ser un número finito.")
        if not self.DURACION_MINIMA <= valor <= self.DURACION_MAXIMA:
            raise ParametroInvalidoError(
                f"La duración para '{self._nombre}' debe estar entre {self.DURACION_MINIMA:g} "
                f"y {self.DURACION_MAXIMA:g} {self.UNIDAD_PLURAL} (recibido: {duracion})."
            )
        return valor

    def _rechazar_parametros_desconocidos(self, detalles: Dict[str, Any]) -> None:
        desconocidos = set(detalles) - self.PARAMETROS_PERMITIDOS
        if desconocidos:
            permitidos = ", ".join(sorted(self.PARAMETROS_PERMITIDOS)) or "ninguno"
            raise ParametroInvalidoError(
                f"Parámetros no válidos para {type(self).__name__}: {', '.join(sorted(desconocidos))}. "
                f"Permitidos: {permitidos}."
            )

    @classmethod
    def _validar_tasa(cls, valor: Any, campo: str) -> float:
        if isinstance(valor, bool):
            raise CalculoInconsistenteError(f"El {campo} debe ser un número.")
        try:
            tasa = float(valor)
        except (TypeError, ValueError) as error:
            raise CalculoInconsistenteError(f"El {campo} '{valor}' no es un número.") from error
        if not math.isfinite(tasa) or not 0 <= tasa <= cls.TASA_MAXIMA:
            raise CalculoInconsistenteError(
                f"El {campo} debe estar entre 0 y {cls.TASA_MAXIMA:g} "
                f"(use 0.19 para 19 %; recibido: {valor})."
            )
        return tasa

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def tarifa(self) -> float:
        return self._tarifa

    @tarifa.setter
    def tarifa(self, valor: Any) -> None:
        self._tarifa = self._validar_tarifa(valor)

    @property
    def disponible(self) -> bool:
        return self._disponible

    def activar(self) -> None:
        if self._disponible:
            raise OperacionNoPermitidaError(f"El servicio {self.identificador} ya está habilitado.")
        self._disponible = True

    def desactivar(self) -> None:
        if not self._disponible:
            raise OperacionNoPermitidaError(f"El servicio {self.identificador} ya está deshabilitado.")
        self._disponible = False

    def verificar_disponibilidad(self) -> None:
        if not self._disponible:
            raise ServicioNoDisponibleError(
                f"El servicio {self.identificador} ({self._nombre}) no está disponible en este momento."
            )

    def validar(self) -> None:
        """Vuelve a validar los datos comunes del servicio."""
        self._validar_nombre(self._nombre)
        self._validar_tarifa(self._tarifa)

    @abstractmethod
    def validar_parametros(self, duracion: Any, **detalles: Any) -> Dict[str, Any]:
        """Valida la duración y los datos propios de cada servicio."""

    @abstractmethod
    def calcular_costo(self, duracion: Any, **detalles: Any) -> float:
        """Calcula el costo base del servicio, sin impuestos ni descuentos."""

    @abstractmethod
    def describir(self) -> str:
        """Devuelve la descripción del servicio."""

    @overload
    def calcular_costo_total(self, duracion: float, **detalles: Any) -> float: ...

    @overload
    def calcular_costo_total(self, duracion: float, *, impuesto: float, **detalles: Any) -> float: ...

    @overload
    def calcular_costo_total(self, duracion: float, *, descuento: float, **detalles: Any) -> float: ...

    @overload
    def calcular_costo_total(
        self, duracion: float, *, impuesto: float, descuento: float, **detalles: Any
    ) -> float: ...

    def calcular_costo_total(
        self,
        duracion: Any,
        *,
        impuesto: Optional[Any] = None,
        descuento: Optional[Any] = None,
        **detalles: Any,
    ) -> float:
        """Método sobrecargado: calcula el costo total con impuesto, descuento, ambos o ninguno."""
        self.verificar_disponibilidad()
        costo = self.calcular_costo(duracion, **detalles)
        return self.aplicar_ajustes(costo, impuesto=impuesto, descuento=descuento)

    def aplicar_ajustes(
        self, costo_base: Any, *, impuesto: Optional[Any] = None, descuento: Optional[Any] = None
    ) -> float:
        """Aplica el descuento y el impuesto a un costo base."""
        try:
            costo = float(costo_base)
        except (TypeError, ValueError) as error:
            raise CalculoInconsistenteError(f"El costo base '{costo_base}' no es un número.") from error
        if descuento is not None:
            costo -= costo * self._validar_tasa(descuento, "descuento")
        if impuesto is not None:
            costo += costo * self._validar_tasa(impuesto, "impuesto")
        if not math.isfinite(costo) or costo <= 0:
            raise CalculoInconsistenteError(
                f"El costo calculado para {self.identificador} es inconsistente: {costo}."
            )
        return round(costo, 2)

    def apartar(self, parametros: Dict[str, Any]) -> None:
        return None

    def liberar(self, parametros: Dict[str, Any]) -> None:
        return None


class SalaReuniones(Servicio):
    """Reserva de salas de reuniones. Se cobra por hora."""

    PREFIJO = "SAL"
    UNIDAD = "hora"
    UNIDAD_PLURAL = "horas"
    DURACION_MINIMA = 1.0
    DURACION_MAXIMA = 12.0
    CAPACIDAD_MAXIMA = 200
    RECARGO_PROYECTOR = 25_000
    PARAMETROS_PERMITIDOS = frozenset({"asistentes"})

    def __init__(
        self, nombre: Any, tarifa: Any, capacidad: Any, incluye_proyector: Any = False, disponible: Any = True
    ) -> None:
        self._capacidad = self._convertir_entero(
            capacidad, "capacidad", 1, self.CAPACIDAD_MAXIMA, ServicioInvalidoError
        )
        self._incluye_proyector = self._validar_bandera(incluye_proyector, "incluye_proyector")
        super().__init__(nombre, tarifa, disponible)

    @property
    def capacidad(self) -> int:
        return self._capacidad

    def validar_parametros(self, duracion: Any, **detalles: Any) -> Dict[str, Any]:
        """Valida las horas y el número de asistentes."""
        self._rechazar_parametros_desconocidos(detalles)
        horas = self._validar_duracion(duracion)
        asistentes = detalles.get("asistentes")
        if asistentes is not None:
            asistentes = self._convertir_entero(asistentes, "asistentes", 1, 10_000, ParametroInvalidoError)
            if asistentes > self._capacidad:
                raise ServicioNoDisponibleError(
                    f"La sala {self.identificador} admite {self._capacidad} personas; se solicitaron {asistentes}."
                )
        return {"duracion": horas, "asistentes": asistentes}

    def calcular_costo(self, duracion: Any, **detalles: Any) -> float:
        """Calcula el costo por horas, más un recargo si la sala tiene proyector."""
        parametros = self.validar_parametros(duracion, **detalles)
        costo = self._tarifa * parametros["duracion"]
        if self._incluye_proyector:
            costo += self.RECARGO_PROYECTOR
        return costo

    def describir(self) -> str:
        proyector = "con proyector" if self._incluye_proyector else "sin proyector"
        estado = "disponible" if self._disponible else "NO disponible"
        return (
            f"Sala {self.identificador} | {self._nombre} | {self._capacidad} personas, {proyector} | "
            f"{formatear_moneda(self._tarifa)}/{self.UNIDAD} | {estado}"
        )


class AlquilerEquipo(Servicio):
    """Alquiler de equipos tecnológicos. Se cobra por día y por unidad."""

    PREFIJO = "EQP"
    UNIDAD = "día"
    UNIDAD_PLURAL = "días"
    DURACION_MINIMA = 1.0
    DURACION_MAXIMA = 30.0
    TIPOS_EQUIPO = ("portatil", "proyector", "camara", "sonido", "tablet")
    UNIDADES_MAXIMAS = 500
    DIAS_TARIFA_SEMANAL = 7
    DESCUENTO_SEMANAL = 0.10
    PARAMETROS_PERMITIDOS = frozenset({"cantidad"})

    def __init__(
        self, nombre: Any, tarifa: Any, tipo_equipo: Any, unidades: Any, disponible: Any = True
    ) -> None:
        self._tipo_equipo = self._validar_tipo_equipo(tipo_equipo)
        self._unidades_totales = self._convertir_entero(
            unidades, "unidades", 0, self.UNIDADES_MAXIMAS, ServicioInvalidoError
        )
        self._unidades = self._unidades_totales
        super().__init__(nombre, tarifa, disponible)

    @classmethod
    def _validar_tipo_equipo(cls, valor: Any) -> str:
        if valor is None or (isinstance(valor, str) and not valor.strip()):
            raise ParametroFaltanteError("El tipo de equipo es obligatorio.")
        if not isinstance(valor, str):
            raise ServicioInvalidoError("El tipo de equipo debe ser texto.")
        tipo = valor.strip().lower()
        if tipo not in cls.TIPOS_EQUIPO:
            raise ServicioInvalidoError(
                f"Tipo de equipo '{valor}' no válido. Opciones: {', '.join(cls.TIPOS_EQUIPO)}."
            )
        return tipo

    @property
    def tipo_equipo(self) -> str:
        return self._tipo_equipo

    @property
    def unidades(self) -> int:
        return self._unidades

    @property
    def unidades_totales(self) -> int:
        return self._unidades_totales

    def apartar(self, parametros: Dict[str, Any]) -> None:
        """Descuenta del inventario las unidades de una reserva confirmada."""
        cantidad = parametros["cantidad"]
        if cantidad > self._unidades:
            raise ServicioNoDisponibleError(
                f"Solo quedan {self._unidades} unidades libres de {self.identificador}; se necesitan {cantidad}."
            )
        self._unidades -= cantidad

    def liberar(self, parametros: Dict[str, Any]) -> None:
        """Devuelve al inventario las unidades de una reserva."""
        cantidad = parametros["cantidad"]
        if self._unidades + cantidad > self._unidades_totales:
            raise OperacionNoPermitidaError(
                f"No se pueden devolver {cantidad} unidades a {self.identificador}: superaría el inventario total."
            )
        self._unidades += cantidad

    def verificar_disponibilidad(self) -> None:
        super().verificar_disponibilidad()
        if self._unidades == 0:
            raise ServicioNoDisponibleError(f"El servicio {self.identificador} no tiene unidades en inventario.")

    def validar_parametros(self, duracion: Any, **detalles: Any) -> Dict[str, Any]:
        """Valida los días y la cantidad de equipos."""
        self._rechazar_parametros_desconocidos(detalles)
        dias = self._validar_duracion(duracion)
        if not dias.is_integer():
            raise ParametroInvalidoError(f"Los equipos se alquilan por días completos (recibido: {duracion}).")
        cantidad = self._convertir_entero(
            detalles.get("cantidad", 1), "cantidad", 1, self.UNIDADES_MAXIMAS, ParametroInvalidoError
        )
        if cantidad > self._unidades:
            raise ServicioNoDisponibleError(
                f"Solo hay {self._unidades} unidades libres de {self.identificador}; se solicitaron {cantidad}."
            )
        return {"duracion": int(dias), "cantidad": cantidad}

    def calcular_costo(self, duracion: Any, **detalles: Any) -> float:
        """Calcula el costo por días y unidades, con descuento desde 7 días."""
        parametros = self.validar_parametros(duracion, **detalles)
        costo = self._tarifa * parametros["duracion"] * parametros["cantidad"]
        if parametros["duracion"] >= self.DIAS_TARIFA_SEMANAL:
            costo -= costo * self.DESCUENTO_SEMANAL
        return costo

    def describir(self) -> str:
        estado = "disponible" if self._disponible else "NO disponible"
        return (
            f"Equipo {self.identificador} | {self._nombre} | tipo: {self._tipo_equipo}, "
            f"{self._unidades} de {self._unidades_totales} unidades libres | "
            f"{formatear_moneda(self._tarifa)}/{self.UNIDAD} por unidad | {estado}"
        )


class AsesoriaEspecializada(Servicio):
    """Asesoría con un consultor. Se cobra por hora según su nivel y la modalidad."""

    PREFIJO = "ASE"
    UNIDAD = "hora"
    UNIDAD_PLURAL = "horas"
    DURACION_MINIMA = 1.0
    DURACION_MAXIMA = 8.0
    ESPECIALIDADES = ("software", "redes", "seguridad", "datos", "nube")
    FACTORES_NIVEL = {"junior": 1.0, "senior": 1.5, "experto": 2.0}
    MODALIDADES = ("virtual", "presencial")
    RECARGO_PRESENCIAL = 0.15
    PARAMETROS_PERMITIDOS = frozenset({"modalidad"})

    def __init__(
        self, nombre: Any, tarifa: Any, especialidad: Any, nivel: Any = "senior", disponible: Any = True
    ) -> None:
        self._especialidad = self._validar_opcion(especialidad, "especialidad", self.ESPECIALIDADES)
        self._nivel = self._validar_opcion(nivel, "nivel", tuple(self.FACTORES_NIVEL))
        super().__init__(nombre, tarifa, disponible)

    @staticmethod
    def _validar_opcion(valor: Any, campo: str, opciones: tuple) -> str:
        if valor is None or (isinstance(valor, str) and not valor.strip()):
            raise ParametroFaltanteError(f"El campo '{campo}' es obligatorio.")
        if not isinstance(valor, str) or valor.strip().lower() not in opciones:
            raise ServicioInvalidoError(f"'{valor}' no es válido para '{campo}'. Opciones: {', '.join(opciones)}.")
        return valor.strip().lower()

    @property
    def especialidad(self) -> str:
        return self._especialidad

    @property
    def nivel(self) -> str:
        return self._nivel

    def validar_parametros(self, duracion: Any, **detalles: Any) -> Dict[str, Any]:
        """Valida las horas y la modalidad (virtual o presencial)."""
        self._rechazar_parametros_desconocidos(detalles)
        horas = self._validar_duracion(duracion)
        modalidad = detalles.get("modalidad", "virtual")
        if not isinstance(modalidad, str) or modalidad.strip().lower() not in self.MODALIDADES:
            raise ParametroInvalidoError(
                f"Modalidad '{modalidad}' no válida. Opciones: {', '.join(self.MODALIDADES)}."
            )
        return {"duracion": horas, "modalidad": modalidad.strip().lower()}

    def calcular_costo(self, duracion: Any, **detalles: Any) -> float:
        """Calcula el costo según las horas y el nivel, con recargo si es presencial."""
        parametros = self.validar_parametros(duracion, **detalles)
        costo = self._tarifa * parametros["duracion"] * self.FACTORES_NIVEL[self._nivel]
        if parametros["modalidad"] == "presencial":
            costo += costo * self.RECARGO_PRESENCIAL
        return costo

    def describir(self) -> str:
        estado = "disponible" if self._disponible else "NO disponible"
        return (
            f"Asesoría {self.identificador} | {self._nombre} | {self._especialidad}, nivel {self._nivel} | "
            f"{formatear_moneda(self._tarifa)}/{self.UNIDAD} base | {estado}"
        )
