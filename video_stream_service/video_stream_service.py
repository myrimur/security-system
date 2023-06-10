from msgs import CameraUrl, CameraId
import uvicorn
from fastapi import FastAPI
from synchronized_urls_map import SynchronizedUrlsHazelcastMap
from contextlib import asynccontextmanager
from msgs import FrameEncodings
import face_recognition
from datetime import datetime
import cv2
import pickle
from kafka import KafkaProducer
from multiprocessing import Process
import requests
import time


class VideoStreamController:
    def __init__(self):
        print("TEEEST")
        self.video_stream_service = VideoStreamService()
        self.app = FastAPI(lifespan=self.video_stream_service.lifespan)
        print("start synchronize_cameras_urls")
        self.video_stream_service.synchronize_cameras_urls()
        print("end synchronize_cameras_urls")

        @self.app.post("/synchronize_new_camera")
        def synchronize_new_camera(msg: CameraUrl):
            self.video_stream_service.synchronize_new_camera(msg)

        @self.app.post("/synchronize_camera_url")
        def synchronize_camera_url(msg: CameraUrl):
            self.video_stream_service.synchronize_camera_url(msg)

        @self.app.post("/synchronize_inactive_camera")
        def synchronize_inactive_camera(msg: CameraId):
            #in case when camera is not active now or was removed from DB
            self.video_stream_service.synchronize_inactive_camera(msg)

class VideoStreamService:
    def __init__(self):
        self.camera_service_active_urls = "http://face-recognition-camera-service:8003/active_urls"
        self.urls = SynchronizedUrlsHazelcastMap()
    
    def synchronize_cameras_urls(self):
        # ADD CHECK IF GET REQUEST IS SUCCESSFUL
        while True:
            # print("send req")
            response = requests.get(self.camera_service_active_urls)
            # print("got req")
            if response.status_code:
                # print("SUCCESS: ", response.json())
                for id_url in response.json():
                    # print("ID URL: ", id_url)
                    self.urls.add_new(CameraUrl(camera_id=id_url["camera_id"], url=id_url["url"]))
                    # print("DONE")
                return
            # print("FAIL")
            time.sleep(1)


    def synchronize_new_camera(self, msg: CameraUrl):
        self.urls.add_new(msg)
        print("SYNCHRONIZED")
        print(msg)

    def synchronize_camera_url(self, msg: CameraUrl):
        self.urls.change_url(msg)

    def synchronize_inactive_camera(self, msg: CameraId):
        self.urls.delete(msg)

    def kafka_producer_loop(self):
        kafka_producer_ip = "kafka:19092"
        skip_rate = 10
        producer = KafkaProducer(bootstrap_servers=kafka_producer_ip,
                                value_serializer=lambda v: pickle.dumps(dict(v)))
        remove_rate = 1000

        urls = SynchronizedUrlsHazelcastMap()
        frame_no = 0

        video_captures = dict()
        while True:
            # print('in loop')
            for camera_id, url in urls.get_entry_set():
                # print(url)
                if url not in video_captures:
                    # print(url)
                    # video_captures[url] = cv2.VideoCapture(url + "/video")
                    video_captures[url] = cv2.VideoCapture(url)
                ret = video_captures[url].grab()
                if not ret:
                    print("grab warning!!!!!")
                    continue
                # video_captures[url].grab()
                # print("RET: ", ret)

                # status, frame = video_captures[url].read()
                # print("STATUS: ", status)
                # if not status:
                #     print("READ warning!!!!!")
                #     continue


                frame_no += 1
                if (frame_no % skip_rate == 0):
                    # print('processing frame')
                    status, frame = video_captures[url].retrieve()
                    # print("STATUS: ", status)
                    if not status:
                        print("retrieve warning!!!!!")
                        continue
                    curr_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

                    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                    face_locations = face_recognition.face_locations(rgb_small_frame)
                    if len(face_locations) != 0:
                        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
                        # print(face_encodings)
                        for i in range(len(face_encodings)):
                            face_encodings[i] = face_encodings[i].tolist()
                        encodings_msg = FrameEncodings(camera_id=camera_id, datetime=curr_time, encodings=face_encodings)
                        producer.send("frame_encodings", encodings_msg)
                        print("done")
                #оця іфка ніби працює, але ще треба потестити
                if (frame_no % remove_rate == 0):
                    for url in video_captures.keys():
                        if not urls.contains_value(url):
                            video_captures.pop(url)


    @asynccontextmanager
    async def lifespan(self, app):
        p = Process(target=self.kafka_producer_loop)
        p.start()
        yield
        p.join()

if __name__ == "__main__":    
    host="0.0.0.0"
    port=8005
    acc = VideoStreamController()
    uvicorn.run(acc.app, host=host, port=port)