from domain.exceptions import DomainException


class UserIsNotAuthenticatedError(DomainException):
    code = 10401
    message = "Authentication credentials were not provided."


class UserIsNotAdminError(DomainException):
    code = 10402
    message = "User has no admin permissions."
