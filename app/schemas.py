from pydantic import BaseModel, ConfigDict, Field, model_validator


class MovieCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    title: str = Field(min_length=1, max_length=200)
    year: int = Field(ge=1888, le=2100)
    genre: str = Field(min_length=1, max_length=50)
    rating: float = Field(default=0.0, ge=0, le=10)
    description: str = Field(default="", max_length=2000)


class MovieUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    title: str | None = Field(default=None, min_length=1, max_length=200)
    year: int | None = Field(default=None, ge=1888, le=2100)
    genre: str | None = Field(default=None, min_length=1, max_length=50)
    rating: float | None = Field(default=None, ge=0, le=10)
    description: str | None = Field(default=None, max_length=2000)

    @model_validator(mode="before")
    @classmethod
    def reject_explicit_null(cls, data):
        if isinstance(data, dict) and any(value is None for value in data.values()):
            raise ValueError("Переданные поля не могут иметь значение null")
        return data


class MovieRead(MovieCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
