from enum import Enum


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    PASSENGER = "PASSENGER"


class BookingStatus(str, Enum):
    RESERVED = "RESERVED"
    CANCELLED = "CANCELLED"
    CONFIRMED = "CONFIRMED"
    EXPIRED = "EXPIRED"
