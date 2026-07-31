from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field

from app.models.country import Currency, Language

PyObjectId = Annotated[str, BeforeValidator(str)]


class FlagDocument(BaseModel):
    emoji: str | None = None
    png: str | None = None
    svg: str | None = None


class GeoPointDocument(BaseModel):
    type: str = "Point"
    coordinates: list[float]


class CountryDocument(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: PyObjectId = Field(alias="_id")
    alpha3_code: str
    name: str
    alpha2_code: str | None = None
    numeric_code: str | None = None
    native_name: str | None = None
    capital: str | None = None
    region: str | None = None
    subregion: str | None = None
    population: int | None = None
    area: float | None = None
    population_density: float | None = None
    gini: float | None = None
    independent: bool | None = None
    demonym: str | None = None
    borders: list[str] = Field(default_factory=list)
    timezones: list[str] = Field(default_factory=list)
    top_level_domain: list[str] = Field(default_factory=list)
    calling_codes: list[str] = Field(default_factory=list)
    flag: FlagDocument | None = None
    currencies: list[Currency] = Field(default_factory=list)
    languages: list[Language] = Field(default_factory=list)
    location: GeoPointDocument | None = None
    source: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class NearbyCountryDocument(CountryDocument):
    distance_m: float


class CurrencyGroupCountry(BaseModel):
    id: str
    name: str


class CurrencyGroupDocument(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    currency_code: str = Field(alias="_id")
    currency_name: str | None = None
    currency_symbol: str | None = None
    country_count: int
    countries: list[CurrencyGroupCountry] = Field(default_factory=list)
