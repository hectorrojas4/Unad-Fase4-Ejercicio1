"""
Módulo: servicios.py
Proyecto: Sistema Integral de Gestión de Clientes, Servicios y Reservas - Software FJ
Curso: Programación (213023) - UNAD - Fase 4

Contiene la clase abstracta Servicio y los tres servicios especializados que
ofrece Software FJ:

    Servicio (abstracta, hereda de Entidad)
    ├── SalaReuniones           -> reserva de salas, se cobra por hora
    ├── AlquilerEquipo          -> alquiler de equipos, se cobra por día
    └── AsesoriaEspecializada   -> asesorías, se cobra por hora según el nivel

Principios aplicados:
    - HERENCIA: los tres servicios heredan atributos y métodos de Servicio.
    - POLIMORFISMO: cada servicio sobrescribe calcular_costo(), describir() y
      validar_parametros(); el sistema los llama igual sin saber de qué tipo son.
    - SOBRECARGA: calcular_costo_total() tiene varias "firmas" (con impuesto,
      con descuento, con ambos o sin ninguno). Ver la explicación en ese método.
"""

import math  # Para detectar valores infinitos o NaN en los cálculos
from abc import abstractmethod  # Para declarar métodos abstractos
from typing import Any, Dict, FrozenSet, Optional, Type, overload  # Anotaciones de tipo

from .entidad import Entidad  # Clase abstracta padre
from .excepciones import (  # Errores propios que puede lanzar este módulo
    CalculoInconsistenteError,
    OperacionNoPermitidaError,
    ParametroFaltanteError,
    ParametroInvalidoError,
    ServicioInvalidoError,
    ServicioNoDisponibleError,
    ValidacionError,
)

IVA_COLOMBIA = 0.19  # Tarifa general del IVA en Colombia (19 %), útil como valor de referencia


def formatear_moneda(valor: float) -> str:
    """Convierte un número a pesos colombianos: 1234567.8 -> '$ 1.234.568'."""
    return "$ " + f"{valor:,.0f}".replace(",", ".")  # Separador de miles con punto


