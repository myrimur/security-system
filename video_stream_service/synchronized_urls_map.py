from msgs import CameraUrl, CameraId
import hazelcast

class SynchronizedUrlsHazelcastMap:
    def __init__(self):
        self.client = hazelcast.HazelcastClient()
        self.urls_map = self.client.get_map("urls-map").blocking()

    def add_new(self, msg: CameraUrl):
        #check if the value is present
        if self.urls_map.contains_key(msg.camera_id):
            print("error")
            return
        self.urls_map.put(msg.camera_id, msg.url)
        
    def delete(self, msg: CameraId):
        if not self.urls_map.contains_key(msg.camera_id):
            print("error")
            return
        self.urls_map.delete(msg.camera_id)

    def change_url(self, msg: CameraUrl):
        if not self.urls_map.contains_key(msg.camera_id):
            print("error")
            return
        self.urls_map.put(msg.camera_id, msg.url)

    def get_entry_set(self):
        return self.urls_map.entry_set()

    # maybe, change arg type
    def contains_value(self, url_string):
        return self.urls_map.contains_value(url_string)