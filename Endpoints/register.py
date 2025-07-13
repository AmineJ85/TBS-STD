from flask import Blueprint, request, jsonify, current_app, redirect, url_for
from werkzeug.security import generate_password_hash
from email_service import send_confirmation_email, confirm_token

register_bp = Blueprint('register_bp', __name__)

@register_bp.route('/register', methods=['POST'])
def register_student():
    data = request.get_json()

    first_name = data.get('firstName')
    last_name = data.get('lastName')
    national_id = data.get('nic')
    email = data.get('email')
    password = data.get('password')

    cursor = current_app.mysql.connection.cursor()

    # Check if email exists in tbs_students
    cursor.execute("SELECT COUNT(*) FROM tbs_students WHERE email_address = %s", (email,))
    email_exists = cursor.fetchone()[0] > 0

    # Check if national ID exists in tbs_students
    cursor.execute("SELECT COUNT(*) FROM tbs_students WHERE national_id = %s", (national_id,))
    nic_exists = cursor.fetchone()[0] > 0

    if not email_exists and not nic_exists:
        return jsonify({'field': 'both', 'message': 'Email and National ID do not exist in TBS records.'}), 400
    elif not email_exists:
        return jsonify({'field': 'email', 'message': 'Email does not exist in TBS records.'}), 400
    elif not nic_exists:
        return jsonify({'field': 'nic', 'message': 'National ID does not exist in TBS records.'}), 400

    # If both exist, check if they match as a pair in tbs_students
    cursor.execute("SELECT COUNT(*) FROM tbs_students WHERE email_address = %s AND national_id = %s", (email, national_id))
    pair_matches = cursor.fetchone()[0] > 0

    if not pair_matches:
        return jsonify({'field': 'both', 'message': 'Email and National ID do not match in TBS records.'}), 400

    # Check if the pair already exists in the student table
    cursor.execute("SELECT COUNT(*) FROM student WHERE email_address = %s AND national_id = %s", (email, national_id))
    already_registered = cursor.fetchone()[0] > 0

    if already_registered:
        return jsonify({'field': 'both', 'message': 'An account with this Email and National ID already exists.'}), 400

    # All checks passed, proceed to register
    hashed_password = generate_password_hash(password)

    # Add email_confirmed column with default FALSE
    cursor.execute("""
        INSERT INTO student (first_name, last_name, national_id, email_address, password, email_confirmed)
        VALUES (%s, %s, %s, %s, %s, FALSE)
    """, (first_name, last_name, national_id, email, hashed_password))

    current_app.mysql.connection.commit()
    cursor.close()
    
    # Send confirmation email
    email_sent = send_confirmation_email(email, first_name)
    
    if email_sent:
        return jsonify({'message': 'Student registered successfully. Please check your email to confirm your account.'}), 201
    else:
        return jsonify({'message': 'Student registered successfully, but there was an issue sending the confirmation email. Please contact support.'}), 201

# Email confirmation route
@register_bp.route('/registration/confirm/<token>')
def confirm_email(token):
    try:
        email = confirm_token(token)
        if not email:
            return redirect(url_for('login_bp.index', message="The confirmation link is invalid or has expired."))
        
        # Update user status in database
        cursor = current_app.mysql.connection.cursor()
        cursor.execute("UPDATE student SET email_confirmed = TRUE WHERE email_address = %s", (email,))
        
        if cursor.rowcount == 0:
            return redirect(url_for('login_bp.index', message="User not found."))
        
        current_app.mysql.connection.commit()
        cursor.close()
        
        return redirect(url_for('login_bp.index', message="Your email has been confirmed. You can now login."))
    except Exception as e:
        return redirect(url_for('login_bp.index', message="An error occurred."))
