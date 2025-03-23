from pydantic import BaseModel, ConfigDict, Field


class CheckHealthSchema(BaseModel):
    status: str


class UserDTO(BaseModel):
    id: int = Field(gt=0, alias="user_id")
    phone: str = Field(alias="sub")

    model_config = ConfigDict(extra="ignore")
