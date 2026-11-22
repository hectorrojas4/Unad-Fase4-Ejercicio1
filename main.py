"""
Programa principal: main.py
Proyecto: Sistema Integral de Gestión de Clientes, Servicios y Reservas - Software FJ
Curso: Programación (213023) - UNAD - Fase 4

Simula operaciones válidas e inválidas sobre el sistema para mostrar que los
errores se manejan sin que el programa se detenga.
"""

import sys
from typing import Any, Callable, Dict, List, Tuple

from software_fj import Entidad, GestorSoftwareFJ, IVA_COLOMBIA, SoftwareFJError, formatear_moneda
from software_fj.logger import RUTA_RELATIVA_LOG, registrar_advertencia, registrar_critico, registrar_evento

Operacion = Tuple[str, Callable[[], Any]]

LINEA = "-" * 78


def mostrar_resultado(resultado: Any) -> None:
    if isinstance(resultado, Entidad):
        print(f"   {resultado.describir()}")
    elif isinstance(resultado, float):
        print(f"   Total: {formatear_moneda(resultado)}")
    elif resultado is not None:
        print(f"   {resultado}")


def ejecutar_operacion(numero: int, descripcion: str, accion: Callable[[], Any], contador: Dict[str, int]) -> None:
    """Ejecuta una operación y maneja sus errores para que el programa siga funcionando."""
    print(f"\n[{numero:02d}] {descripcion}")
    try:
        resultado = accion()
    except SoftwareFJError as error:  # Errores previstos del sistema, como datos inválidos
        contador["fallidas"] += 1
        print(f"   [ERROR CONTROLADO] {type(error).__name__}: {error}")
        if error.__cause__ is not None:
            causa = error.__cause__
            print(f"   -> Causa original: {type(causa).__name__}: {causa}")
        registrar_advertencia(
            f"Operación {numero:02d} '{descripcion}' falló de forma controlada -> {type(error).__name__}: {error}"
        )
    except Exception as error:  # Cualquier otro error que no se esperaba
        contador["imprevistas"] += 1
        print(f"   [ERROR IMPREVISTO] {type(error).__name__}: {error}")
        registrar_critico(f"Operación {numero:02d} '{descripcion}' produjo un error imprevisto", error)
    else:
        contador["exitosas"] += 1
        print("   [OK]")
        mostrar_resultado(resultado)
        registrar_evento(f"Operación {numero:02d} '{descripcion}' completada.")
    finally:
        print(f"   {LINEA[:40]}")