class Servicio(Entidad):
    """Clase abstracta que representa un servicio ofrecido por Software FJ.

    No se puede instanciar directamente: obliga a las clases hijas a
    implementar calcular_costo(), validar_parametros() y describir().
    """

    PREFIJO = "SRV"  # Prefijo genérico (cada hija define el suyo)
    UNIDAD = "unidad"  # Unidad de cobro en singular (hora, día...)
    UNIDAD_PLURAL = "unidades"  # Unidad de cobro en plural
    DURACION_MINIMA = 1.0  # Duración mínima permitida (cada hija la ajusta)
    DURACION_MAXIMA = 1.0  # Duración máxima permitida (cada hija la ajusta)
    TARIFA_MAXIMA = 10_000_000  # Tope de tarifa para detectar valores absurdos
    TASA_MAXIMA = 0.5  # Ningún descuento o impuesto puede superar el 50 %
    PARAMETROS_PERMITIDOS: FrozenSet[str] = frozenset()  # Detalles extra que acepta cada servicio

    def __init__(self, nombre: Any, tarifa: Any, disponible: Any = True) -> None:
        """Valida los datos comunes a todo servicio y luego asigna el identificador."""
        self._nombre = self._validar_nombre(nombre)  # Nombre comercial del servicio
        self._tarifa = self._validar_tarifa(tarifa)  # Precio por unidad de cobro
        self._disponible = self._validar_bandera(disponible, "disponible")  # ¿Se puede usar hoy?
        super().__init__(self.PREFIJO)  # Todo válido: se asigna el identificador (ej. SAL-001)

    # ------------------------------------------------------------------
    # Validadores reutilizables por todas las clases hijas
    # ------------------------------------------------------------------
    @staticmethod
    def _validar_nombre(valor: Any) -> str:
        """Valida el nombre comercial del servicio."""
        if valor is None or (isinstance(valor, str) and not valor.strip()):  # Vacío o ausente
            raise ParametroFaltanteError("El nombre del servicio es obligatorio.")
        if not isinstance(valor, str):  # Debe ser texto
            raise ServicioInvalidoError("El nombre del servicio debe ser texto.")
        texto = " ".join(valor.split())  # Normaliza los espacios
        if not 3 <= len(texto) <= 80:  # Longitud razonable
            raise ServicioInvalidoError("El nombre del servicio debe tener entre 3 y 80 caracteres.")
        return texto  # Nombre válido

    @classmethod
    def _validar_tarifa(cls, valor: Any) -> float:
        """Valida que la tarifa sea un número positivo y razonable."""
        if valor is None:  # La tarifa no puede faltar
            raise ParametroFaltanteError("La tarifa del servicio es obligatoria.")
        if isinstance(valor, bool):  # True/False no son tarifas (bool hereda de int)
            raise ServicioInvalidoError("La tarifa debe ser un número, no un valor lógico.")
        try:  # Intenta convertir el valor a número decimal
            tarifa = float(valor)  # "50000" -> 50000.0 ; "abc" -> ValueError ; [1] -> TypeError
        except (TypeError, ValueError) as error:  # Error técnico de conversión...
            raise ServicioInvalidoError(  # ...encadenado con un error del dominio
                f"La tarifa '{valor}' no es un número válido."
            ) from error
        if not math.isfinite(tarifa) or tarifa <= 0:  # Rechaza negativos, cero, infinito y NaN
            raise ServicioInvalidoError(f"La tarifa debe ser mayor que cero (recibido: {valor}).")
        if tarifa > cls.TARIFA_MAXIMA:  # Rechaza valores fuera de toda lógica
            raise ServicioInvalidoError(f"La tarifa supera el máximo de {formatear_moneda(cls.TARIFA_MAXIMA)}.")
        return tarifa  # Tarifa válida

    @staticmethod
    def _validar_bandera(valor: Any, campo: str) -> bool:
        """Valida que un indicador sí/no sea realmente True o False."""
        if not isinstance(valor, bool):  # Evita que "no" o 0 se interpreten mal
            raise ServicioInvalidoError(f"El campo '{campo}' debe ser True o False.")
        return valor  # Valor lógico válido

    @staticmethod
    def _convertir_entero(
        valor: Any, campo: str, minimo: int, maximo: int, clase_error: Type[ValidacionError]
    ) -> int:
        """Convierte un valor a entero dentro de un rango; si no puede, lanza clase_error."""
        if valor is None:  # El dato no puede faltar
            raise ParametroFaltanteError(f"El campo '{campo}' es obligatorio.")
        if isinstance(valor, bool):  # True/False no son cantidades
            raise clase_error(f"El campo '{campo}' debe ser un número entero.")
        try:  # Intenta convertir a número
            numero = float(valor)  # Acepta 12, 12.0 y "12"
        except (TypeError, ValueError) as error:  # Texto como "doce" o tipos raros
            raise clase_error(  # Encadenamiento con el error original
                f"El campo '{campo}' debe ser un número entero (recibido: {valor!r})."
            ) from error
        if not numero.is_integer():  # Rechaza 12.5, infinito y NaN
            raise clase_error(f"El campo '{campo}' debe ser un número entero (recibido: {valor!r}).")
        entero = int(numero)  # Conversión segura a entero
        if not minimo <= entero <= maximo:  # Verifica el rango permitido
            raise clase_error(f"El campo '{campo}' debe estar entre {minimo} y {maximo}.")
        return entero  # Entero válido

    def _validar_duracion(self, duracion: Any) -> float:
        """Valida la duración solicitada según los límites de cada tipo de servicio."""
        if duracion is None:  # La duración es obligatoria
            raise ParametroFaltanteError("La duración es obligatoria.")
        if isinstance(duracion, bool):  # True/False no son duraciones
            raise ParametroInvalidoError("La duración debe ser un número.")
        try:  # Intenta convertir a número
            valor = float(duracion)  # "3" -> 3.0 ; "tres" -> ValueError
        except (TypeError, ValueError) as error:  # Conversión imposible
            raise ParametroInvalidoError(  # Encadenamiento con el error original
                f"La duración '{duracion}' no es un número válido."
            ) from error
        if not math.isfinite(valor):  # Rechaza infinito y NaN
            raise ParametroInvalidoError("La duración debe ser un número finito.")
        if not self.DURACION_MINIMA <= valor <= self.DURACION_MAXIMA:  # Límites del servicio
            raise ParametroInvalidoError(
                f"La duración para '{self._nombre}' debe estar entre {self.DURACION_MINIMA:g} "
                f"y {self.DURACION_MAXIMA:g} {self.UNIDAD_PLURAL} (recibido: {duracion})."
            )
        return valor  # Duración válida

    def _rechazar_parametros_desconocidos(self, detalles: Dict[str, Any]) -> None:
        """Evita que se acepten en silencio parámetros que este servicio no usa."""
        desconocidos = set(detalles) - self.PARAMETROS_PERMITIDOS  # Parámetros sobrantes
        if desconocidos:  # Si llegó alguno que no corresponde
            permitidos = ", ".join(sorted(self.PARAMETROS_PERMITIDOS)) or "ninguno"  # Texto de ayuda
            raise ParametroInvalidoError(
                f"Parámetros no válidos para {type(self).__name__}: {', '.join(sorted(desconocidos))}. "
                f"Permitidos: {permitidos}."
            )

    @classmethod
    def _validar_tasa(cls, valor: Any, campo: str) -> float:
        """Valida una tasa (impuesto o descuento) expresada como fracción: 0.19 = 19 %."""
        if isinstance(valor, bool):  # True/False no son tasas
            raise CalculoInconsistenteError(f"El {campo} debe ser un número.")
        try:  # Intenta convertir a número
            tasa = float(valor)  # "0.19" -> 0.19
        except (TypeError, ValueError) as error:  # Conversión imposible
            raise CalculoInconsistenteError(f"El {campo} '{valor}' no es un número.") from error
        if not math.isfinite(tasa) or not 0 <= tasa <= cls.TASA_MAXIMA:  # Fuera de rango
            raise CalculoInconsistenteError(
                f"El {campo} debe estar entre 0 y {cls.TASA_MAXIMA:g} "
                f"(use 0.19 para 19 %; recibido: {valor})."
            )
        return tasa  # Tasa válida

    # ------------------------------------------------------------------
    # Propiedades (encapsulación)
    # ------------------------------------------------------------------
    @property
    def nombre(self) -> str:
        """Nombre comercial del servicio."""
        return self._nombre  # Solo lectura

    @property
    def tarifa(self) -> float:
        """Tarifa por unidad de cobro (hora o día)."""
        return self._tarifa  # Lectura

    @tarifa.setter
    def tarifa(self, valor: Any) -> None:
        """Permite actualizar la tarifa, siempre validándola."""
        self._tarifa = self._validar_tarifa(valor)  # Solo se asigna si es válida

    @property
    def disponible(self) -> bool:
        """Indica si el servicio está habilitado."""
        return self._disponible  # Solo lectura: se cambia con activar()/desactivar()

    # ------------------------------------------------------------------
    # Disponibilidad
    # ------------------------------------------------------------------
    def activar(self) -> None:
        """Habilita el servicio; falla si ya estaba habilitado."""
        if self._disponible:  # No tiene sentido activar algo activo
            raise OperacionNoPermitidaError(f"El servicio {self.identificador} ya está habilitado.")
        self._disponible = True  # Cambia el estado

    def desactivar(self) -> None:
        """Deshabilita el servicio; falla si ya estaba deshabilitado."""
        if not self._disponible:  # No tiene sentido desactivar algo inactivo
            raise OperacionNoPermitidaError(f"El servicio {self.identificador} ya está deshabilitado.")
        self._disponible = False  # Cambia el estado

    def verificar_disponibilidad(self) -> None:
        """Lanza ServicioNoDisponibleError si el servicio no se puede usar."""
        if not self._disponible:  # Servicio deshabilitado
            raise ServicioNoDisponibleError(
                f"El servicio {self.identificador} ({self._nombre}) no está disponible en este momento."
            )

    def validar(self) -> None:
        """Implementa el método abstracto de Entidad: revalida los datos comunes."""
        self._validar_nombre(self._nombre)  # Lanza excepción si el nombre se corrompió
        self._validar_tarifa(self._tarifa)  # Lanza excepción si la tarifa se corrompió

    # ------------------------------------------------------------------
    # Métodos abstractos (cada servicio los implementa a su manera)
    # ------------------------------------------------------------------
    @abstractmethod
    def validar_parametros(self, duracion: Any, **detalles: Any) -> Dict[str, Any]:
        """Valida duración y detalles propios del servicio; devuelve los valores normalizados."""

    @abstractmethod
    def calcular_costo(self, duracion: Any, **detalles: Any) -> float:
        """Calcula el costo base del servicio (sin impuestos ni descuentos)."""

    @abstractmethod
    def describir(self) -> str:
        """Devuelve la descripción legible del servicio."""

    # ------------------------------------------------------------------
    # SOBRECARGA del cálculo de costos
    # ------------------------------------------------------------------
    # Python no permite definir varias funciones con el mismo nombre y
    # distintos parámetros (la última reemplazaría a las anteriores). La forma
    # propia de Python es:
    #   1) declarar cada variante con @overload (documenta las firmas y la
    #      revisan herramientas como mypy o el IDE), y
    #   2) escribir UNA implementación real que decide qué hacer según los
    #      parámetros opcionales que se reciban.
    # Variantes disponibles:
    #   calcular_costo_total(duracion)                          -> costo base
    #   calcular_costo_total(duracion, impuesto=0.19)           -> costo + impuesto
    #   calcular_costo_total(duracion, descuento=0.10)          -> costo - descuento
    #   calcular_costo_total(duracion, impuesto=.., descuento=..) -> descuento y luego impuesto
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
        """Implementación única de todas las variantes de cálculo de costo total.

        Orden de cálculo: costo base -> se resta el descuento -> se suma el impuesto.
        """
        self.verificar_disponibilidad()  # 1. El servicio debe estar disponible
        costo = self.calcular_costo(duracion, **detalles)  # 2. POLIMORFISMO: cada hija calcula distinto
        if descuento is not None:  # 3. Variante con descuento
            costo -= costo * self._validar_tasa(descuento, "descuento")  # Resta el porcentaje
        if impuesto is not None:  # 4. Variante con impuesto
            costo += costo * self._validar_tasa(impuesto, "impuesto")  # Suma el porcentaje
        if not math.isfinite(costo) or costo <= 0:  # 5. Control final de consistencia
            raise CalculoInconsistenteError(
                f"El costo calculado para {self.identificador} es inconsistente: {costo}."
            )
        return round(costo, 2)  # Se redondea a 2 decimales


