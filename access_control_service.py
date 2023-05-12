import face_recognition
from fastapi import FastAPI
from msgs import Appearance, Permission, CameraInfo
import requests
import uvicorn
from database_class import PermissionsDB

DEBUG = True


class AccessControlController:
    def __init__(self):
        self.access_serv = AccessControlService()
        self.app = FastAPI()

        self.identity_url = "http://127.0.0.1:8001/identity_service"
       
        # TODO: change url to the real one
        self.notification_serv_url = "http://127.0.0.1:8001/notification_service"
        self.camera_serv_url = "http://127.0.0.1:8001/camera_service"

    


        @self.app.post("/access_service_check")
        async def check_permission(msg: Appearance):
            '''
            POST request that is received from identity service
            
            Check person's permission
            '''
            res = self.access_serv.check_person(msg.person_id, msg.camera_id)
            print(f"Person {msg.person_id} detected at {msg.appearance_time}, conclusion={res}")

            if res != "ok":
                requests.post(self.notification_serv_url, json={"person_id": msg.person_id,
                                                        "camers_id": msg.camera_id,
                                                        "location": msg.location,
                                                        "appearance_time": msg.appearance_time,
                                                        "permission": res})


        @self.app.post("/access_service")
        def send_encoding_data(msg: Permission):
            '''
            POST request that is received when new encoding needs to be saved

            *not sure if to do this like this or not*
            '''
            enc = self.access_serv.get_encodings(msg.image_path)
            self.access_serv.save_permission(msg.name, msg.permission, msg.camera_id)
            requests.post(self.identity_url, json={"name": msg.name,
                                                    "encoding": str(enc)})
            
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
        if not DEBUG:
            self.perm_database = PermissionsDB()

    def get_encodings(self, ref_img_path):
        '''
        return encoding from an image
        '''
        person_image = face_recognition.load_image_file(ref_img_path)
        person_face_encoding = face_recognition.face_encodings(person_image, model="large", num_jitters=100)[0]

        return person_face_encoding
    
    def check_person(self, name, camera_id):
        '''
        check person's permissions or if unknown 

        *will be changed*
        '''

        if name == "Unknown":
            return "unknown person"
        
        if DEBUG:
            with open("temp_permission.csv", 'r', encoding="utf-8") as perms:
                lines = perms.readlines()

                perm = -1
                for line in lines:
                    temp = line.strip().split(',')
                    
                    if temp[0] == name and temp[1] == camera_id:
                        perm = int(temp[2])
                        break
                
                if perm == -1:
                    print("error csv")
                    return "error csv"
        else:

            result = self.perm_database.select_person(name, camera_id)

            if len(result) > 1 or len(result) == 0:
                print("error db")
                return "error"
            
            perm = result[0][1]

        # TODO: come up with permissions
        if perm == 0:
            return "ok"
        elif perm == 1:
            return "forbidden person"
        else:
            return "unknown permission"
    
    def save_permission(self, name, permission, camera_id):
        if DEBUG:
            with open("temp_permission.csv", 'a', encoding="utf-8") as perms:
                perms.writelines(f"{name},{permission},{camera_id}\n")
        else:
            self.perm_database.insert_into_bd(name, permission, camera_id)


acc = AccessControlController()
uvicorn.run(acc.app)