def construir_operaciones(gestor: GestorSoftwareFJ) -> List[Operacion]:
    """Arma la lista de operaciones a simular, con casos válidos e inválidos."""
    return [
        ("Registrar cliente válido: Ana María Restrepo",
         lambda: gestor.registrar_cliente("ana maría  restrepo", "1036456789", "Ana.Restrepo@Correo.com", "300 123 4567")),
        ("Registrar cliente válido: Carlos Andrés Gómez",
         lambda: gestor.registrar_cliente("Carlos Andrés Gómez", 98765432, "cgomez@softwarefj.co", "6044441234")),
        ("Registrar cliente con correo inválido",
         lambda: gestor.registrar_cliente("Laura Pérez", "52111222", "laura.perez@@correo", "3201112233")),
        ("Registrar cliente con documento duplicado (mismo documento con puntos)",
         lambda: gestor.registrar_cliente("Ana Restrepo", "1.036.456.789", "otra@correo.com", "3001112233")),
        ("Registrar cliente sin nombre (parámetro faltante)",
         lambda: gestor.registrar_cliente("   ", "71222333", "sin.nombre@correo.com", "3104445566")),
        ("Registrar cliente con teléfono no numérico (excepción encadenada)",
         lambda: gestor.registrar_cliente("Pedro Ruiz", "80123456", "pruiz@correo.com", "300-ABC-4567")),
        ("Actualizar el correo de un cliente existente (encapsulación)",
         lambda: gestor.actualizar_contacto_cliente("CLI-001", correo="ana.mr@nuevo.com")),
        ("Buscar un cliente que no existe",
         lambda: gestor.buscar_cliente("CLI-999")),
        ("Crear servicio válido: sala de reuniones",
         lambda: gestor.registrar_servicio("sala", nombre="Sala Innovación", tarifa=60000,
                                           capacidad=12, incluye_proyector=True)),
        ("Crear servicio válido: alquiler de equipos",
         lambda: gestor.registrar_servicio("equipo", nombre="Portátiles de alto rendimiento",
                                           tarifa=85000, tipo_equipo="Portatil", unidades=5)),
        ("Crear servicio válido: asesoría especializada",
         lambda: gestor.registrar_servicio("asesoria", nombre="Asesoría en ciberseguridad",
                                           tarifa=120000, especialidad="seguridad", nivel="experto")),
        ("Crear servicio con tarifa negativa",
         lambda: gestor.registrar_servicio("sala", nombre="Sala Básica", tarifa=-5000, capacidad=4)),
        ("Crear servicio de un tipo que no existe",
         lambda: gestor.registrar_servicio("transporte", nombre="Van ejecutiva", tarifa=200000)),
        ("Crear servicio sin parámetros obligatorios (excepción encadenada)",
         lambda: gestor.registrar_servicio("equipo", nombre="Proyectores", tarifa=40000)),
        ("Crear servicio con capacidad no numérica (excepción encadenada)",
         lambda: gestor.registrar_servicio("sala", nombre="Sala Norte", tarifa=50000, capacidad="doce")),
        ("Cotizar sala 3 horas - variante: costo base",
         lambda: gestor.cotizar_servicio("SAL-001", 3)),
        ("Cotizar sala 3 horas - variante: con IVA",
         lambda: gestor.cotizar_servicio("SAL-001", 3, impuesto=IVA_COLOMBIA)),
        ("Cotizar 2 portátiles por 7 días - variante: con descuento del 10 %",
         lambda: gestor.cotizar_servicio("EQP-001", 7, descuento=0.10, cantidad=2)),
        ("Cotizar asesoría presencial 4 horas - variante: con descuento e IVA",
         lambda: gestor.cotizar_servicio("ASE-001", 4, impuesto=IVA_COLOMBIA, descuento=0.05, modalidad="presencial")),
        ("Cotizar con descuento del 150 % (cálculo inconsistente)",
         lambda: gestor.cotizar_servicio("SAL-001", 2, descuento=1.5)),
        ("Cotizar sala para más asistentes que su capacidad",
         lambda: gestor.cotizar_servicio("SAL-001", 2, asistentes=30)),
        ("Cotizar más equipos de los que hay en inventario",
         lambda: gestor.cotizar_servicio("EQP-001", 3, cantidad=8)),
        ("Cotizar sala con duración en texto (excepción encadenada)",
         lambda: gestor.cotizar_servicio("SAL-001", "tres")),
        ("Deshabilitar la asesoría ASE-001",
         lambda: gestor.cambiar_disponibilidad_servicio("ASE-001", False)),
        ("Cotizar la asesoría deshabilitada (servicio no disponible)",
         lambda: gestor.cotizar_servicio("ASE-001", 2)),
        ("Deshabilitar de nuevo ASE-001 (operación no permitida)",
         lambda: gestor.cambiar_disponibilidad_servicio("ASE-001", False)),
        ("Reservar la sala SAL-001 por 3 horas para 10 personas (Ana)",
         lambda: gestor.crear_reserva("CLI-001", "SAL-001", 3, asistentes=10)),
        ("Confirmar la reserva RES-001",
         lambda: gestor.confirmar_reserva("RES-001")),
        ("Procesar RES-001: prestar el servicio y cobrar con IVA",
         lambda: gestor.procesar_reserva("RES-001", impuesto=IVA_COLOMBIA)),
        ("Cancelar RES-001 después de prestado el servicio (no permitido)",
         lambda: gestor.cancelar_reserva("RES-001", "el cliente cambió de planes")),
        ("Reservar 3 portátiles por 5 días (Carlos)",
         lambda: gestor.crear_reserva("CLI-002", "EQP-001", 5, cantidad=3)),
        ("Confirmar la reserva RES-002 (se apartan 3 de 5 portátiles)",
         lambda: gestor.confirmar_reserva("RES-002")),
        ("Confirmar RES-002 por segunda vez (no permitido)",
         lambda: gestor.confirmar_reserva("RES-002")),
        ("Reservar 4 portátiles cuando solo quedan 2 libres (excepción encadenada)",
         lambda: gestor.crear_reserva("CLI-001", "EQP-001", 2, cantidad=4)),
        ("Procesar RES-002 con descuento del 80 % (cálculo inconsistente; la reserva sigue confirmada)",
         lambda: gestor.procesar_reserva("RES-002", descuento=0.80)),
        ("Procesar RES-002 con descuento del 10 % e IVA (los portátiles vuelven al inventario)",
         lambda: gestor.procesar_reserva("RES-002", impuesto=IVA_COLOMBIA, descuento=0.10)),
        ("Reservar la asesoría ASE-001 mientras está deshabilitada (excepción encadenada)",
         lambda: gestor.crear_reserva("CLI-002", "ASE-001", 2)),
        ("Habilitar de nuevo la asesoría ASE-001",
         lambda: gestor.cambiar_disponibilidad_servicio("ASE-001", True)),
        ("Reservar la asesoría ASE-001 por 2 horas en modalidad presencial (Carlos)",
         lambda: gestor.crear_reserva("CLI-002", "ASE-001", 2, modalidad="presencial")),
        ("Procesar RES-003 sin haberla confirmado (no permitido)",
         lambda: gestor.procesar_reserva("RES-003")),
        ("Cancelar la reserva pendiente RES-003",
         lambda: gestor.cancelar_reserva("RES-003", "el cliente reprogramará la asesoría")),
        ("Reservar la sala por 15 horas, más de lo permitido (excepción encadenada)",
         lambda: gestor.crear_reserva("CLI-001", "SAL-001", 15)),
        ("Reservar para un cliente que no existe",
         lambda: gestor.crear_reserva("CLI-050", "SAL-001", 2)),
        ("Confirmar una reserva que no existe",
         lambda: gestor.confirmar_reserva("RES-099")),
        ("Simular un error imprevisto: acceder a un cliente en una posición inexistente",
         lambda: gestor.listar_clientes()[50]),
    ]


