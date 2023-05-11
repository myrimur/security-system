import face_recognition
from fastapi import FastAPI
from msgs import Appearance, Permission
import requests
import uvicorn
from database_class import PermissionsDB

DEBUG = False


class AccessControlController:
    def __init__(self):
        self.access_serv = AccessControlService()
        self.app = FastAPI()

        self.identity_url = "http://127.0.0.1:8001/identity_service"

        
        @self.app.post("/access_service_check")
        async def check_permission(msg: Appearance):
            '''
            POST request that is received from identity service
            
            Check person's permission
            '''
            res = self.access_serv.check_person(msg.person_id)
            print(f"Person {msg.person_id} detected at {msg.appearance_time}, conclusion={res}")


        @self.app.post("/access_service")
        def send_encoding_data(msg: Permission):
            '''
            POST request that is received when new encoding needs to be saved

            *not sure if to do this like this or not*
            '''
            enc = self.access_serv.get_encodings(msg.image_path)
            self.access_serv.save_permission(msg.name, msg.permission)
            requests.post(self.identity_url, json={"name": msg.name,
                                                    "encoding": str(enc)})


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
    
    def check_person(self, name):
        '''
        check person's permissions or if unknown 

        *will be changed*
        '''
        if DEBUG:
            with open("temp_permission.csv", 'r', encoding="utf-8") as perms:
                lines = perms.readlines()

                perm_dict = dict()
                for line in lines:
                    temp = line.strip().split(',')
                    perm_dict[temp[0]] = temp[1]
        else:

            result = self.perm_database.select_person(name)[:][1:]

            perm_dict = dict(result)

        if name == "Unknown":
            return "very bad"

        #TODO: come up with permissions
        if perm_dict[name] == 0:
            return "good"
        elif perm_dict[name] == 1:
            return "bad"
        else:
            return "so so"
    
    def save_permission(self, name, permission):
        if DEBUG:
            with open("temp_permission.csv", 'a', encoding="utf-8") as perms:
                perms.writelines(f"{name},{permission}\n")
        else:
            self.perm_database.insert_into_bd(name, permission)


acc = AccessControlController()
uvicorn.run(acc.app)
