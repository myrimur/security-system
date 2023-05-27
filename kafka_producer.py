from msgs import FrameEncodings
import face_recognition
from datetime import datetime
import cv2
import pickle
from kafka import KafkaProducer

video = cv2.VideoCapture("http://192.168.43.1:8080/video")
skip_rate = 5
frame_no = 0

producer = KafkaProducer(bootstrap_servers='localhost:9092',
                        value_serializer=lambda v: pickle.dumps(dict(v)))

while True:
    ret = video.grab()
    frame_no += 1

    if (frame_no % skip_rate == 0):
      status, frame = video.retrieve()
      curr_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
      small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
      # cv2.imshow("TEST", small_frame)

      rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
      face_locations = face_recognition.face_locations(rgb_small_frame)
      if len(face_locations) != 0:
         face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
         for i in range(len(face_encodings)):
            face_encodings[i] = face_encodings[i].tolist()
         # print(type(face_encodings[0][0]))
         encodings_msg = FrameEncodings(camera_id=0, datetime=curr_time, encodings=face_encodings)
         # print(pickle.dumps(dict(encodings_msg)))
         # print(encodings_msg.json())
         producer.send("frame_encodings", encodings_msg)
         print("done")
         # print(face_encodings[0])

cv2.destroyAllWindows()