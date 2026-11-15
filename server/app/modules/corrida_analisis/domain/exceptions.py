"""Excepciones de dominio para el módulo corrida_analisis."""

from app.shared.domain.exceptions import NotFoundException, ValidationException


class CorridaAnalisisNotFoundException(NotFoundException):
    code = "CORRIDA_ANALISIS_NOT_FOUND"
    message = "El recurso solicitado de corrida_analisis no fue encontrado."


class InvalidCorridaAnalisisDataException(ValidationException):
    code = "INVALID_CORRIDA_ANALISIS_DATA"
    message = "Los datos proporcionados para corrida_analisis no son válidos."
