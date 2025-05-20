from backend.routes.connection import get_db_connection
from mysql.connector import Error
from datetime import datetime, timedelta
import threading
import logging

# Global lock for email sending
email_lock = threading.Lock()

# Store the last email sent times and values (in-memory, resets on server restart)
last_email_data = {
    'toxic': {'time': None, 'value': None, 'sent': False},
    'nonbio': {'time': None, 'value': None, 'sent': False},
    'recyclable': {'time': None, 'value': None, 'sent': False}
}

# Minimum time between emails (in minutes)
EMAIL_INTERVALS = {
    'toxic': 30,  # 30 minutes between toxic alerts
    'nonbio': 60,  # 1 hour between non-bio fill alerts
    'recyclable': 60  # 1 hour between recyclable fill alerts
}

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
    categories = ['Recyclable', 'Biodegradable', 'Non-biodegradable']
    result = {cat: 0 for cat in categories}
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            sql = """
                SELECT 
                    category,
                    COUNT(*) as count
                FROM trash 
                WHERE category IN ('Recyclable', 'Biodegradable', 'Non-biodegradable')
                GROUP BY category
            """
            print("Executing trash counts query:", sql)  # Debug log
            cursor.execute(sql)
            counts = cursor.fetchall()
            print("Raw counts from database:", counts)  # Debug log
            cursor.close()
            connection.close()
            for row in counts:
                result[row['category']] = row['count']
            final_result = [{'category': cat, 'count': result[cat]} for cat in categories]
            print("Final trash counts result:", final_result)  # Debug log
            return final_result
        except Error as e:
            print(f"Error fetching trash counts: {e}")
            return [{'category': cat, 'count': 0} for cat in categories]
    return [{'category': cat, 'count': 0} for cat in categories]

def fetch_classification_distribution():
    connection = get_db_connection()
    categories = ['Recyclable', 'Biodegradable', 'Non-biodegradable']
    result = {cat: 0 for cat in categories}
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            sql = """
                SELECT 
                    category,
                    COUNT(*) as count
                FROM trash 
                WHERE category IN ('Recyclable', 'Biodegradable', 'Non-biodegradable')
                GROUP BY category
            """
            print("Executing classification distribution query:", sql)  # Debug log
            cursor.execute(sql)
            distribution = cursor.fetchall()
            print("Raw distribution from database:", distribution)  # Debug log
            cursor.close()
            connection.close()
            for row in distribution:
                result[row['category']] = row['count']
            final_result = [{'category': cat, 'count': result[cat]} for cat in categories]
            print("Final classification distribution result:", final_result)  # Debug log
            return final_result
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

def fetch_latest_toxic_status():
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            sql = """
                SELECT sensor_id, reading_value, timestamp
                FROM sensor
                WHERE sensor_id = 3
                ORDER BY timestamp DESC
                LIMIT 1
            """
            cursor.execute(sql)
            toxic_row = cursor.fetchone()
            cursor.close()
            connection.close()
            if toxic_row:
                return [toxic_row]
            return []
        except Error as e:
            print(f"Error fetching latest toxic status: {e}")
            return None
    return None

def fetch_latest_non_bio_status():
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            sql = """
                SELECT sensor_id, reading_value, timestamp
                FROM sensor
                WHERE sensor_id = 1
                ORDER BY timestamp DESC
                LIMIT 1
            """
            cursor.execute(sql)
            non_bio_row = cursor.fetchone()
            cursor.close()
            connection.close()
            if non_bio_row:
                # Convert reading_value to int if it contains '%'
                rv = non_bio_row['reading_value']
                if isinstance(rv, str) and rv.endswith('%'):
                    try:
                        non_bio_row['reading_value'] = int(rv.replace('%', '').strip())
                    except Exception:
                        pass
                return [non_bio_row]
            return []
        except Error as e:
            print(f"Error fetching latest non-bio status: {e}")
            return None
    return None

def fetch_latest_recyclable_status():
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            sql = """
                SELECT sensor_id, reading_value, timestamp
                FROM sensor
                WHERE sensor_id = 2
                ORDER BY timestamp DESC
                LIMIT 1
            """
            cursor.execute(sql)
            recyclable_row = cursor.fetchone()
            cursor.close()
            connection.close()
            if recyclable_row:
                # Convert reading_value to int if it contains '%'
                rv = recyclable_row['reading_value']
                if isinstance(rv, str) and rv.endswith('%'):
                    try:
                        recyclable_row['reading_value'] = int(rv.replace('%', '').strip())
                    except Exception:
                        pass
                return [recyclable_row]
            return []
        except Error as e:
            print(f"Error fetching latest recyclable status: {e}")
            return None
    return None

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

