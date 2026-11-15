"""Excepciones de dominio para el módulo composicion_celda."""

from app.shared.domain.exceptions import NotFoundException, ValidationException


class ComposicionCeldaNotFoundException(NotFoundException):
    code = "COMPOSICION_CELDA_NOT_FOUND"
    message = "El recurso solicitado de composicion_celda no fue encontrado."


class InvalidComposicionCeldaDataException(ValidationException):
    code = "INVALID_COMPOSICION_CELDA_DATA"
    message = "Los datos proporcionados para composicion_celda no son válidos."
