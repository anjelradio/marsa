"""Excepciones de dominio para el módulo dataset."""

from app.shared.domain.exceptions import NotFoundException, ValidationException


class DatasetNotFoundException(NotFoundException):
    code = "DATASET_NOT_FOUND"
    message = "El recurso solicitado de dataset no fue encontrado."


class InvalidDatasetDataException(ValidationException):
    code = "INVALID_DATASET_DATA"
    message = "Los datos proporcionados para dataset no son válidos."
