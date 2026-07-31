import strawberry
from pydantic import ValidationError
from strawberry.types import Info

from app.graphql.context import GraphQLContext
from app.graphql.types import AddCountryInput, Country
from app.models.country import CountryCreate, Currency, Language


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def add_country(
        self, info: Info[GraphQLContext, None], input: AddCountryInput
    ) -> Country:
        try:
            data = CountryCreate(
                name=input.name,
                alpha3_code=input.alpha3_code,
                alpha2_code=input.alpha2_code,
                capital=input.capital,
                region=input.region,
                subregion=input.subregion,
                area=input.area,
                population=input.population,
                currencies=[
                    Currency(code=c.code, name=c.name, symbol=c.symbol)
                    for c in (input.currencies or [])
                ],
                languages=[
                    Language(
                        name=lang.name,
                        iso639_1=lang.iso639_1,
                        iso639_2=lang.iso639_2,
                        native_name=lang.native_name,
                    )
                    for lang in (input.languages or [])
                ],
                latitude=input.latitude,
                longitude=input.longitude,
            )
        except ValidationError as exc:
            raise ValueError(_describe_first_error(exc)) from None

        doc = await info.context.service.add_country(data)
        return Country.from_document(doc)

    @strawberry.mutation
    async def update_country_name(
        self, info: Info[GraphQLContext, None], id: str, name: str
    ) -> Country:
        doc = await info.context.service.update_country_name(id, name)
        return Country.from_document(doc)


def _describe_first_error(exc: ValidationError) -> str:
    error = exc.errors()[0]
    field = ".".join(str(part) for part in error["loc"])
    return f"{field}: {error['msg']}"
