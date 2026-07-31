.PHONY: help install run cron up down build logs test schema

help:
	@echo "install  - uv sync (create/update the local venv)"
	@echo "run      - run the API locally with uv --reload (needs mongo reachable, e.g. via 'make up')"
	@echo "cron     - run the country sync job once, locally (app cron)"
	@echo "up       - docker compose up -d (mongo + api + scheduler)"
	@echo "down     - docker compose down"
	@echo "build    - docker compose build"
	@echo "logs     - tail docker compose logs"
	@echo "test     - uv run pytest"
	@echo "schema   - regenerate schema.graphqls from the live Strawberry schema"

install:
	uv sync

run:
	uv run uvicorn app.main:app --reload

cron:
	uv run app cron

up:
	docker compose up -d

down:
	docker compose down

build:
	docker compose build

logs:
	docker compose logs -f

test:
	uv run pytest

schema:
	uv run python -c "from app.graphql.schema import schema; open('schema.graphqls', 'w', encoding='utf-8').write(schema.as_str() + '\n')"
