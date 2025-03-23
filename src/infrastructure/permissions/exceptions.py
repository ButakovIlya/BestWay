from domain.exceptions import DomainException


class UserHasNoPermissionError(DomainException):
    code = 10402
    message = "You don't have permission to access this resource."