def mostrar_resumen(gestor: GestorSoftwareFJ, contador: Dict[str, int]) -> None:
    """Imprime el estado final del sistema y los totales de la simulación."""
    print(f"\n{LINEA}\nRESUMEN FINAL\n{LINEA}")
    print("Clientes registrados:")
    for cliente in gestor.listar_clientes():
        print(f"  - {cliente}")
    print("Servicios registrados:")
    for servicio in gestor.listar_servicios():
        print(f"  - {servicio}")
    print("Reservas:")
    for reserva in gestor.listar_reservas():
        print(f"  - {reserva}")
        for fecha, estado, nota in reserva.historial:
            print(f"      {fecha:%H:%M:%S} [{estado}] {nota}")
    print(f"Total cobrado: {formatear_moneda(gestor.resumen()['total_cobrado'])}")
    total = sum(contador.values())
    print(
        f"\nOperaciones simuladas: {total} | exitosas: {contador['exitosas']} | "
        f"fallidas controladas: {contador['fallidas']} | imprevistas controladas: {contador['imprevistas']}"
    )
    print(f"Estado del gestor: {gestor.resumen()}")
    print(f"Registro de eventos y errores: {RUTA_RELATIVA_LOG}")
    print("\nLa aplicación terminó sin interrupciones a pesar de los errores.")


def main() -> None:
    """Ejecuta la simulación completa y muestra el resumen final."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    registrar_evento("=" * 20 + " INICIO DE LA SIMULACIÓN " + "=" * 20)
    print(f"{LINEA}\nSOFTWARE FJ - Sistema Integral de Gestión de Clientes, Servicios y Reservas\n{LINEA}")
    gestor = GestorSoftwareFJ()
    contador = {"exitosas": 0, "fallidas": 0, "imprevistas": 0}
    for numero, (descripcion, accion) in enumerate(construir_operaciones(gestor), start=1):
        ejecutar_operacion(numero, descripcion, accion, contador)
    mostrar_resumen(gestor, contador)
    registrar_evento(f"Fin de la simulación: {contador}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:  # El usuario presionó Ctrl+C
        print("\nSimulación interrumpida por el usuario.")
        registrar_advertencia("Simulación interrumpida por el usuario (Ctrl+C).")
        sys.exit(130)
    finally:
        registrar_evento("Ejecución finalizada.")