# ======================================================================
# Servicio 1: Reserva de salas
# ======================================================================
class SalaReuniones(Servicio):
    """Reserva de salas de reuniones. Se cobra por hora."""

    PREFIJO = "SAL"  # Identificadores SAL-001, SAL-002...
    UNIDAD = "hora"  # Se cobra por hora
    UNIDAD_PLURAL = "horas"  # Plural para los mensajes
    DURACION_MINIMA = 1.0  # Mínimo 1 hora
    DURACION_MAXIMA = 12.0  # Máximo una jornada de 12 horas
    CAPACIDAD_MAXIMA = 200  # Tope de personas por sala
    RECARGO_PROYECTOR = 25_000  # Valor fijo por uso de proyector (por reserva)
    PARAMETROS_PERMITIDOS = frozenset({"asistentes"})  # Detalle extra que acepta esta sala

    def __init__(
        self, nombre: Any, tarifa: Any, capacidad: Any, incluye_proyector: Any = False, disponible: Any = True
    ) -> None:
        """Valida los datos propios de la sala y luego los comunes (clase padre)."""
        self._capacidad = self._convertir_entero(  # Número máximo de asistentes
            capacidad, "capacidad", 1, self.CAPACIDAD_MAXIMA, ServicioInvalidoError
        )
        self._incluye_proyector = self._validar_bandera(incluye_proyector, "incluye_proyector")  # ¿Tiene proyector?
        super().__init__(nombre, tarifa, disponible)  # HERENCIA: reutiliza las validaciones del padre

    @property
    def capacidad(self) -> int:
        """Capacidad máxima de personas de la sala."""
        return self._capacidad  # Solo lectura

    def validar_parametros(self, duracion: Any, **detalles: Any) -> Dict[str, Any]:
        """Sobrescribe: valida horas y, si se indica, el número de asistentes."""
        self._rechazar_parametros_desconocidos(detalles)  # Solo se acepta "asistentes"
        horas = self._validar_duracion(duracion)  # Entre 1 y 12 horas
        asistentes = detalles.get("asistentes")  # Puede no venir (es opcional)
        if asistentes is not None:  # Si viene, se valida
            asistentes = self._convertir_entero(asistentes, "asistentes", 1, 10_000, ParametroInvalidoError)
            if asistentes > self._capacidad:  # La sala no alcanza para tantas personas
                raise ServicioNoDisponibleError(
                    f"La sala {self.identificador} admite {self._capacidad} personas; se solicitaron {asistentes}."
                )
        return {"duracion": horas, "asistentes": asistentes}  # Parámetros normalizados

    def calcular_costo(self, duracion: Any, **detalles: Any) -> float:
        """Sobrescribe: tarifa por hora x horas + recargo fijo si incluye proyector."""
        parametros = self.validar_parametros(duracion, **detalles)  # Valida antes de calcular
        costo = self._tarifa * parametros["duracion"]  # Costo por tiempo de uso
        if self._incluye_proyector:  # Recargo por equipo audiovisual
            costo += self.RECARGO_PROYECTOR  # Se suma una sola vez por reserva
        return costo  # Costo base de la sala

    def describir(self) -> str:
        """Sobrescribe: descripción de la sala."""
        proyector = "con proyector" if self._incluye_proyector else "sin proyector"  # Texto del equipamiento
        estado = "disponible" if self._disponible else "NO disponible"  # Texto del estado
        return (
            f"Sala {self.identificador} | {self._nombre} | {self._capacidad} personas, {proyector} | "
            f"{formatear_moneda(self._tarifa)}/{self.UNIDAD} | {estado}"
        )


