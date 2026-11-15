"""Errores de las fuentes de datos de la malla."""


class FuenteError(Exception):
    """Una fuente no pudo dar el dato de una celda."""


class FuenteSinDatos(FuenteError):
    """La fuente respondió, pero no hay datos válidos para esa celda."""


class FuenteNoDisponible(FuenteError):
    """La fuente no respondió (red caída, límite de uso, error del servidor)."""
