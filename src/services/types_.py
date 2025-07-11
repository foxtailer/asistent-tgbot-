import re
from datetime import date

from pydantic import BaseModel, field_validator, model_validator

from src.services.variables import ALLOWED_LANGUAGES


class Word(BaseModel):
    text: str
    examples: tuple[str, ...] | None = None
    language: str
    freq: int | None = None
    cefr: str | None = None
    id_: int | None = None

    @field_validator('language')
    @classmethod
    def validate_languages(cls, v):
        if v not in ALLOWED_LANGUAGES:
            raise ValueError(
                f"Language '{v}' is not in allowed languages: {ALLOWED_LANGUAGES}"
            )
        return v


class WordRow(BaseModel):
    languages: tuple[str, ...]
    words: tuple[tuple[Word, ...], ...]
    date: date | str

    @field_validator('date', mode='before')
    @classmethod
    def validate_date_format(cls, v):
        if isinstance(v, (date)):
            return v.strftime('%Y-%m-%d')
        elif isinstance(v, str):
            if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', v):
                raise ValueError('date must be in format YYYY-MM-DD')
            return v
        else:
            raise ValueError('date must be a string, or date')
        
    @model_validator(mode='after')
    def check_lengths_match(self):
        if len(self.languages) != len(self.words):
            raise ValueError(
                f'Length of languages ({len(self.languages)}) must equal length of words ({len(self.words)})'
            )
        
        lengths = {len(inner) for inner in self.words}

        if len(lengths) > 1:
            raise ValueError(f"All inner tuples in 'words' must have the same length, found lengths: {lengths}")
        return self
    
    @field_validator('languages')
    @classmethod
    def validate_languages(cls, langs):
        for lang in langs:
            if lang not in ALLOWED_LANGUAGES:
                raise ValueError(
                    f"Language '{lang}' is not in allowed languages: {ALLOWED_LANGUAGES}"
                )
        return langs


class DelArgs(BaseModel):
    language: str | None = None
    flags: tuple[str, ...] | None = None
    ids: tuple[int, ...] | None = None
    words: tuple[str, ...] | None = None

    @field_validator('flags')
    @classmethod
    def validate_flags(cls, v):
        allowed_flags = {'d', 'w', 's'}
        for flag in v:
            if flag not in allowed_flags:
                raise ValueError(f"Invalid flag '{flag}'. Allowed flags: {allowed_flags}")
        if len(v) > 1:
            raise ValueError(f"Invalid flag '{v}'. Allowed flags: {allowed_flags}")
        return v
    
    @field_validator('language')
    @classmethod
    def validate_languages(cls, v):
        if v not in ALLOWED_LANGUAGES:
            raise ValueError(f"Language '{v}' is not in allowed languages: {ALLOWED_LANGUAGES}")
        return v
