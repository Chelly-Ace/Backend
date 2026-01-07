import os
import mysql.connector
from mysql.connector import Error
from contextlib import contextmanager
from dotenv import load_dotenv


load_dotenv() 

def get_connection():
   try:
        connection = mysql.connector.connect(
            host=os.environ.get("DB_HOST"),
            user=os.environ.get("DB_USER"),
            password=os.environ.get("DB_PASSWORD"),
            database=os.environ.get("MYSQL_DATABASE"),
            port=os.environ.get("DB_PORT")
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