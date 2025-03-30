import re
from enum import Enum

from domain.entities.enums import CityCategory, ModelType, PlaceCategory, PlaceType


def enum_regex(enum_cls: type[Enum]) -> str:
    """Создаёт regex с перечислением всех .value через |"""
    return "^(" + "|".join(map(re.escape, [e.value for e in enum_cls])) + ")$"


any_printable_characters_regex = r".*\S.*"
coordinates_regex = r"^\[\s*-?\d+(\.\d+)?\s*,\s*-?\d+(\.\d+)?\s*\]$"
json_regex = r"^\{.*\}$"
datetime_iso_regex = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"

RESOURCE_REGEX_DICT: dict[ModelType, dict[str, str]] = {
    ModelType.PLACES: {
        "name": any_printable_characters_regex,
        "city": enum_regex(CityCategory),
        "category": enum_regex(PlaceCategory),
        "type": enum_regex(PlaceType),
        "tags": any_printable_characters_regex,
        "coordinates": coordinates_regex,
        "photo": any_printable_characters_regex,
        "map_name": any_printable_characters_regex,
        "json": json_regex,
    },
    ModelType.ROUTES: {
        "name": any_printable_characters_regex,
        "created_at": datetime_iso_regex,
        "updated_at": datetime_iso_regex,
        "duration": r"^\d+$",
        "distance": r"^\d+$",
        "json": json_regex,
    },
}


class ModelRegexGetter:
    def __init__(self, model: ModelType) -> None:
        self._regex_dict = RESOURCE_REGEX_DICT.get(model)

    def get_field_regex(self, field: str) -> str | None:
        if not self._regex_dict:
            return None
        return self._regex_dict.get(field)

    def get_regex_dict(self) -> dict:
        return self._regex_dict if self._regex_dict else {}
