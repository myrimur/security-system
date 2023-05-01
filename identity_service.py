import requests
from fastapi import FastAPI
import face_recognition
import cv2
import numpy as np
from datetime import datetime
import pickle

class IdentityService:
    '''
    inspired by documentation of face recognition
    '''
    def __init__(self):
        self.app = FastAPI()
        self.video_capture = self.get_camera()
        self.known_face_encodings, self.known_face_names = self.load_encodings()

        self.to_logging_service = []
        self.to_access_service = []

        # TODO send to access and logging service once in a while and clear


    @staticmethod
    def get_camera():
        """
        or get frame from message queue?
        """
        # TODO: read id from database (get stream from video stream service)
        return cv2.VideoCapture(0)

    @staticmethod
    def load_encodings():
        # TODO: read encodings from hazelcast shtuky

        with open("temp_database.csv", "rb") as data:
            all_data = pickle.load(data)

        return np.asarray(list(all_data.values())), np.asarray(list(all_data.keys()))


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

                    matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                    name = "Unknown"

                    face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = self.known_face_names[best_match_index]


                    face_names.append(name)
                
                # TODO: send to logging service and access control
                print(f"Date and time: {now.strftime('%d/%m/%Y %H:%M:%S')} Faces detected: {face_names}")
                self.to_logging_service.append(f"Date and time: {now.strftime('%d/%m/%Y %H:%M:%S')} Faces detected: {face_names}")
                self.to_access_service.append([now.strftime('%d/%m/%Y %H:%M:%S'), face_names])
                    
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

serv = IdentityService()
serv.detection_loop()