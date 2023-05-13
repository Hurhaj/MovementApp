from typing import List

import requests as req
import srtm
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from pymongo import MongoClient

class Elevationdata(BaseModel):
    ID: str
    elevation: List[float]
class Elevationcheck(BaseModel):
    ID: str
    elevationversion: bool
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


class SynchronizationAnswer(BaseModel):
    activities: List[Activity]
    IDs: List[str]


class NewActitivityReceive(BaseModel):
    activities: List[Activity]


# load environment variables
# port = os.environ["PORT"]
authentication_api = "https://authenticationmicroservice.azurewebsites.net/authenticate"
Database_api = "https://mongorepositoryservice.azurewebsites.net/"
connection_string = "mongodb+srv://user:user@cluster0.hbniblw.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(connection_string)
db = client["userdata"]

# initialize FastAPI
app = FastAPI()


@app.get("/")
def index():
    return {"data": "Application ran successfully -version 0.0.5"}

@app.post("/syncreq")
async def syncreq(sync:List[str],token:str):
    auth = authenticate(token)
    if (auth == "error"):
        return "token invalid"
    else:
        for id in sync:
            if (authorize(auth, id)):
                continue
            else:
                sync.remove(id)
        if not sync:
            return "not Authorized"
        else:
            ans = await req.post(Database_api + "syncreq", data=sync)
            return ans
@app.post("/newactivities")
async def newactivities (newac: List[Activity], token:str):
    auth = authenticate(token)
    if (auth == "error"):
        return "token invalid"
    else:
        for id in newac:
            if (authorize(auth, id.ID)):
                continue
            else:
                newac.remove(id.ID)
        if not newac:
            return "not Authorized"
        else:
            ans = await req.post(Database_api+"newactivities", data=newac)
            return ans
@app.post("/synccheck")
async def synccheck(syncc: List[Elevationcheck], token:str):
    auth = authenticate(token)
    if(auth == "error"):
        return "token invalid"
    else:
        for id in syncc:
            if (authorize(auth, id.ID)):
                continue
            else:
                syncc.remove(id.ID)
        if not syncc:
            return "not Authorized"
        else:
            ans = await req.post(Database_api+"synccheck", data=syncc)
            return ans
@app.post("/delete")
async def delete(deleteid: str, token: str):
    auth = authenticate(token)
    if auth == "error":
        return "token invalid"
    else:
        if authorize(auth, deleteid):
            payload = {"deleteid": deleteid}
            ans = await req.post(Database_api+"delete", data=payload)
            return ans
        else:
            return "not Authorized"
async def authenticate(token: str):
    payload = {"token": token}
    authenticated: Authenticated = await req.post(authentication_api, params=payload)
    if authenticated.error:
        return "error"
    else:
        return authenticated.email
def authorize(user: str, IDactivity: str):
    if user == IDactivity:
        return True
    else:
        return False
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
