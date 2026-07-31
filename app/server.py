import uvicorn

from app.settings import settings


def run() -> None:
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.app_port, workers=2)
