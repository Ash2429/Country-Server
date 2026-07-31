from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.ingestion_run import IngestionRun


class IngestionRunRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self._collection = db["ingestion_runs"]

    async def ensure_indexes(self) -> None:
        await self._collection.create_index([("started_at", -1)])

    async def record(self, run: IngestionRun) -> None:
        await self._collection.insert_one(run.model_dump())
