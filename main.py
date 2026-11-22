"""
Programa principal: main.py
Proyecto: Sistema Integral de Gestión de Clientes, Servicios y Reservas - Software FJ
Curso: Programación (213023) - UNAD - Fase 4

Simula operaciones completas sobre el sistema, mezclando casos válidos e
inválidos, para demostrar que la aplicación NUNCA se detiene: cada error se
captura, se registra en logs/sistema.log y la simulación continúa.

PARTE 1 (este archivo): operaciones de clientes y servicios.
PARTE 2 (pendiente):    operaciones de reservas (exitosas y fallidas).

Ejecución:
    python3 main.py      (macOS / Linux)
    python main.py       (Windows)
"""

import sys  # Para ajustar la salida de consola y finalizar el programa
from typing import Any, Callable, Dict, List, Tuple  # Anotaciones de tipo

from software_fj import Entidad, GestorSoftwareFJ, IVA_COLOMBIA, SoftwareFJError, formatear_moneda
from software_fj.logger import RUTA_RELATIVA_LOG, registrar_advertencia, registrar_critico, registrar_evento

# Tipo de dato de cada operación: (descripción, función sin argumentos que la ejecuta)
Operacion = Tuple[str, Callable[[], Any]]

LINEA = "-" * 78  # Separador visual para la consola


def mostrar_resultado(resultado: Any) -> None:
    """Muestra en consola el resultado de una operación exitosa según su tipo."""
    if isinstance(resultado, Entidad):  # Cliente o servicio: se usa su descripción (polimorfismo)
        print(f"   {resultado.describir()}")  # describir() cambia según la clase del objeto
    elif isinstance(resultado, float):  # Un costo calculado
        print(f"   Total: {formatear_moneda(resultado)}")  # Se muestra en pesos
    elif resultado is not None:  # Cualquier otro valor
        print(f"   {resultado}")  # Se imprime tal cual


def ejecutar_operacion(numero: int, descripcion: str, accion: Callable[[], Any], contador: Dict[str, int]) -> None:
    """Ejecuta UNA operación de forma segura: pase lo que pase, el programa sigue.

    - except SoftwareFJError: errores previstos del dominio (datos inválidos, etc.).
    - except Exception:       errores imprevistos de Python; también se capturan
                              para que la aplicación no se caiga.
    - else:                   solo si la operación fue exitosa.
    - finally:                siempre: cierra el bloque visual de la operación.
    """
    print(f"\n[{numero:02d}] {descripcion}")  # Encabezado de la operación
    try:  # Se intenta ejecutar la operación
        resultado = accion()  # Llama a la función de la operación
    except SoftwareFJError as error:  # Error controlado (ya quedó registrado por el gestor)
        contador["fallidas"] += 1  # Se cuenta como fallo controlado
        print(f"   [ERROR CONTROLADO] {type(error).__name__}: {error}")  # Se informa en consola
        if error.__cause__ is not None:  # Si el error fue encadenado con "from"
            causa = error.__cause__  # Error técnico original
            print(f"   -> Causa original: {type(causa).__name__}: {causa}")  # Se muestra la causa
        registrar_advertencia(  # Log: así TODO error queda registrado, aunque el gestor no lo haya hecho
            f"Operación {numero:02d} '{descripcion}' falló de forma controlada -> {type(error).__name__}: {error}"
        )
    except Exception as error:  # Error IMPREVISTO: no es del dominio, pero no debe tumbar la app
        contador["imprevistas"] += 1  # Se cuenta aparte
        print(f"   [ERROR IMPREVISTO] {type(error).__name__}: {error}")  # Se informa en consola
        registrar_critico(f"Operación {numero:02d} '{descripcion}' produjo un error imprevisto", error)  # Log con traza
    else:  # La operación terminó sin errores
        contador["exitosas"] += 1  # Se cuenta como éxito
        print("   [OK]")  # Marca de éxito
        mostrar_resultado(resultado)  # Muestra lo que devolvió la operación
        registrar_evento(f"Operación {numero:02d} '{descripcion}' completada.")  # Log
    finally:  # Se ejecuta SIEMPRE
        print(f"   {LINEA[:40]}")  # Cierre visual de la operación


