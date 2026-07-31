from __future__ import annotations

import strawberry

from app.models.country import Currency as CurrencyDocument
from app.models.country import Language as LanguageDocument
from app.models.documents import CountryDocument, CurrencyGroupDocument


@strawberry.type
class Currency:
    code: str | None
    name: str | None
    symbol: str | None

    @classmethod
    def from_document(cls, doc: CurrencyDocument) -> "Currency":
        return cls(**doc.model_dump())


@strawberry.type
class Language:
    name: str
    iso639_1: str | None = strawberry.field(name="iso639_1", default=None)
    iso639_2: str | None = strawberry.field(name="iso639_2", default=None)
    native_name: str | None = None

    @classmethod
    def from_document(cls, doc: LanguageDocument) -> "Language":
        return cls(**doc.model_dump())


@strawberry.type
class Flags:
    png: str | None
    svg: str | None


@strawberry.type
class Country:
    id: str
    name: str
    native_name: str | None
    alpha2_code: str | None
    alpha3_code: str
    numeric_code: str | None
    capital: str | None
    region: str | None
    subregion: str | None
    area: float | None
    population: int | None
    population_density: float | None
    gini: float | None
    demonym: str | None
    currencies: list[Currency]
    languages: list[Language]
    latitude: float | None
    longitude: float | None
    timezones: list[str]
    borders: list[str]
    calling_codes: list[str]
    top_level_domain: list[str]
    flag: str | None
    flags: Flags | None
    independent: bool | None

    @classmethod
    def from_document(cls, doc: CountryDocument) -> "Country":
        return cls(
            id=doc.alpha3_code,
            name=doc.name,
            native_name=doc.native_name,
            alpha2_code=doc.alpha2_code,
            alpha3_code=doc.alpha3_code,
            numeric_code=doc.numeric_code,
            capital=doc.capital,
            region=doc.region,
            subregion=doc.subregion,
            area=doc.area,
            population=doc.population,
            population_density=doc.population_density,
            gini=doc.gini,
            demonym=doc.demonym,
            currencies=[Currency.from_document(c) for c in doc.currencies],
            languages=[Language.from_document(lang) for lang in doc.languages],
            longitude=doc.location.coordinates[0] if doc.location else None,
            latitude=doc.location.coordinates[1] if doc.location else None,
            timezones=doc.timezones,
            borders=doc.borders,
            calling_codes=doc.calling_codes,
            top_level_domain=doc.top_level_domain,
            flag=doc.flag.emoji if doc.flag else None,
            flags=Flags(png=doc.flag.png, svg=doc.flag.svg) if doc.flag else None,
            independent=doc.independent,
        )


@strawberry.type
class CountryPage:
    items: list[Country]
    total_count: int
    limit: int
    offset: int


@strawberry.type
class CountryDistance:
    country: Country
    distance_km: float


@strawberry.type
class CountrySummary:
    id: str
    name: str


@strawberry.type
class CurrencyGroup:
    currency_code: str
    currency_name: str | None
    currency_symbol: str | None
    country_count: int
    countries: list[CountrySummary]

    @classmethod
    def from_document(cls, doc: CurrencyGroupDocument) -> "CurrencyGroup":
        return cls(
            currency_code=doc.currency_code,
            currency_name=doc.currency_name,
            currency_symbol=doc.currency_symbol,
            country_count=doc.country_count,
            countries=[CountrySummary(id=c.id, name=c.name) for c in doc.countries],
        )


@strawberry.input
class CurrencyInput:
    code: str | None = None
    name: str | None = None
    symbol: str | None = None


@strawberry.input
class LanguageInput:
    name: str
    iso639_1: str | None = strawberry.field(name="iso639_1", default=None)
    iso639_2: str | None = strawberry.field(name="iso639_2", default=None)
    native_name: str | None = None


@strawberry.input
class AddCountryInput:
    name: str
    alpha3_code: str
    alpha2_code: str | None = None
    capital: str | None = None
    region: str | None = None
    subregion: str | None = None
    area: float | None = None
    population: int | None = None
    currencies: list[CurrencyInput] | None = None
    languages: list[LanguageInput] | None = None
    latitude: float | None = None
    longitude: float | None = None
