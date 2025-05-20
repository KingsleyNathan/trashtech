import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app
import os

def send_email(subject, body, recipients):
    """
    Send email using configured SMTP settings
    """
    try:
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = current_app.config['MAIL_DEFAULT_SENDER']
        msg['To'] = ', '.join(recipients)
        
        msg.attach(MIMEText(body, 'html'))
        
        with smtplib.SMTP(current_app.config['MAIL_SERVER'], current_app.config['MAIL_PORT']) as server:
            if current_app.config['MAIL_USE_TLS']:
                server.starttls()
            if current_app.config['MAIL_USERNAME']:
                server.login(current_app.config['MAIL_USERNAME'], current_app.config['MAIL_PASSWORD'])
            server.send_message(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send email: {str(e)}")
        return False

def get_toxic_alert_email(toxic_status):
    """
    Generate toxic alert email content
    """
    subject = f"🚨 Toxic Alert: {toxic_status}"
    
    if toxic_status == "Toxic":
        urgency = "CRITICAL"
        action = "immediate action required"
    else:  # Above Normal
        urgency = "HIGH"
        action = "urgent attention needed"
        
    body = f"""
    <h2>Toxic Alert Notification</h2>
    <p>Warning: {urgency} toxicity level detected in the trash can system.</p>
    <ul>
        <li>Status: <strong>{toxic_status}</strong></li>
        <li>Urgency Level: <strong>{urgency}</strong></li>
    </ul>
    <p>Please take {action} to address this issue.</p>
    """
    return subject, body

def get_fill_level_email(category, level):
    """
    Generate fill level alert email content
    """
    subject = f"⚠️ {category} Fill Level Alert: {level}%"
    
    if level >= 100:
        urgency = "CRITICAL"
        action = "immediate emptying required"
    elif level >= 90:
        urgency = "HIGH"
        action = "urgent emptying needed"
    else:  # 80%
        urgency = "MODERATE"
        action = "scheduled emptying recommended"
        
    body = f"""
    <h2>{category} Fill Level Alert</h2>
    <p>Alert Level: <strong>{urgency}</strong></p>
    <p>Current Fill Level: <strong>{level}%</strong></p>
    <p>Recommended Action: {action}</p>
    <p>Please ensure the bin is emptied as soon as possible to prevent overflow.</p>
    """
    return subject, body 