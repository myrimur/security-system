import asyncio
from collections import defaultdict
from datetime import date
import requests
from fastapi import FastAPI

app = FastAPI()
alltime_stats = {}
daily_stats = {}


async def process_stats(location: str, daily: bool = False):
    url = "http://face-recognition-logging-service:8004/appearances_by_location/" + location
    if daily:
        url += "/" + str(date.today())
    response = requests.get(url)

    appearances = defaultdict(int)
    for appearance in response.json():
        appearances[appearance['person_id']] += 1

    if daily:
        daily_stats[location] = sorted(appearances.items(), key=lambda x: x[1], reverse=True)
    else:
        alltime_stats[location] = sorted(appearances.items(), key=lambda x: x[1], reverse=True)


async def scheduled_call(location: str, daily: bool = False):
    while True:
        await process_stats(location, daily)
        await asyncio.sleep(1)


@app.on_event("startup")
async def startup_event():
    locations = ['entrance', 'hallway', 'server_room', 'office']  # TODO: retrieve from camera service
    for location in locations:
        asyncio.create_task(scheduled_call(location))
        asyncio.create_task(scheduled_call(location, daily=True))


@app.get("/alltime_stats")
async def get_alltime_stats():
    return alltime_stats


@app.get("/daily_stats")
async def get_daily_stats():
    return daily_stats