# ======================================================================
# Servicio 2: Alquiler de equipos
# ======================================================================
class AlquilerEquipo(Servicio):
    """Alquiler de equipos tecnológicos. Se cobra por día y por unidad."""

    PREFIJO = "EQP"  # Identificadores EQP-001, EQP-002...
    UNIDAD = "día"  # Se cobra por día
    UNIDAD_PLURAL = "días"  # Plural para los mensajes
    DURACION_MINIMA = 1.0  # Mínimo 1 día
    DURACION_MAXIMA = 30.0  # Máximo 30 días
    TIPOS_EQUIPO = ("portatil", "proyector", "camara", "sonido", "tablet")  # Catálogo permitido
    UNIDADES_MAXIMAS = 500  # Tope de inventario por servicio
    DIAS_TARIFA_SEMANAL = 7  # Desde 7 días se aplica tarifa preferencial
    DESCUENTO_SEMANAL = 0.10  # 10 % menos por alquiler semanal o más largo
    PARAMETROS_PERMITIDOS = frozenset({"cantidad"})  # Detalle extra que acepta este servicio

    def __init__(
        self, nombre: Any, tarifa: Any, tipo_equipo: Any, unidades: Any, disponible: Any = True
    ) -> None:
        """Valida el tipo de equipo y el inventario, y luego los datos comunes."""
        self._tipo_equipo = self._validar_tipo_equipo(tipo_equipo)  # Categoría del equipo
        self._unidades = self._convertir_entero(  # Unidades en inventario (0 = agotado)
            unidades, "unidades", 0, self.UNIDADES_MAXIMAS, ServicioInvalidoError
        )
        super().__init__(nombre, tarifa, disponible)  # HERENCIA: validaciones comunes

    @classmethod
    def _validar_tipo_equipo(cls, valor: Any) -> str:
        """Valida que el tipo de equipo pertenezca al catálogo."""
        if valor is None or (isinstance(valor, str) and not valor.strip()):  # Ausente o vacío
            raise ParametroFaltanteError("El tipo de equipo es obligatorio.")
        if not isinstance(valor, str):  # Debe ser texto
            raise ServicioInvalidoError("El tipo de equipo debe ser texto.")
        tipo = valor.strip().lower()  # Normaliza a minúsculas
        if tipo not in cls.TIPOS_EQUIPO:  # Debe estar en el catálogo
            raise ServicioInvalidoError(
                f"Tipo de equipo '{valor}' no válido. Opciones: {', '.join(cls.TIPOS_EQUIPO)}."
            )
        return tipo  # Tipo válido

    @property
    def tipo_equipo(self) -> str:
        """Categoría del equipo."""
        return self._tipo_equipo  # Solo lectura

    @property
    def unidades(self) -> int:
        """Unidades disponibles en inventario."""
        return self._unidades  # Solo lectura

    def verificar_disponibilidad(self) -> None:
        """Sobrescribe: además de estar habilitado, debe tener unidades en inventario."""
        super().verificar_disponibilidad()  # Reutiliza la verificación del padre
        if self._unidades == 0:  # Inventario agotado
            raise ServicioNoDisponibleError(f"El servicio {self.identificador} no tiene unidades en inventario.")

    def validar_parametros(self, duracion: Any, **detalles: Any) -> Dict[str, Any]:
        """Sobrescribe: valida días completos y la cantidad de equipos."""
        self._rechazar_parametros_desconocidos(detalles)  # Solo se acepta "cantidad"
        dias = self._validar_duracion(duracion)  # Entre 1 y 30 días
        if not dias.is_integer():  # Los equipos se alquilan por días completos
            raise ParametroInvalidoError(f"Los equipos se alquilan por días completos (recibido: {duracion}).")
        cantidad = self._convertir_entero(  # Por defecto se alquila 1 unidad
            detalles.get("cantidad", 1), "cantidad", 1, self.UNIDADES_MAXIMAS, ParametroInvalidoError
        )
        if cantidad > self._unidades:  # No hay suficientes equipos
            raise ServicioNoDisponibleError(
                f"Solo hay {self._unidades} unidades de {self.identificador}; se solicitaron {cantidad}."
            )
        return {"duracion": int(dias), "cantidad": cantidad}  # Parámetros normalizados

    def calcular_costo(self, duracion: Any, **detalles: Any) -> float:
        """Sobrescribe: tarifa diaria x días x unidades, con tarifa semanal preferencial."""
        parametros = self.validar_parametros(duracion, **detalles)  # Valida antes de calcular
        costo = self._tarifa * parametros["duracion"] * parametros["cantidad"]  # Costo bruto
        if parametros["duracion"] >= self.DIAS_TARIFA_SEMANAL:  # Alquiler de 7 días o más
            costo -= costo * self.DESCUENTO_SEMANAL  # Se aplica la tarifa preferencial
        return costo  # Costo base del alquiler

    def describir(self) -> str:
        """Sobrescribe: descripción del alquiler de equipos."""
        estado = "disponible" if self._disponible else "NO disponible"  # Texto del estado
        return (
            f"Equipo {self.identificador} | {self._nombre} | tipo: {self._tipo_equipo}, "
            f"{self._unidades} unidades | {formatear_moneda(self._tarifa)}/{self.UNIDAD} por unidad | {estado}"
        )


