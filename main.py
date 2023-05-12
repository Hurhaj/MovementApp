from typing import List

import requests as req
import srtm
import uvicorn
from fastapi import FastAPI
from google.auth.transport import requests
from pydantic import BaseModel
from pymongo import MongoClient


class Location(BaseModel):
    latitude: float
    longitude: float


class Delete(BaseModel):
    token: str
    ID: str


class Authenticated(BaseModel):
    email: str
    error: bool


class RoutePoints(BaseModel):
    latitude: float
    longitude: float
    altitude: float


class Activity(BaseModel):
    ID: str
    sport_type: str
    date: str
    distance: int
    time: str
    max_speed: int
    average_speed: int
    data: List[RoutePoints]


class SynchronizationRequest(BaseModel):
    token: str
    IDs: List[str]


class SynchronizationAnswer(BaseModel):
    activities: List[Activity]
    IDs: List[str]


class NewActitivityReceive(BaseModel):
    activities: List[Activity]


# load environment variables
# port = os.environ["PORT"]
authentication_api = "https://authenticationmicroservice.azurewebsites.net/authenticate"
connection_string = "mongodb+srv://user:user@cluster0.hbniblw.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(connection_string)
db = client["userdata"]

# initialize FastAPI
app = FastAPI()


@app.get("/")
def index():
    return {"data": "Application ran successfully -version 0.0.2"}


@app.post("/mongo")
async def put(user: str):
    doc = {"user": user}
    try:
        news = db["users"].insert_one(doc)
        return "done"
    except Exception as e:
        return e + "error"


@app.post("/erase")
async def erase(deleteactivity: Delete):
    # send request to authentication microservice,where params is jwt token...in this case, deleteactivity
    authenticated = req.post(authentication_api, params=deleteactivity.token)
    if authenticated.status_code == 200:
        return {"authentication": "SUCCESS"}


def return_elevation(locations: List[Location]):
    elevation_data = srtm.get_data()
    elevations = []
    for lo in locations:
        elevations.append(elevation_data.get_elevation(lo.latitude, lo.longitude))
    return elevations


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
