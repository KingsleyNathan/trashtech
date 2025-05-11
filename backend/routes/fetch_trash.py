from backend.routes.connection import get_db_connection
from mysql.connector import Error
from datetime import datetime, timedelta

def fetch_trash_by_category_and_timestamp(category, timestamp):
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            sql = "SELECT * FROM trash WHERE category = %s AND timestamp = %s ORDER BY id DESC LIMIT 1"
            cursor.execute(sql, (category, timestamp))
            row = cursor.fetchone()
            cursor.close()
            connection.close()
            return row
        except Error as e:
            print(f"Error fetching from trash table: {e}")
            return None
    return None

def fetch_all_trash():
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            sql = "SELECT * FROM trash ORDER BY id ASC"
            cursor.execute(sql)
            rows = cursor.fetchall()
            cursor.close()
            connection.close()
            return rows
        except Error as e:
            print(f"Error fetching all from trash table: {e}")
            return []
    return []

def fetch_biodegradable_trash():
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            sql = """
                SELECT category, timestamp 
                FROM trash 
                WHERE category = 'Biodegradable'
                ORDER BY timestamp DESC
            """
            cursor.execute(sql)
            rows = cursor.fetchall()
            cursor.close()
            connection.close()
            return rows
        except Error as e:
            print(f"Error fetching biodegradable trash: {e}")
            return []
    return []

def fetch_non_biodegradable_trash():
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            sql = """
                SELECT category, timestamp 
                FROM trash 
                WHERE category = 'Non-biodegradable'
                ORDER BY timestamp DESC
            """
            cursor.execute(sql)
            rows = cursor.fetchall()
            cursor.close()
            connection.close()
            return rows
        except Error as e:
            print(f"Error fetching non-biodegradable trash: {e}")
            return []
    return []

def fetch_recyclable_trash():
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            sql = """
                SELECT category, timestamp 
                FROM trash 
                WHERE category = 'Recyclable'
                ORDER BY timestamp DESC
            """
            cursor.execute(sql)
            rows = cursor.fetchall()
            cursor.close()
            connection.close()
            return rows
        except Error as e:
            print(f"Error fetching recyclable trash: {e}")
            return []
    return []

def fetch_trash_by_category():
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            sql = """
                SELECT category, COUNT(*) as count 
                FROM trash 
                WHERE category IN ('Recyclable', 'Biodegradable', 'Non-biodegradable')
                GROUP BY category
            """
            cursor.execute(sql)
            stats = cursor.fetchall()
            cursor.close()
            connection.close()
            return stats
        except Error as e:
            print(f"Error fetching trash stats: {e}")
            return []
    return []

def fetch_trash_by_time(interval='day'):
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Calculate time range based on interval
            now = datetime.now()
            if interval == 'day':
                start_time = now - timedelta(days=1)
                time_format = '%Y-%m-%d %H:00:00'
            elif interval == 'week':
                start_time = now - timedelta(days=7)
                time_format = '%Y-%m-%d'
            else:  # month
                start_time = now - timedelta(days=30)
                time_format = '%Y-%m-%d'

            # Get trash count by time period
            sql = """
                SELECT 
                    DATE_FORMAT(timestamp, %s) as time_period,
                    category,
                    COUNT(*) as count
                FROM trash
                WHERE timestamp >= %s
                AND category IN ('Recyclable', 'Biodegradable', 'Non-biodegradable')
                GROUP BY time_period, category
                ORDER BY time_period
            """
            cursor.execute(sql, (time_format, start_time))
            stats = cursor.fetchall()
            cursor.close()
            connection.close()
            return stats
        except Error as e:
            print(f"Error fetching time-based stats: {e}")
            return []
    return []

def fetch_sensor_status():
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            sql = """
                SELECT s.sensor_id, 
                       CASE 
                           WHEN s.sensor_id = '001' THEN 'Recyclable'
                           WHEN s.sensor_id = '002' THEN 'Non-biodegradable'
                           WHEN s.sensor_id = '003' THEN 'Biodegradable'
                       END as category,
                       COUNT(t.id) as trash_count
                FROM sensor s
                LEFT JOIN trash t ON t.category = 
                    CASE 
                        WHEN s.sensor_id = '001' THEN 'Recyclable'
                        WHEN s.sensor_id = '002' THEN 'Non-biodegradable'
                        WHEN s.sensor_id = '003' THEN 'Biodegradable'
                    END
                WHERE s.sensor_id IN ('001', '002', '003')
                GROUP BY s.sensor_id
            """
            cursor.execute(sql)
            status = cursor.fetchall()
            cursor.close()
            connection.close()
            return status
        except Error as e:
            print(f"Error fetching sensor status: {e}")
            return []
    return []

def fetch_trash_counts():
    connection = get_db_connection()
    categories = ['Recyclable', 'Biodegradable', 'Non-Biodegradable']
    result = {cat: 0 for cat in categories}
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            sql = """
                SELECT 
                    category,
                    COUNT(*) as count
                FROM trash 
                WHERE category IN ('Recyclable', 'Biodegradable', 'Non-Biodegradable')
                GROUP BY category
            """
            cursor.execute(sql)
            counts = cursor.fetchall()
            cursor.close()
            connection.close()
            for row in counts:
                result[row['category']] = row['count']
            return [{'category': cat, 'count': result[cat]} for cat in categories]
        except Error as e:
            print(f"Error fetching trash counts: {e}")
            return [{'category': cat, 'count': 0} for cat in categories]
    return [{'category': cat, 'count': 0} for cat in categories]

def fetch_classification_distribution():
    connection = get_db_connection()
    categories = ['Recyclable', 'Biodegradable', 'Non-Biodegradable']
    result = {cat: 0 for cat in categories}
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            sql = """
                SELECT 
                    category,
                    COUNT(*) as count
                FROM trash 
                WHERE category IN ('Recyclable', 'Biodegradable', 'Non-Biodegradable')
                GROUP BY category
            """
            cursor.execute(sql)
            distribution = cursor.fetchall()
            cursor.close()
            connection.close()
            for row in distribution:
                result[row['category']] = row['count']
            return [{'category': cat, 'count': result[cat]} for cat in categories]
        except Error as e:
            print(f"Error fetching classification distribution: {e}")
            return [{'category': cat, 'count': 0} for cat in categories]
    return [{'category': cat, 'count': 0} for cat in categories]

def fetch_latest_detection():
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            sql = """
                SELECT category, timestamp
                FROM trash
                WHERE category IN ('Recyclable', 'Biodegradable', 'Non-biodegradable')
                ORDER BY timestamp DESC
                LIMIT 1
            """
            cursor.execute(sql)
            latest = cursor.fetchone()
            cursor.close()
            connection.close()
            return latest
        except Error as e:
            print(f"Error fetching latest detection: {e}")
            return None
    return None

def fetch_last_detection_per_sensor():
    connection = get_db_connection()
    categories = ['Recyclable', 'Biodegradable', 'Non-Biodegradable']
    result = {cat: None for cat in categories}
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            sql = """
                SELECT category, MAX(timestamp) as last_detection
                FROM trash
                WHERE category IN ('Recyclable', 'Biodegradable', 'Non-Biodegradable')
                GROUP BY category
            """
            cursor.execute(sql)
            rows = cursor.fetchall()
            cursor.close()
            connection.close()
            for row in rows:
                result[row['category']] = row['last_detection']
            return result
        except Error as e:
            print(f"Error fetching last detection per sensor: {e}")
            return result
    return result 