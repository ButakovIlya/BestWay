class DomainException(Exception):
    code: int
    message: str
    detail: str | None = None

    def __init__(self, *args: object) -> None:
        self.args = args

    def __str__(self) -> str:
        return self.get_detail() if self.detail else self.message

    def get_detail(self) -> str:
        if not self.detail:
            return ""
        return self.detail.format(*self.args)
