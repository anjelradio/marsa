"""Excepciones de dominio para el módulo analogia."""

from app.shared.domain.exceptions import NotFoundException, ValidationException


class AnalogiaNotFoundException(NotFoundException):
    code = "ANALOGIA_NOT_FOUND"
    message = "El recurso solicitado de analogia no fue encontrado."


class InvalidAnalogiaDataException(ValidationException):
    code = "INVALID_ANALOGIA_DATA"
    message = "Los datos proporcionados para analogia no son válidos."
