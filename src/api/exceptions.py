from domain.exceptions import DomainException


class ResourceNotFound(DomainException):
    code = 10403
    message = "Resource not found."


class WrongFiltersFormat(DomainException):
    code = 10404
    message = "Filters must be in json format."


class InvalidCopyOptionError(DomainException):
    code = 10408
    message = "Invalid copy option."
