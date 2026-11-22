# Software FJ - Sistema de Gestión de Clientes, Servicios y Reservas

Proyecto en Python para el curso de Programación - Ejercicio #1.

## Cómo ejecutar

Requiere Python 3.8 o superior.

```bash
python main.py
```

## Sobre los archivos de log

El archivo `logs/sistema_ejemplo.log` es un ejemplo del log que el programa crea cada vez que se ejecuta.

## Avance

Todavía falta la parte de las reservas. Un cliente debería poder reservar una sala de reuniones, unos equipos o un asesor por un tiempo determinado, y el sistema tiene que guardar esa reserva.

Cada reserva también tiene que seguirse de principio a fin. Empieza como pendiente, luego se confirma y al final se presta el servicio y se cobra. También debería poder cancelarse antes de que se preste el servicio.

El sistema tiene que impedir las reservas que no tienen sentido, como reservar algo que está deshabilitado, pedir más equipos de los que hay, confirmar dos veces la misma reserva o cancelar algo que ya se prestó. Cuando eso pase, debe explicar qué salió mal, anotarlo en el log y seguir funcionando.

Por último, la simulación tiene que mostrar reservas que salen bien y reservas que fallan, y el log de ejemplo tiene que actualizarse con esa ejecución final.
