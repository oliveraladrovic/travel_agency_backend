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
