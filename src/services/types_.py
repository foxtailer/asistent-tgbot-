import re
from datetime import date

from pydantic import BaseModel, field_validator

from src.services.variables import ALLOWED_LANGUAGES


class Word(BaseModel):
    text: str
    tg_id: int
    id_: int | None = None


class WordRow(BaseModel):
    language: tuple[str, ...]
    word: Word
    trans: tuple[Word, ...]
    date: date | str
    example: tuple[tuple[str]] | None = None
    freq: int | None = None
    cefr: str | None = None

    @field_validator('date', mode='before')
    def validate_date_format(cls, v):
        if isinstance(v, (date)):
            return v.strftime('%Y-%m-%d')
        elif isinstance(v, str):
            if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', v):
                raise ValueError('date must be in format YYYY-MM-DD')
            return v
        else:
            raise ValueError('date must be a string, or date')
        
    @field_validator('language')
    def validate_languages(cls, v):
        for lang in v:
            if lang not in ALLOWED_LANGUAGES:
                raise ValueError(f"Language '{lang}' is not in allowed languages: {ALLOWED_LANGUAGES}")
        return v


class DelArgs(BaseModel):
    flags: tuple[str, ...]
    range: tuple[int, ...]
    words: tuple[str, ...] | None = None

    @field_validator('flags')
    def validate_flags(cls, v):
        allowed_flags = {'d', 'w', 's'}
        for flag in v:
            if flag not in allowed_flags:
                raise ValueError(f"Invalid flag '{flag}'. Allowed flags: {allowed_flags}")
        if len(v) > 1:
            raise ValueError(f"Invalid flag '{v}'. Allowed flags: {allowed_flags}")
        return v