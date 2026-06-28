class ServiceError(Exception):
    code = "service_error"
    status_code = 400

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class NotFoundError(ServiceError):
    code = "not_found"
    status_code = 404


class ForbiddenError(ServiceError):
    code = "forbidden"
    status_code = 403


class UnauthorizedError(ServiceError):
    code = "unauthorized"
    status_code = 401


class ConflictError(ServiceError):
    code = "conflict"
    status_code = 409


class ValidationError(ServiceError):
    code = "validation_error"
    status_code = 400

