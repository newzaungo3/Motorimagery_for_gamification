from pydantic import BaseModel
from typing import Union

from fastapi import FastAPI

class Item(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    tax: Union[float, None] = None