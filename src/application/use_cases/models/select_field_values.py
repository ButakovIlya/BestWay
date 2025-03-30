from application.use_cases.base import UseCase
from domain.entities.enums import ModelType
from domain.validators.model_regex import ModelRegexGetter


class SelectFieldValuesUseCase(UseCase):
    """Get values for select field."""

    async def execute(self, model: ModelType, field_name: str) -> list[str]:
        field_regex = ModelRegexGetter(model).get_field_regex(field_name) or ""
        return field_regex.strip("^$()").split("|")
