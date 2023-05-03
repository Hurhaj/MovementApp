import uvicorn
import srtm
from fastapi import FastAPI
from pymongo import MongoClient
from pydantic import BaseModel
import os
from typing import List

class location(BaseModel):
    latitude: float
    longitude: float
# load environment variables
port = os.environ["PORT"]
#connection_string = "mongodb+srv://<username>:<password>@<cluster-name>.mongodb.net/<database-name>?retryWrites=true&w=majority"
#client = MongoClient(connection_string)
#db = client.<database-name>
#collection = db.<collection-name>

# initialize FastAPI
app = FastAPI()


@app.get("/")
def index():
    return {"data": "Application ran successfully - FastAPI V5! checkout apis: /hello /hens /another"}


@app.get("/hello")
def hello():
    return {"data": "Hello hens!"}


@app.get("/hens")
def hens():
    return {"data": "Hey hens!"}


@app.get("/fixed")
def another():
    return {"datas": "Secret deploy!!!!!!!!"}

@app.post("/elevation")
async def return_elevation(locations : List[location]):
    elevation_data = srtm.get_data()
    elevations = []
    for lo in locations:
        elevations.append(elevation_data.get_elevation(lo.latitude,lo.longitude))
    return elevations


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
