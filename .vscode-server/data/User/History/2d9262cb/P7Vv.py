from tokenize import Double
from typing import Union,List
from fastapi import FastAPI,Body
from pydantic import BaseModel

fake_db = {
    "Nut" : {"name":"Nut","data":[1,2,3]}
}
app = FastAPI()
class Item(BaseModel):
    name: str
    data: List[float] = []

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.post("/items/",response_model=Item)
async def create_item(item: Item,key:str = Body(...)):
    print(item)
    fake_db[key] = item
    return {"result":1}