"""Validadores compartidos para entidades y atributos de dominio."""

import math

from app.shared.domain.exceptions import ValidationException


def require_non_empty_text(
    value: str,
    field_name: str,
    max_length: int,
    exc_cls: type[ValidationException],
) -> str:
    """Valida que una cadena no esté vacía tras recortar espacios ni exceda max_length."""
    cleaned = value.strip()
    if not cleaned:
        raise exc_cls(f"El campo '{field_name}' es obligatorio y no puede estar vacío.")
    if len(cleaned) > max_length:
        raise exc_cls(
            f"El campo '{field_name}' no puede superar {max_length} caracteres."
        )
    return cleaned


def validate_optional_text(
    value: str | None,
    field_name: str,
    max_length: int | None,
    exc_cls: type[ValidationException],
) -> str | None:
    """Normaliza una cadena opcional y valida su longitud máxima si aplica."""
    if value is None:
        return None
    cleaned = value.strip()
    if not cleaned:
        return None
    if max_length is not None and len(cleaned) > max_length:
        raise exc_cls(
            f"El campo '{field_name}' no puede superar {max_length} caracteres."
        )
    return cleaned


def require_positive_id(
    value: int,
    field_name: str,
    exc_cls: type[ValidationException],
) -> int:
    """Valida que un identificador entero de referencia sea estrictamente positivo."""
    if value <= 0:
        raise exc_cls(f"El identificador '{field_name}' debe ser mayor que 0.")
    return value


def require_positive_float(
    value: float,
    field_name: str,
    exc_cls: type[ValidationException],
) -> float:
    """Valida que un valor numérico real sea estrictamente mayor que 0."""
    if value <= 0:
        raise exc_cls(f"El campo '{field_name}' debe ser mayor que 0.")
    return float(value)


def require_unit_interval(
    value: float,
    field_name: str,
    exc_cls: type[ValidationException],
) -> float:
    """Valida que un valor numérico pertenezca al intervalo cerrado [0, 1]."""
    if not 0.0 <= value <= 1.0:
        raise exc_cls(f"El campo '{field_name}' debe estar entre 0 y 1.")
    return float(value)


def require_in_range(
    value: float,
    field_name: str,
    minimum: float,
    maximum: float,
    exc_cls: type[ValidationException],
) -> float:
    """Valida que un número sea finito y esté dentro del intervalo cerrado [minimum, maximum]."""
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise exc_cls(f"El campo '{field_name}' debe ser un número finito.")
    if not minimum <= value <= maximum:
        raise exc_cls(f"El campo '{field_name}' debe estar entre {minimum:g} y {maximum:g}.")
    return float(value)


def require_non_negative(
    value: float,
    field_name: str,
    exc_cls: type[ValidationException],
) -> float:
    """Valida que un número finito sea mayor o igual que 0."""
    return require_in_range(value, field_name, 0.0, math.inf, exc_cls)


def require_one_of(
    value: str,
    field_name: str,
    allowed: tuple[str, ...],
    exc_cls: type[ValidationException],
) -> str:
    """Valida que una cadena pertenezca a un conjunto cerrado de valores."""
    if value not in allowed:
        raise exc_cls(f"El campo '{field_name}' debe ser uno de: {', '.join(allowed)}.")
    return value
