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

home_blueprint = Blueprint('home_blueprint', __name__)

# Store the last toxic status and fill levels emailed (in-memory, resets on server restart)
last_toxic_status_emailed = {'status': None}
last_nonbio_fill_emailed = {'level': None}
last_recy_fill_emailed = {'level': None}

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

@home_blueprint.route('/api/dashboard-data')
def dashboard_data():
    trash_counts = fetch_trash_counts()
    classification_distribution = fetch_classification_distribution()
    latest_detection = fetch_latest_detection()
    sensor_status = fetch_sensor_status()
    last_detection_per_sensor = fetch_last_detection_per_sensor()
    toxic_alert = fetch_latest_toxic_status()
    non_bio_alert = fetch_latest_non_bio_status()
    recyclable_alert = fetch_latest_recyclable_status()

    # Toxic alert email logic
    if toxic_alert and len(toxic_alert) > 0:
        toxic_status = toxic_alert[0]['reading_value']
        if toxic_status in ["ABOVE NORMAL", "TOXIC"]:
            if last_toxic_status_emailed['status'] != toxic_status:
                subject, body = get_toxic_alert_email(toxic_status)
                recipients = current_app.config['ALERT_RECIPIENTS']
                send_email(subject, body, recipients)
                last_toxic_status_emailed['status'] = toxic_status

    # Non-Biodegradable fill level alert logic
    print("non_bio_alert:", non_bio_alert)
    if non_bio_alert and len(non_bio_alert) > 0:
        nonbio_level_raw = non_bio_alert[0]['reading_value']
        print("NonBio DB value:", nonbio_level_raw)
        try:
            if isinstance(nonbio_level_raw, int):
                nonbio_level_num = nonbio_level_raw
            else:
                nonbio_level_num = int(str(nonbio_level_raw).replace('%', '').strip())
            if nonbio_level_num in [80, 90, 100]:
                if last_nonbio_fill_emailed['level'] != nonbio_level_num:
                    subject, body = get_fill_level_email("Non-Biodegradable", nonbio_level_num)
                    recipients = current_app.config['ALERT_RECIPIENTS']
                    send_email(subject, body, recipients)
                    last_nonbio_fill_emailed['level'] = nonbio_level_num
        except Exception as e:
            print("Error parsing NonBio fill level:", e)

    # Recyclable fill level alert logic
    print("recyclable_alert:", recyclable_alert)
    if recyclable_alert and len(recyclable_alert) > 0:
        recy_level_raw = recyclable_alert[0]['reading_value']
        print("Recy DB value:", recy_level_raw)
        try:
            if isinstance(recy_level_raw, int):
                recy_level_num = recy_level_raw
            else:
                recy_level_num = int(str(recy_level_raw).replace('%', '').strip())
            if recy_level_num in [80, 90, 100]:
                if last_recy_fill_emailed['level'] != recy_level_num:
                    subject, body = get_fill_level_email("Recyclable", recy_level_num)
                    recipients = current_app.config['ALERT_RECIPIENTS']
                    send_email(subject, body, recipients)
                    last_recy_fill_emailed['level'] = recy_level_num
        except Exception as e:
            print("Error parsing Recy fill level:", e)

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
        data = request.get_json()
        toxic_status = data.get('toxic_status')
        
        subject, body = get_toxic_alert_email(toxic_status)
        recipients = current_app.config['ALERT_RECIPIENTS']
        
        if send_email(subject, body, recipients):
            return jsonify({'status': 'success', 'message': 'Toxic alert email sent'})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to send toxic alert email'}), 500
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Fill level alert route
@home_blueprint.route('/api/send-fill-alert', methods=['POST'])
def send_fill_alert():
    try:
        data = request.get_json()
        category = data.get('category')
        level = data.get('level')
        
        subject, body = get_fill_level_email(category, level)
        recipients = current_app.config['ALERT_RECIPIENTS']
        
        if send_email(subject, body, recipients):
            return jsonify({'status': 'success', 'message': 'Fill level alert email sent'})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to send fill level alert email'}), 500
            
    except Exception as e:
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