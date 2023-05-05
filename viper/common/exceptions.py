from typing import Optional


class GenericException(Exception):
    def __init__(self, message: str, level: Optional[str] = ""):
        self.message = message.strip() + "\n"
        self.level = level.strip()

    def __str__(self):
        return f"{self.level}: {self.message}"

    def get(self):
        return self.level, self.message


class ArgumentErrorCallback(GenericException):
    pass
