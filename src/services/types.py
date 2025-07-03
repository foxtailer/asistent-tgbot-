from datetime import date
from pydantic import BaseModel


class Word(BaseModel):
    language: str
    word: str
    date: date
    example: str | None = None
    freq: int | None = None
    cefr: str | None = None