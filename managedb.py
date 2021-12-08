import mysql.connector

class managedb():
    conn: mysql.connector.connection.MySQLConnection
    def __init__(self):
        self.conn = mysql.connector.connect(
            host="iotpython.mysql.database.azure.com",
            user="dmitry@iotpython",
            password="IOTpassword!",
            database="iotpython",
        )

    def die(self):
        self.conn.close()

    def query(self, query):
        cursor = self.conn.cursor()
        cursor.execute(query)
        columns = cursor.description
        result = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
        return result


    def execute(self, query):
        cursor = self.conn.cursor()
        cursor.execute(query)
        self.conn.commit()

