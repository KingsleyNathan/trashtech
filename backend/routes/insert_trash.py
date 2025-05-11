from connection import get_db_connection
from mysql.connector import Error

def insert_test_trash(category, timestamp):
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            sql = "INSERT INTO trash (category, timestamp) VALUES (%s, %s)"
            cursor.execute(sql, (category, timestamp))
            connection.commit()
            print(f"Inserted row with category='{category}', timestamp='{timestamp}'")
            cursor.close()
            connection.close()
            return True
        except Error as e:
            print(f"Error inserting into trash table: {e}")
            return False
    return False 