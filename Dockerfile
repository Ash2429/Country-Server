FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    PATH="/code/.venv/bin:$PATH"

WORKDIR /code

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

COPY app ./app

COPY scheduler.sh ./scheduler.sh
RUN chmod +x ./scheduler.sh

RUN uv sync --frozen --no-dev

EXPOSE 8000


ENTRYPOINT ["app"]
CMD ["server"]
