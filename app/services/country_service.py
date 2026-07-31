from pymongo.errors import DuplicateKeyError

from app.errors import CountryNotFoundError, DuplicateCountryError
from app.models.country import CountryCreate
from app.models.documents import CountryDocument, CurrencyGroupDocument
from app.repositories.country_repository import CountryRepository
from app.settings import settings


class CountryService:
    def __init__(self, repository: CountryRepository):
        self._repository = repository

    async def list_countries(self, limit: int, offset: int) -> tuple[list[CountryDocument], int]:
        limit = max(1, min(limit, settings.max_page_size))
        offset = max(0, offset)
        return await self._repository.find_page(limit=limit, offset=offset)

    async def get_country(self, alpha3_code: str) -> CountryDocument | None:
        return await self._repository.find_by_alpha3_code(_normalise_code(alpha3_code))

    async def get_countries_nearby(
        self, latitude: float, longitude: float, limit: int
    ) -> list[tuple[CountryDocument, float]]:
        limit = max(1, min(limit, settings.max_page_size))
        docs = await self._repository.find_nearby(
            longitude=longitude, latitude=latitude, limit=limit
        )
        return [(doc, doc.distance_m / 1000) for doc in docs]

    async def get_countries_by_language(self, language: str) -> list[CountryDocument]:
        return await self._repository.find_by_language(language)

    async def get_countries_by_currency(self) -> list[CurrencyGroupDocument]:
        return await self._repository.group_by_currency()

    async def add_country(self, data: CountryCreate) -> CountryDocument:
        try:
            return await self._repository.insert(_build_document(data))
        except DuplicateKeyError:
            raise DuplicateCountryError(data.alpha3_code) from None

    async def update_country_name(self, alpha3_code: str, name: str) -> CountryDocument:
        name = name.strip()
        if not name:
            raise ValueError("name must not be empty")
        updated = await self._repository.update_name(_normalise_code(alpha3_code), name)
        if updated is None:
            raise CountryNotFoundError(alpha3_code)
        return updated


def _normalise_code(alpha3_code: str) -> str:
    return alpha3_code.strip().upper()


def _build_document(data: CountryCreate) -> dict:
    doc = {
        "alpha3_code": data.alpha3_code,
        "alpha2_code": data.alpha2_code,
        "name": data.name,
        "capital": data.capital,
        "region": data.region,
        "subregion": data.subregion,
        "area": data.area,
        "population": data.population,
        "currencies": [c.model_dump() for c in data.currencies],
        "languages": [lang.model_dump() for lang in data.languages],
        "borders": [],
        "timezones": [],
        "top_level_domain": [],
        "calling_codes": [],
        "source": "manual",
    }
    if data.latitude is not None and data.longitude is not None:
        doc["location"] = {
            "type": "Point",
            "coordinates": [data.longitude, data.latitude],
        }
    return doc
