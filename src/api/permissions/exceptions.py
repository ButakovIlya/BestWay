from domain.exceptions import DomainException


class UserIsNotAuthenticatedError(DomainException):
    code = 10401
    message = "Authentication credentials were not provided."
