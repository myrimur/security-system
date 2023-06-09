# # import sys
# # sys.path.insert(1, '../')
# #
# # import requests
# # from fastapi import FastAPI
# # import face_recognition
# # import cv2
# # import numpy as np
# # from datetime import datetime
# # import hazelcast
# # from msgs import EncodingMsg
# # import uvicorn
# # from threading import Thread
# #
# # from uuid import uuid4
# #
# #
# # class IdentityController:
# #     def __init__(self):
# #         self.ident_serv = IdentityService()
# #         self.app = FastAPI()
# #
# #         self.access_url = "http://face-recognition-access-service:8000/access_service"
# #
# #         t = Thread(target=self.ident_serv.detection_loop, daemon=True)
# #         t.start()
# #
# #
# #         @self.app.post("/identity_service")
# #         async def receive_permission(msg: EncodingMsg):
# #             self.ident_serv.save_encoding(msg.person_id, msg.encoding)
# #
# #
# # class IdentityService:
# #     '''
# #     inspired by documentation of face recognition
# #     '''
# #     def __init__(self):
# #         self.video_capture = self.get_camera()
# #
# #         self.client = hazelcast.HazelcastClient(cluster_members=['face-recognition-hazelcast-node-1:5701'])
# #         self.encodings_map = self.client.get_map("encodings-map").blocking()
# #
# #         self.logging_url = "http://face-recognition-logging-service:8004"
# #         self.access_url = "http://face-recognition-access-service:8000/access_service_check"
# #
# #     def save_encoding(self, uuid_id, enc):
# #         self.encodings_map.put(uuid_id, enc)
# #
# #
# #     def send_logs(self, uuids, time_ap):
# #         lst = []
# #         for uuid_id in uuids:
# #             if uuid_id == "Unknown":
# #                 uuid_id = str(uuid4())
# #             lst.append({
# #             "person_id": uuid_id,
# #             "camera_id": "6d52f90e-0177-4796-9fc7-536a9bff1ddb",           # dummy
# #             "location": "it space",     # dummy
# #             "appearance_time": time_ap
# #             })
# #
# #         headers = {'Content-Type': 'application/json'}
# #
# #         requests.post(self.logging_url, json=lst, headers=headers)
# #
# #     def send_recognised_names(self, uuids, time_ap):
# #         lst = []
# #         for uuid_id in uuids:
# #             if uuid_id == "Unknown":
# #                 uuid_id = str(uuid4())
# #             lst.append({
# #             "person_id": uuid_id,
# #             "camera_id": "6d52f90e-0177-4796-9fc7-536a9bff1ddb",           # dummy
# #             "location": "it space",     # dummy
# #             "appearance_time": time_ap
# #             })
# #         headers = {'Content-Type': 'application/json'}
# #
# #         requests.post(self.access_url, json=lst, headers=headers)
# #
# #
# #
# #     @staticmethod
# #     def get_camera():
# #         # TODO: receive strean from message queue
# #         return cv2.VideoCapture(0)
# #
# #
# #     def detection_loop(self):
# #         face_locations = []
# #         face_encodings = []
# #         face_uuids = []
# #         process_this_frame = True
# #
# #         while True:
# #             ret, frame = self.video_capture.read()
# #
# #             if process_this_frame:
# #                 now = datetime.now()
# #                 small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
# #
# #                 rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
# #
# #                 face_locations = face_recognition.face_locations(rgb_small_frame)
# #                 face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
# #
# #                 face_uuids = []
# #                 for face_encoding in face_encodings:
# #                     known_faces_and_names = np.asarray(self.encodings_map.entry_set())
# #                     known_enc = []
# #
# #                     if len(known_faces_and_names) == 0:
# #                         print("No names were registered!")
# #                         face_uuids.append("Unknown")
# #                         break
# #
# #                     for i, (_, elem) in enumerate(known_faces_and_names):
# #                         known_enc.append(np.fromstring(elem[1:-1], sep=" "))
# #
# #                     matches = face_recognition.compare_faces(known_enc, face_encoding)
# #                     name = "Unknown"
# #
# #                     face_distances = face_recognition.face_distance(known_enc, face_encoding)
# #                     best_match_index = np.argmin(face_distances)
# #                     if matches[best_match_index]:
# #                         name = known_faces_and_names[best_match_index, 0]
# #
# #
# #                     face_uuids.append(name)
# #
# #                 print(f"Date and time: {now.strftime('%Y-%m-%d %H:%M:%S')} Faces detected: {face_uuids}")
# #
# #                 # TODO: add camera_id and location as in Appearance msg
# #                 if face_uuids:
# #                     self.send_logs(face_uuids, now.strftime('%Y-%m-%d %H:%M:%S'))
# #                     self.send_recognised_names(face_uuids, now.strftime('%Y-%m-%d %H:%M:%S'))
# #
# #             # TODO: maybe will be managed by message queue
# #             process_this_frame = not process_this_frame
# #
# #             # for (top, right, bottom, left), name in zip(face_locations, face_uuids):
# #             #     top *= 4
# #             #     right *= 4
# #             #     bottom *= 4
# #             #     left *= 4
# #             #
# #             #     cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
# #             #
# #             #     cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
# #             #     font = cv2.FONT_HERSHEY_DUPLEX
# #             #     cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
# #             #
# #             # # TODO: need to think if we want to see this
# #             # cv2.imshow('Video', frame)
# #             #
# #             # if cv2.waitKey(1) & 0xFF == ord('q'):
# #             #     break
# #
# #         # self.video_capture.release()
# #         # cv2.destroyAllWindows()
# #         # self.client.shutdown()
# #
# #     def __del__(self):
# #         self.video_capture.release()
# #         self.client.shutdown()
# #
# #
# # serv = IdentityController()
# # uvicorn.run(serv.app, host = "127.0.0.1", port=8001)

