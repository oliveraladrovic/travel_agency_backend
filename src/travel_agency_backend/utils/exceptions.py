from fastapi import status


class DomainException(Exception):
    message: str = "Domain Error"
    code: str = "DOMAIN_ERROR"
    status_code: int = status.HTTP_400_BAD_REQUEST


class EmailAlreadyExistsError(DomainException):
    message: str = "Email already exists"
    code: str = "EMAIL_ALREADY_EXISTS"
    status_code: int = status.HTTP_409_CONFLICT


class InvalidCredentialsError(DomainException):
    message: str = "Invalid email or password"
    code: str = "INVALID_CREDENTIALS"
    status_code: int = status.HTTP_401_UNAUTHORIZED


class TokenExpiredError(DomainException):
    message: str = "Token has expired"
    code: str = "TOKEN_EXPIRED"
    status_code: int = status.HTTP_401_UNAUTHORIZED


class InvalidTokenError(DomainException):
    message: str = "Invalid token"
    code: str = "INVALID_TOKEN"
    status_code: int = status.HTTP_401_UNAUTHORIZED


class AdminPrivilegesRequiredError(DomainException):
    message: str = "Admin privileges required"
    code: str = "ADMIN_PRIVILEGES_REQUIRED"
    status_code: int = status.HTTP_403_FORBIDDEN


class TripAlreadyExistsError(DomainException):
    message: str = "Trip slug already exists"
    code: str = "TRIP_ALREADY_EXISTS"
    status_code: int = status.HTTP_409_CONFLICT


class TripNotFoundError(DomainException):
    message: str = "Trip not found"
    code: str = "TRIP_NOT_FOUND"
    status_code: int = status.HTTP_404_NOT_FOUND


class DeleteConflictError(DomainException):
    message: str = "Conflict while deleting resource"
    code: str = "DELETE_CONFLICT"
    status_code: int = status.HTTP_409_CONFLICT


class UpdateConflictError(DomainException):
    message: str = "Conflict while updating resource"
    code: str = "UPDATE_CONFLICT"
    status_code: int = status.HTTP_409_CONFLICT


class DepartureNotFoundError(DomainException):
    message: str = "Departure not found"
    code: str = "DEPARTURE_NOT_FOUND"
    status_code: int = status.HTTP_404_NOT_FOUND


class InvalidDepartureDateError(DomainException):
    message: str = "Departure date must be in future"
    code: str = "INVALID_DEPARTURE_DATE"
    status_code: int = status.HTTP_400_BAD_REQUEST


class DepartureIntegrityError(DomainException):
    message: str = "Integrity error while creating departure"
    code: str = "DEPARTURE_INTEGRITY_ERROR"
    status_code: int = status.HTTP_409_CONFLICT
