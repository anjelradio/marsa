"""Excepciones de dominio para el módulo sitio."""

from app.shared.domain.exceptions import NotFoundException, ValidationException


class SitioNotFoundException(NotFoundException):
    code = "SITIO_NOT_FOUND"
    message = "El recurso solicitado de sitio no fue encontrado."


class InvalidSitioDataException(ValidationException):
    code = "INVALID_SITIO_DATA"
    message = "Los datos proporcionados para sitio no son válidos."
