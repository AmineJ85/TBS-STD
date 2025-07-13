from flask import current_app
from flask_mail import Mail, Message
import os
from itsdangerous import URLSafeTimedSerializer

mail = Mail()

def init_mail(app):
    """Initialize the mail extension with the Flask app"""
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    
    # Add fallback values in case environment variables aren't loaded
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'YOUR_EMAIL@gmail.com')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'YOUR_APP_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'TBS Registration <YOUR_EMAIL@gmail.com>')
    app.config['SECURITY_EMAIL_SENDER'] = os.environ.get('SECURITY_EMAIL_SENDER', 'TBS Registration <YOUR_EMAIL@gmail.com>')
    
    # Initialize the mail extension
    mail.init_app(app)
    
    # Set up the serializer for generating secure tokens
    app.config['SECURITY_PASSWORD_SALT'] = os.environ.get('SECURITY_PASSWORD_SALT', 'YOUR_PASSWORD_SALT')

def generate_confirmation_token(email):
    """Generate a secure token for email confirmation"""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=current_app.config['SECURITY_PASSWORD_SALT'])

def confirm_token(token, expiration=3600):
    """Verify the token and return the email if valid"""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=current_app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
        return email
    except Exception:
        return False

def send_confirmation_email(to_email, first_name):
    """Send a confirmation email to the user"""
    token = generate_confirmation_token(to_email)
    
    # Create confirmation link with the new route
    confirm_url = f"{current_app.config.get('BASE_URL', 'http://localhost:5000')}/registration/confirm/{token}"
    
    # Get logo URL
    logo_url = f"{current_app.config.get('BASE_URL', 'http://localhost:5000')}/static/images/logo.png"
    
    # Create email
    subject = "Please confirm your TBS account"
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e5ec; border-radius: 5px; background-color: #f8f9fa;">
        <div style="text-align: center; margin-bottom: 20px;">
            <img src="{logo_url}" alt="TBS Logo" style="max-width: 200px; height: auto;">
            <h2 style="color: #4a5568;">Tunis Business School</h2>
        </div>
        <h2 style="color: #4a5568;">Welcome to TBS!</h2>
        <p>Hello {first_name},</p>
        <p>Thank you for registering with Tunis Business School. Please confirm your email address by clicking the link below:</p>
        <p style="margin: 25px 0; text-align: center;">
            <a href="{confirm_url}" style="background-color: #4a5568; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold;">Confirm Email</a>
        </p>
        <p>This link will expire in 1 hour.</p>
        <p>If you did not register for a TBS account, please ignore this email.</p>
        <p>Best regards,<br>TBS Registration Team</p>
    </div>
    """
    
    # Send email
    try:
        msg = Message(
            subject=subject,
            recipients=[to_email],
            html=html,
            sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'TBS Registration <YOUR_EMAIL@gmail.com>')
        )
        mail.send(msg)
        current_app.logger.info(f"Confirmation email sent to {to_email}")
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send confirmation email: {str(e)}")
        return False

def send_password_reset_email(to_email, first_name, code):
    """Send a password reset email with a 6-digit verification code (valid 10 min)"""

    reset_url = f"{current_app.config.get('BASE_URL', 'http://localhost:5000')}"  # can be homepage since flow is in modal

    subject = "TBS – Password Reset Verification Code"

    html = f"""
    <div style=\"font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e5ec; border-radius: 5px; background-color: #f8f9fa;\">
        <div style=\"text-align: center; margin-bottom: 20px;\">
            <img src=\"{current_app.config.get('BASE_URL', 'http://localhost:5000')}/static/images/logo.png\" alt=\"TBS Logo\" style=\"max-width: 200px; height: auto;\">
            <h2 style=\"color: #4a5568;\">Tunis Business School</h2>
        </div>
        <h2 style=\"color: #4a5568;\">Password Reset Request</h2>
        <p>Hello {first_name},</p>
        <p>Use the following verification code to reset your password. The code is valid for <strong>10 minutes</strong>.</p>
        <p style=\"font-size: 2rem; font-weight: bold; text-align: center; letter-spacing: 4px; margin: 20px 0;\">{code}</p>
        <p>If you did not request a password reset, please ignore this email.</p>
        <p>Best regards,<br>TBS Registration Team</p>
    </div>
    """

    try:
        msg = Message(
            subject=subject,
            recipients=[to_email],
            html=html,
            sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'TBS Registration <YOUR_EMAIL@gmail.com>')
        )
        mail.send(msg)
        current_app.logger.info(f"Password reset email sent to {to_email}")
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send password reset email: {str(e)}")
        return False 