import requests
from fastapi import FastAPI
import face_recognition
import cv2
import numpy as np
from datetime import datetime
import requests
import hazelcast
from msgs import EncodingMsg
import uvicorn
from threading import Thread


#     !!!!              !!!!
#     !!!!              !!!! 
#     !!!!  Hazelcast!  !!!!
#     !!!!              !!!!
#
#     !!!!              !!!!

#
#
# won't work without access service - change ports in urls
#
#

class IdentityController:
    def __init__(self):
        self.ident_serv = IdentityService()
        self.app = FastAPI()

        self.access_url = "http://127.0.0.1:8000/access_service"

        # TODO: ¿stupid¿
        t = Thread(target=self.ident_serv.detection_loop, daemon=True)
        t.start()
        

        @self.app.post("/identity_service")
        async def receive_permission(msg: EncodingMsg):
            self.ident_serv.save_encoding(msg.name, msg.encoding)


class IdentityService:
    '''
    inspired by documentation of face recognition
    '''
    def __init__(self):
        self.video_capture = self.get_camera()

        self.client = hazelcast.HazelcastClient()
        self.encodings_map = self.client.get_map("encodings-map").blocking()

        self.logging_url = "http://127.0.0.1:8000"
        self.access_url = "http://127.0.0.1:8000/access_service_check"

    def save_encoding(self, name, enc):
        self.encodings_map.put(name, enc)


    # TODO: think about it (should it be by request or every couple of seconds)
    # TODO x2: should it be in a loop?
    # TODO x3: should every name be a different request?
    def send_logs(self, names, time_ap):
        for name in names:
            requests.post(self.logging_url, json={
                "person_id": name,
                "camera_id": "0",           # dummy
                "location": "universe",     # dummy
                "appearance_time": time_ap
            })

    def send_recognised_names(self, names, time_ap):
        for name in names:
            requests.post(self.access_url, json={
                "person_id": name,
                "camera_id": "0",           # dummy
                "location": "universe",     # dummy
                "appearance_time": time_ap
            })



    @staticmethod
    def get_camera():
        # TODO: receive strean from message queue
        return cv2.VideoCapture(0)


    def detection_loop(self):
        face_locations = []
        face_encodings = []
        face_names = []
        process_this_frame = True

        while True:
            ret, frame = self.video_capture.read()

            if process_this_frame:
                now = datetime.now()
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

                rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

                face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

                face_names = []
                for face_encoding in face_encodings:
                    # TODO: hazelcast but seems baaad
                    known_faces_and_names = np.asarray(self.encodings_map.entry_set())
                    known_enc = []

                    if len(known_faces_and_names) == 0:
                        print("No names were registered!")
                        break

                    for i, (_, elem) in enumerate(known_faces_and_names):
                        known_enc.append(np.fromstring(elem[1:-1], sep=" "))

                    matches = face_recognition.compare_faces(known_enc, face_encoding)
                    name = "Unknown"

                    face_distances = face_recognition.face_distance(known_enc, face_encoding)
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = known_faces_and_names[best_match_index, 0]


                    face_names.append(name)
                
                print(f"Date and time: {now.strftime('%d/%m/%Y %H:%M:%S')} Faces detected: {face_names}")
                
                # TODO: add camera_id and location as in Appearance msg 
                # TODO x2: maybe not requests?
                if face_names:
                    self.send_logs(face_names, now.strftime('%d/%m/%Y %H:%M:%S'))
                    self.send_recognised_names(face_names, now.strftime('%d/%m/%Y %H:%M:%S'))

            # TODO: maybe will be managed by message queue
            process_this_frame = not process_this_frame

            for (top, right, bottom, left), name in zip(face_locations, face_names):
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

            # TODO: need to think if we want to see this
            cv2.imshow('Video', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.video_capture.release()
        cv2.destroyAllWindows()
        self.client.shutdown()

serv = IdentityController()
uvicorn.run(serv.app, host = "127.0.0.1", port=8001)
