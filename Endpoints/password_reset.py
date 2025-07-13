from flask import Blueprint, request, jsonify, current_app, render_template
from werkzeug.security import generate_password_hash
from email_service import send_password_reset_email
import random
from datetime import datetime, timedelta

password_reset_bp = Blueprint('password_reset_bp', __name__)

# In-memory stores (simple implementation)
reset_codes = {}  # {email: {'code': '123456', 'expires': datetime}}
reset_request_log = {}  # {email: [datetime, ...]}

@password_reset_bp.route('/forgot-password')
def forgot_password_page():
    """Render the password reset request page"""
    return render_template('ForgotPassword.html')


@password_reset_bp.route('/password-reset/initiate', methods=['POST'])
def initiate_password_reset():
    """Verify email & national ID then send reset code via email"""
    data = request.get_json() or {}
    email = data.get('email')
    national_id = data.get('national_id')

    if not email or not national_id:
        return jsonify(success=False, message='Email and national ID are required'), 400

    cursor = current_app.mysql.connection.cursor()
    cursor.execute(
        "SELECT first_name FROM student WHERE email_address = %s AND national_id = %s",
        (email, national_id)
    )
    row = cursor.fetchone()
    cursor.close()

    if not row:
        return jsonify(success=False, message='No student matches the provided details'), 404

    first_name = row[0]

    # ---- RATE LIMIT: 3 requests per 30 min ----
    now = datetime.utcnow()
    history = reset_request_log.get(email, [])
    # prune old
    history = [t for t in history if (now - t) < timedelta(minutes=30)]
    if len(history) >= 3:
        return jsonify(success=False, message='You have reached the maximum number of reset attempts. Please try again later.'), 429

    # Generate 6-digit numeric code
    code = f"{random.randint(0, 999999):06d}"

    # Store code with expiry (10 min)
    reset_codes[email] = {'code': code, 'expires': now + timedelta(minutes=10)}

    # Update history
    history.append(now)
    reset_request_log[email] = history

    # Send password reset email
    if send_password_reset_email(email, first_name, code):
        return jsonify(success=True, message='A reset code has been sent to your email. It is valid for 10 minutes.'), 200
    else:
        return jsonify(success=False, message='Failed to send password reset email. Please try again later.'), 500


@password_reset_bp.route('/password-reset/complete', methods=['POST'])
def complete_password_reset():
    """Verify code/token and update the student's password"""
    data = request.get_json() or {}
    email = data.get('email')
    code = data.get('code')
    new_password = data.get('new_password')

    if not all([email, code, new_password]):
        return jsonify(success=False, message='Missing data'), 400

    entry = reset_codes.get(email)
    if not entry or entry['code'] != code or datetime.utcnow() > entry['expires']:
        return jsonify(success=False, message='Invalid or expired reset code'), 400

    hashed_pw = generate_password_hash(new_password)

    cursor = current_app.mysql.connection.cursor()
    cursor.execute("UPDATE student SET password = %s WHERE email_address = %s", (hashed_pw, email))
    current_app.mysql.connection.commit()
    cursor.close()

    # Clear used code
    reset_codes.pop(email, None)

    return jsonify(success=True, message='Your password has been updated successfully.') 