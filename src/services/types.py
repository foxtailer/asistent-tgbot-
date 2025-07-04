import re
from datetime import date, datetime

from pydantic import BaseModel, field_validator


class Word(BaseModel):
    language: str
    word: str
    date: date
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