# Software FJ - Sistema de Gestión de Clientes, Servicios y Reservas

Proyecto en Python para el curso de Programación (213023) de la UNAD, Fase 4 - Ejercicio #1.

## Resumen de lo realizado

El sistema gestiona los clientes, los servicios y las reservas de la empresa Software FJ sin usar bases de datos. Toda la información se guarda en objetos y listas mientras el programa se ejecuta, y el único archivo que se usa es el log, donde quedan los eventos y los errores.

### Clientes

Cada cliente se registra con nombre, documento, correo y teléfono. Los datos se validan antes de guardarse y no se permiten dos clientes con el mismo documento.

### Servicios

La empresa ofrece tres servicios: reserva de salas, alquiler de equipos y asesorías especializadas. Los tres parten de una misma clase abstracta y cada uno calcula su costo a su manera. El costo total se puede calcular solo, con impuesto, con descuento o con ambos.

### Reservas

Un cliente puede reservar un servicio por un tiempo determinado. Cada reserva empieza como pendiente, luego se confirma y al final se presta el servicio y se cobra. También se puede cancelar antes de que se preste el servicio. El sistema rechaza las reservas que no tienen sentido, como reservar algo deshabilitado, pedir más equipos de los que hay, confirmar dos veces la misma reserva o cancelar algo que ya se prestó.

### Manejo de errores

El sistema tiene sus propias excepciones para cada tipo de problema y usa los bloques try, except, else y finally. Cuando algo sale mal, muestra qué pasó, lo anota en el log y sigue funcionando.

### Simulación

El archivo `main.py` ejecuta 45 operaciones con datos válidos e inválidos para demostrar que el programa no se detiene ante los errores.

## Cómo ejecutar

Requiere Python 3.8 o superior. No es necesario instalar paquetes adicionales.

1. Clonar el repositorio:

```bash
git clone https://github.com/hectorrojas4/Unad-Fase4-Ejercicio1.git
```

2. Entrar a la carpeta del proyecto:

```bash
cd Unad-Fase4-Ejercicio1
```

3. Ejecutar el programa (en macOS o Linux puede ser `python3 main.py`):

```bash
python main.py
```

La consola muestra cada operación con su resultado, ya sea OK, error controlado o error imprevisto, y al final un resumen con los clientes, los servicios y las reservas.

## Sobre los archivos de log

El archivo `logs/sistema_ejemplo.log` es un ejemplo del log que el programa crea cada vez que se ejecuta.
