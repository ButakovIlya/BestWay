from domain.exceptions import DomainException


class AuthenticationError(DomainException):
    code = 10001
    message = "Authentication token is invalid."


class TokenExpiredError(DomainException):
    code = 10002
    message = "Authentication token has expired."
