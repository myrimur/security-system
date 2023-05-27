import sys
sys.path.insert(1, '../')

import face_recognition
from fastapi import FastAPI
from msgs import Appearance, Permission, CameraInfo
import requests
import uvicorn
from database_class import PermissionsDB


class AccessControlController:
    def __init__(self):
        self.access_serv = AccessControlService()
        self.app = FastAPI()

        self.identity_url = "http://127.0.0.1:8001/identity_service"
        self.notification_serv_url = "http://127.0.0.1:8002/notification"

        # TODO: change url to the real one
        self.camera_serv_url = "http://127.0.0.1:8001/camera_service"


        @self.app.post("/access_service_check")
        async def check_permission(msgs: list[Appearance]):
            '''
            POST request that is received from identity service
            
            Check person's permission
            '''
            to_send = []
            for msg in msgs:
                res = self.access_serv.check_person(msg.person_id, msg.camera_id)
                if res == "Unknown":
                    to_send.append({"person_id": msg.person_id,
                                    "person_name": "Unknown",
                                    "camera_id": msg.camera_id,
                                    "location": msg.location,
                                    "appearance_time": msg.appearance_time,
                                    "permission": "unknown person"})
                else:
                    if res[0] != "ok":
                        to_send.append({"person_id": msg.person_id,
                                        "person_name": res[1],
                                        "camera_id": msg.camera_id,
                                        "location": msg.location,
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
                                                        "encoding": str(enc)})
            else:
                print(f"Person {msg.name} and camera {msg.camera_id} are in bd already")


        @self.app.post("/access_service_add_camera")
        def save_camera(msg: CameraInfo):
            '''
            POST request that is received when new encoding needs to be saved

            *not sure if to do this like this or not*
            '''
            requests.post(self.camera_serv_url, json={"camera_id": msg.camera_id,
                                                      "location": msg.location})


class AccessControlService:
    def __init__(self):
        self.perm_database = PermissionsDB()

    def check_if_in_bd(self, name, camera_id):
        return not bool(self.perm_database.select_person(name, camera_id))


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
            print(f"Error: too many entries in db: {result}")
            return "error"
                
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


acc = AccessControlController()
uvicorn.run(acc.app, host = "127.0.0.1", port=8000)
