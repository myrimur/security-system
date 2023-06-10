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
import logging

logging.basicConfig(level=logging.INFO)

class VideoStreamController:
    def __init__(self):
        self.video_stream_service = VideoStreamService()
        self.app = FastAPI(lifespan=self.video_stream_service.lifespan)
        self.video_stream_service.synchronize_cameras_urls()

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
        while True:
            try:
                response = requests.get(self.camera_service_active_urls)
                if response.status_code:
                    for id_url in response.json():
                        self.urls.add_new(CameraUrl(camera_id=id_url["camera_id"], url=id_url["url"]))
                    return
                logging.warning("unsuccessful get request while synchronizing active urls")
                time.sleep(1)
            except:
                logging.warning("unsuccessful get request while synchronizing active urls")
                time.sleep(1)

    def synchronize_new_camera(self, msg: CameraUrl):
        self.urls.add_new(msg)
        logging.info("new camera was synchronized: camera_id = " + msg.camera_id + ", url = " + msg.url)

    def synchronize_camera_url(self, msg: CameraUrl):
        self.urls.change_url(msg)
        logging.info("camera url was synchronized: camera_id = " + msg.camera_id + ", url = " + msg.url)

    def synchronize_inactive_camera(self, msg: CameraId):
        self.urls.delete(msg)
        logging.info("camera was removed: camera_id = " + msg.camera_id)

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
            for camera_id, url in urls.get_entry_set():
                if url not in video_captures:
                    video_captures[url] = cv2.VideoCapture(url)
                    logging.info("VideoCapture was created for url = " + url)
                ret = video_captures[url].grab()
                if not ret:
                    logging.warning("GRAB: connection problems with camera_id = " + camera_id + ", url = " + url)
                    continue

                frame_no += 1
                if (frame_no % skip_rate == 0):
                    status, frame = video_captures[url].retrieve()
                    if not status:
                        logging.warning("RETRIEVE: problem with camera_id = " + camera_id + ", url = " + url)
                        continue
                    curr_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

                    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                    face_locations = face_recognition.face_locations(rgb_small_frame)
                    if len(face_locations) != 0:
                        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
                        for i in range(len(face_encodings)):
                            face_encodings[i] = face_encodings[i].tolist()
                        encodings_msg = FrameEncodings(camera_id=camera_id, datetime=curr_time, encodings=face_encodings)
                        producer.send("frame_encodings", encodings_msg)
                        logging.info("face encodings were detected on camera_id = " + camera_id + ", url = " + url)
                
                #оця іфка ніби працює, але ще треба потестити
                if (frame_no % remove_rate == 0):
                    for url in video_captures.keys():
                        if not urls.contains_value(url):
                            video_captures.pop(url)
                            logging.info("unactive url was removed: " + url)


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