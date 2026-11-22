# Software FJ — Sistema Integral de Gestión de Clientes, Servicios y Reservas

**Curso:** Programación (213023) — UNAD, Escuela de Ciencias Básicas, Tecnología e Ingeniería (ECBTI)
**Actividad:** Fase 4 — Componente práctico, prácticas simuladas (Ejercicio 1)

Sistema orientado a objetos en Python, **sin base de datos**, que gestiona clientes, servicios
(reserva de salas, alquiler de equipos y asesorías especializadas) y reservas para la empresa
Software FJ. Toda la información vive en objetos y listas en memoria; el único archivo que se usa
es el registro de eventos y errores (`logs/sistema.log`).

El objetivo central es demostrar un **manejo robusto de excepciones**: la aplicación sigue
funcionando aunque se presenten errores durante su ejecución.

## Requisitos

- Python 3.8 o superior (solo biblioteca estándar, no requiere instalar paquetes).

## Ejecución

```bash
python3 main.py      # macOS / Linux
python main.py       # Windows
```

Al ejecutar se crea (o amplía) el archivo `logs/sistema.log` con todos los eventos y errores.

### Sobre los archivos de log

- `logs/sistema.log` **no se sube al repositorio** (está en `.gitignore`): se genera en cada
  ejecución, crece con cada corrida y contiene rutas propias del equipo de quien lo ejecuta.
- `logs/sistema_ejemplo.log` **sí se sube**: es el registro de una ejecución limpia de la
  simulación y sirve como evidencia del requisito de logs sin necesidad de ejecutar el programa.
  Se actualizará al terminar la Parte 2 para que incluya también las reservas.

## Estructura del proyecto

```
Unad-Fase4-Ejercicio1/
├── main.py                  # Simulación de operaciones válidas e inválidas
├── software_fj/
│   ├── __init__.py          # Exporta las clases del paquete
│   ├── excepciones.py       # Jerarquía de excepciones personalizadas
│   ├── logger.py            # Registro de eventos y errores en archivo
│   ├── entidad.py           # Clase abstracta Entidad (base de todo el sistema)
│   ├── cliente.py           # Clase Cliente (encapsulación y validaciones)
│   ├── servicios.py         # Clase abstracta Servicio + 3 servicios especializados
│   ├── gestor.py            # Gestor del sistema (listas internas en memoria)
│   └── reserva.py           # (PARTE 2) Clase Reserva
└── logs/
    ├── sistema_ejemplo.log  # Evidencia: log de una ejecución limpia (versionado)
    └── sistema.log          # Se genera al ejecutar (no se versiona)
```

## Diseño orientado a objetos

| Principio | Dónde se aplica |
|---|---|
| Abstracción | `Entidad` y `Servicio` son clases abstractas (`ABC`, `@abstractmethod`). |
| Herencia | `Cliente` y `Servicio` heredan de `Entidad`; `SalaReuniones`, `AlquilerEquipo` y `AsesoriaEspecializada` heredan de `Servicio`. |
| Polimorfismo | Cada servicio sobrescribe `calcular_costo()`, `describir()` y `validar_parametros()`. |
| Encapsulación | Atributos privados (`__nombre`, `__documento`...) con propiedades que validan; el documento es de solo lectura y se muestra enmascarado. |
| Sobrecarga | `Servicio.calcular_costo_total()` con variantes declaradas con `@overload`: costo base, con impuesto, con descuento o con ambos. |

## Manejo de excepciones

- **Excepciones personalizadas** (`excepciones.py`), todas derivadas de `SoftwareFJError`, con
  código propio (`SFJ-101`, `SFJ-400`, etc.).
- **`try/except`**: en validaciones de conversión de datos (`cliente.py`, `servicios.py`).
- **`try/except/else`**: en `logger.py` (apertura del archivo de log) y en `main.py`.
- **`try/except/else/finally`**: en cada operación del gestor (`gestor.py`) y en `main.py`.
- **Encadenamiento** (`raise ... from error`): un `ValueError`, `TypeError` o `KeyError` técnico
  se convierte en un error del dominio conservando la causa original, que también queda en el log.
- **Errores imprevistos**: `main.py` los captura aparte (`except Exception`), los registra con su
  traza completa y continúa con la siguiente operación.

## Avance

### Parte 1 — Base funcional ✅
- [x] Jerarquía de excepciones personalizadas
- [x] Registro de eventos y errores en archivo
- [x] Clase abstracta `Entidad`
- [x] Clase `Cliente` con validaciones y encapsulación
- [x] Clase abstracta `Servicio` y tres servicios especializados
- [x] Sobrecarga del cálculo de costos (impuesto, descuento, parámetros opcionales)
- [x] Gestor con listas internas para clientes y servicios
- [x] Simulación de operaciones de clientes y servicios (válidas e inválidas)

### Parte 2 — Pendiente ⏳

Hoy el sistema ya sabe quiénes son los clientes, qué servicios se ofrecen y cuánto cuestan,
pero todavía **nadie puede reservar nada**. Lo que falta, dicho en sencillo:

- [ ] **Hacer una reserva:** que un cliente pueda apartar un servicio (una sala, unos equipos
      o una asesoría) indicando por cuánto tiempo, y que el sistema guarde esa reserva.
- [ ] **Seguir la reserva de principio a fin:** que al crearla quede pendiente, que luego se
      pueda confirmar, que al final se preste el servicio y se cobre, y que en cualquier momento
      antes de prestarlo se pueda cancelar.
- [ ] **Impedir reservas que no tienen sentido:** por ejemplo, reservar algo deshabilitado,
      pedir más equipos de los que hay, confirmar dos veces la misma reserva o cancelar algo que
      ya se prestó. En cada caso el sistema debe avisar qué pasó, dejarlo anotado en el registro
      y seguir funcionando como si nada.
- [ ] **Mostrarlo en la simulación:** agregar ejemplos de reservas que salen bien y otras que
      fallan, para completar las operaciones que pide el enunciado.
- [ ] **Actualizar el log de ejemplo** con una ejecución final que incluya las reservas.

## Integrantes

| Nombre | Aporte |
|---|---|
| _Integrante 1_ | |
| _Integrante 2_ | |
| _Integrante 3_ | |
| _Integrante 4_ | |
| _Integrante 5_ | |