def construir_operaciones(gestor: GestorSoftwareFJ) -> List[Operacion]:
    """Define la lista de operaciones a simular (casos válidos e inválidos).

    Se usan funciones lambda para que cada operación se ejecute DENTRO del
    bloque try de ejecutar_operacion y no en el momento de armar la lista.
    """
    return [
        # ---------------------------- CLIENTES ----------------------------
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
        # ---------------------------- SERVICIOS ---------------------------
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
        # --------------------- COSTOS (SOBRECARGA) -------------------------
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
        # ------------------------- DISPONIBILIDAD --------------------------
        ("Deshabilitar la asesoría ASE-001",
         lambda: gestor.cambiar_disponibilidad_servicio("ASE-001", False)),
        ("Cotizar la asesoría deshabilitada (servicio no disponible)",
         lambda: gestor.cotizar_servicio("ASE-001", 2)),
        ("Deshabilitar de nuevo ASE-001 (operación no permitida)",
         lambda: gestor.cambiar_disponibilidad_servicio("ASE-001", False)),
        # ------------------------ ERROR IMPREVISTO -------------------------
        ("Simular un error imprevisto: acceder a un cliente en una posición inexistente",
         lambda: gestor.listar_clientes()[50]),
        # ======================= PARTE 2 (pendiente) =======================
        # Aquí se agregarán las operaciones de reservas: creación exitosa,
        # confirmación, cancelación, procesamiento y los intentos fallidos.
    ]


def mostrar_resumen(gestor: GestorSoftwareFJ, contador: Dict[str, int]) -> None:
    """Imprime el estado final del sistema y los totales de la simulación."""
    print(f"\n{LINEA}\nRESUMEN FINAL\n{LINEA}")  # Encabezado del resumen
    print("Clientes registrados:")  # Lista de clientes
    for cliente in gestor.listar_clientes():  # Recorre los clientes
        print(f"  - {cliente}")  # __str__ llama a describir()
    print("Servicios registrados:")  # Lista de servicios
    for servicio in gestor.listar_servicios():  # Recorre los servicios
        print(f"  - {servicio}")  # Cada tipo de servicio se describe distinto (polimorfismo)
    total = sum(contador.values())  # Total de operaciones simuladas
    print(  # Totales de la simulación
        f"\nOperaciones simuladas: {total} | exitosas: {contador['exitosas']} | "
        f"fallidas controladas: {contador['fallidas']} | imprevistas controladas: {contador['imprevistas']}"
    )
    print(f"Estado del gestor: {gestor.resumen()}")  # Resumen interno del gestor
    print(f"Registro de eventos y errores: {RUTA_RELATIVA_LOG}")  # Dónde quedó el log (ruta relativa)
    print("\nLa aplicación terminó sin interrupciones a pesar de los errores.")  # Mensaje de cierre


def main() -> None:
    """Punto de entrada del programa."""
    if hasattr(sys.stdout, "reconfigure"):  # Python 3.7+: evita fallos de codificación en consolas antiguas
        sys.stdout.reconfigure(errors="replace")  # Un carácter no imprimible se reemplaza en vez de fallar
    registrar_evento("=" * 20 + " INICIO DE LA SIMULACIÓN " + "=" * 20)  # Marca de inicio en el log
    print(f"{LINEA}\nSOFTWARE FJ - Sistema Integral de Gestión de Clientes, Servicios y Reservas\n{LINEA}")
    gestor = GestorSoftwareFJ()  # Crea el sistema con listas vacías en memoria
    contador = {"exitosas": 0, "fallidas": 0, "imprevistas": 0}  # Totales de la simulación
    for numero, (descripcion, accion) in enumerate(construir_operaciones(gestor), start=1):  # Recorre operaciones
        ejecutar_operacion(numero, descripcion, accion, contador)  # Cada una protegida por try/except
    mostrar_resumen(gestor, contador)  # Muestra el estado final
    registrar_evento(f"Fin de la simulación: {contador}")  # Marca de fin en el log


if __name__ == "__main__":  # Solo se ejecuta si se corre este archivo directamente
    try:  # Protección de último nivel
        main()  # Ejecuta la simulación
    except KeyboardInterrupt:  # El usuario presionó Ctrl+C
        print("\nSimulación interrumpida por el usuario.")  # Salida ordenada
        registrar_advertencia("Simulación interrumpida por el usuario (Ctrl+C).")  # Log
        sys.exit(130)  # Código de salida estándar para interrupción
    finally:  # Siempre, termine como termine
        registrar_evento("Ejecución finalizada.")  # Última línea del log
