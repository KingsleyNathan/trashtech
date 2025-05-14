from flask import Blueprint, render_template, jsonify, request
from backend.routes.fetch_trash import (
    fetch_trash_by_category,
    fetch_trash_by_time,
    fetch_sensor_status,
    fetch_biodegradable_trash,
    fetch_non_biodegradable_trash,
    fetch_recyclable_trash,
    fetch_trash_counts,
    fetch_classification_distribution,
    fetch_latest_detection,
    fetch_last_detection_per_sensor,
    fetch_latest_toxic_status,
    fetch_latest_non_bio_status,
    fetch_latest_recyclable_status
)
from home.utils.email_notifications import send_email, get_toxic_alert_email, get_fill_level_email
from flask import current_app
from datetime import datetime, timedelta
import threading
import logging
from backend.utils.db_connection import get_db_connection
from backend.utils.error import Error

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

home_blueprint = Blueprint('home_blueprint', __name__)

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
    """Check if enough time has passed and the value has changed since the last email"""
    with email_lock:
        last_data = last_email_data.get(alert_type)
        if last_data['time'] is None or last_data['value'] is None:
            return True
        
        # If we've already sent an email for this exact value, don't send again
        if last_data['value'] == current_value and last_data['sent']:
            logger.info(f"Preventing duplicate email for {alert_type} with value {current_value}")
            return False
        
        # Check if enough time has passed
        interval = EMAIL_INTERVALS.get(alert_type, 60)  # Default to 60 minutes
        time_since_last = datetime.now() - last_data['time']
        time_check = time_since_last.total_seconds() >= (interval * 60)
        
        # Check if the value has changed
        value_check = last_data['value'] != current_value
        
        return time_check or value_check

def update_last_email_data(alert_type, value):
    """Update the last email sent time and value for a specific alert type"""
    with email_lock:
        last_email_data[alert_type] = {
            'time': datetime.now(),
            'value': value,
            'sent': True
        }
        logger.info(f"Updated last email data for {alert_type}: value={value}")

def reset_email_sent_flag(alert_type):
    """Reset the sent flag for an alert type"""
    with email_lock:
        if alert_type in last_email_data:
            last_email_data[alert_type]['sent'] = False
            logger.info(f"Reset sent flag for {alert_type}")

@home_blueprint.route('/')
def index():
    # Get dashboard data
    trash_counts = fetch_trash_counts()
    classification_distribution = fetch_classification_distribution()
    latest_detection = fetch_latest_detection()
    sensor_status = fetch_sensor_status()
    last_detection_per_sensor = fetch_last_detection_per_sensor()
    
    return render_template('pages/index.html', 
                         segment='dashboard',
                         trash_counts=trash_counts,
                         classification_distribution=classification_distribution,
                         latest_detection=latest_detection,
                         sensor_status=sensor_status,
                         last_detection_per_sensor=last_detection_per_sensor)

@home_blueprint.route('/documentation')
def documentation():
    return render_template('pages/documentation.html')

