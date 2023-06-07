from fastapi import FastAPI
from msgs import CameraInfo, CameraUrl, CameraUrlList, CameraLocation, \
                    CameraLocationList, CameraActivity, CameraId
import uvicorn
import requests
from cameras_db import CamerasDB


class CameraController:
    def __init__(self):
        self.camera_service = CameraService()
        self.app = FastAPI()
        #create queue for lambda

        # TODO: change url to the real one
        self.video_stream_service = "http://face-recognition-video-stream-service:9000"
        #add synchronize_new_camera and synchronize_removed_camera to access_control_service
        self.access_control_service = "http://face-recognition-access-service:8000"

        @self.app.get("/active_urls")
        def get_active_urls():
            cameras_urls = self.camera_service.get_active_urls()
            return cameras_urls.json()

        @self.app.get("/locations")
        def get_locations():
            cameras_locations = self.camera_service.get_locations()
            return cameras_locations.json()

        @self.app.post("/add_new_camera")
        def add_new_camera(msg: CameraInfo):
            #check if operation is ok?
            msg_uuid = self.camera_service.add_new_camera(msg)

            camera_url_msg = CameraUrl(camera_id=msg_uuid, url=msg.url)
            camera_location_msg = CameraLocation(camera_id=msg_uuid, location=msg.location)

            requests.post(self.video_stream_service + "/synchronize_new_camera", camera_url_msg.json())
            #uncomment for access control service 
            # requests.post(self.access_control_service + "/synchronize_new_camera", camera_location_msg.json())

        @self.app.post("/update_camera_url")
        def update_camera_url(msg: CameraUrl):
            #check if operation is ok?
            self.camera_service.update_camera_url(msg)
            requests.post(self.video_stream_service + "/synchronize_camera_url", msg.json())

        @self.app.post("/update_camera_location")
        def update_camera_location(msg: CameraLocation):
            #check if operation is ok?
            self.camera_service.update_camera_location(msg)
            # requests.post(self.access_control_service + "/synchronize_camera_location", msg.json())

        @self.app.post("/update_camera_activity")
        def update_camera_activity(msg: CameraActivity):
            #check if operation is ok?
            self.camera_service.update_camera_activity(msg)
            camera_id = CameraId(camera_id=msg.camera_id)
            # print(self.camera_service.get_url(camera_id))
            camera_url = CameraUrl(camera_id=msg.camera_id, url=self.camera_service.get_url(camera_id))

            #should we manipulate active/inactive cameras in access control service???????
            #I think that no
            if bool(int(msg.is_active)):
               requests.post(self.video_stream_service + "/synchronize_new_camera", camera_url.json())
            else:
               requests.post(self.video_stream_service + "/synchronize_inactive_camera", camera_id.json())
                

        @self.app.post("/remove_camera")
        def remove_camera(msg: CameraId):
            #check if operation is ok?
            self.camera_service.remove_camera(msg)
            requests.post(self.video_stream_service + "/synchronize_inactive_camera", msg.json())
            # requests.post(self.access_control_service + "/synchronize_removed_camera", msg.json())

class CameraService:
    def __init__(self):
        self.database = CamerasDB()
    
    def get_active_urls(self):
        cameras_urls = self.database.select_active_cameras()
        msgs = []
        for (camera_id, url) in cameras_urls:
            # print(camera_id, url)
            msgs.append(CameraUrl(camera_id=camera_id, url=url))
        return CameraUrlList(each_camera_url=msgs)
    
    def get_locations(self):
        cameras_locations = self.database.select_all_cameras_locations()
        msgs = []
        for (camera_id, location) in cameras_locations:
            # print(camera_id, location)
            msgs.append(CameraLocation(camera_id=camera_id, location=location))
        return CameraLocationList(each_camera_location=msgs)
    
    def add_new_camera(self, msg: CameraInfo):
        return self.database.insert_into_bd(msg)

    def update_camera_url(self, msg: CameraUrl):
        self.database.update_url(msg)

    def update_camera_location(self, msg: CameraLocation):
        self.database.update_location(msg)

    def update_camera_activity(self, msg: CameraActivity):
        self.database.update_activity(msg)
    
    def remove_camera(self, msg: CameraId):
        self.database.remove_camera(msg)
    
    def get_url(self, msg: CameraId):
        urls = self.database.get_url(msg)
        if len(urls) > 1:
            print("error")
            return
        return urls[0][0]



acc = CameraController()
uvicorn.run(acc.app, host="0.0.0.0", port=8000)

