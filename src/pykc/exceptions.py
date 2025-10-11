class DataError(Exception): ...


class IntegrityError(DataError): ...


class MultiplicityError(DataError): ...


class ValidationError(Exception):
    def __init__(self, errors: list[tuple[str, str]]):
        super().__init__("Data validation failed: " + str(errors))


class PatternError(Exception):
    def __init__(self):
        super().__init__("no matching case for pattern")
