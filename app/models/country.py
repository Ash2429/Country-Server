import logging

from pydantic import BaseModel, ConfigDict, Field, field_validator

logger = logging.getLogger(__name__)


class Currency(BaseModel):
    code: str | None = None
    name: str | None = None
    symbol: str | None = None


class Language(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str
    iso639_1: str | None = None
    iso639_2: str | None = None
    native_name: str | None = Field(default=None, alias="nativeName")


class CountryCreate(BaseModel):
    name: str = Field(min_length=1)
    alpha3_code: str
    alpha2_code: str | None = None
    capital: str | None = None
    region: str | None = None
    subregion: str | None = None
    area: float | None = Field(default=None, ge=0)
    population: int | None = Field(default=None, ge=0)
    currencies: list[Currency] = Field(default_factory=list)
    languages: list[Language] = Field(default_factory=list)
    latitude: float | None = None
    longitude: float | None = None

    @field_validator("alpha3_code")
    @classmethod
    def normalise_alpha3_code(cls, value: str) -> str:
        value = value.strip().upper()
        if len(value) != 3 or not value.isalpha():
            raise ValueError("alpha3_code must be exactly 3 letters, e.g. 'IND'")
        return value


class FlagsIn(BaseModel):
    png: str | None = None
    svg: str | None = None


class CountryIn(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(min_length=1)
    alpha3_code: str = Field(alias="alpha3Code")
    region: str = Field(min_length=1)
    population: int = Field(ge=0)

    native_name: str | None = Field(default=None, alias="nativeName")
    alpha2_code: str | None = Field(default=None, alias="alpha2Code")
    numeric_code: str | None = Field(default=None, alias="numericCode")
    capital: str | None = None
    subregion: str | None = None
    area: float | None = Field(default=None, ge=0)
    population_density: float | None = Field(default=None, alias="populationDensity")
    gini: float | None = None
    demonym: str | None = None
    independent: bool | None = None
    borders: list[str] = Field(default_factory=list)
    timezones: list[str] = Field(default_factory=list)
    top_level_domain: list[str] = Field(default_factory=list, alias="topLevelDomain")
    calling_codes: list[str] = Field(default_factory=list, alias="callingCodes")
    currencies: list[Currency] = Field(default_factory=list)
    languages: list[Language] = Field(default_factory=list)
    flag_emoji: str | None = Field(default=None, alias="flag")
    flags: FlagsIn | None = None
    latlng: list[float] | None = None

    @field_validator("alpha3_code")
    @classmethod
    def normalise_alpha3_code(cls, value: str) -> str:
        value = value.strip().upper()
        if len(value) != 3 or not value.isalpha():
            raise ValueError("alpha3Code must be exactly 3 letters, e.g. 'IND'")
        return value

    @field_validator("latlng")
    @classmethod
    def validate_latlng(cls, value: list[float] | None) -> list[float] | None:
        if value is not None and len(value) != 2:
            raise ValueError("latlng must be a [lat, lng] pair")
        return value

    def to_document(self) -> dict:
        flag = None
        if self.flag_emoji or self.flags:
            flag = {
                "emoji": self.flag_emoji,
                "png": self.flags.png if self.flags else None,
                "svg": self.flags.svg if self.flags else None,
            }

        location = None
        if self.latlng:
            lat, lng = self.latlng
            if lat == 0 and lng == 0:
                logger.warning("%s has suspect [0, 0] coordinates", self.alpha3_code)
            location = {"type": "Point", "coordinates": [lng, lat]}

        return {
            "alpha2_code": self.alpha2_code,
            "alpha3_code": self.alpha3_code,
            "numeric_code": self.numeric_code,
            "name": self.name,
            "native_name": self.native_name,
            "capital": self.capital,
            "region": self.region,
            "subregion": self.subregion,
            "population": self.population,
            "area": self.area,
            "population_density": self.population_density,
            "gini": self.gini,
            "independent": self.independent,
            "demonym": self.demonym,
            "borders": self.borders,
            "timezones": self.timezones,
            "top_level_domain": self.top_level_domain,
            "calling_codes": self.calling_codes,
            "flag": flag,
            "currencies": [c.model_dump() for c in self.currencies],
            "languages": [lang.model_dump() for lang in self.languages],
            "location": location,
            "source": "apicountries.com",
        }