def create_indexes():
    """Create necessary indexes for better query performance"""
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            # Create indexes for commonly queried columns
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_trash_category ON trash(category)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_trash_timestamp ON trash(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_trash_category_timestamp ON trash(category, timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sensor_id ON sensor(sensor_id)")
            connection.commit()
            cursor.close()
            connection.close()
            print("Indexes created successfully")
        except Error as e:
            print(f"Error creating indexes: {e}")
    return None

def fetch_toxic_alert_history(hours=None):
    """
    Fetch all toxic alert history data
    """
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            sql = """
                SELECT sensor_id, reading_value, timestamp
                FROM sensor
                WHERE sensor_id = 3
                ORDER BY timestamp ASC
            """
            print("Executing toxic alert history query for all data")
            cursor.execute(sql)
            rows = cursor.fetchall()
            print(f"Found {len(rows)} toxic alert history records")
            if rows:
                print(f"First record: {rows[0]}")
                print(f"Last record: {rows[-1]}")
            cursor.close()
            connection.close()
            return rows
        except Error as e:
            print(f"Error fetching toxic alert history: {e}")
            return []
    return []

def fetch_fill_level_history():
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            # Get the last 24 hours of data
            sql = """
                SELECT 
                    timestamp,
                    CASE 
                        WHEN sensor_id = '002' THEN 'Non-Biodegradable'
                        WHEN sensor_id = '001' THEN 'Recyclable'
                    END as category,
                    CAST(REPLACE(reading_value, '%', '') AS DECIMAL(5,2)) as fill_level
                FROM sensor
                WHERE sensor_id IN ('001', '002')
                ORDER BY timestamp ASC
            """
            cursor.execute(sql)
            data = cursor.fetchall()
            cursor.close()
            connection.close()

            # Format the data for the chart
            formatted_data = {
                'Non-Biodegradable': [],
                'Recyclable': []
            }
            
            for row in data:
                timestamp = int(datetime.strptime(str(row['timestamp']), '%Y-%m-%d %H:%M:%S').timestamp() * 1000)
                formatted_data[row['category']].append({
                    'x': timestamp,
                    'y': float(row['fill_level'])
                })

            return {
                'status': 'success',
                'data': formatted_data
            }
    except Exception as e:
        print(f"Error fetching fill level history: {str(e)}")
        return {
            'status': 'error',
            'message': str(e)
        }

def is_valid_timestamp(timestamp):
    """Check if the timestamp is valid (not in the future and not too old)"""
    try:
        # Convert string timestamp to datetime if needed
        if isinstance(timestamp, str):
            timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        now = datetime.now()
        # Check if timestamp is not in the future
        if timestamp > now:
            return False
        # Check if timestamp is not too old (e.g., not older than 24 hours)
        if now - timestamp > timedelta(hours=24):
            return False
        return True
    except Exception as e:
        print(f"Error validating timestamp: {e}")
        return False

def can_send_email(alert_type, current_value):
    """Check if we should send an email based on new data"""
    with email_lock:
        last_data = last_email_data.get(alert_type)
        
        # If this is the first email or no previous data
        if last_data['time'] is None or last_data['value'] is None:
            return True
            
        # For toxic alerts, only send if:
        # 1. The value is different from last sent value
        # 2. The new value is ABOVE NORMAL or TOXIC
        if alert_type == 'toxic':
            if current_value != last_data['value'] and current_value in ["ABOVE NORMAL", "TOXIC"]:
                logging.info(f"Sending email for new toxic status: {current_value}")
                return True
            logging.info(f"Skipping email - no new toxic status or status not critical")
            return False
            
        # For fill level alerts, only send if the value is different
        return current_value != last_data['value']

def update_last_email_data(alert_type, value):
    """Update the last email sent time and value for a specific alert type"""
    with email_lock:
        last_email_data[alert_type] = {
            'time': datetime.now(),
            'value': value,
            'sent': True
        }
        logging.info(f"Updated last email data for {alert_type}: value={value}, time={datetime.now()}")

def reset_email_sent_flag(alert_type):
    """Reset the sent flag for an alert type"""
    with email_lock:
        if alert_type in last_email_data:
            last_email_data[alert_type]['sent'] = False
            logging.info(f"Reset sent flag for {alert_type}") 