from pydantic import BaseModel


class Word(BaseModel):
    id_: int
    language: str
    word: str
    freq: int | None = None
    cefr: str | None = None