# Software FJ - Client, Service and Booking Management System

Python project for the Programming course - Exercise #1.

## How to run

It needs Python 3.8 or later.

```bash
python main.py
```

## About the log files

The file `logs/sistema_ejemplo.log` is an example of the log the program creates every time it runs.

## Progress

The booking part is still missing. A client should be able to book a meeting room, some equipment or a consultant for a certain amount of time, and the system has to keep that booking.

Each booking also has to be followed from start to finish. It starts as pending, then it is confirmed, and at the end the service is delivered and charged. It should also be possible to cancel it before the service is delivered.

The system has to stop bookings that make no sense, such as booking something that is turned off, asking for more equipment than there is, confirming the same booking twice or cancelling something that was already delivered. When that happens, it should explain what went wrong, write it down in the log and keep working.

Finally, the simulation has to show bookings that work and bookings that fail, and the example log has to be updated with that final run.
