"""Excepciones de dominio para el módulo cuerpo_celeste."""

from app.shared.domain.exceptions import NotFoundException, ValidationException


class CuerpoCelesteNotFoundException(NotFoundException):
    code = "CUERPO_CELESTE_NOT_FOUND"
    message = "El recurso solicitado de cuerpo_celeste no fue encontrado."


class InvalidCuerpoCelesteDataException(ValidationException):
    code = "INVALID_CUERPO_CELESTE_DATA"
    message = "Los datos proporcionados para cuerpo_celeste no son válidos."
