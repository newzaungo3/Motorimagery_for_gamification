import requests



data = {
    "name":"bitch",
    "price": 200
}

requests.post("http://localhost:8000/items")