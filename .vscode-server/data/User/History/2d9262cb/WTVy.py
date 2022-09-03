from fastapi import FastAPI
from model import Item
app = FastAPI()


@app.get("/")
def root():
    return {"message": "Hello World"}

@app.post("/items/")
async def create_item(item: Item):
    return item