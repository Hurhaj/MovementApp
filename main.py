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

class location(BaseModel):
    latitude: float
    longitude: float

class delete(BaseModel):
    token: string
    ID: string

# load environment variables
port = os.environ["PORT"]
#connection_string = "mongodb+srv://<username>:<password>@<cluster-name>.mongodb.net/<database-name>?retryWrites=true&w=majority"
#client = MongoClient(connection_string)
#db = client.<database-name>
#collection = db.<collection-name>
public_keys_url = "https://www.googleapis.com/oauth2/v1/certs"
public_keys = requests.get(public_keys_url).json()
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

@app.post("/erase")
async def erase(deleteactivity : delete):
    kid = jwt.get_unverified_header(deleteactivity.token).get("kid")
    public_key = public_keys.get(kid)
    try:
        decoded_token = jwt.decode(
            id_token,
            public_key,
            algorithms=["RS256"],
            audience="168397874560-5uso2lk8p5pa43h3sb3eg9futfisese0.apps.googleusercontent.com"  # replace with your client ID
        )
        # ID token is valid
        print("ID token is valid.")
        # Extract user information from the decoded token as needed
        user_id = decoded_token.get("sub")
        email = decoded_token.get("email")
        # ...
    except jwt.exceptions.InvalidSignatureError:
        return "Invalid_token_error"
    except jwt.exceptions.DecodeError:
       return  "Decode_error"

    return "error"
@app.post("/elevation")
async def return_elevation(locations : List[location]):
    elevation_data = srtm.get_data()
    elevations = []
    for lo in locations:
        elevations.append(elevation_data.get_elevation(lo.latitude,lo.longitude))
    return elevations

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