@home_blueprint.route('/api/dashboard-data')
def dashboard_data():
    # Reset all email sent flags at the start of each request
    for alert_type in last_email_data:
        reset_email_sent_flag(alert_type)

    trash_counts = fetch_trash_counts()
    classification_distribution = fetch_classification_distribution()
    latest_detection = fetch_latest_detection()
    sensor_status = fetch_sensor_status()
    last_detection_per_sensor = fetch_last_detection_per_sensor()
    toxic_alert = fetch_latest_toxic_status()
    non_bio_alert = fetch_latest_non_bio_status()
    recyclable_alert = fetch_latest_recyclable_status()

    # Log all alert data for debugging
    logger.info("Current alert data:")
    logger.info(f"Toxic alert: {toxic_alert}")
    logger.info(f"Non-bio alert: {non_bio_alert}")
    logger.info(f"Recyclable alert: {recyclable_alert}")

    # Toxic alert email logic
    if toxic_alert and len(toxic_alert) > 0:
        toxic_data = toxic_alert[0]
        toxic_status = toxic_data['reading_value']
        logger.info(f"Processing toxic alert: {toxic_status}")
        
        if toxic_status in ["ABOVE NORMAL", "TOXIC"] and can_send_email('toxic', toxic_status):
            subject, body = get_toxic_alert_email(toxic_status)
            recipients = current_app.config['ALERT_RECIPIENTS']
            if send_email(subject, body, recipients):
                update_last_email_data('toxic', toxic_status)
                logger.info(f"Sent toxic alert email for status: {toxic_status}")

    # Non-Biodegradable fill level alert logic
    if non_bio_alert and len(non_bio_alert) > 0:
        nonbio_data = non_bio_alert[0]
        nonbio_level_raw = nonbio_data['reading_value']
        logger.info(f"Processing non-bio alert: {nonbio_level_raw}")
        
        try:
            if isinstance(nonbio_level_raw, int):
                nonbio_level_num = nonbio_level_raw
            else:
                nonbio_level_num = int(str(nonbio_level_raw).replace('%', '').strip())
            logger.info(f"Parsed non-bio level: {nonbio_level_num}")
            
            if nonbio_level_num in [80, 90, 100] and can_send_email('nonbio', nonbio_level_num):
                subject, body = get_fill_level_email("Non-Biodegradable", nonbio_level_num)
                recipients = current_app.config['ALERT_RECIPIENTS']
                if send_email(subject, body, recipients):
                    update_last_email_data('nonbio', nonbio_level_num)
                    logger.info(f"Sent non-bio fill alert email for level: {nonbio_level_num}%")
        except Exception as e:
            logger.error(f"Error parsing NonBio fill level: {e}")

    # Recyclable fill level alert logic
    if recyclable_alert and len(recyclable_alert) > 0:
        recy_data = recyclable_alert[0]
        recy_level_raw = recy_data['reading_value']
        logger.info(f"Processing recyclable alert: {recy_level_raw}")
        
        try:
            if isinstance(recy_level_raw, int):
                recy_level_num = recy_level_raw
            else:
                recy_level_num = int(str(recy_level_raw).replace('%', '').strip())
            logger.info(f"Parsed recyclable level: {recy_level_num}")
            
            if recy_level_num in [80, 90, 100] and can_send_email('recyclable', recy_level_num):
                subject, body = get_fill_level_email("Recyclable", recy_level_num)
                recipients = current_app.config['ALERT_RECIPIENTS']
                if send_email(subject, body, recipients):
                    update_last_email_data('recyclable', recy_level_num)
                    logger.info(f"Sent recyclable fill alert email for level: {recy_level_num}%")
        except Exception as e:
            logger.error(f"Error parsing Recy fill level: {e}")

    return jsonify({
        'trash_counts': trash_counts,
        'classification_distribution': classification_distribution,
        'latest_detection': latest_detection,
        'sensor_status': sensor_status,
        'last_detection_per_sensor': last_detection_per_sensor,
        'toxic_alert': toxic_alert,
        'non_bio_alert': non_bio_alert,
        'recyclable_alert': recyclable_alert
    })

# Trash stats route
@home_blueprint.route('/api/trash-stats')
def trash_stats():
    category_stats = fetch_trash_by_category()
    time_stats = fetch_trash_by_time()
    return jsonify({
        'category_stats': category_stats,
        'time_stats': time_stats
    })

# Time stats route
@home_blueprint.route('/api/time-stats/<interval>')
def time_stats(interval):
    time_stats = fetch_trash_by_time(interval)
    return jsonify(time_stats)

# Sensor status route
@home_blueprint.route('/api/sensor-status')
def sensor_status():
    status = fetch_sensor_status()
    return jsonify(status)

# Tables route
@home_blueprint.route('/tables')
def tables():
    biodegradable_data = fetch_biodegradable_trash()
    return render_template('pages/tables.html', biodegradable_data=biodegradable_data, segment='Biodegradable')

# Non-biodegradable data route
@home_blueprint.route('/tables2')
def tables2():
    non_biodegradable_data = fetch_non_biodegradable_trash()
    return render_template('pages/tables2.html', non_biodegradable_data=non_biodegradable_data, segment='Non-Biodegradable')

# Recyclable data route
@home_blueprint.route('/tables3')
def tables3():
    recyclable_data = fetch_recyclable_trash()
    return render_template('pages/tables3.html', recyclable_data=recyclable_data, segment='Recyclable')

# Biodegradable data route
@home_blueprint.route('/api/biodegradable-data')
def biodegradable_data():
    data = fetch_biodegradable_trash()
    return jsonify(data)

# Non-biodegradable data route
@home_blueprint.route('/api/non-biodegradable-data')
def non_biodegradable_data():
    data = fetch_non_biodegradable_trash()
    return jsonify(data)

