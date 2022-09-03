from typing import Union,List
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
class Item(BaseModel):
    name: str
    data: List[int] = []

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.post("/items/")
async def create_item(item: Item):
    print(item)
    return {"result":1}