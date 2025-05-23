from backend.routes.connection import get_db_connection
from mysql.connector import Error
from datetime import datetime, timedelta
import threading

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
                WHERE category = 'Non-Biodegradable'
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
                WHERE category IN ('Recyclable', 'Biodegradable', 'Non-Biodegradable')
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
                AND category IN ('Recyclable', 'Biodegradable', 'Non-Biodegradable')
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
                           WHEN s.sensor_id = 1 THEN 'Non-Biodegradable'
                           WHEN s.sensor_id = 2 THEN 'Recyclable'
                           WHEN s.sensor_id = 3 THEN 'Biodegradable'
                       END as category,
                       COUNT(t.id) as trash_count
                FROM sensor s
                LEFT JOIN trash t ON t.category = 
                    CASE 
                        WHEN s.sensor_id = 1 THEN 'Non-Biodegradable'
                        WHEN s.sensor_id = 2 THEN 'Recyclable'
                        WHEN s.sensor_id = 3 THEN 'Biodegradable'
                    END
                WHERE s.sensor_id IN (1, 2, 3)
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
            final_result = [{'category': cat, 'count': result[cat]} for cat in categories]
            return final_result
        except Error as e:
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
            final_result = [{'category': cat, 'count': result[cat]} for cat in categories]
            return final_result
        except Error as e:
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
                WHERE category IN ('Recyclable', 'Biodegradable', 'Non-Biodegradable')
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

def is_valid_timestamp(timestamp):
    """Check if the timestamp is valid (not in the future and not too old)"""
    try:
        # Convert string timestamp to datetime if needed
        if isinstance(timestamp, str):
            # Try our format first (DD/MM/YYYY HH:MM)
            try:
                timestamp = datetime.strptime(timestamp, '%d/%m/%Y %H:%M')
            except ValueError:
                # Try the alternative format (YYYY-MM-DD HH:MM:SS)
                timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        
        now = datetime.now()
        # Check if timestamp is not in the future
        if timestamp > now:
            return False
        # Check if timestamp is not too old (e.g., not older than 24 hours)
        if now - timestamp > timedelta(hours=24):
            return False
        return True
    except Exception:
        return False

def fetch_latest_toxic_status():
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            sql = """
                SELECT id, sensor_id, reading_value, timestamp
                FROM sensor
                WHERE sensor_id = 3
                ORDER BY timestamp DESC
                LIMIT 1
            """
            cursor.execute(sql)
            toxic_row = cursor.fetchone()
            
            if toxic_row:
                try:
                    # Map the status to numeric values for consistency
                    status = toxic_row['reading_value'].upper()
                    status_value = 0  # Default to Normal
                    if status == 'ABOVE NORMAL':
                        status_value = 1
                    elif status == 'TOXIC':
                        status_value = 2
                    toxic_row['status_value'] = status_value
                    
                    # Ensure timestamp is in the correct format
                    if isinstance(toxic_row['timestamp'], str):
                        # If it's already a string, keep it as is
                        pass
                    else:
                        # If it's a datetime object, format it
                        toxic_row['timestamp'] = toxic_row['timestamp'].strftime('%d/%m/%Y %H:%M')
                    
                    return [toxic_row]
                except Exception as e:
                    return []
            return []
        except Error as e:
            return []
    return []

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
                ORDER BY timestamp DESC
                LIMIT 100
            """
            cursor.execute(sql)
            rows = cursor.fetchall()
            
            # Process and format the data
            formatted_rows = []
            for row in rows:
                try:
                    # Handle timestamp conversion
                    if isinstance(row['timestamp'], str):
                        timestamp = datetime.strptime(row['timestamp'], '%Y-%m-%d %H:%M:%S')
                    else:
                        timestamp = row['timestamp']
                    
                    # Convert to milliseconds for the chart
                    timestamp_ms = int(timestamp.timestamp() * 1000)
                    
                    # Map the status to numeric values
                    status = row['reading_value'].upper()
                    status_value = 0  # Default to Normal
                    if status == 'ABOVE NORMAL':
                        status_value = 1
                    elif status == 'TOXIC':
                        status_value = 2
                    
                    formatted_rows.append({
                        'sensor_id': row['sensor_id'],
                        'reading_value': status,
                        'timestamp': timestamp_ms,
                        'status_value': status_value
                    })
                except Exception as e:
                    continue
            
            cursor.close()
            connection.close()
            return formatted_rows
        except Error as e:
            return []
    return []

def fetch_fill_level_history():
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            # Get recent data with limit
            sql = """
                SELECT 
                    timestamp,
                    CASE 
                        WHEN sensor_id = 1 THEN 'Non-Biodegradable'
                        WHEN sensor_id = 2 THEN 'Recyclable'
                    END as category,
                    reading_value
                FROM sensor
                WHERE sensor_id IN (1, 2)
                ORDER BY timestamp DESC
                LIMIT 100
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
                try:
                    # Handle timestamp conversion
                    if isinstance(row['timestamp'], str):
                        try:
                            # Try the standard format first
                            timestamp = datetime.strptime(row['timestamp'], '%Y-%m-%d %H:%M:%S')
                        except ValueError:
                            try:
                                # Try the alternative format (DD/MM/YYYY HH:MM)
                                timestamp = datetime.strptime(row['timestamp'], '%d/%m/%Y %H:%M')
                            except ValueError:
                                # If both formats fail, skip this row
                                continue
                    else:
                        timestamp = row['timestamp']
                    
                    # Convert to milliseconds for the chart
                    timestamp_ms = int(timestamp.timestamp() * 1000)
                    
                    # Handle fill level value
                    fill_level = row['reading_value']
                    if isinstance(fill_level, str):
                        # Remove any % symbol and convert to float
                        fill_level = float(fill_level.replace('%', '').strip())
                    else:
                        fill_level = float(fill_level)
                    
                    formatted_data[row['category']].append({
                        'x': timestamp_ms,
                        'y': fill_level
                    })
                except Exception as e:
                    continue

            return {
                'status': 'success',
                'data': formatted_data
            }
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }

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
                return True
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

def reset_email_sent_flag(alert_type):
    """Reset the sent flag for an alert type"""
    with email_lock:
        if alert_type in last_email_data:
            last_email_data[alert_type]['sent'] = False 