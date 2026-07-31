class CountryNotFoundError(Exception):
    def __init__(self, alpha3_code: str):
        super().__init__(f"No country found with alpha3Code '{alpha3_code}'")
        self.alpha3_code = alpha3_code


class DuplicateCountryError(Exception):
    def __init__(self, alpha3_code: str):
        super().__init__(f"A country with alpha3Code '{alpha3_code}' already exists")
        self.alpha3_code = alpha3_code
