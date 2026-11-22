"""
Módulo: cliente.py
Proyecto: Sistema Integral de Gestión de Clientes, Servicios y Reservas - Software FJ
Curso: Programación (213023) - UNAD - Fase 4

Contiene la clase Cliente, que guarda y valida los datos personales de cada cliente.
"""

import re
from typing import Any, Optional

from .entidad import Entidad
from .excepciones import ClienteInvalidoError, ParametroFaltanteError

PATRON_NOMBRE = re.compile(r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+(?: [A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+)*$")
PATRON_CORREO = re.compile(r"^[\w.+-]+@[\w-]+(?:\.[\w-]+)+$")
PATRON_DIGITOS = re.compile(r"^[0-9]+$")


class Cliente(Entidad):
    """Cliente de Software FJ con sus datos personales validados."""

    PREFIJO = "CLI"
    LONGITUD_NOMBRE = (3, 60)
    LONGITUD_DOCUMENTO = (6, 10)
    LONGITUD_CORREO_MAXIMA = 80
    LONGITUD_TELEFONO = 10
    INICIOS_TELEFONO = ("3", "6")

    def __init__(self, nombre: Any, documento: Any, correo: Any, telefono: Any) -> None:
        self.__nombre = self.normalizar_nombre(nombre)
        self.__documento = self.normalizar_documento(documento)
        self.__correo = self.normalizar_correo(correo)
        self.__telefono = self.normalizar_telefono(telefono)
        super().__init__(self.PREFIJO)

    @staticmethod
    def _exigir(valor: Any, campo: str) -> None:
        if valor is None or (isinstance(valor, str) and not valor.strip()):
            raise ParametroFaltanteError(
                f"El campo '{campo}' es obligatorio para el cliente."
            )

    @classmethod
    def normalizar_nombre(cls, valor: Any) -> str:
        """Valida el nombre y lo devuelve con espacios simples y mayúscula inicial."""
        cls._exigir(valor, "nombre")
        if not isinstance(valor, str):
            raise ClienteInvalidoError(f"El nombre debe ser texto (recibido: {type(valor).__name__}).")
        texto = " ".join(valor.split())
        minimo, maximo = cls.LONGITUD_NOMBRE
        if not minimo <= len(texto) <= maximo:
            raise ClienteInvalidoError(f"El nombre debe tener entre {minimo} y {maximo} caracteres.")
        if not PATRON_NOMBRE.match(texto):
            raise ClienteInvalidoError(f"El nombre '{texto}' solo puede contener letras y espacios.")
        return texto.title()

    @classmethod
    def normalizar_documento(cls, valor: Any) -> str:
        """Valida el documento y lo devuelve solo con dígitos."""
        cls._exigir(valor, "documento")
        if isinstance(valor, bool) or not isinstance(valor, (str, int)):
            raise ClienteInvalidoError("El documento debe ser texto o número entero.")
        texto = str(valor).replace(".", "").replace(" ", "")
        if not PATRON_DIGITOS.match(texto):
            raise ClienteInvalidoError(f"El documento '{valor}' solo puede contener números.")
        minimo, maximo = cls.LONGITUD_DOCUMENTO
        if not minimo <= len(texto) <= maximo:
            raise ClienteInvalidoError(f"El documento debe tener entre {minimo} y {maximo} dígitos.")
        return texto

    @classmethod
    def normalizar_correo(cls, valor: Any) -> str:
        """Valida el correo electrónico y lo devuelve en minúsculas."""
        cls._exigir(valor, "correo")
        if not isinstance(valor, str):
            raise ClienteInvalidoError("El correo debe ser texto.")
        texto = valor.strip().lower()
        if len(texto) > cls.LONGITUD_CORREO_MAXIMA:
            raise ClienteInvalidoError(f"El correo supera {cls.LONGITUD_CORREO_MAXIMA} caracteres.")
        if not PATRON_CORREO.match(texto):
            raise ClienteInvalidoError(f"El correo '{valor}' no tiene un formato válido.")
        return texto

    @classmethod
    def normalizar_telefono(cls, valor: Any) -> str:
        """Valida el teléfono: 10 dígitos que empiezan por 3 o 6."""
        cls._exigir(valor, "telefono")
        if isinstance(valor, bool) or not isinstance(valor, (str, int)):
            raise ClienteInvalidoError("El teléfono debe ser texto o número entero.")
        limpio = str(valor).replace(" ", "").replace("-", "")
        try:
            int(limpio)
        except ValueError as error:  # Si el teléfono no es numérico
            raise ClienteInvalidoError(
                f"El teléfono '{valor}' contiene caracteres no numéricos."
            ) from error
        if not PATRON_DIGITOS.match(limpio):
            raise ClienteInvalidoError(f"El teléfono '{valor}' solo puede contener dígitos.")
        if len(limpio) != cls.LONGITUD_TELEFONO or not limpio.startswith(cls.INICIOS_TELEFONO):
            raise ClienteInvalidoError(
                f"El teléfono '{valor}' debe tener {cls.LONGITUD_TELEFONO} dígitos "
                "e iniciar por 3 (celular) o 6 (fijo)."
            )
        return limpio

    @property
    def nombre(self) -> str:
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: Any) -> None:
        self.__nombre = self.normalizar_nombre(valor)

    @property
    def documento(self) -> str:
        return self.__documento

    @property
    def documento_enmascarado(self) -> str:
        return "*" * (len(self.__documento) - 4) + self.__documento[-4:]

    @property
    def correo(self) -> str:
        return self.__correo

    @correo.setter
    def correo(self, valor: Any) -> None:
        self.__correo = self.normalizar_correo(valor)

    @property
    def telefono(self) -> str:
        return self.__telefono

    @telefono.setter
    def telefono(self, valor: Any) -> None:
        self.__telefono = self.normalizar_telefono(valor)

    def actualizar_contacto(self, correo: Optional[Any] = None, telefono: Optional[Any] = None) -> None:
        """Actualiza el correo y/o el teléfono solo si los datos nuevos son válidos."""
        if correo is None and telefono is None:
            raise ParametroFaltanteError("Indique al menos el correo o el teléfono a actualizar.")
        nuevo_correo = self.normalizar_correo(correo) if correo is not None else self.__correo
        nuevo_telefono = self.normalizar_telefono(telefono) if telefono is not None else self.__telefono
        self.__correo, self.__telefono = nuevo_correo, nuevo_telefono

    def validar(self) -> None:
        """Vuelve a validar todos los datos del cliente."""
        self.normalizar_nombre(self.__nombre)
        self.normalizar_documento(self.__documento)
        self.normalizar_correo(self.__correo)
        self.normalizar_telefono(self.__telefono)

    def describir(self) -> str:
        return (
            f"Cliente {self.identificador} | {self.__nombre} | Doc. {self.documento_enmascarado} | "
            f"{self.__correo} | Tel. {self.__telefono}"
        )
