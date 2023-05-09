
import face_recognition
from fastapi import FastAPI
from msgs import Appearance, Permission
import requests
import uvicorn

class AccessControlController:
    def __init__(self):
        self.access_serv = AccessControlService()
        self.app = FastAPI()

        self.identity_url = "http://127.0.0.1:8001/identity_service"

        
        @self.app.post("/access_service_check")
        async def check_permission(msg: Appearance):
            res = self.access_serv.check_person(msg.person_id)
            print(f"Person {msg.person_id} detected at {msg.appearance_time}, conclusion={res}")

        @self.app.post("/access_service")
        def send_encoding_data(msg: Permission):
            enc = self.access_serv.get_encodings(msg.image_path)
            self.access_serv.save_permission(msg.name, msg.permission)
            print("post, acces")
            requests.post(self.identity_url, json={"name": msg.name,
                                                    "encoding": str(enc)})


class AccessControlService:
    def __init__(self):
        pass 

    def get_encodings(self, ref_img_path):
        person_image = face_recognition.load_image_file(ref_img_path)
        person_face_encoding = face_recognition.face_encodings(person_image, model="large", num_jitters=100)[0]

        return person_face_encoding
    
    def check_person(self, name):
        # TODO: MySQL
        with open("temp_permission.csv", 'r', encoding="utf-8") as perms:
            lines = perms.readlines()

        perm_dict = {}
        for line in lines:
            temp = line.strip().split(',')
            perm_dict[temp[0]] = temp[1]

        if name == "Unknown":
            return "very bad"

        #TODO: come up with permissions
        if perm_dict[name] == "Allowed":
            return "good"
        elif perm_dict[name] == "Not allowed":
            return "bad"
        else:
            return "so so"
    
    def save_permission(self, name, permission):
        # TODO: MySQL
        with open("temp_permission.csv", 'a', encoding="utf-8") as perms:
            perms.writelines(f"{name},{permission}\n")



acc = AccessControlController()
uvicorn.run(acc.app)

# acc.send_encoding_data("photo_2023-02-22_21-33-46.jpg", "Dasha", "Allowed")