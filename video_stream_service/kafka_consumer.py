from kafka import KafkaConsumer
import pickle
from msgs import FrameEncodings

print('test')
consumer = KafkaConsumer('frame_encodings',
                        value_deserializer=lambda v: FrameEncodings.parse_obj(pickle.loads(v)))
print("test")

for message in consumer:
   print(message.value.camera_id)
   print(message.value.datetime)
   print(message.value.encodings)
