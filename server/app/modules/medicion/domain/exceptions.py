"""Excepciones de dominio para el módulo medicion."""

from app.shared.domain.exceptions import NotFoundException, ValidationException


class MedicionNotFoundException(NotFoundException):
    code = "MEDICION_NOT_FOUND"
    message = "El recurso solicitado de medicion no fue encontrado."


class InvalidMedicionDataException(ValidationException):
    code = "INVALID_MEDICION_DATA"
    message = "Los datos proporcionados para medicion no son válidos."
