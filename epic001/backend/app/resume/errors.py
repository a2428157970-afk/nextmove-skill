class ResumeParseError(Exception):
    def __init__(self, code: str, message: str, status_code: int) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code

    def as_response(self) -> dict[str, bool | str]:
        return {
            "success": False,
            "code": self.code,
            "message": self.message,
        }
