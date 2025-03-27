from domain.exceptions import DomainException


class AuthenticationError(DomainException):
    code = 10001
    message = "Authentication token is invalid."
    detail = "The provided token is malformed, missing, or failed verification."


class TokenExpiredError(DomainException):
    code = 10002
    message = "Authentication token has expired."
    detail = "The token expired at the expected expiration time. Please re-authenticate."
