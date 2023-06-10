import sys
sys.path.insert(1, '../')

from typing import List
import face_recognition
from fastapi import FastAPI
from msgs import Appearance, Permission, CameraLocation, CameraId
import requests
import uvicorn
from database_class import PermissionsDB
import warnings

class AccessControlController:
    def __init__(self):
        self.access_serv = AccessControlService()
        self.app = FastAPI()

        self.identity_url = "http://face-recognition-identity-service:8001/identity_service"
        self.notification_serv_url = "http://face-recognition-notification-service:8002/notification"

        self.camera_serv_url = "http://face-recognition-camera-service:8003/locations"

        # sync to get initial cameras
        msgs_res = requests.get(self.camera_serv_url)

        for msg in msgs_res.json():
            self.access_serv.save_location(msg["camera_id"], msg["location"])


        @self.app.post("/access_service_check")
        async def check_permission(msgs: List[Appearance]):
            '''
            POST request that is received from identity service
            
            Check person's permission
            '''
            to_send = []
            for msg in msgs:
                res = self.access_serv.check_person(msg.person_id, msg.camera_id)
                location = self.access_serv.get_location(msg.camera_id)
                if res == "Unknown":
                    to_send.append({"person_id": msg.person_id,
                                    "person_name": "Unknown",
                                    "camera_id": msg.camera_id,
                                    "location": location,
                                    "appearance_time": msg.appearance_time,
                                    "permission": "unknown person"})
                else:
                    if res[0] != "ok":
                        to_send.append({"person_id": msg.person_id,
                                        "person_name": res[1],
                                        "camera_id": msg.camera_id,
                                        "location": location,
                                        "appearance_time": msg.appearance_time,
                                        "permission": res[0]})
            
            if to_send:
                headers = {'Content-Type': 'application/json'}

                requests.post(self.notification_serv_url, json=to_send, headers=headers)
                        

        @self.app.post("/access_service")
        def send_encoding_data(msg: Permission):
            '''
            POST request that is received when new encoding needs to be saved

            *not sure if to do this like this or not*
            '''
            if self.access_serv.check_if_in_bd(msg.name, msg.camera_id):
                enc = self.access_serv.get_encodings(msg.image_path)
                uuid = self.access_serv.save_permission(msg.name, msg.permission, msg.camera_id)
                requests.post(self.identity_url, json={"person_id": uuid,
                                                        "encoding": str(enc.tolist())})
            else:
                print(f"Person {msg.name} and camera {msg.camera_id} are in bd already")

        
        @self.app.post("/synchronize_new_location")
        def sync_camera_receive(msg: CameraLocation):
            self.access_serv.save_location(msg.camera_id, msg.location)
        
        @self.app.post("/synchronize_update_location")
        def req_update_location(msg: CameraLocation):
            print("start synchronize_update_location")
            self.access_serv.update_location(msg.camera_id, msg.location)
            print("end synchronize_update_location")

        @self.app.post("/synchronize_removed_camera")
        def req_remove_location(msg: CameraId):
            self.access_serv.remove_location(msg.camera_id)


class AccessControlService:
    def __init__(self):
        self.perm_database = PermissionsDB()

    def check_if_in_bd(self, name, camera_id):
        return not bool(self.perm_database.select_person(name, camera_id))
    
    def get_location(self, camera_id):
        result = self.perm_database.select_location_name(camera_id)

        if len(result) > 1:
            raise ValueError("Too many entries in db: {result}")
        
        if len(result) == 0:
            warnings.warn("Locations database is empty")

        return result

    def save_location(self, camera_id, location_name):
        self.perm_database.save_location_name(camera_id, location_name)


    def get_encodings(self, ref_img_path):
        '''
        return encoding from an image
        '''
        person_image = face_recognition.load_image_file(ref_img_path)
        person_face_encoding = face_recognition.face_encodings(person_image, model="large", num_jitters=100)[0]

        return person_face_encoding
    
    def check_person(self, uuid, camera_id):
        '''
        check person's permissions or if unknown 
        '''
        result = self.perm_database.select_uuid(uuid, camera_id)

        if len(result) > 1:
            raise ValueError("Too many entries in db: {result}")
                
        if len(result) == 0:
            return ("Unknown")
        
        perm = result[0][1]
        name = result[0][0]


        if perm == 0:
            return ("ok", name)
        elif perm == 1:
            return ("forbidden person", name)
        else:
            return ("unknown permission", name)
    
    def save_permission(self, name, permission, camera_id):
        return self.perm_database.insert_into_bd(name, permission, camera_id)

    def check_if_location_in_bd(self, camera_id):
        return not bool(self.perm_database.select_location_name(camera_id))
    

    def update_location(self, camera_id, location_name):
        print("before if")
        if self.check_if_location_in_bd(camera_id):
            print("if")
            self.perm_database.update_location(camera_id, location_name)
        print("after if")

    def remove_location(self, camera_id):
        if self.check_if_location_in_bd(camera_id):
            self.perm_database.remove_location(camera_id)

acc = AccessControlController()
uvicorn.run(acc.app, host = "0.0.0.0", port=8000)
