"""
Módulo: logger.py
Proyecto: Sistema Integral de Gestión de Clientes, Servicios y Reservas - Software FJ
Curso: Programación (213023) - UNAD - Fase 4

Registra los eventos y errores del sistema en el archivo logs/sistema.log.
"""

import logging
import sys
from pathlib import Path

RAIZ_PROYECTO = Path(__file__).resolve().parent.parent
RUTA_LOGS = RAIZ_PROYECTO / "logs"
ARCHIVO_LOG = RUTA_LOGS / "sistema.log"
RUTA_RELATIVA_LOG = ARCHIVO_LOG.relative_to(RAIZ_PROYECTO).as_posix()
NOMBRE_LOGGER = "SoftwareFJ"
FORMATO = "%(asctime)s | %(levelname)-8s | %(message)s"
FORMATO_FECHA = "%Y-%m-%d %H:%M:%S"


def obtener_logger() -> logging.Logger:
    """Devuelve el logger del sistema y lo configura la primera vez que se usa."""
    logger = logging.getLogger(NOMBRE_LOGGER)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    logger.propagate = False
    formateador = logging.Formatter(FORMATO, FORMATO_FECHA)

    try:
        RUTA_LOGS.mkdir(parents=True, exist_ok=True)
        manejador = logging.FileHandler(ARCHIVO_LOG, encoding="utf-8")
    except OSError as error:  # Si no se puede crear la carpeta o abrir el archivo del log
        manejador = logging.StreamHandler(sys.stderr)
        print(
            f"[ADVERTENCIA] No se pudo abrir {RUTA_RELATIVA_LOG} ({error}). "
            "Los registros se mostrarán en la consola.",
            file=sys.stderr,
        )
        destino = "consola (stderr)"
    else:
        destino = RUTA_RELATIVA_LOG

    manejador.setFormatter(formateador)
    logger.addHandler(manejador)
    logger.info(f"Registro de eventos iniciado. Destino: {destino}")
    return logger


def registrar_evento(mensaje: str) -> None:
    obtener_logger().info(mensaje)


def registrar_advertencia(mensaje: str) -> None:
    obtener_logger().warning(mensaje)


def registrar_error(contexto: str, error: BaseException) -> None:
    """Registra un error controlado junto con sus causas originales."""
    logger = obtener_logger()
    logger.error(f"{contexto} -> {type(error).__name__}: {error}")
    causa = error.__cause__
    while causa is not None:
        logger.error(f"    causa original -> {type(causa).__name__}: {causa}")
        causa = causa.__cause__


def registrar_critico(contexto: str, error: BaseException) -> None:
    obtener_logger().critical(
        f"{contexto} -> {type(error).__name__}: {error}",
        exc_info=error,
    )
