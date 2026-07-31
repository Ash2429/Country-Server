import logging
from dataclasses import dataclass
from datetime import UTC, datetime

from pydantic import ValidationError

from app.db import create_client, get_database
from app.ingestion.source import fetch_countries
from app.models.country import CountryIn
from app.models.ingestion_run import IngestionRun
from app.repositories.country_repository import CountryRepository
from app.repositories.ingestion_run_repository import IngestionRunRepository

logger = logging.getLogger(__name__)


@dataclass
class SyncStats:
    fetched_count: int = 0
    valid_count: int = 0
    skipped_count: int = 0
    inserted_count: int = 0
    updated_count: int = 0


async def sync_countries(repository: CountryRepository) -> SyncStats:
    raw_countries = await fetch_countries()
    logger.info("fetched %d countries from source", len(raw_countries))

    documents = []
    for raw in raw_countries:
        try:
            documents.append(CountryIn.model_validate(raw).to_document())
        except ValidationError as exc:
            logger.warning("skipping invalid country record %r: %s", raw.get("name"), exc)

    inserted = await repository.upsert_many(documents)
    stats = SyncStats(
        fetched_count=len(raw_countries),
        valid_count=len(documents),
        skipped_count=len(raw_countries) - len(documents),
        inserted_count=inserted,
        updated_count=len(documents) - inserted,
    )
    logger.info(
        "sync complete: %d valid, %d skipped, %d newly inserted, %d updated",
        stats.valid_count,
        stats.skipped_count,
        stats.inserted_count,
        stats.updated_count,
    )
    return stats


async def run_sync_job() -> None:
    client = create_client()
    try:
        db = get_database(client)
        repository = CountryRepository(db)
        run_repository = IngestionRunRepository(db)
        await repository.ensure_indexes()
        await run_repository.ensure_indexes()

        started_at = datetime.now(UTC)
        error: str | None = None
        stats = SyncStats()
        try:
            stats = await sync_countries(repository)
        except Exception as exc:
            error = str(exc)
            raise
        finally:
            await run_repository.record(
                IngestionRun(
                    started_at=started_at,
                    finished_at=datetime.now(UTC),
                    fetched_count=stats.fetched_count,
                    valid_count=stats.valid_count,
                    skipped_count=stats.skipped_count,
                    inserted_count=stats.inserted_count,
                    updated_count=stats.updated_count,
                    error=error,
                )
            )
    finally:
        client.close()
