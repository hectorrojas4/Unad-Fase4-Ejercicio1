"""
Módulo: cliente.py
Proyecto: Sistema Integral de Gestión de Clientes, Servicios y Reservas - Software FJ
Curso: Programación (213023) - UNAD - Fase 4

Contiene la clase Cliente, que hereda de Entidad.

Aplica ENCAPSULACIÓN: los datos personales se guardan en atributos privados
(con doble guion bajo) y solo se accede a ellos mediante propiedades que
validan cada valor antes de aceptarlo.
"""

import re  # Expresiones regulares para validar formatos (nombre, correo)
from typing import Any, Optional  # Anotaciones de tipo

from .entidad import Entidad  # Clase abstracta padre
from .excepciones import ClienteInvalidoError, ParametroFaltanteError  # Errores propios

# Solo letras (con tildes y ñ) separadas por un único espacio
PATRON_NOMBRE = re.compile(r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+(?: [A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+)*$")
# usuario@dominio.ext, con subdominios opcionales (ej.: ana.r@correo.com.co)
PATRON_CORREO = re.compile(r"^[\w.+-]+@[\w-]+(?:\.[\w-]+)+$")
# Solo dígitos del 0 al 9 (evita aceptar caracteres Unicode raros como "²")
PATRON_DIGITOS = re.compile(r"^[0-9]+$")


class Cliente(Entidad):
    """Cliente de Software FJ con datos personales validados y encapsulados."""

    PREFIJO = "CLI"  # Los identificadores de clientes serán CLI-001, CLI-002...
    LONGITUD_NOMBRE = (3, 60)  # Mínimo y máximo de caracteres del nombre
    LONGITUD_DOCUMENTO = (6, 10)  # Rango de dígitos de una cédula colombiana
    LONGITUD_CORREO_MAXIMA = 80  # Límite razonable para un correo
    LONGITUD_TELEFONO = 10  # Números colombianos: 10 dígitos (celular o fijo)
    INICIOS_TELEFONO = ("3", "6")  # 3 = celular, 6 = fijo (marcación nacional)

    def __init__(self, nombre: Any, documento: Any, correo: Any, telefono: Any) -> None:
        """Crea un cliente validando todos sus datos ANTES de asignarle identificador.

        Si algún dato es inválido se lanza la excepción correspondiente y el
        cliente no llega a crearse (no se gasta un consecutivo).
        """
        self.__nombre = self.normalizar_nombre(nombre)  # Atributo privado: _Cliente__nombre
        self.__documento = self.normalizar_documento(documento)  # Atributo privado, sin setter
        self.__correo = self.normalizar_correo(correo)  # Atributo privado con setter validado
        self.__telefono = self.normalizar_telefono(telefono)  # Atributo privado con setter validado
        super().__init__(self.PREFIJO)  # Todo es válido: ahora sí se asigna el identificador

    # ------------------------------------------------------------------
    # Validadores (métodos estáticos: no dependen de un cliente concreto)
    # ------------------------------------------------------------------
    @staticmethod
    def _exigir(valor: Any, campo: str) -> None:
        """Lanza ParametroFaltanteError si el valor viene vacío o como None."""
        if valor is None or (isinstance(valor, str) and not valor.strip()):  # None o texto en blanco
            raise ParametroFaltanteError(  # Dato obligatorio ausente
                f"El campo '{campo}' es obligatorio para el cliente."
            )

    @classmethod
    def normalizar_nombre(cls, valor: Any) -> str:
        """Valida el nombre y lo devuelve normalizado (espacios simples, tipo Título)."""
        cls._exigir(valor, "nombre")  # No puede faltar
        if not isinstance(valor, str):  # Debe ser texto
            raise ClienteInvalidoError(f"El nombre debe ser texto (recibido: {type(valor).__name__}).")
        texto = " ".join(valor.split())  # Elimina espacios repetidos y en los extremos
        minimo, maximo = cls.LONGITUD_NOMBRE  # Desempaqueta los límites de longitud
        if not minimo <= len(texto) <= maximo:  # Verifica la longitud
            raise ClienteInvalidoError(f"El nombre debe tener entre {minimo} y {maximo} caracteres.")
        if not PATRON_NOMBRE.match(texto):  # Verifica que solo tenga letras y espacios
            raise ClienteInvalidoError(f"El nombre '{texto}' solo puede contener letras y espacios.")
        return texto.title()  # "ana maría" -> "Ana María"

    @classmethod
    def normalizar_documento(cls, valor: Any) -> str:
        """Valida el número de documento y lo devuelve solo con dígitos."""
        cls._exigir(valor, "documento")  # No puede faltar
        if isinstance(valor, bool) or not isinstance(valor, (str, int)):  # bool es subclase de int: se rechaza
            raise ClienteInvalidoError("El documento debe ser texto o número entero.")
        texto = str(valor).replace(".", "").replace(" ", "")  # Acepta "1.036.456.789" -> "1036456789"
        if not PATRON_DIGITOS.match(texto):  # Solo puede contener dígitos
            raise ClienteInvalidoError(f"El documento '{valor}' solo puede contener números.")
        minimo, maximo = cls.LONGITUD_DOCUMENTO  # Límites de longitud
        if not minimo <= len(texto) <= maximo:  # Verifica la cantidad de dígitos
            raise ClienteInvalidoError(f"El documento debe tener entre {minimo} y {maximo} dígitos.")
        return texto  # Documento limpio

    @classmethod
    def normalizar_correo(cls, valor: Any) -> str:
        """Valida el correo electrónico y lo devuelve en minúsculas."""
        cls._exigir(valor, "correo")  # No puede faltar
        if not isinstance(valor, str):  # Debe ser texto
            raise ClienteInvalidoError("El correo debe ser texto.")
        texto = valor.strip().lower()  # Quita espacios y pasa a minúsculas
        if len(texto) > cls.LONGITUD_CORREO_MAXIMA:  # Evita valores absurdamente largos
            raise ClienteInvalidoError(f"El correo supera {cls.LONGITUD_CORREO_MAXIMA} caracteres.")
        if not PATRON_CORREO.match(texto):  # Verifica el formato usuario@dominio.ext
            raise ClienteInvalidoError(f"El correo '{valor}' no tiene un formato válido.")
        return texto  # Correo normalizado

    @classmethod
    def normalizar_telefono(cls, valor: Any) -> str:
        """Valida el teléfono colombiano (10 dígitos, inicia en 3 o 6)."""
        cls._exigir(valor, "telefono")  # No puede faltar
        if isinstance(valor, bool) or not isinstance(valor, (str, int)):  # Tipos aceptados: texto o entero
            raise ClienteInvalidoError("El teléfono debe ser texto o número entero.")
        limpio = str(valor).replace(" ", "").replace("-", "")  # Acepta "300 123-4567"
        try:  # Intenta convertir a número para confirmar que es numérico
            int(limpio)  # Si tiene letras, int() lanza ValueError
        except ValueError as error:  # Se captura el error técnico de Python...
            raise ClienteInvalidoError(  # ...y se ENCADENA con un error propio del dominio
                f"El teléfono '{valor}' contiene caracteres no numéricos."
            ) from error  # "from error" conserva la causa original (encadenamiento)
        if not PATRON_DIGITOS.match(limpio):  # int() acepta "+" o "_": aquí se exigen solo dígitos
            raise ClienteInvalidoError(f"El teléfono '{valor}' solo puede contener dígitos.")
        if len(limpio) != cls.LONGITUD_TELEFONO or not limpio.startswith(cls.INICIOS_TELEFONO):
            raise ClienteInvalidoError(  # Longitud o prefijo incorrectos
                f"El teléfono '{valor}' debe tener {cls.LONGITUD_TELEFONO} dígitos "
                "e iniciar por 3 (celular) o 6 (fijo)."
            )
        return limpio  # Teléfono limpio

    # ------------------------------------------------------------------
    # Propiedades (acceso controlado a los atributos privados)
    # ------------------------------------------------------------------
    @property
    def nombre(self) -> str:
        """Nombre completo del cliente."""
        return self.__nombre  # Lectura del atributo privado

    @nombre.setter
    def nombre(self, valor: Any) -> None:
        """Permite corregir el nombre, siempre pasando por la validación."""
        self.__nombre = self.normalizar_nombre(valor)  # Solo se asigna si es válido

    @property
    def documento(self) -> str:
        """Documento del cliente. Es de solo lectura: identifica a la persona."""
        return self.__documento  # No existe setter: no se puede cambiar después de crearlo

    @property
    def documento_enmascarado(self) -> str:
        """Documento oculto parcialmente para mostrarlo en pantalla (protección de datos)."""
        return "*" * (len(self.__documento) - 4) + self.__documento[-4:]  # Ej.: ******6789

    @property
    def correo(self) -> str:
        """Correo electrónico del cliente."""
        return self.__correo  # Lectura del atributo privado

    @correo.setter
    def correo(self, valor: Any) -> None:
        """Cambia el correo validándolo primero."""
        self.__correo = self.normalizar_correo(valor)  # Solo se asigna si es válido

    @property
    def telefono(self) -> str:
        """Teléfono del cliente."""
        return self.__telefono  # Lectura del atributo privado

    @telefono.setter
    def telefono(self, valor: Any) -> None:
        """Cambia el teléfono validándolo primero."""
        self.__telefono = self.normalizar_telefono(valor)  # Solo se asigna si es válido

    # ------------------------------------------------------------------
    # Comportamiento
    # ------------------------------------------------------------------
    def actualizar_contacto(self, correo: Optional[Any] = None, telefono: Optional[Any] = None) -> None:
        """Actualiza correo y/o teléfono en modo "todo o nada".

        Primero se validan los valores nuevos; solo si TODOS son válidos se
        asignan. Así el cliente nunca queda con datos a medio actualizar.
        """
        if correo is None and telefono is None:  # Debe llegar al menos un dato
            raise ParametroFaltanteError("Indique al menos el correo o el teléfono a actualizar.")
        nuevo_correo = self.normalizar_correo(correo) if correo is not None else self.__correo  # Valida o conserva
        nuevo_telefono = self.normalizar_telefono(telefono) if telefono is not None else self.__telefono  # Valida o conserva
        self.__correo, self.__telefono = nuevo_correo, nuevo_telefono  # Asignación conjunta (todo o nada)

    def validar(self) -> None:
        """Implementa el método abstracto: revalida todos los datos del cliente."""
        self.normalizar_nombre(self.__nombre)  # Lanza excepción si el nombre se corrompió
        self.normalizar_documento(self.__documento)  # Ídem para el documento
        self.normalizar_correo(self.__correo)  # Ídem para el correo
        self.normalizar_telefono(self.__telefono)  # Ídem para el teléfono

    def describir(self) -> str:
        """Implementa el método abstracto: descripción legible del cliente."""
        return (  # Se muestra el documento enmascarado para proteger el dato personal
            f"Cliente {self.identificador} | {self.__nombre} | Doc. {self.documento_enmascarado} | "
            f"{self.__correo} | Tel. {self.__telefono}"
        )
