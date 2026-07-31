# Country Server

GraphQL service for ingesting and querying country data, backed by MongoDB.

## Architecture

- **`app/graphql`** — Strawberry schema, queries, and mutations. Each request
  gets its own `GraphQLContext` (`app/graphql/context.py`) holding a
  `CountryService` and a `CountryLoader`.
- **`app/services`** — business rules and input validation
  (`CountryService`), independent of both GraphQL and Mongo specifics.
- **`app/repositories`** — the only layer that talks to Motor/MongoDB
  (`CountryRepository`, `IngestionRunRepository`); owns index creation and
  query/aggregation pipelines (`$geoNear`, currency grouping, etc.).
- **`app/models`** — `country.py` holds inbound schemas (`CountryIn` from the
  source API, `CountryCreate` from the `addCountry` mutation);
  `documents.py` holds the outbound schemas read back from Mongo.
- **DataLoader** — `country(id)` resolves through `CountryLoader`
  (`strawberry.dataloader.DataLoader`), so multiple `country(id)` lookups in
  one GraphQL request batch into a single `$in` query instead of N
  round-trips.
- **`app/ingestion`** — the sync job is decoupled from the API process:
  `source.py` fetches from `COUNTRIES_SOURCE_URL`, `sync.py` validates each
  record and upserts via `CountryRepository.upsert_many`, then records an
  `IngestionRun`. Triggered by `app cron` (see Makefile) or, in Docker
  Compose, the `scheduler.sh` loop (every 30 minutes) — a separate container
  from `api`.
- **`app/main.py`** — wires the FastAPI app, mounts the GraphQL router, and
  gates `/graphql` behind an `X-API-Key` header check.

## Running it

### Quickstart (Docker Compose)

```bash
cp .env.example .env   # adjust values if needed
make up                 # docker compose up -d: mongo + api + scheduler
```

- GraphQL: `http://localhost:8000/graphql`, requires an `X-API-Key` header
  matching `API_KEY` (see Configuration below).
- Health check (no API key needed): `curl http://localhost:8000/health`
- The `scheduler` container runs `app cron` on a loop (`scheduler.sh`, every
  30 minutes) in its own container, separate from `api`.

Other Compose targets: `make down`, `make build`, `make logs`.

### Local development

```bash
make install            # uv sync
docker compose up -d mongo   # only Mongo, run the API/cron locally instead
make run                 # uv run uvicorn app.main:app --reload
```

### Running the ingestion job manually

```bash
make cron                # uv run app cron — fetches, validates, and
                          # upserts countries, then records an IngestionRun
```

### Regenerating the schema file

```bash
make schema               # regenerates schema.graphqls from the live schema
```

## Configuration

Environment variables (see `.env.example`), all optional with defaults baked
into `app/settings.py`:

| Variable | Default | Purpose |
|---|---|---|
| `MONGO_URI` | `mongodb://localhost:27017` | Mongo connection string |
| `MONGO_DB_NAME` | `country_server` | Database name |
| `APP_PORT` | `8000` | Port the API listens on |
| `COUNTRIES_SOURCE_URL` | `https://www.apicountries.com/countries` | Ingestion source (currently redirects to `countries.dev`) |
| `MAX_PAGE_SIZE` | `100` | Cap on `limit` args for paginated/nearby queries |
| `API_KEY` | `changeme` | Required `X-API-Key` header value for `/graphql` |
