from msgs import CameraUrl, CameraId
import hazelcast
import logging

class SynchronizedUrlsHazelcastMap:
    def __init__(self):
        self.client = hazelcast.HazelcastClient(cluster_members=["face-recognition-synchronized-urls-map-1"])
        logging.info("hazelcast client created: face-recognition-synchronized-urls-map-1")
        self.urls_map = self.client.get_map("urls-map").blocking()
        logging.info("hazelcast map created: urls-map")

    def add_new(self, msg: CameraUrl):
        #check if the value is present
        if self.urls_map.contains_key(msg.camera_id):
            logging.warning("new camera was not added as camera with this id is already exists: " + msg.camera_id)
            return
        self.urls_map.put(msg.camera_id, msg.url)
        
    def delete(self, msg: CameraId):
        if not self.urls_map.contains_key(msg.camera_id):
            logging.warning("camera was not removed as camera with this id is not present in urls-map: " + msg.camera_id)
            return
        self.urls_map.delete(msg.camera_id)

    def change_url(self, msg: CameraUrl):
        if not self.urls_map.contains_key(msg.camera_id):
            logging.warning("url for camera was not changed as camera with this id is not present in urls-map: " + msg.camera_id)
            return
        self.urls_map.put(msg.camera_id, msg.url)

    def get_entry_set(self):
        return self.urls_map.entry_set()

    # maybe, change arg type
    def contains_value(self, url_string):
        return self.urls_map.contains_value(url_string)