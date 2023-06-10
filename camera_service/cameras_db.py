import mysql.connector
from msgs import CameraInfo, CameraUrl, CameraLocation, \
                    CameraActivity, CameraId

#https://www.geeksforgeeks.org/generating-random-ids-using-uuid-python/
import uuid

class CamerasDB:
    def __init__(self):
        self.db_cameras = mysql.connector.connect(
            host="face-recognition-cameras-db",
            user="karyna",
            password="2222",
            database="cameras_db"
        )
        self.cursor_db = self.db_cameras.cursor()
        
        # #not sure about this part
        # self.information_schema = mysql.connector.connect(
        #     host="127.0.0.1",
        #     user="karyna",
        #     password="2222",
        #     database="information_schema"
        # )
        # self.cursor_inf_schema = self.information_schema.cursor()

        # self.last_update_for_vs = time.time()
        # self.last_update_for_ac = self.last_update_for_vs
        self.__set_up_database()

    def __set_up_database(self):
        self.cursor_db.execute("CREATE TABLE IF NOT EXISTS cameras (camera_id VARCHAR(36), url TINYTEXT, location TINYTEXT, is_active BOOLEAN)")
    
    def insert_into_bd(self, msg: CameraInfo):
        # msg_uuid = str(uuid.uuid4())
        to_exec = "INSERT INTO cameras (camera_id, url, location, is_active) VALUES (%s, %s, %s, %s)"
        values = (msg.camera_id, msg.url, msg.location, msg.is_active)
        self.cursor_db.execute(to_exec, values)
        self.db_cameras.commit()

        # print(msg.url, msg.location, msg.is_active)
        # return msg_uuid

        # self.last_update_for_vs = time.time()
        # self.last_update_for_ac = self.last_update_for_vs

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

    
    # def get_last_update_for_vs(self):
    #     return self.last_update_for_vs

    # def get_last_update_for_ac(self):
    #     return self.last_update_for_ac

    # #check if it works
    # def get_last_update(self):
    #     to_exec = "SELECT update_time FROM tables WHERE table_schema = 'cameras_db' AND table_name = 'cameras'"
    #     self.cursor_inf_schema.execute(to_exec)
    #     return self.cursor_inf_schema.fetchall()

    # def check_if_changed(self):
    #     last_update = self.get_last_update()
    #     if self.last_update > last_update:
    #         self.last_update = last_update
    #         return True
    #     return False
