from kafka import KafkaConsumer
from json import loads
import base64
import cv2
import pickle
from io import BytesIO
import numpy as np
from msgs import FrameEncodings

print('test')
consumer = KafkaConsumer('frame_encodings',
                        value_deserializer=lambda v: FrameEncodings.parse_obj(pickle.loads(v)))
print("test")

for message in consumer:
   print(message.value.camera_id)
   print(message.value.datetime)
   print(message.value.encodings)
