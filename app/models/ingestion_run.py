from datetime import datetime

from pydantic import BaseModel


class IngestionRun(BaseModel):
    started_at: datetime
    finished_at: datetime
    fetched_count: int
    valid_count: int
    skipped_count: int
    inserted_count: int
    updated_count: int
    error: str | None = None
