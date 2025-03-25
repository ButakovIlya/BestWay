



from pydantic import BaseModel


class UserFileFiels(BaseModel):
    photo: str = "photo"


from enum import Enum

class ModelType(str, Enum):
    USERS = "users"