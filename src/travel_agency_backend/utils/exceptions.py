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
