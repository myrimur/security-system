from fastapi import FastAPI
from msgs import CameraInfo, CameraUrl, CameraLocation, CameraActivity, CameraId
import uvicorn
import requests
from cameras_db import CamerasDB
import logging
import time


class CameraController:
    def __init__(self):
        self.camera_service = CameraService()
        self.app = FastAPI()

        self.video_stream_service = "http://face-recognition-video-stream-service:8005"
        self.access_control_service = "http://face-recognition-access-service:8000"

        @self.app.get("/active_urls")
        def get_active_urls():
            active_urls = self.camera_service.get_active_urls()
            logging.info("ACTIVE URLS: " + str(active_urls))
            return active_urls

        @self.app.get("/locations")
        def get_locations():
            locations = self.camera_service.get_locations()
            logging.info("LOCATIONS: " + str(locations))
            return locations

        @self.app.post("/add_new_camera")
        def add_new_camera(msg: CameraInfo):
            self.camera_service.add_new_camera(msg)
            camera_url_msg = CameraUrl(camera_id=msg.camera_id, url=msg.url)
            camera_location_msg = CameraLocation(camera_id=msg.camera_id, location=msg.location)

            while True:
                try:
                    response = requests.post(self.video_stream_service + "/synchronize_new_camera", camera_url_msg.json())
                    if response.status_code:
                        break
                    logging.warning("problem with post request to: " + self.video_stream_service + "/synchronize_new_camera")
                    time.sleep(1)
                except:
                    logging.warning("problem with post request to: " + self.video_stream_service + "/synchronize_new_camera")
                    time.sleep(1)

            while True:
                try:
                    response = requests.post(self.access_control_service + "/synchronize_new_location", camera_location_msg.json())
                    if response.status_code:
                        break
                    logging.warning("problem with post request to: " + self.access_control_service + "/synchronize_new_location")
                    time.sleep(1)
                except:
                    logging.warning("problem with post request to: " + self.access_control_service + "/synchronize_new_location")
                    time.sleep(1)

            

        @self.app.post("/update_camera_url")
        def update_camera_url(msg: CameraUrl):
            self.camera_service.update_camera_url(msg)
            while True:
                try:
                    response = requests.post(self.video_stream_service + "/synchronize_camera_url", msg.json())
                    if response.status_code:
                        break
                    logging.warning("problem with post request to: " + self.video_stream_service + "/synchronize_camera_url")
                    time.sleep(1)
                except:
                    logging.warning("problem with post request to: " + self.video_stream_service + "/synchronize_camera_url")
                    time.sleep(1)

        @self.app.post("/update_camera_location")
        def update_camera_location(msg: CameraLocation):
            #check if operation is ok?
            self.camera_service.update_camera_location(msg)
            while True:
                try:
                    response = requests.post(self.access_control_service + "/synchronize_update_location", msg.json())
                    if response.status_code:
                        break
                    logging.warning("problem with post request to: " + self.access_control_service + "/synchronize_update_location")
                    time.sleep(1)
                except:
                    logging.warning("problem with post request to: " + self.access_control_service + "/synchronize_update_location")
                    time.sleep(1)

            

        @self.app.post("/update_camera_activity")
        def update_camera_activity(msg: CameraActivity):
            self.camera_service.update_camera_activity(msg)
            camera_id = CameraId(camera_id=msg.camera_id)
            camera_url = CameraUrl(camera_id=msg.camera_id, url=self.camera_service.get_url(camera_id))


            if bool(int(msg.is_active)):
                while True:
                    try:
                        response = requests.post(self.video_stream_service + "/synchronize_new_camera", camera_url.json())
                        if response.status_code:
                            break
                        logging.warning("problem with post request to: " + self.video_stream_service + "/synchronize_new_camera")
                        time.sleep(1)
                    except:
                        logging.warning("problem with post request to: " + self.video_stream_service + "/synchronize_new_camera")
                        time.sleep(1)
            else:
                while True:
                    try:
                        response = requests.post(self.video_stream_service + "/synchronize_inactive_camera", camera_id.json())
                        if response.status_code:
                            break
                        logging.warning("problem with post request to: " + self.video_stream_service + "/synchronize_inactive_camera")
                        time.sleep(1)
                    except:
                        logging.warning("problem with post request to: " + self.video_stream_service + "/synchronize_inactive_camera")
                        time.sleep(1)

               
                

        @self.app.post("/remove_camera")
        def remove_camera(msg: CameraId):
            self.camera_service.remove_camera(msg)
            while True:
                try:
                    response = requests.post(self.video_stream_service + "/synchronize_inactive_camera", msg.json())
                    if response.status_code:
                        break
                    logging.warning("problem with post request to: " + self.video_stream_service + "/synchronize_inactive_camera")
                    time.sleep(1)
                except:
                    logging.warning("problem with post request to: " + self.video_stream_service + "/synchronize_inactive_camera")
                    time.sleep(1)

            while True:
                try:
                    response = requests.post(self.access_control_service + "/synchronize_removed_camera", msg.json())
                    if response.status_code:
                        break
                    logging.warning("problem with post request to: " + self.access_control_service + "/synchronize_removed_camera")
                    time.sleep(1)
                except:
                    logging.warning("problem with post request to: " + self.access_control_service + "/synchronize_removed_camera")
                    time.sleep(1)

        

class CameraService:
    def __init__(self):
        self.database = CamerasDB()
    
    def get_active_urls(self):
        cameras_urls = self.database.select_active_cameras()
        msgs = []
        for (camera_id, url) in cameras_urls:
            msgs.append(CameraUrl(camera_id=camera_id, url=url))
        return msgs
    
    def get_locations(self):
        cameras_locations = self.database.select_all_cameras_locations()
        msgs = []
        for (camera_id, location) in cameras_locations:
            msgs.append(CameraLocation(camera_id=camera_id, location=location))
        return msgs
    
    def add_new_camera(self, msg: CameraInfo):
        self.database.insert_into_bd(msg)

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
            logging.warning("more than one camera with the same camera_id in database")
            return
        return urls[0][0]



acc = CameraController()
uvicorn.run(acc.app, host="0.0.0.0", port=8003)

