import uvicorn
from fastapi import FastAPI
import os

# load environment variables
port = os.environ["PORT"]

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


@app.get("/fixed/another")
def another():
    return {"datas": "Secret deploy!!!!!!!!"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
