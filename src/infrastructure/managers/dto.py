
from pydantic import BaseModel, Field


class UserCreateDTO(BaseModel):
    user_id: int = Field(gt=0, alias="user_id")
    phone: str = Field(alias="phone")
    is_admin: bool = Field(alias="is_admin")
    
