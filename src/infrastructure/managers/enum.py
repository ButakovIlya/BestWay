from enum import Enum


class UserFileFiels(Enum):
    PHOTO: str = "photo"


class ModelType(str, Enum):
    USERS = "users"
