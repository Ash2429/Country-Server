import re
from collections.abc import Iterator
from datetime import UTC, datetime

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReturnDocument, UpdateOne

from app.models.documents import CountryDocument, CurrencyGroupDocument, NearbyCountryDocument

UPSERT_BATCH_SIZE = 100


def _chunked(items: list[dict], size: int) -> Iterator[list[dict]]:
    for i in range(0, len(items), size):
        yield items[i : i + size]


class CountryRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self._collection = db["countries"]

    async def ensure_indexes(self) -> None:
        await self._collection.create_index("alpha3_code", unique=True)
        await self._collection.create_index([("location", "2dsphere")])
        await self._collection.create_index("languages.iso639_1")
        await self._collection.create_index("name")

    async def find_page(self, limit: int, offset: int) -> tuple[list[CountryDocument], int]:
        cursor = self._collection.find().sort("alpha3_code", 1).skip(offset).limit(limit)
        items = [CountryDocument.model_validate(doc) async for doc in cursor]
        total = await self._collection.count_documents({})
        return items, total

    async def find_by_alpha3_code(self, alpha3_code: str) -> CountryDocument | None:
        doc = await self._collection.find_one({"alpha3_code": alpha3_code})
        return CountryDocument.model_validate(doc) if doc else None

    async def find_many_by_alpha3_codes(self, alpha3_codes: list[str]) -> list[CountryDocument]:
        cursor = self._collection.find({"alpha3_code": {"$in": alpha3_codes}})
        return [CountryDocument.model_validate(doc) async for doc in cursor]

    async def find_nearby(
        self, longitude: float, latitude: float, limit: int
    ) -> list[NearbyCountryDocument]:
        pipeline = [
            {
                "$geoNear": {
                    "near": {"type": "Point", "coordinates": [longitude, latitude]},
                    "distanceField": "distance_m",
                    "spherical": True,
                }
            },
            {"$limit": limit},
        ]
        return [
            NearbyCountryDocument.model_validate(doc)
            async for doc in self._collection.aggregate(pipeline)
        ]

    async def find_by_language(self, language: str) -> list[CountryDocument]:
        pattern = f"^{re.escape(language.strip())}$"
        cursor = self._collection.find(
            {
                "$or": [
                    {"languages.name": {"$regex": pattern, "$options": "i"}},
                    {"languages.iso639_1": {"$regex": pattern, "$options": "i"}},
                ]
            }
        )
        return [CountryDocument.model_validate(doc) async for doc in cursor]

    async def insert(self, doc: dict) -> CountryDocument:
        now = datetime.now(UTC)
        doc = {**doc, "created_at": now, "updated_at": now}
        await self._collection.insert_one(doc)
        return CountryDocument.model_validate(doc)

    async def update_name(self, alpha3_code: str, name: str) -> CountryDocument | None:
        doc = await self._collection.find_one_and_update(
            {"alpha3_code": alpha3_code},
            {"$set": {"name": name, "updated_at": datetime.now(UTC)}},
            return_document=ReturnDocument.AFTER,
        )
        return CountryDocument.model_validate(doc) if doc else None

    async def upsert_many(self, docs: list[dict], batch_size: int = UPSERT_BATCH_SIZE) -> int:
        if not docs:
            return 0

        now = datetime.now(UTC)
        upserted_count = 0
        for batch in _chunked(docs, batch_size):
            operations = [
                UpdateOne(
                    {"alpha3_code": doc["alpha3_code"]},
                    {"$set": {**doc, "updated_at": now}, "$setOnInsert": {"created_at": now}},
                    upsert=True,
                )
                for doc in batch
            ]
            result = await self._collection.bulk_write(operations, ordered=False)
            upserted_count += result.upserted_count
        return upserted_count

    async def group_by_currency(self) -> list[CurrencyGroupDocument]:
        pipeline = [
            {"$unwind": "$currencies"},
            {"$match": {"currencies.code": {"$ne": None}}},
            {
                "$group": {
                    "_id": "$currencies.code",
                    "currency_name": {"$first": "$currencies.name"},
                    "currency_symbol": {"$first": "$currencies.symbol"},
                    "country_count": {"$sum": 1},
                    "countries": {"$push": {"id": "$alpha3_code", "name": "$name"}},
                }
            },
            {"$sort": {"_id": 1}},
        ]
        return [
            CurrencyGroupDocument.model_validate(doc)
            async for doc in self._collection.aggregate(pipeline)
        ]
