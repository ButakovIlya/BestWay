from typing import Dict

from pydantic import BaseModel


class RoutePlacesOrderUpdateDTO(BaseModel):
    order_dict: Dict[int, int]
