import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    mongo_uri: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    mongo_db_name: str = os.getenv("MONGO_DB_NAME", "country_server")
    app_port: int = int(os.getenv("APP_PORT", "8000"))
    countries_source_url: str = os.getenv(
        "COUNTRIES_SOURCE_URL", "https://www.apicountries.com/countries"
    )
    max_page_size: int = int(os.getenv("MAX_PAGE_SIZE", "100"))
    api_key: str = os.getenv("API_KEY", "changeme")


settings = Settings()
