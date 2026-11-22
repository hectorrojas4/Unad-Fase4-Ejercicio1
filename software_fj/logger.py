"""
Módulo: logger.py
Proyecto: Sistema Integral de Gestión de Clientes, Servicios y Reservas - Software FJ
Curso: Programación (213023) - UNAD - Fase 4

Centraliza el registro de eventos y errores en el archivo logs/sistema.log.

El enunciado no permite bases de datos; el único archivo que usa el sistema
es este log, donde quedan todos los eventos relevantes (registros, cotizaciones,
cambios de estado) y todos los errores, incluida la cadena de causas cuando
una excepción se encadenó con `raise ... from ...`.
"""

import logging  # Módulo estándar de Python para registrar mensajes con niveles
import sys  # Da acceso a la salida de errores (stderr) si el archivo no se puede abrir
from pathlib import Path  # Maneja rutas de forma independiente del sistema operativo

RAIZ_PROYECTO = Path(__file__).resolve().parent.parent  # Carpeta raíz del proyecto
RUTA_LOGS = RAIZ_PROYECTO / "logs"  # Carpeta logs/ en la raíz del proyecto
ARCHIVO_LOG = RUTA_LOGS / "sistema.log"  # Ruta completa del archivo de registro
RUTA_RELATIVA_LOG = ARCHIVO_LOG.relative_to(RAIZ_PROYECTO).as_posix()  # "logs/sistema.log" (no expone rutas del equipo)
NOMBRE_LOGGER = "SoftwareFJ"  # Nombre único del logger de la aplicación
FORMATO = "%(asctime)s | %(levelname)-8s | %(message)s"  # Fecha | nivel | mensaje
FORMATO_FECHA = "%Y-%m-%d %H:%M:%S"  # Ejemplo: 2026-11-21 19:30:05


def obtener_logger() -> logging.Logger:
    """Devuelve el logger de la aplicación, configurándolo solo la primera vez."""
    logger = logging.getLogger(NOMBRE_LOGGER)  # Obtiene (o crea) el logger con ese nombre
    if logger.handlers:  # Si ya tiene manejadores, ya fue configurado antes
        return logger  # Se reutiliza tal cual para no duplicar líneas en el archivo

    logger.setLevel(logging.INFO)  # Registra desde nivel INFO hacia arriba (INFO, WARNING, ERROR, CRITICAL)
    logger.propagate = False  # Evita que los mensajes se repitan en el logger raíz de Python
    formateador = logging.Formatter(FORMATO, FORMATO_FECHA)  # Define cómo se verá cada línea

    try:  # Intenta preparar el archivo de log
        RUTA_LOGS.mkdir(parents=True, exist_ok=True)  # Crea la carpeta logs/ si no existe
        manejador = logging.FileHandler(ARCHIVO_LOG, encoding="utf-8")  # Abre el archivo en modo agregar
    except OSError as error:  # Sin permisos, disco lleno, ruta inválida, etc.
        manejador = logging.StreamHandler(sys.stderr)  # Plan B: escribir los registros en consola
        print(  # Avisa al usuario sin detener la aplicación
            f"[ADVERTENCIA] No se pudo abrir {RUTA_RELATIVA_LOG} ({error}). "
            "Los registros se mostrarán en la consola.",
            file=sys.stderr,  # Se envía por la salida de errores
        )
        destino = "consola (stderr)"  # Recuerda a dónde quedaron yendo los registros
    else:  # Solo se ejecuta si el bloque try terminó sin errores
        destino = RUTA_RELATIVA_LOG  # El archivo se abrió correctamente (se muestra la ruta relativa)

    manejador.setFormatter(formateador)  # Aplica el formato definido al manejador elegido
    logger.addHandler(manejador)  # Conecta el manejador al logger
    logger.info(f"Registro de eventos iniciado. Destino: {destino}")  # Primera línea de cada ejecución
    return logger  # Entrega el logger listo para usar


def registrar_evento(mensaje: str) -> None:
    """Registra un evento normal del sistema (nivel INFO)."""
    obtener_logger().info(mensaje)  # Escribe el mensaje como información


def registrar_advertencia(mensaje: str) -> None:
    """Registra una situación anómala pero controlada (nivel WARNING)."""
    obtener_logger().warning(mensaje)  # Escribe el mensaje como advertencia


def registrar_error(contexto: str, error: BaseException) -> None:
    """Registra un error controlado y toda su cadena de causas (nivel ERROR).

    Args:
        contexto: descripción breve de lo que se intentaba hacer.
        error: la excepción capturada.
    """
    logger = obtener_logger()  # Obtiene el logger configurado
    logger.error(f"{contexto} -> {type(error).__name__}: {error}")  # Línea principal del error
    causa = error.__cause__  # Causa original si se usó "raise ... from ..."
    while causa is not None:  # Recorre toda la cadena de excepciones encadenadas
        logger.error(f"    causa original -> {type(causa).__name__}: {causa}")  # Registra cada causa
        causa = causa.__cause__  # Avanza a la causa anterior (si existe)


def registrar_critico(contexto: str, error: BaseException) -> None:
    """Registra un error imprevisto con su traza completa (nivel CRITICAL)."""
    obtener_logger().critical(  # Nivel más alto: errores que no se esperaban
        f"{contexto} -> {type(error).__name__}: {error}",  # Mensaje resumido
        exc_info=error,  # Incluye el traceback completo para poder depurarlo
    )
