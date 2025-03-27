from pydantic import BaseModel, ConfigDict, Field

from infrastructure.permissions.enums import RoleEnum


class CheckHealthSchema(BaseModel):
    status: str


class UserDTO(BaseModel):
    id: int = Field(gt=0, alias="user_id")
    phone: str = Field(alias="phone")
    is_admin: bool = Field(alias="is_admin")
    role: RoleEnum = Field(alias="role")

    model_config = ConfigDict(extra="ignore")
