import json
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
    user: str
    elevationversion: bool
    def to_dict(self):
        return self.dict()
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
    user: str
    sport_type: str
    date: str
    distance: int
    time: str
    max_speed: int
    average_speed: int
    data: List[RoutePoints]
    def to_dict(self):
        return self.dict()

class SynchronizationRequest(BaseModel):
    ID: str
    user: str
    def to_dict(self):
        return self.dict()
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
    return {"data": "Application ran successfully -version 0.0.10"}

@app.post("/syncreq")
async def syncreq(sync:List[SynchronizationRequest],token:str):
    auth = await authenticate(token)
    if auth == "error":
        return "token invalid"
    else:
        if not sync:
            sync.append(SynchronizationRequest(ID="none",user=auth))
            my_json = json.dumps([obj.dict() for obj in sync])
            ans = req.post(Database_api + "syncreq", data=my_json)
            json_data = ans.json()
            return json_data
        for id in sync:
            if authorize(auth, id.user):
                continue
            else:
                sync.remove(id)
        if not sync:
            return "not Authorized"
        else:
            my_json = json.dumps([obj.dict() for obj in sync])
            print(my_json)
            ans = req.post(Database_api + "syncreq", data=my_json)
            json_data = ans.json()
            return json_data
@app.post("/newactivities")
async def newactivities (newac: List[Activity], token:str):
    auth = await authenticate(token)
    print(auth)
    if auth == "error":
        return "token invalid"
    else:
        for id in newac:
            if authorize(auth, id.user):
                continue
            else:
                newac.remove(id)
        if not newac:
            return "not Authorized"
        else:
            my_json = json.dumps([activity.dict() for activity in newac])
            ans = req.post(Database_api+"newactivities", data=my_json)
            json_data = ans.json()
            return json_data
@app.post("/synccheck")
async def synccheck(syncc: List[Elevationcheck], token:str):
    auth = await authenticate(token)
    if(auth == "error"):
        return "token invalid"
    else:
        for id in syncc:
            if authorize(auth, id.user):
                continue
            else:
                syncc.remove(id)
        if not syncc:
            return "not Authorized"
        else:
            my_json = json.dumps([activity.dict() for activity in syncc])
            ans = req.post(Database_api+"synccheck", data=my_json)
            json_data = ans.json()
            return json_data
@app.post("/delete")
async def delete(deleteid: str,user: str, token: str):
    auth = await authenticate(token)
    if auth == "error":
        return "token invalid"
    else:
        if authorize(auth, user):
            payload = {"deleteid": deleteid, "user": user}
            ans = req.post(Database_api+"delete", params=payload)
            json_data = ans.json()
            return json_data
        else:
            return "not Authorized"
async def authenticate(token: str):
    payload = {"token": token}
    try:
        ans = req.post(authentication_api, params=payload)
    except Exception as e:
        print(e)
    content = ans.text
    try:
        obj = json.loads(content)
        if obj["error"]:
            return "error"
        else:
            return obj["msg"]
    except Exception as e:
        print(e)
        return "error"
def authorize(user: str, IDactivity: str):
    if user == IDactivity:
        return True
    else:
        return False
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
