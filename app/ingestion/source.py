import httpx

from app.settings import settings


async def fetch_countries() -> list[dict]:
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        response = await client.get(settings.countries_source_url)
        response.raise_for_status()
        return response.json()
