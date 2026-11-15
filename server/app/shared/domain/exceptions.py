class DomainException(Exception):
    """Clase base para todos los errores de negocio."""

    code: str = "INTERNAL_DOMAIN_ERROR"
    message: str = "Ocurrió un error inesperado en el dominio."

    def __init__(self, message: str | None = None, code: str | None = None):
        if message:
            self.message = message
        if code:
            self.code = code
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"


class NotFoundException(DomainException):
    """Mapea a HTTP 404 (Not Found)."""

    code = "NOT_FOUND"


class ValidationException(DomainException):
    """Mapea a HTTP 400 (Bad Request)."""

    code = "VALIDATION_ERROR"


class ConflictException(DomainException):
    """Mapea a HTTP 409 (Conflict)."""

    code = "CONFLICT_ERROR"


class SinDatosException(NotFoundException):
    """La entrada es válida pero la fuente no devolvió datos utilizables. Mapea a HTTP 404."""

    code = "SIN_DATOS"
    message = "La fuente no devolvió datos para los parámetros indicados."


class FuenteExternaException(DomainException):
    """Fallo al consultar una API externa (red, 4xx/5xx). Mapea a HTTP 502."""

    code = "FUENTE_EXTERNA_ERROR"
    message = "La fuente de datos externa no está disponible."
