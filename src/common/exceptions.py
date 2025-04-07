class APIException(Exception):
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message


class ResponsesLimitExceededException(Exception):
    def __init__(self, message="ChatGPT responses limit per day exceeded", code=429):
        self.message = message
        self.code = code
