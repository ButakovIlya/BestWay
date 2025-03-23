from domain.entities.enums import ResourceErrorType

from pydantic import BaseModel


class ResourceDTO(BaseModel):
    class Config:
        from_attributes = True


class CreateLocationDTO(ResourceDTO):
    imp_location_id: str
    location_description: str
    location_code: str
    region: str
    division: str
    imp_location_type: str


class UpdateLocationDTO(CreateLocationDTO):
    id: int


class LocationListResponseDTO(UpdateLocationDTO):
    has_duplicate_error: bool
    error_type: ResourceErrorType | None
