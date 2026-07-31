from strawberry.dataloader import DataLoader

from app.models.documents import CountryDocument
from app.repositories.country_repository import CountryRepository


class CountryLoader(DataLoader[str, CountryDocument | None]):
    def __init__(self, repository: CountryRepository):
        super().__init__(load_fn=self._batch_load)
        self._repository = repository

    async def _batch_load(self, alpha3_codes: list[str]) -> list[CountryDocument | None]:
        docs = await self._repository.find_many_by_alpha3_codes(alpha3_codes)
        by_code = {doc.alpha3_code: doc for doc in docs}
        return [by_code.get(code) for code in alpha3_codes]
