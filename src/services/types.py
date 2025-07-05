import re
from datetime import date, datetime

from pydantic import BaseModel, field_validator

from src.services.variables import ALLOWED_LANGUAGES


class WordRow(BaseModel):
    language: tuple[str, str]
    word: str
    trans: str
    date: date | str
    example: str | None = None
    freq: int | None = None
    cefr: str | None = None

    @field_validator('date', mode='before')
    def ensure_date_format(cls, v):
        if isinstance(v, (datetime, date)):
            return v.strftime('%Y-%m-%d')
        elif isinstance(v, str):
            if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', v):
                raise ValueError('date must be in format YYYY-MM-DD')
            return v
        else:
            raise ValueError('date must be a string, date, or datetime')
        
    @field_validator('language')
    def validate_languages(cls, v):
        for lang in v:
            if lang not in ALLOWED_LANGUAGES:
                raise ValueError(f"Language '{lang}' is not in allowed languages: {ALLOWED_LANGUAGES}")
        return v