# ======================================================================
# Servicio 3: Asesorías especializadas
# ======================================================================
class AsesoriaEspecializada(Servicio):
    """Asesoría con un consultor. Se cobra por hora según su nivel y la modalidad."""

    PREFIJO = "ASE"  # Identificadores ASE-001, ASE-002...
    UNIDAD = "hora"  # Se cobra por hora
    UNIDAD_PLURAL = "horas"  # Plural para los mensajes
    DURACION_MINIMA = 1.0  # Mínimo 1 hora
    DURACION_MAXIMA = 8.0  # Máximo una jornada laboral
    ESPECIALIDADES = ("software", "redes", "seguridad", "datos", "nube")  # Áreas de asesoría
    FACTORES_NIVEL = {"junior": 1.0, "senior": 1.5, "experto": 2.0}  # Multiplicador por experiencia
    MODALIDADES = ("virtual", "presencial")  # Formas de prestar la asesoría
    RECARGO_PRESENCIAL = 0.15  # 15 % adicional por desplazamiento del consultor
    PARAMETROS_PERMITIDOS = frozenset({"modalidad"})  # Detalle extra que acepta este servicio

    def __init__(
        self, nombre: Any, tarifa: Any, especialidad: Any, nivel: Any = "senior", disponible: Any = True
    ) -> None:
        """Valida especialidad y nivel del consultor, y luego los datos comunes."""
        self._especialidad = self._validar_opcion(especialidad, "especialidad", self.ESPECIALIDADES)  # Área
        self._nivel = self._validar_opcion(nivel, "nivel", tuple(self.FACTORES_NIVEL))  # Experiencia
        super().__init__(nombre, tarifa, disponible)  # HERENCIA: validaciones comunes

    @staticmethod
    def _validar_opcion(valor: Any, campo: str, opciones: tuple) -> str:
        """Valida que un texto pertenezca a una lista de opciones permitidas."""
        if valor is None or (isinstance(valor, str) and not valor.strip()):  # Ausente o vacío
            raise ParametroFaltanteError(f"El campo '{campo}' es obligatorio.")
        if not isinstance(valor, str) or valor.strip().lower() not in opciones:  # Fuera del catálogo
            raise ServicioInvalidoError(f"'{valor}' no es válido para '{campo}'. Opciones: {', '.join(opciones)}.")
        return valor.strip().lower()  # Opción normalizada

    @property
    def especialidad(self) -> str:
        """Área de la asesoría."""
        return self._especialidad  # Solo lectura

    @property
    def nivel(self) -> str:
        """Nivel de experiencia del consultor."""
        return self._nivel  # Solo lectura

    def validar_parametros(self, duracion: Any, **detalles: Any) -> Dict[str, Any]:
        """Sobrescribe: valida horas y modalidad (virtual o presencial)."""
        self._rechazar_parametros_desconocidos(detalles)  # Solo se acepta "modalidad"
        horas = self._validar_duracion(duracion)  # Entre 1 y 8 horas
        modalidad = detalles.get("modalidad", "virtual")  # Por defecto es virtual
        if not isinstance(modalidad, str) or modalidad.strip().lower() not in self.MODALIDADES:  # Opción inválida
            raise ParametroInvalidoError(
                f"Modalidad '{modalidad}' no válida. Opciones: {', '.join(self.MODALIDADES)}."
            )
        return {"duracion": horas, "modalidad": modalidad.strip().lower()}  # Parámetros normalizados

    def calcular_costo(self, duracion: Any, **detalles: Any) -> float:
        """Sobrescribe: tarifa x horas x factor de nivel, con recargo si es presencial."""
        parametros = self.validar_parametros(duracion, **detalles)  # Valida antes de calcular
        costo = self._tarifa * parametros["duracion"] * self.FACTORES_NIVEL[self._nivel]  # Costo por experiencia
        if parametros["modalidad"] == "presencial":  # El consultor se desplaza
            costo += costo * self.RECARGO_PRESENCIAL  # Se suma el recargo
        return costo  # Costo base de la asesoría

    def describir(self) -> str:
        """Sobrescribe: descripción de la asesoría."""
        estado = "disponible" if self._disponible else "NO disponible"  # Texto del estado
        return (
            f"Asesoría {self.identificador} | {self._nombre} | {self._especialidad}, nivel {self._nivel} | "
            f"{formatear_moneda(self._tarifa)}/{self.UNIDAD} base | {estado}"
        )
