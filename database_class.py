import mysql.connector


class PermissionsDB:
    def __init__(self):
        self.db_perms = mysql.connector.connect(
            host="127.0.0.1",
            user="daria",
            password="2222",
            database="permissions_db"
        )

        self.cursor_db = self.db_perms.cursor()
        self.__set_up_database()

    def __set_up_database(self):
        self.cursor_db.execute("CREATE TABLE IF NOT EXISTS permissions (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), permission INT)")

    
    # TODO: multiple insertion?
    def insert_into_bd(self, name, permission):
        to_exec = "INSERT INTO permissions (name, permission) VALUES (%s, %s)"
        values = (name, permission)

        self.cursor_db.execute(to_exec, values)

        self.db_perms.commit()

    
    def update_permission(self, name, new_permission):
        to_exec = "UPDATE permissions SET permission = %s WHERE name = '%s'"
        values = (new_permission, name)

        self.cursor_db.execute(to_exec, values)

        self.db_perms.commit()


    # TODO: should we delete people from database?
    def remove_permission(self, name):
        to_exec = "DELETE FROM permissions WHERE name = '%s'"
        values = (name,)

        self.cursor_db.execute(to_exec, values)

        self.db_perms.commit()

    def select_person(self, name):
        to_exec = "SELECT name, permission FROM permissions WHERE name IN (%s)"
        values = (name,)

        self.cursor_db.execute(to_exec, values)

        return self.cursor_db.fetchall()
