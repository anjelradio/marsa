"""Excepciones de dominio para el módulo caracteristica."""

from app.shared.domain.exceptions import NotFoundException, ValidationException


class CaracteristicaNotFoundException(NotFoundException):
    code = "CARACTERISTICA_NOT_FOUND"
    message = "El recurso solicitado de caracteristica no fue encontrado."


class InvalidCaracteristicaDataException(ValidationException):
    code = "INVALID_CARACTERISTICA_DATA"
    message = "Los datos proporcionados para caracteristica no son válidos."
