import uvicorn
import srtm
from fastapi import FastAPI
from pymongo import MongoClient
from pydantic import BaseModel
import os
import jwt
import requests
from typing import List
from datetime import datetime, timezone
from google.oauth2 import id_token
from google.auth.transport import requests

class Location(BaseModel):
    latitude: float
    longitude: float

class Delete(BaseModel):
    token: str
    ID: str

class Authenticated(BaseModel):
    email: str
    error: bool


class Routepoints(BaseModel):
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
    data: List[Routepoints]

class Synchronizationrequest(BaseModel):
    token: str
    IDs: List[str]

class Synchronizationanswer(BaseModel):
    activities: List[Activity]
    IDs: List[str]

class Newactitivityreceive(BaseModel):
    activities: List[Activity]
# load environment variables
port = os.environ["PORT"]
connection_string = "mongodb+srv://user:user@cluster0.hbniblw.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(connection_string)
db = client["userdata"]

# initialize FastAPI
app = FastAPI()


@app.get("/")
def index():
    return {"data": "Application ran successfully - FastAPI V5! checkout apis: /hello /hens /another"}

@app.post("/mongo")
async def put(user:str):
    doc = {"user": user}
    try:
        news = db["users"].insert_one(doc)
        return "done"
    except Exception as e:
        return e+"error"

@app.post("/erase")
async def erase(deleteactivity : Delete):
    return authentificate(deleteactivity.token)
def return_elevation(locations : List[Location]):
    elevation_data = srtm.get_data()
    elevations = []
    for lo in locations:
        elevations.append(elevation_data.get_elevation(lo.latitude,lo.longitude))
    return elevations
def authentificate(token:str):
    try:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), "168397874560-5uso2lk8p5pa43h3sb3eg9futfisese0.apps.googleusercontent.com")
        expiration_time = datetime.fromtimestamp(idinfo['exp'], timezone.utc)
        if datetime.now(timezone.utc) >= expiration_time:
            return Authenticated(email="token expired", error=True)
        return Authenticated(email=idinfo["email"], error=False)
    except jwt.exceptions.InvalidSignatureError:
        return Authenticated(email="Invalid_token_error", error=True)
    except jwt.exceptions.DecodeError:
        return Authenticated(email="Decode_error", error=True)
    except jwt.exceptions.InvalidTokenError:
        return Authenticated(email="Invalid_token_error", error=True)
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
