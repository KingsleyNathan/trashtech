from flask import Blueprint, render_template, jsonify
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
    fetch_last_detection_per_sensor
)

home_blueprint = Blueprint('home_blueprint', __name__)

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
    
    return jsonify({
        'trash_counts': trash_counts,
        'classification_distribution': classification_distribution,
        'latest_detection': latest_detection,
        'sensor_status': sensor_status,
        'last_detection_per_sensor': last_detection_per_sensor
    })

@home_blueprint.route('/api/trash-stats')
def trash_stats():
    category_stats = fetch_trash_by_category()
    time_stats = fetch_trash_by_time()
    return jsonify({
        'category_stats': category_stats,
        'time_stats': time_stats
    })

@home_blueprint.route('/api/time-stats/<interval>')
def time_stats(interval):
    time_stats = fetch_trash_by_time(interval)
    return jsonify(time_stats)

@home_blueprint.route('/api/sensor-status')
def sensor_status():
    status = fetch_sensor_status()
    return jsonify(status)


@home_blueprint.route('/tables')
def tables():
    biodegradable_data = fetch_biodegradable_trash()
    return render_template('pages/tables.html', biodegradable_data=biodegradable_data, segment='Biodegradable')

@home_blueprint.route('/tables2')
def tables2():
    non_biodegradable_data = fetch_non_biodegradable_trash()
    return render_template('pages/tables2.html', non_biodegradable_data=non_biodegradable_data, segment='Non-Biodegradable')

@home_blueprint.route('/tables3')
def tables3():
    recyclable_data = fetch_recyclable_trash()
    return render_template('pages/tables3.html', recyclable_data=recyclable_data, segment='Recyclable')

@home_blueprint.route('/api/biodegradable-data')
def biodegradable_data():
    data = fetch_biodegradable_trash()
    return jsonify(data)

@home_blueprint.route('/api/non-biodegradable-data')
def non_biodegradable_data():
    data = fetch_non_biodegradable_trash()
    return jsonify(data)

@home_blueprint.route('/api/recyclable-data')
def recyclable_data():
    data = fetch_recyclable_trash()
    return jsonify(data) 