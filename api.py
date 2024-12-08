from fastapi import FastAPI
from pydantic import BaseModel
import requests
import uvicorn
app = FastAPI()



@app.get("/")
def read_root():
    fetchh = requests.get("https://randomuser.me/api/").json()
    lst= [
    {
    "id": "123",
    "signup_ts": "2017-06-01 12:22"
    },
    {
    "id": "123",
    "signup_ts": "2017-06-01 12:22"
    }
]
    lst.append(fetchh)
    return lst


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}


if __name__ == "__main__":
    uvicorn.run(app=app)