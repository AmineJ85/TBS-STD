from flask import Blueprint, request, jsonify, current_app, session, redirect, url_for, render_template
from werkzeug.security import check_password_hash
import sys
import os

# Add parent directory to path to import auth
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth import login_required
from Endpoints.student import get_student_data  # Import the get_student_data function

login_bp = Blueprint('login_bp', __name__)

@login_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    cursor = current_app.mysql.connection.cursor()

    # Check student - updated to get all needed fields including level and enrollment status
    cursor.execute(
        """SELECT student_id, first_name, last_name, national_id, 
           email_address, password, level, profile_picture, enrollment_status, email_confirmed
           FROM student WHERE email_address = %s""",
        (email,)
    )
    student_row = cursor.fetchone()

    if student_row and check_password_hash(student_row[5], password):
        # Check if email is confirmed
        if not student_row[9]:  # email_confirmed is False
            cursor.close()
            return jsonify(success=False, message='Please confirm your email before logging in.'), 401
            
        # Check if student is dismissed
        if student_row[8] == 'dismissed':
            cursor.close()
            return jsonify(success=False, message='You are dismissed. Please contact the administration.'), 403
            
        # Store complete student information in session
        session['student'] = {
            'student_id': student_row[0],
            'first_name': student_row[1],
            'last_name': student_row[2],
            'national_id': student_row[3],
            'email_address': student_row[4],
            'level': student_row[6],  # level field
            'profile_picture': student_row[7] if student_row[7] else None,
            'enrollment_status': student_row[8]  # enrollment status
        }
        cursor.close()
        return jsonify(success=True, role='student', redirect_url=url_for('login_bp.student_page'))

    # Check admin with profile data
    cursor.execute(
        """SELECT admin_id, first_name, last_name, email_address, password, 
           profile_image, national_id, phone FROM admin WHERE email_address = %s""", 
        (email,)
    )
    admin_row = cursor.fetchone()

    if admin_row and check_password_hash(admin_row[4], password):
        # Convert profile image to base64 if it exists
        profile_image = None
        if admin_row[5]:  # profile_image
            import base64
            profile_image = base64.b64encode(admin_row[5]).decode('utf-8')
            
        session['admin'] = {
            'admin_id': admin_row[0],
            'first_name': admin_row[1],
            'last_name': admin_row[2],
            'email_address': admin_row[3],
            'profile_image': profile_image,
            'national_id': admin_row[6],
            'phone': admin_row[7]
        }
        cursor.close()
        return jsonify(success=True, role='admin', redirect_url=url_for('login_bp.admin_page'))

    cursor.close()
    return jsonify(success=False, message='Invalid email or password'), 401

@login_bp.route('/student')
@login_required
def student_page():
    # Ensure all student data is refreshed
    student_id = session.get('student', {}).get('student_id')
    if not student_id:
        return redirect(url_for('login_bp.login'))
    
    # Get fresh data from database including level and enrollment status
    student_data = get_student_data(student_id)
    if student_data:
        # Check if student has been dismissed
        if student_data.get('enrollment_status') == 'dismissed':
            session.clear()  # Clear session
            return redirect(url_for('login_bp.index'))
        
        session['student'].update(student_data)
    
    return render_template('StudentPage.html')

@login_bp.route('/admin')
def admin_page():
    admin = session.get('admin')
    if not admin:
        return redirect(url_for('login_bp.login'))
    return render_template('AdminPage.html', admin=admin)

@login_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_bp.index'))

@login_bp.route('/')
def index():
    return render_template('index.html')