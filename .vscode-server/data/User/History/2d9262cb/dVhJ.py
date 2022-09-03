from tokenize import Double
from typing import Union,List
from fastapi import FastAPI,Body
from pydantic import BaseModel

app = FastAPI()
class Item(BaseModel):
    name: str
    data: List[List[float]]

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.post("/items/",response_model=Item)
async def create_item(item: Item):
    print(item)
    return {"result":1}