import sys
from contextlib import asynccontextmanager

sys.path.insert(1, '../')

import requests
from fastapi import FastAPI
import face_recognition
import numpy as np
from datetime import datetime
import hazelcast
from msgs import EncodingMsg
import uvicorn
from threading import Thread
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

        # t = Thread(target=self.ident_serv.detection_loop, daemon=True)
        # t = Process(target=self.ident_serv.detection_loop)
        # t.start()

        @self.app.post("/identity_service")
        async def receive_permission(msg: EncodingMsg):
            self.ident_serv.save_encoding(msg.person_id, msg.encoding)
            # print("IDENTITY POST REQUEST")


class IdentityService:
    '''
    inspired by documentation of face recognition
    '''

    def __init__(self):
        print('encoding map init')
        self.encodings_map = EncodingsMap()
        # self.client = hazelcast.HazelcastClient(cluster_members=['face-recognition-hazelcast-node-1:5701'])
        # print("hazelcast done")
        # self.encodings_map = self.client.get_map("encodings-map").blocking()
        # print("encoding map done")

        self.logging_url = "http://face-recognition-logging-service:8004"
        self.access_url = "http://face-recognition-access-service:8000/access_service_check"


    def save_encoding(self, uuid_id, enc):
        self.encodings_map.add_new(uuid_id, enc)

    def send_logs(self, uuids, time_ap, camera_id):
        # print("send logs start")
        lst = []
        for uuid_id in uuids:
            lst.append({
            "person_id": uuid_id,
            "camera_id": camera_id,        
            "location": "it space",     # dummy
            "appearance_time": time_ap
            })

        headers = {'Content-Type': 'application/json'}
        ##### add error codes?

        print("TO LOGGING: ", lst)

        requests.post(self.logging_url, json=lst, headers=headers)
        # print("send logs end")

    def send_recognised_names(self, uuids, time_ap, camera_id):
        # print("send_recognised_names start")
        lst = []
        for uuid_id in uuids:
            lst.append({
            "person_id": uuid_id,
            "camera_id": camera_id,          
            "location": "it space",     # dummy
            "appearance_time": time_ap
            })
        headers = {'Content-Type': 'application/json'}

        print("TO ACCESS: ", lst)
        
        ##### add error codes?
        requests.post(self.access_url, json=lst, headers=headers)
        # print("send_recognised_names end")

    # def deal_with_unknown(self, face_uuids, unknown_count):
    #     for i, (uuid, _) in enumerate(face_uuids):
    #         if uuid == "Unknown":
    #             face_uuids[i][0] = str(uuid4())
    #             self.encodings_map.add_new(face_uuids[i][0], face_uuids[i][1])
    #             unknown_count += 1

    #     return unknown_count

    def detection_loop(self):
        # face_uuids = []
        encodings_map = EncodingsMap()
        unknown_count = 0
        # print("before consumer")
        consumer = KafkaConsumer('frame_encodings',
                            value_deserializer=lambda v: FrameEncodings.parse_obj(pickle.loads(v)),
                            bootstrap_servers=['kafka:19092'])
        

        # print('consumer done')
        # print('in fn')

        
        while True:
            for message in consumer:
                # print('consumed')
                # print(message.value.camera_id)
                # print(message.value.datetime)
                # print(message.value.encodings)
                face_uuids = []
                for face_encoding in message.value.encodings:
                    print("DONE")
                    known_faces_and_names = encodings_map.get_entry_set()
                    known_enc = []

                    if len(known_faces_and_names) == 0:
                        print("No names were registered!")
                        face_uuids.append("Unknown")
                        break

                    for i, (_, elem) in enumerate(known_faces_and_names):
                        # print("ELEM 2: ", elem)
                        known_enc.append(np.fromstring(elem[1:-1], sep=", "))

                    matches = face_recognition.compare_faces(known_enc, np.array(face_encoding))
                    name = "Unknown"

                    face_distances = face_recognition.face_distance(known_enc, np.array(face_encoding))
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = known_faces_and_names[best_match_index, 0]


                    face_uuids.append(name)

                    if name == "Unknown":
                        encodings_map.add_new(str(uuid4()), str(face_encoding))
                        unknown_count += 1


                # print("DEBUG ", face_uuids)
                
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


