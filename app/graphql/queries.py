import strawberry
from strawberry.types import Info

from app.graphql.context import GraphQLContext
from app.graphql.types import Country, CountryDistance, CountryPage, CurrencyGroup


@strawberry.type
class Query:
    @strawberry.field
    async def countries(
        self, info: Info[GraphQLContext, None], limit: int = 25, offset: int = 0
    ) -> CountryPage:
        items, total = await info.context.service.list_countries(limit=limit, offset=offset)
        return CountryPage(
            items=[Country.from_document(doc) for doc in items],
            total_count=total,
            limit=limit,
            offset=offset,
        )

    @strawberry.field
    async def country(self, info: Info[GraphQLContext, None], id: str) -> Country | None:
        doc = await info.context.country_loader.load(id.strip().upper())
        return Country.from_document(doc) if doc else None

    @strawberry.field
    async def countries_nearby(
        self,
        info: Info[GraphQLContext, None],
        latitude: float,
        longitude: float,
        limit: int = 5,
    ) -> list[CountryDistance]:
        results = await info.context.service.get_countries_nearby(
            latitude=latitude, longitude=longitude, limit=limit
        )
        return [
            CountryDistance(country=Country.from_document(doc), distance_km=distance_km)
            for doc, distance_km in results
        ]

    @strawberry.field
    async def countries_by_language(
        self, info: Info[GraphQLContext, None], language: str
    ) -> list[Country]:
        docs = await info.context.service.get_countries_by_language(language)
        return [Country.from_document(doc) for doc in docs]

    @strawberry.field
    async def countries_by_currency(
        self, info: Info[GraphQLContext, None]
    ) -> list[CurrencyGroup]:
        groups = await info.context.service.get_countries_by_currency()
        return [CurrencyGroup.from_document(group) for group in groups]
