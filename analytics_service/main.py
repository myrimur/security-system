import asyncio
import requests
from fastapi import FastAPI

app = FastAPI()


async def get_alltime_stats():
    url = "http://127.0.0.1:8004/appearances_by_person_id/3d1ab1d4-ba42-45fe-9394-1a2a1f5376dc"
    response = requests.get(url)
    # process the response here
    print(response.json())


async def scheduled_call():
    while True:
        await get_alltime_stats()
        await asyncio.sleep(60)


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(scheduled_call())
