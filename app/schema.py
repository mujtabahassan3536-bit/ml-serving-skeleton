from typing import Literal

from pydantic import BaseModel, Field, field_validator


class PredictionRequest(BaseModel):
    city: Literal["faisalabad", "lahore", "islamabad"]
    area_sqft: float = Field(..., gt=200, le=50000)
    bedrooms: int = Field(..., ge=1, le=20)
    age_years: int = Field(..., ge=0, le=100)

    @field_validator("city", mode="before")
    @classmethod
    def normalize_city(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip().lower()
        return value


class PredictionResponse(BaseModel):
    city: str
    predicted_price: float
    city_avg_price_per_sqft: float
    model_version: str


class HealthResponse(BaseModel):
    status: str
    raw_rows: int
    clean_rows: int
    dropped_rows: int
