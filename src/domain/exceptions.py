class DomainException(Exception):
    code: int
    message: str
    detail: str | None = None

    def __init__(self, *args: object, detail: str | None = None) -> None:
        self.args = args
        if detail:
            self.detail = detail

    def __str__(self) -> str:
        base = f"[Error {self.code}] {self.message}"
        if self.detail:
            try:
                return f"{base} - {self.detail.format(*self.args)}"
            except Exception:
                return f"{base} - {self.detail}"  # Fallback if formatting fails
        return base

    def get_detail(self) -> str:
        if not self.detail:
            return self.message
        try:
            return self.detail.format(*self.args)
        except Exception:
            return self.detail
