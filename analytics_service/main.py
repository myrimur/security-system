import asyncio
from collections import defaultdict
import requests
from fastapi import FastAPI

app = FastAPI()
stats = {}


async def get_alltime_stats(location: str):
    url = "http://face-recognition-logging-service:8004/appearances_by_location/" + location
    response = requests.get(url)

    appearances = defaultdict(int)
    for appearance in response.json():
        appearances[appearance['person_id']] += 1

    stats[location] = sorted(appearances.items(), key=lambda x: x[1], reverse=True)
    # stats[location] = appearances

async def scheduled_call(location: str):
    while True:
        await get_alltime_stats(location)
        await asyncio.sleep(1)


@app.on_event("startup")
async def startup_event():
    locations = ['entrance', 'hallway', 'server_room', 'office']  # TODO: retrieve from camera service
    for location in locations:
        asyncio.create_task(scheduled_call(location))


@app.get("/")
async def get():
    # return stats
    # url = "http://face-recognition-logging-service:8004/appearances_by_location/" + 'office'
    # response = requests.get(url)
    # stats = response.json()
    return stats
