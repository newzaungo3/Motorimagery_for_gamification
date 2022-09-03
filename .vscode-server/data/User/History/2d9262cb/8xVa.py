from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
app = FastAPI()
class Item(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    tax: Union[float, None] = None
    

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.post("/items/")
async def create_item(item: Item):
    print(item)
    return {"result":1}