from domain.exceptions import DomainException


class InvalidResourceCopyTarget(DomainException):
    code = 10409
    message = "Invalid resource copy target."
