from dataclasses import dataclass


@dataclass
class AppError:
    code: str
    title: str
    message: str
    detail: str = ""
    suggestion: str = ""
