from glob import glob
from collections import defaultdict
from cassandra.cluster import Cluster
from cassandra.query import dict_factory
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Appearance(BaseModel):
    person_id: str
    camera_id: str
    location: str
    appearance_time: str


cluster = Cluster(['face-recognition-cassandra-node-1'])
session = cluster.connect('appearances')
session.row_factory = dict_factory


@app.get("/healthcheck")
async def healthcheck():
    return {"status": "ok"}


@app.post("/")
async def store_appearance(appearances: list[Appearance]):
    futures = []
    for a in appearances:
        for table in ["by_person_id", "by_location", "by_camera_id"]:
            futures.append(session.execute_async(
                f"INSERT INTO {table} (person_id, camera_id, location, appearance_time)"
                f" VALUES ({a.person_id}, {a.camera_id}, '{a.location}', '{a.appearance_time}')"
            ))

    for future in futures:
        future.result()

    return {"message": "Data stored successfully."}


@app.on_event("shutdown")
async def shutdown_event():
    session.shutdown()
    cluster.shutdown()


@app.get("/appearances_by_person_id/{person_id}")
async def get_appearances_by_person_id(person_id: str):
    return list(session.execute(f"SELECT * FROM by_person_id WHERE person_id = {person_id}"))


@app.get("/{day}")
async def get(day: str):
    return list(session.execute(f"SELECT * FROM by_person_id WHERE appearance_time >= '{day}' AND appearance_time <= '{day} 23:59:59'"))


@app.get("/")
async def get():
    try:
        with open(glob('/opt/app/results/*.json')[0]) as f:
            dicts = [eval(line.rstrip()) for line in f]
            merged = defaultdict(list)
            for d in dicts:
                merged[d['location']] += [{d['person_id']: d['total_appearances']}]
            return merged
    except IndexError:
        return {"message": "No analytics yet."}


@app.get("/appearances_by_person_id/{person_id}/{day}")
async def get_appearances_by_person_id(person_id: str, day: str):
    return list(session.execute(f"SELECT * FROM by_person_id WHERE person_id = {person_id} AND appearance_time >= '{day}' AND appearance_time <= '{day} 23:59:59'"))


@app.get("/appearances_by_location/{location}")
async def get_appearances_by_location(location: str):
    return list(session.execute(f"SELECT * FROM by_location WHERE location = '{location}'"))


@app.get("/appearances_by_location/{location}/{day}")
async def get_appearances_by_location(location: str, day: str):
    return list(session.execute(f"SELECT * FROM by_location WHERE location = '{location}' AND appearance_time >= '{day}' AND appearance_time <= '{day} 23:59:59'"))


@app.get("/appearances_by_camera_id/{camera_id}")
async def get_appearances_by_camera_id(camera_id: str):
    return list(session.execute(f"SELECT * FROM by_camera_id WHERE camera_id = {camera_id}"))


@app.get("/appearances_by_camera_id/{camera_id}/{day}")
async def get_appearances_by_camera_id(camera_id: str, day: str):
    return list(session.execute(f"SELECT * FROM by_camera_id WHERE camera_id = {camera_id} AND appearance_time >= '{day}' AND appearance_time <= '{day} 23:59:59'"))
