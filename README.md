# Testing

## Prerequisites

Mongo needs to be running before you test anything — startup builds indexes on
the `countries` collection (see the lifespan hook in `app/main.py`), so even
the `/health` check needs a live DB connection.

```bash
make up      # or: docker compose up -d mongo
```

## Running the tests

```bash
make test    # or: uv run pytest
```

## What's covered

- `tests/test_health.py` boots the app with `TestClient` and checks
  `GET /health` returns `200 {"status": "ok"}`. If Mongo isn't reachable it
  skips instead of failing, so `pytest` still passes on a machine without
  Mongo running.

## GraphQL

No automated tests for the resolvers yet — queries and mutations
(pagination, `country(id)`, `countriesNearby`, `countriesByLanguage`,
`addCountry`, `updateCountryName`, and their error cases) were checked
manually against a local Mongo instance. `schema.graphqls` has the current
schema. Adding resolver-level tests (e.g. with `mongomock`) is the obvious
next step.
