from domain.exceptions import DomainException


class InvalidResourceCopyTarget(DomainException):
    code = 10409
    message = "Invalid resource copy target."


class UserNotFound(DomainException):
    code = 10404
    message = "User not found."
