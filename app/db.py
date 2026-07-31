from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.settings import settings


def create_client() -> AsyncIOMotorClient:
    return AsyncIOMotorClient(settings.mongo_uri)


def get_database(client: AsyncIOMotorClient) -> AsyncIOMotorDatabase:
    return client[settings.mongo_db_name]