# import sys
# sys.path.insert(1, '../')

# import requests
# from fastapi import FastAPI
# import face_recognition
# import numpy as np
# from msgs import EncodingMsg
# import uvicorn
# from threading import Thread

# from uuid import uuid4

# from kafka import KafkaConsumer
# import pickle
# from msgs import FrameEncodings

# from contextlib import asynccontextmanager
# from multiprocessing import Process
# from encodings_map import EncodingsMap



# class IdentityController:
#     def __init__(self):
#         self.ident_serv = IdentityService()
#         self.app = FastAPI()

#         self.access_url = "http://face-recognition-access-service:8000/access_service"

#         # t = Thread(target=self.ident_serv.detection_loop, daemon=True)
#         # t.start()
        

#         @self.app.post("/identity_service")
#         async def receive_permission(msg: EncodingMsg):
#             self.ident_serv.save_encoding(msg.person_id, msg.encoding)


# class IdentityService:
#     '''
#     inspired by documentation of face recognition
#     '''
#     def __init__(self):
#         self.encodings_map = EncodingsMap()

#         self.logging_url = "http://face-recognition-logging-service:8004"
#         self.access_url = "http://face-recognition-access-service:8000/access_service_check"

#     def save_encoding(self, uuid_id, enc):
#         ##### check for hazelcast??
#         self.encodings_map.add_new(uuid_id, enc)


#     def send_logs(self, uuids, time_ap, camera_id):
#         lst = []
#         for uuid_id in uuids:
#             lst.append({
#             "person_id": uuid_id,
#             "camera_id": camera_id,        
#             "location": "it space",     # dummy
#             "appearance_time": time_ap
#             })

#         headers = {'Content-Type': 'application/json'}
#         ##### add error codes?

#         requests.post(self.logging_url, json=lst, headers=headers)

#     def send_recognised_names(self, uuids, time_ap, camera_id):
#         lst = []
#         for uuid_id in uuids:
#             lst.append({
#             "person_id": uuid_id,
#             "camera_id": camera_id,          
#             "location": "it space",     # dummy
#             "appearance_time": time_ap
#             })
#         headers = {'Content-Type': 'application/json'}
        
#         ##### add error codes?
#         requests.post(self.access_url, json=lst, headers=headers)


#     def deal_with_unknown(self, face_uuids, unknown_count):
#         for i, (uuid, _) in enumerate(face_uuids):
#             if uuid == "Unknown":
#                 face_uuids[i][0] = str(uuid4())
#                 self.encodings_map.add_new(face_uuids[i][0], face_uuids[i][1])
#                 unknown_count += 1

#         return unknown_count


#     def detection_loop(self):
#         encodings_map = EncodingsMap()
#         unknown_count = 0

#         print("before consumer")
#         consumer = KafkaConsumer('frame_encodings',
#                             value_deserializer=lambda v: FrameEncodings.parse_obj(pickle.loads(v)),
#                             bootstrap_servers=['kafka:19092'])
        
#         for message in consumer:
#             print('consumed')
#             print(message.value.camera_id)
#             print(message.value.datetime)
#             print(message.value.encodings)
#             # face_uuids = []
#             # for face_encoding in message.value.encodings:
#             #     known_faces_and_names = encodings_map.entry_set()
#             #     known_enc = []

#             #     if len(known_faces_and_names) == 0:
#             #         print("No names were registered!")
#             #         face_uuids.append(["Unknown", face_encoding])
#             #         break

#             #     for i, (_, elem) in enumerate(known_faces_and_names):
#             #         known_enc.append(np.fromstring(elem[1:-1], sep=" "))

#             #     matches = face_recognition.compare_faces(known_enc, face_encoding)
#             #     name = "Unknown"

#             #     face_distances = face_recognition.face_distance(known_enc, face_encoding)
#             #     best_match_index = np.argmin(face_distances)
#             #     if matches[best_match_index]:
#             #         name = known_faces_and_names[best_match_index, 0]


#             #     face_uuids.appned([name, face_encoding])

#             # unknown_count = self.deal_with_unknown(face_uuids, unknown_count)
#             # print("DEBUG ", face_uuids)
            
#             # print(f"Date and time: {message.value.datetime} Faces detected: {[i[0] for i in face_uuids]}")
            
#             # if face_uuids:
#             #     self.send_logs([i[0] for i in face_uuids], message.value.datetime, message.value.camera_id)
#             #     self.send_recognised_names([i[0] for i in face_uuids], message.value.datetime, message.value.camera_id)

#     @asynccontextmanager
#     async def lifespan(self, app):
#         p = Process(target=self.detection_loop)
#         p.start()
#         yield
#         p.join()

# serv = IdentityController()
# uvicorn.run(serv.app, host = "0.0.0.0", port=8001)