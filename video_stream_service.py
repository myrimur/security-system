from fastapi import FastAPI
from msgs import CameraUrl, CameraId
import uvicorn

class VideoStreamController:
    def __init__(self):
        self.video_stream_service = VideoStreamService()
        self.app = FastAPI()

        @self.app.post("/synchronize_new_camera")
        def synchronize_new_camera(msg: CameraUrl):
            #add meesage to queue
            self.video_stream_service.synchronize_new_camera(msg)

        @self.app.post("/synchronize_camera_url")
        def synchronize_camera_url(msg: CameraUrl):
            #add meesage to queue
            self.video_stream_service.synchronize_camera_url(msg)

        @self.app.post("/synchronize_inactive_camera")
        def synchronize_inactive_camera(msg: CameraId):
            #add meesage to queue
            #in case when camera is not active now or was removed from DB
            self.video_stream_service.synchronize_inactive_camera(msg)

class VideoStreamService:
    def __init__(self):
        self.urls = SynchronizedUrls()
    
    def synchronize_new_camera(self, msg: CameraUrl):
        self.urls.add_new(msg)
        print("SYNCHRONIZED")
        print(msg)

    def synchronize_camera_url(self, msg: CameraUrl):
        self.urls.change_url(msg)

    def synchronize_inactive_camera(self, msg: CameraId):
        self.urls.remove(msg)

class SynchronizedUrls:
    def __init__(self):
        self.dict = dict() 

    def add_new(self, msg: CameraUrl):
        if msg.camera_id in self.dict:
            print("error")
            return
        self.dict[msg.camera_id] = msg.url

    def remove(self, msg: CameraUrl):
        if msg.camera_id not in self.dict:
            print("error")
            return
        self.dict.pop(msg.camera_id)

    def change_url(self, msg: CameraUrl):
        if msg.camera_id not in self.dict:
            print("error")
            return
        self.dict[msg.camera_id] = msg.url


acc = VideoStreamController()
uvicorn.run(acc.app, host="127.0.0.1", port=9000)

