from fastapi import Request
from strawberry.fastapi import BaseContext

from app.graphql.loaders import CountryLoader
from app.repositories.country_repository import CountryRepository
from app.services.country_service import CountryService


class GraphQLContext(BaseContext):
    def __init__(self, repository: CountryRepository):
        super().__init__()
        self.service = CountryService(repository)
        self.country_loader = CountryLoader(repository)


async def get_context(request: Request) -> GraphQLContext:
    repository = CountryRepository(request.app.state.db)
    return GraphQLContext(repository)
