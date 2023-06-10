# import mysql.connector


# class PermissionsDB:
#     def __init__(self):
#         self.db_perms = mysql.connector.connect(
#             host="face-recognition-permissions-db",
#             user="karyna",
#             password="2222",
#             database="permissions_db"
#         )

#         self.cursor_db = self.db_perms.cursor()
#         self.__set_up_database()


#     def __set_up_database(self):
#         ###### FOR DEBUG ######
#         self.cursor_db.execute("DROP TABLE IF EXISTS permissions")
#         ###### FOR DEBUG ######

#         self.cursor_db.execute("CREATE TABLE IF NOT EXISTS permissions (id INT AUTO_INCREMENT PRIMARY KEY, uuid VARCHAR(36), name VARCHAR(255), camera_id VARCHAR(36), permission INT)")
        
#         self.cursor_db.close()
    
#     # TODO: multiple insertion?
#     def insert_into_bd(self, name, permission, camera_id):
#         self.cursor_db = self.db_perms.cursor()
#         self.cursor_db.execute('SELECT UUID()')
#         uuid_id, = self.cursor_db.fetchone()

#         to_exec = "INSERT INTO permissions (uuid, name, camera_id, permission) VALUES (%s, %s, %s, %s)"
#         values = (uuid_id, name, camera_id, permission)

#         self.cursor_db.execute(to_exec, values)

#         self.db_perms.commit()
#         self.cursor_db.close()

#         return uuid_id

    
#     def update_permission(self, name, camera_id, new_permission):
#         self.cursor_db = self.db_perms.cursor()
#         to_exec = "UPDATE permissions SET permission = %s WHERE name = '%s' AND camera_id = '%s'"
#         values = (new_permission, name, camera_id)

#         self.cursor_db.execute(to_exec, values)

#         self.db_perms.commit()
#         self.cursor_db.close()


#     # TODO: should we delete people from database?
#     def remove_permission(self, name):
#         self.cursor_db = self.db_perms.cursor()
#         to_exec = "DELETE FROM permissions WHERE name = '%s'"
#         values = (name,)

#         self.cursor_db.execute(to_exec, values)

#         self.db_perms.commit()
#         self.cursor_db.close()

#     def select_person(self, name, camera_id):
#         self.cursor_db = self.db_perms.cursor()
#         to_exec = "SELECT name, permission FROM permissions WHERE name IN (%s) AND camera_id IN (%s)"
#         values = (name, camera_id)

#         self.cursor_db.execute(to_exec, values)

#         res = self.cursor_db.fetchall()
#         self.cursor_db.close()

#         return res

    
#     def select_uuid(self, uuid, camera_id):
#         self.cursor_db = self.db_perms.cursor()
#         to_exec = "SELECT name, permission FROM permissions WHERE uuid IN (%s) AND camera_id IN (%s)"
#         values = (uuid, camera_id)

#         self.cursor_db.execute(to_exec, values)

#         res = self.cursor_db.fetchall()
#         self.cursor_db.close()

#         return res
    
import mysql.connector


class PermissionsDB:
    def __init__(self):
        self.db_perms = mysql.connector.connect(
            host="face-recognition-permissions-db",
            user="karyna",
            password="2222",
            database="permissions_db"
        )

        self.cursor_db = self.db_perms.cursor()
        self.__set_up_database()


    def __set_up_database(self):
        ###### FOR DEBUG ######
        self.cursor_db.execute("DROP TABLE IF EXISTS permissions")
        self.cursor_db.execute("DROP TABLE IF EXISTS locations")
        ###### FOR DEBUG ######

        self.cursor_db.execute("CREATE TABLE IF NOT EXISTS permissions (id INT AUTO_INCREMENT PRIMARY KEY, uuid VARCHAR(36), name VARCHAR(255), camera_id VARCHAR(36), permission INT)")
        self.cursor_db.execute("CREATE TABLE IF NOT EXISTS locations (id INT AUTO_INCREMENT PRIMARY KEY, camera_id VARCHAR(36), location_name VARCHAR(255))")

        
        self.cursor_db.close()
    
    # TODO: multiple insertion?
    def insert_into_bd(self, name, permission, camera_id):
        self.cursor_db = self.db_perms.cursor()
        self.cursor_db.execute('SELECT UUID()')
        uuid_id, = self.cursor_db.fetchone()

        to_exec = "INSERT INTO permissions (uuid, name, camera_id, permission) VALUES (%s, %s, %s, %s)"
        values = (uuid_id, name, camera_id, permission)

        self.cursor_db.execute(to_exec, values)

        self.db_perms.commit()
        self.cursor_db.close()

        return uuid_id

    
    def update_permission(self, name, camera_id, new_permission):
        self.cursor_db = self.db_perms.cursor()
        to_exec = "UPDATE permissions SET permission = %s WHERE name = '%s' AND camera_id = '%s'"
        values = (new_permission, name, camera_id)

        self.cursor_db.execute(to_exec, values)

        self.db_perms.commit()
        self.cursor_db.close()


    # TODO: should we delete people from database?
    def remove_permission(self, name):
        self.cursor_db = self.db_perms.cursor()
        to_exec = "DELETE FROM permissions WHERE name = '%s'"
        values = (name,)

        self.cursor_db.execute(to_exec, values)

        self.db_perms.commit()
        self.cursor_db.close()

    def select_person(self, name, camera_id):
        self.cursor_db = self.db_perms.cursor()
        to_exec = "SELECT name, permission FROM permissions WHERE name IN (%s) AND camera_id IN (%s)"
        values = (name, camera_id)

        self.cursor_db.execute(to_exec, values)

        res = self.cursor_db.fetchall()
        self.cursor_db.close()

        return res

    
    def select_uuid(self, uuid, camera_id):
        self.cursor_db = self.db_perms.cursor()
        to_exec = "SELECT name, permission FROM permissions WHERE uuid IN (%s) AND camera_id IN (%s)"
        values = (uuid, camera_id)

        self.cursor_db.execute(to_exec, values)

        res = self.cursor_db.fetchall()
        self.cursor_db.close()

        return res


    ## location table

    def select_location_name(self, camera_uuid):
        self.cursor_db = self.db_perms.cursor()
        to_exec = "SELECT location_name FROM locations WHERE camera_id IN (%s)"
        values = (camera_uuid, )

        self.cursor_db.execute(to_exec, values)

        res = self.cursor_db.fetchall()
        self.cursor_db.close()

        return res
    
    def save_location_name(self, camera_uuid, location_name):
        self.cursor_db = self.db_perms.cursor()

        to_exec = "INSERT INTO locations (camera_id, location_name) VALUES (%s, %s)"
        values = (camera_uuid, location_name)

        self.cursor_db.execute(to_exec, values)

        self.db_perms.commit()
        self.cursor_db.close()

    def update_location(self, camera_id, location_name):
        print("INPUT: ", camera_id, location_name)
        self.cursor_db = self.db_perms.cursor()
        print("before to exec")
        to_exec = "UPDATE locations SET location_name = %s WHERE camera_id IN (%s)"
        print("after to exec")
        values = (location_name, camera_id)
        print("Values: ", values)
        print("before execute")
        self.cursor_db.execute(to_exec, values)
        print("after execute")

        self.db_perms.commit()
        print("commited")
        self.cursor_db.close()
        print("closed")


    def remove_location(self, camera_id):
        self.cursor_db = self.db_perms.cursor()
        to_exec = "DELETE FROM locations WHERE camera_id IN (%s)"
        values = (camera_id,)

        self.cursor_db.execute(to_exec, values)

        self.db_perms.commit()
        self.cursor_db.close()