# Recyclable data route
@home_blueprint.route('/api/recyclable-data')
def recyclable_data():
    data = fetch_recyclable_trash()
    return jsonify(data)

# Toxic alert route
@home_blueprint.route('/api/send-toxic-alert', methods=['POST'])
def send_toxic_alert():
    try:
        if not request.is_json:
            logger.error("Request is not JSON")
            return jsonify({'status': 'error', 'message': 'Request must be JSON'}), 400

        data = request.get_json()
        if not data:
            logger.error("No data in request")
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400

        toxic_status = data.get('toxic_status')
        if not toxic_status:
            logger.error("No toxic_status in request data")
            return jsonify({'status': 'error', 'message': 'No toxic_status provided'}), 400

        logger.info(f"Received toxic alert request with status: {toxic_status}")
        
        subject, body = get_toxic_alert_email(toxic_status)
        recipients = current_app.config['ALERT_RECIPIENTS']
        
        if not recipients:
            logger.error("No recipients configured")
            return jsonify({'status': 'error', 'message': 'No recipients configured'}), 500
        
        if send_email(subject, body, recipients):
            logger.info(f"Successfully sent toxic alert email for status: {toxic_status}")
            return jsonify({'status': 'success', 'message': 'Toxic alert email sent'})
        else:
            logger.error(f"Failed to send toxic alert email for status: {toxic_status}")
            return jsonify({'status': 'error', 'message': 'Failed to send toxic alert email'}), 500
            
    except Exception as e:
        logger.error(f"Error in send_toxic_alert: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Fill level alert route
@home_blueprint.route('/api/send-fill-alert', methods=['POST'])
def send_fill_alert():
    try:
        data = request.get_json()
        category = data.get('category')
        level = data.get('level')
        logger.info(f"Received fill alert request - Category: {category}, Level: {level}")
        
        # Determine alert type based on category
        alert_type = 'nonbio' if category == 'Non-Biodegradable' else 'recyclable'
        
        # Reset the sent flag before checking
        reset_email_sent_flag(alert_type)
        
        # Check if we can send an email
        if not can_send_email(alert_type, level):
            logger.info(f"Throttling email for {category} at {level}%")
            return jsonify({
                'status': 'throttled',
                'message': f'Email already sent recently for this level. Please wait {EMAIL_INTERVALS[alert_type]} minutes between alerts.'
            }), 429
        
        subject, body = get_fill_level_email(category, level)
        recipients = current_app.config['ALERT_RECIPIENTS']
        
        if send_email(subject, body, recipients):
            update_last_email_data(alert_type, level)
            logger.info(f"Sent fill alert email for {category} at {level}%")
            return jsonify({'status': 'success', 'message': 'Fill level alert email sent'})
        else:
            logger.error(f"Failed to send fill alert email for {category} at {level}%")
            return jsonify({'status': 'error', 'message': 'Failed to send fill level alert email'}), 500
            
    except Exception as e:
        logger.error(f"Error in send_fill_alert: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# # Test email route
# @home_blueprint.route('/api/test-email', methods=['GET'])
# def test_email():
#     try:
#         subject = "🧪 Test Email - Trash Monitoring System"
#         body = """
#         <h2>Test Email from Trash Monitoring System</h2>
#         <p>This is a test email to verify that the email notification system is working correctly.</p>
#         <p>If you're receiving this email, it means:</p>
#         <ul>
#             <li>✅ Email configuration is correct</li>
#             <li>✅ SMTP connection is working</li>
#             <li>✅ Recipient list is properly configured</li>
#         </ul>
#         <p>You will now receive notifications for:</p>
#         <ul>
#             <li>🚨 High toxic alerts</li>
#             <li>⚠️ Fill level alerts (80%, 90%, 100%)</li>
#         </ul>
#         """
#         recipients = current_app.config['ALERT_RECIPIENTS']
        
#         if not recipients:
#             return jsonify({
#                 'status': 'error',
#                 'message': 'No recipients configured. Please set ALERT_RECIPIENTS in your environment variables.'
#             }), 400
            
#         if send_email(subject, body, recipients):
#             return jsonify({
#                 'status': 'success',
#                 'message': f'Test email sent successfully to {", ".join(recipients)}'
#             })
#         else:
#             return jsonify({
#                 'status': 'error',
#                 'message': 'Failed to send test email'
#             }), 500
            
#     except Exception as e:
#         return jsonify({
#             'status': 'error',
#             'message': f'Error sending test email: {str(e)}'
#         }), 500 