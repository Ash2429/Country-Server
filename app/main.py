from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from strawberry.fastapi import GraphQLRouter

from app.db import create_client, get_database
from app.graphql.context import get_context
from app.graphql.schema import schema
from app.repositories.country_repository import CountryRepository
from app.repositories.ingestion_run_repository import IngestionRunRepository
from app.settings import settings

API_KEY_HEADER = "X-API-Key"


@asynccontextmanager
async def lifespan(app: FastAPI):
    client = create_client()
    app.state.mongo_client = client
    app.state.db = get_database(client)
    await CountryRepository(app.state.db).ensure_indexes()
    await IngestionRunRepository(app.state.db).ensure_indexes()
    yield
    client.close()


app = FastAPI(title="Country Server", lifespan=lifespan)


@app.middleware("http")
async def require_api_key(request: Request, call_next):
    if request.url.path.startswith("/graphql") and request.headers.get(API_KEY_HEADER) != settings.api_key:
        return JSONResponse({"detail": "Invalid or missing API key"}, status_code=401)
    return await call_next(request)


graphql_router = GraphQLRouter(schema, context_getter=get_context)
app.include_router(graphql_router, prefix="/graphql")


@app.get("/health")
async def health():
    return {"status": "ok"}
