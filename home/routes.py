from flask import Blueprint, render_template

home_blueprint = Blueprint('home_blueprint', __name__)

@home_blueprint.route('/')
def index():
    return render_template('pages/index.html', segment='dashboard')

@home_blueprint.route('/notifications')
def notifications():
    return render_template('pages/notifications.html', segment='notifications')

@home_blueprint.route('/tables')
def tables():
    return render_template('pages/tables.html', segment='Biodegradable')

@home_blueprint.route('/tables2')
def tables2():
    return render_template('pages/tables2.html', segment='Non-Biodegradable')

@home_blueprint.route('/tables3')
def tables3():
    return render_template('pages/tables3.html', segment='Recyclable') 