from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UserDataDTO(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=255)
    phone: str = Field(..., min_length=10, max_length=15)
