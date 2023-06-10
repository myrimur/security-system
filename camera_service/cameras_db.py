import mysql.connector
from msgs import CameraInfo, CameraUrl, CameraLocation, \
                    CameraActivity, CameraId
import logging
import time

#https://www.geeksforgeeks.org/generating-random-ids-using-uuid-python/
import uuid

class CamerasDB:
    def __init__(self):
        while True:
            try:
                self.db_cameras = mysql.connector.connect(
                    host="face-recognition-cameras-db",
                    user="karyna",
                    password="2222",
                    database="cameras_db"
                )
                self.cursor_db = self.db_cameras.cursor()
                logging.info("successful mysql connection")
                break
            except:
                logging.warning("was not connected to mysql")
                time.sleep(1)
        self.__set_up_database()

    def __set_up_database(self):
        self.cursor_db.execute("CREATE TABLE IF NOT EXISTS cameras (camera_id VARCHAR(36), url TINYTEXT, location TINYTEXT, is_active BOOLEAN)")
        logging.info("cameras table was created in cameras_db database")
    
    def insert_into_bd(self, msg: CameraInfo):
        # msg_uuid = str(uuid.uuid4())
        to_exec = "INSERT INTO cameras (camera_id, url, location, is_active) VALUES (%s, %s, %s, %s)"
        values = (msg.camera_id, msg.url, msg.location, msg.is_active)
        self.cursor_db.execute(to_exec, values)
        self.db_cameras.commit()

    def update_url(self, msg: CameraUrl):
        to_exec = "UPDATE cameras SET url = %s WHERE camera_id = %s"
        values = (msg.url, msg.camera_id)

        self.cursor_db.execute(to_exec, values)
        self.db_cameras.commit()

    def update_location(self, msg: CameraLocation):
        to_exec = "UPDATE cameras SET location = %s WHERE camera_id = %s"
        values = (msg.location, msg.camera_id)

        self.cursor_db.execute(to_exec, values)
        self.db_cameras.commit()

    def update_activity(self, msg: CameraActivity):
        to_exec = "UPDATE cameras SET is_active = %s WHERE camera_id = %s"
        values = (msg.is_active, msg.camera_id)

        self.cursor_db.execute(to_exec, values)
        self.db_cameras.commit()

    def remove_camera(self, msg: CameraId):
        to_exec = "DELETE FROM cameras WHERE camera_id = %s"
        values = (msg.camera_id,)

        self.cursor_db.execute(to_exec, values)
        self.db_cameras.commit()

    def get_url(self, msg: CameraId):
        to_exec = "SELECT url FROM cameras WHERE camera_id = %s"
        values = (msg.camera_id,)

        self.cursor_db.execute(to_exec, values)
        return self.cursor_db.fetchall()
        
    #NOT SURE ABOUT BOOLEAN
    def select_active_cameras(self):
        to_exec = "SELECT camera_id, url FROM cameras WHERE is_active"
        self.cursor_db.execute(to_exec)
        return self.cursor_db.fetchall()
    
    def select_all_cameras_locations(self):
        to_exec = "SELECT camera_id, location FROM cameras"
        self.cursor_db.execute(to_exec)
        return self.cursor_db.fetchall()
