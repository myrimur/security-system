import hazelcast
import warnings
import numpy as np

class EncodingsMap:
    def __init__(self):
        self.client = hazelcast.HazelcastClient(cluster_members=[
            "face-recognition-hazelcast-node-1:5701",
            "face-recognition-hazelcast-node-2:5701",
        ])
        self.encodings_map = self.client.get_map("encodings-map").blocking()

    def add_new(self, uuid_id, enc):
        if self.encodings_map.contains_key(uuid_id):
            warnings.warn(f"UUID already in hazelcast")
            return
        self.encodings_map.put(uuid_id, enc)
        
    # def delete(self, msg: CameraId):
    #     if not self.urls_map.contains_key(msg.camera_id):
    #         print("error")
    #         return
    #     self.urls_map.delete(msg.camera_id)

    def get_entry_set(self):
        return np.asarray(self.encodings_map.entry_set())
