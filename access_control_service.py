
import face_recognition
import pickle

import hazelcast


class AccessControlService:
    def __init__(self):
        self.client = hazelcast.HazelcastClient()
        self.encodings_map = self.client.get_map("my-distributed-map").blocking()

    def get_encodings(self, ref_img_path, name):
        person_image = face_recognition.load_image_file(ref_img_path)
        person_face_encoding = face_recognition.face_encodings(person_image, model="large", num_jitters=100)[0]

        self.encodings_map.put(name, person_face_encoding)


