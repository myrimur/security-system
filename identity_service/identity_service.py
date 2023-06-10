import sys
from contextlib import asynccontextmanager

sys.path.insert(1, '../')

import requests
from fastapi import FastAPI
import face_recognition
import numpy as np
from datetime import datetime
from msgs import EncodingMsg
import uvicorn
from multiprocessing import Process

from uuid import uuid4

from kafka import KafkaConsumer
import pickle
from msgs import FrameEncodings
from encodings_map import EncodingsMap


class IdentityController:
    def __init__(self):
        print('IdentityController init')
        self.ident_serv = IdentityService()
        self.app = FastAPI(lifespan=self.ident_serv.lifespan)

        self.access_url = "http://face-recognition-access-service:8000/access_service"

        @self.app.post("/identity_service")
        async def receive_permission(msg: EncodingMsg):
            self.ident_serv.save_encoding(msg.person_id, msg.encoding)


class IdentityService:
    '''
    inspired by documentation of face recognition
    '''

    def __init__(self):
        print('encoding map init')
        self.encodings_map = EncodingsMap()

        self.logging_url = "http://face-recognition-logging-service:8004"
        self.access_url = "http://face-recognition-access-service:8000/access_service_check"


    def save_encoding(self, uuid_id, enc):
        self.encodings_map.add_new(uuid_id, enc)

    def send_logs(self, uuids, time_ap, camera_id):
        lst = []
        for uuid_id in uuids:
            lst.append({
            "person_id": uuid_id,
            "camera_id": camera_id,        
            "location": "it space",     # dummy
            "appearance_time": time_ap
            })

        headers = {'Content-Type': 'application/json'}

        print("TO LOGGING: ", lst)

        requests.post(self.logging_url, json=lst, headers=headers)

    def send_recognised_names(self, uuids, time_ap, camera_id):
        lst = []
        for uuid_id in uuids:
            lst.append({
            "person_id": uuid_id,
            "camera_id": camera_id,          
            "appearance_time": time_ap
            })
        headers = {'Content-Type': 'application/json'}

        print("TO ACCESS: ", lst)
        
        requests.post(self.access_url, json=lst, headers=headers)

    def detection_loop(self):
        encodings_map = EncodingsMap()
        unknown_count = 0
        consumer = KafkaConsumer('frame_encodings',
                            value_deserializer=lambda v: FrameEncodings.parse_obj(pickle.loads(v)),
                            bootstrap_servers=['kafka:19092'])
        
        
        while True:
            for message in consumer:
                face_uuids = []
                for face_encoding in message.value.encodings:
                    print("DONE")
                    known_faces_and_names = encodings_map.get_entry_set()
                    known_enc = []

                    if len(known_faces_and_names) == 0:
                        print("No names were registered!")
                        name = "Unknown"
                    else:
                        for i, (_, elem) in enumerate(known_faces_and_names):
                            known_enc.append(np.fromstring(elem[1:-1], sep=", "))

                        matches = face_recognition.compare_faces(known_enc, np.array(face_encoding))
                        name = "Unknown"

                        face_distances = face_recognition.face_distance(known_enc, np.array(face_encoding))
                        best_match_index = np.argmin(face_distances)
                        if matches[best_match_index]:
                            name = known_faces_and_names[best_match_index, 0]

                    if name == "Unknown":
                        name = str(uuid4())
                        encodings_map.add_new(name, str(face_encoding))
                        unknown_count += 1

                    face_uuids.append(name)


                
                print(f"Date and time: {message.value.datetime} Faces detected: {face_uuids}")
                
                if face_uuids:
                    self.send_logs(face_uuids, message.value.datetime, message.value.camera_id)
                    self.send_recognised_names(face_uuids, message.value.datetime, message.value.camera_id)

    @asynccontextmanager
    async def lifespan(self, app):
        p = Process(target=self.detection_loop)
        p.start()
        yield
        p.join()


if __name__ == "__main__":
    serv = IdentityController()
    uvicorn.run(serv.app, host="0.0.0.0", port=8001)

