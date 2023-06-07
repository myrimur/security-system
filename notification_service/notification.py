import sys
sys.path.insert(1, '../')

from fastapi import FastAPI
import requests
import uvicorn
from msgs import Notification

class NotificationController:
    def __init__(self):
        self.notification_service = NotificationService()
        self.app = FastAPI()

        @self.app.post("/notification")
        async def receive_info(msgs: list[Notification]):
            self.notification_service.react(msgs)


class NotificationService:
    def react(self, msgs: list[Notification]):
        for msg in msgs:
            if msg.permission == "unknown person":
                print(f"Unknown person was spotted at location {msg.location} on camera {msg.camera_id} at {msg.appearance_time}")
            elif msg.permission == "forbidden person":
                print(f"Forbidden person {msg.person_name} was spotted at location {msg.location} on camera {msg.camera_id} at {msg.appearance_time}")
            else:
                print("Unknown permission")

serv = NotificationController()
uvicorn.run(serv.app, host = "0.0.0.0", port=8002)
