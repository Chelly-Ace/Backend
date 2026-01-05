import os
import mysql.connector
from mysql.connector import Error
from contextlib import contextmanager

def get_connection():
   try:
        connection = mysql.connector.connect(
            host=os.environ.get("MYSQL_HOST", "localhost"),
            user=os.environ.get("MYSQL_USER", "root"),
            password=os.environ.get("MYSQL_PASSWORD", ""),
            database=os.environ.get("MYSQL_DATABASE", "health_monitoring"),
            port=int(os.environ.get("MYSQL_PORT", 3306))
        )
        return connection
   except Error as e:
        print("Error connecting to MySQL:", e)
        return None

@contextmanager
def get_connection_cursor(dictionary=False):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        if connection is None:
            raise Exception("Could not connect to the database!")
        
        cursor = connection.cursor(dictionary=dictionary)
        yield cursor
        connection.commit()


    except Error as e:
        if connection:
            connection.rollback()
        raise e
    finally: 
        if cursor: 
            cursor.close()
        if connection and connection.is_connected():
            connection.close()