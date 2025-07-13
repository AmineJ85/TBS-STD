import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth import login_required
from flask import Blueprint, request, jsonify, current_app, g, session
from course_select import get_course_registration_data, get_current_courses, get_notenrolled_courses
from schedule_optimizer import optimize_student_schedule
from functools import wraps
from datetime import datetime, date
import base64
from werkzeug.security import check_password_hash, generate_password_hash
import math

# Database connection function
def get_db_connection():
    return current_app.mysql.connection


student_bp = Blueprint('student_bp', __name__, url_prefix='/student')

# Helper function to get current active semester
def get_current_semester():
    try:
        cursor = current_app.mysql.connection.cursor()
        cursor.execute("""
            SELECT academic_year, semester
            FROM academic_calendar
            WHERE is_current = 1
            LIMIT 1
        """)
        
        semester_info = cursor.fetchone()
        if not semester_info:
            current_app.logger.warning("No active semester found")
            return None, None
        
        current_year, current_semester = semester_info
        cursor.close()
        return current_year, current_semester
    except Exception as e:
        current_app.logger.error(f"Error getting current semester: {str(e)}")
        return None, None

# Helper function to get student's year of study
def get_student_year(student_id):
    try:
        cursor = current_app.mysql.connection.cursor()
        cursor.execute("""
            SELECT year_of_study
            FROM student
            WHERE student_id = %s
        """, (student_id,))
        
        student_info = cursor.fetchone()
        cursor.close()
        
        if not student_info:
            current_app.logger.warning(f"No student info found for ID {student_id}")
            return None
            
        return student_info[0]
    except Exception as e:
        current_app.logger.error(f"Error getting student year: {str(e)}")
        return None

# Check if student is awaiting board decision
def check_and_update_dismissal_status(student_id):
    """
    Check if a student's probation counter has reached max_probation_total and update their status to dismissed if needed.
    Returns True if student was dismissed, False otherwise.
    """
    try:
        cursor = current_app.mysql.connection.cursor()
        
        # First check if the student is already dismissed
        cursor.execute("""
            SELECT enrollment_status
            FROM student
            WHERE student_id = %s
        """, (student_id,))
        
        student_status = cursor.fetchone()
        if student_status and student_status[0] == 'dismissed':
            current_app.logger.info(f"Student {student_id} is already dismissed")
            return True
            
        # Get the student's latest probation counter
        cursor.execute("""
            SELECT probation_counter 
            FROM student_semester_summary
            WHERE student_id = %s
            ORDER BY year DESC, semester DESC
            LIMIT 1
        """, (student_id,))
        
        probation_result = cursor.fetchone()
        if not probation_result:
            current_app.logger.info(f"No probation record found for student {student_id}")
            return False
            
        probation_counter = probation_result[0] if probation_result[0] is not None else 0
        
        # Get max_probation_total from system parameters
        cursor.execute("""
            SELECT max_probation_total
            FROM system_parameters
            ORDER BY last_updated DESC
            LIMIT 1
        """)
        system_param = cursor.fetchone()
        max_probation_total = system_param[0] if system_param and system_param[0] is not None else 3  # Default to 3 if not set
        
        # Check for student override
        cursor.execute("""
            SELECT max_probation_total
            FROM student_parameters_overrides
            WHERE student_id = %s
        """, (student_id,))
        
        override = cursor.fetchone()
        if override and override[0] is not None:
            max_probation_total = override[0]
            
        current_app.logger.info(f"Student {student_id} probation counter: {probation_counter}, max_probation_total: {max_probation_total}")
        
        # Check if student has an approved probation extension
        cursor.execute("""
            SELECT id 
            FROM board_probation_extension
            WHERE student_id = %s AND status = 'approved'
            ORDER BY decision_date DESC
            LIMIT 1
        """, (student_id,))
        
        has_approved_extension = cursor.fetchone() is not None
        
        # If student has reached or exceeded max_probation_total and has an approved extension
        if probation_counter >= max_probation_total and has_approved_extension:
            # Update student status to dismissed
            cursor.execute("""
                UPDATE student
                SET enrollment_status = 'dismissed'
                WHERE student_id = %s
            """, (student_id,))
            
            current_app.mysql.connection.commit()
            current_app.logger.warning(f"Student {student_id} has been dismissed due to reaching max probation total ({probation_counter} >= {max_probation_total})")
            return True
        
        return False
            
    except Exception as e:
        current_app.logger.error(f"Error checking dismissal status: {str(e)}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return False

def is_awaiting_board_decision(student_id):
    try:
        cursor = current_app.mysql.connection.cursor()
        
        # Get the student's latest probation counter
        cursor.execute("""
            SELECT probation_counter 
            FROM student_semester_summary
            WHERE student_id = %s
            ORDER BY year DESC, semester DESC
            LIMIT 1
        """, (student_id,))
        
        probation_result = cursor.fetchone()
        if not probation_result:
            current_app.logger.info(f"No probation record found for student {student_id}")
            return False
            
        probation_counter = probation_result[0] if probation_result[0] is not None else 0
        current_app.logger.info(f"Student {student_id} probation counter: {probation_counter}")
        
        # Get max_probation_board from system parameters
        cursor.execute("""
            SELECT max_probation_board
            FROM system_parameters
            ORDER BY last_updated DESC
            LIMIT 1
        """)
        system_param = cursor.fetchone()
        max_probation_board = system_param[0] if system_param and system_param[0] is not None else 2  # Default to 2 if not set
        
        # Check for student override
        cursor.execute("""
            SELECT max_probation_board
            FROM student_parameters_overrides
            WHERE student_id = %s
        """, (student_id,))
        
        override = cursor.fetchone()
        if override and override[0] is not None:
            max_probation_board = override[0]
            
        current_app.logger.info(f"Max probation board threshold for student {student_id}: {max_probation_board}")
        
        # Check if there's an approved extension request
        cursor.execute("""
            SELECT id FROM board_probation_extension
            WHERE student_id = %s AND status = 'approved'
            ORDER BY decision_date DESC
            LIMIT 1
        """, (student_id,))
        
        has_approved_extension = cursor.fetchone() is not None
        
        # Immediately restrict access if probation counter reaches or exceeds the limit AND there's no approved extension
        if probation_counter >= max_probation_board and not has_approved_extension:
            current_app.logger.warning(f"Student {student_id} has reached probation limit: {probation_counter} >= {max_probation_board}")
            
            # Check if there's already a pending request
            cursor.execute("""
                SELECT id FROM board_probation_extension
                WHERE student_id = %s AND status = 'pending'
                LIMIT 1
            """, (student_id,))
            
            pending_request = cursor.fetchone()
            
            if not pending_request:
                # First delete any existing pending requests for this student (just to be safe)
                try:
                    cursor.execute("""
                        DELETE FROM board_probation_extension
                        WHERE student_id = %s AND status = 'pending'
                    """, (student_id,))
                    
                    # Then insert a new pending request
                    cursor.execute("""
                        INSERT INTO board_probation_extension
                        (student_id, status)
                        VALUES (%s, 'pending')
                    """, (student_id,))
                    current_app.mysql.connection.commit()
                    current_app.logger.info(f"Created board_probation_extension entry for student {student_id}")
                except Exception as e:
                    current_app.logger.error(f"Error creating board_probation_extension entry: {str(e)}")
                    # Continue even if there's an error creating the entry
            
            return True
        else:
            current_app.logger.info(f"Student {student_id} access check: probation_counter={probation_counter}, max_probation_board={max_probation_board}, has_approved_extension={has_approved_extension}")
            return False
            
    except Exception as e:
        current_app.logger.error(f"Error checking if awaiting board decision: {str(e)}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        # Default to false if there's an error checking
        return False

# Helper function to check registration status and get enrolled courses
def get_registration_status_and_courses(student_id):
    try:
        cursor = current_app.mysql.connection.cursor()
        
        # Get the last entry in registration_config table
        cursor.execute("""
            SELECT id, status, start_date, end_date 
            FROM registration_config 
            ORDER BY id DESC 
            LIMIT 1
        """)
        
        reg_config = cursor.fetchone()
        if not reg_config:
            current_app.logger.warning("No registration config found, defaulting to closed")
            return {"status": "closed", "courses": [], "start_date": None, "end_date": None}
        
        config_id, status, start_date, end_date = reg_config
        current_app.logger.info(f"Last registration config found: id={config_id}, status='{status}', start_date={start_date}, end_date={end_date}")
        
        # Make sure we use the exact status from the database
        if status not in ['open', 'closed', 'scheduled']:
            current_app.logger.warning(f"Invalid status '{status}' found in database. Valid values are: open, closed, scheduled")
            status = 'closed'  # Default to closed if invalid
        
        # Get current active semester
        current_year, current_semester = get_current_semester()
        if not current_year or not current_semester:
            return {"status": status, "courses": [], "start_date": start_date, "end_date": end_date}
            
        current_app.logger.info(f"Active semester: year={current_year}, semester={current_semester}")
        
        # Get student's year of study
        student_year = get_student_year(student_id)
        if not student_year:
            return {"status": status, "courses": [], "start_date": start_date, "end_date": end_date}
        
        # Get enrolled courses for current semester if any
        cursor.execute("""
            SELECT ac.course_code, c.course_name, c.coefficient as credits, 
                   ac.lecture_study_group, ac.tutorial_study_group
            FROM add_course ac
            JOIN courses c ON ac.course_code = c.course_code
            WHERE ac.student_id = %s 
            AND ac.year = %s 
            AND ac.semester = %s
            AND ac.status = 'enrolled'
        """, (student_id, current_year, current_semester))
        
        enrolled_courses = []
        for row in cursor.fetchall():
            course_code, course_name, credits, lecture_group, tutorial_group = row
            enrolled_courses.append({
                "course_code": course_code,
                "course_name": course_name,
                "credits": credits,
                "lecture_study_group": lecture_group,
                "tutorial_study_group": tutorial_group
            })
        
        # Get drop course requests
        drop_requests = get_drop_course_requests(student_id)
        current_app.logger.info(f"Retrieved drop requests: {drop_requests}")
        
        # Get non-droppable courses with reasons
        non_droppable_courses = {}
        
        # 1. Find failed courses that are being retaken
        cursor.execute("""
            SELECT DISTINCT ac1.course_code
            FROM add_course ac1
            JOIN add_course ac2 ON ac1.student_id = ac2.student_id AND ac1.course_code = ac2.course_code
            WHERE ac1.student_id = %s 
            AND ac1.status = 'failed'
            AND ac1.year < %s
            AND ac2.year = %s
            AND ac2.semester = %s
            AND ac2.status = 'enrolled'
        """, (student_id, current_year, current_year, current_semester))
        
        for row in cursor.fetchall():
            course_code = row[0]
            non_droppable_courses[course_code] = "You cannot drop a failed course that you are retaking"
        
        # 2. Check if student has ANY courses with 'notenrolled' or 'failed' status
        # If they don't, then all courses are autochecked (except those already marked as non-droppable)
        cursor.execute("""
            SELECT COUNT(*)
            FROM (
                SELECT ac.course_code, ac.status
                FROM add_course ac
                WHERE ac.student_id = %s
                AND NOT (ac.year = %s AND ac.semester = %s AND ac.status = 'enrolled')
                AND ac.status IN ('notenrolled', 'failed')
                ORDER BY ac.id DESC
                LIMIT 1
            ) AS subquery
        """, (student_id, current_year, current_semester))
        
        has_notenrolled_or_failed = cursor.fetchone()[0] > 0
        
        # If student has no 'notenrolled' or 'failed' courses, all current courses are autochecked
        if not has_notenrolled_or_failed:
            current_app.logger.info(f"Student {student_id} has no 'notenrolled' or 'failed' courses, marking all as autochecked")
            
            # Mark all enrolled courses as non-droppable (except those already marked)
            for course in enrolled_courses:
                course_code = course["course_code"]
                if course_code not in non_droppable_courses:
                    non_droppable_courses[course_code] = "This is a required course for your program"
        
        current_app.logger.info(f"Non-droppable courses: {non_droppable_courses}")
        
        response_data = {
            "status": status,
            "start_date": start_date,
            "end_date": end_date,
            "courses": enrolled_courses,
            "current_year": current_year,
            "current_semester": current_semester,
            "student_year": student_year,
            "drop_requests": drop_requests,
            "non_droppable_courses": non_droppable_courses
        }
        
        current_app.logger.info(f"Returning registration status: '{status}' with {len(enrolled_courses)} enrolled courses and {len(drop_requests)} drop requests")
        return response_data
    
    except Exception as e:
        current_app.logger.error(f"Error checking registration status: {str(e)}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return {"status": "error", "courses": [], "start_date": None, "end_date": None}

# Login required decorator - original from login blueprint
from functools import wraps
from flask import session, jsonify, current_app, redirect, url_for, request

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'student' not in session:
            current_app.logger.warning("Unauthorized access attempt: No student in session")
            return jsonify({
                'success': False,
                'message': 'User not logged in',
                'code': 'UNAUTHORIZED'
            }), 401
            
        # Check if student is dismissed
        student = session['student']
        student_id = student['student_id']
        
        # Check enrollment status directly from database to ensure it's current
        cursor = current_app.mysql.connection.cursor()
        cursor.execute("""
            SELECT enrollment_status FROM student WHERE student_id = %s
        """, (student_id,))
        result = cursor.fetchone()
        
        # Check if student is graduated
        if result and result[0] == 'graduated':
            # Set graduated flag in session
            session['student']['is_graduated'] = True
            
            # If this is an API endpoint (not a page load), and not the profile endpoint
            # Block access to all backend functions except profile viewing
            if request.path != '/student/profile-info' and request.is_json:
                return jsonify({
                    'success': False, 
                    'message': 'Congratulations on your graduation! Your account is now in view-only mode.',
                    'graduated': True
                }), 403
        else:
            # Make sure the graduated flag is removed if they're not graduated
            if 'is_graduated' in session['student']:
                session['student']['is_graduated'] = False
        
        cursor.close()
        
        if result and result[0] == 'dismissed':
            current_app.logger.warning(f"Access attempt by dismissed student {student_id}")
            session.clear()  # Clear session for dismissed student
            
            # Check if this is an API request or a page request
            if request.path.startswith('/student/') and not request.is_xhr:
                # For page requests, redirect to login page
                return redirect(url_for('login_bp.index'))
            else:
                # For API requests, return JSON
                return jsonify({
                    'success': False,
                    'message': 'Your account has been dismissed. Please contact the administration.',
                    'code': 'DISMISSED'
                }), 403
            
        # Check if student should be dismissed due to reaching max_probation_total
        if check_and_update_dismissal_status(student_id):
            current_app.logger.warning(f"Student {student_id} has been dismissed due to reaching max probation total")
            session.clear()  # Clear session for dismissed student
            return jsonify({
                'success': False,
                'message': 'Your account has been dismissed due to reaching maximum probation limit. Please contact the administration.',
                'code': 'DISMISSED'
            }), 403
            
        # Check if student is awaiting board decision
        current_app.logger.info(f"Checking board decision status for student {student_id}")
        
        # Store the result in Flask's g object to avoid repeated database queries
        if not hasattr(g, 'awaiting_board_decision'):
            g.awaiting_board_decision = is_awaiting_board_decision(student_id)
            
        if g.awaiting_board_decision:
            current_app.logger.warning(f"Access restricted for student {student_id}: Awaiting board decision")
            return jsonify({
                'success': False,
                'message': 'Awaiting Scientific Board decision whether to grant an extension semester or not',
                'code': 'AWAITING_BOARD_DECISION'
            }), 403
            
        return f(*args, **kwargs)
    return decorated_function

# Apply login_required to all student blueprint endpoints
@student_bp.before_request
def restrict_if_awaiting_board_decision_or_dismissed():
    """
    Global check that runs before any student blueprint request.
    This provides an additional layer of security beyond the @login_required decorator.
    Checks both for awaiting board decision and dismissed status.
    """
    if 'student' not in session:
        return jsonify({
            'success': False,
            'message': 'User not logged in',
            'code': 'UNAUTHORIZED'
        }), 401
        
    student_id = session['student']['student_id']
    
    # Check if student is dismissed
    cursor = current_app.mysql.connection.cursor()
    cursor.execute("""
        SELECT enrollment_status FROM student WHERE student_id = %s
    """, (student_id,))
    result = cursor.fetchone()
    cursor.close()
    
    if result and result[0] == 'dismissed':
        current_app.logger.warning(f"Global restriction applied for student {student_id}: Dismissed status")
        session.clear()  # Clear session for dismissed student
        
        # Check if this is an API request or a page request
        if request.path.startswith('/student/') and not request.is_xhr:
            # For page requests, redirect to login page
            return redirect(url_for('login_bp.index'))
        else:
            # For API requests, return JSON
            return jsonify({
                'success': False,
                'message': 'Your account has been dismissed. Please contact the administration.',
                'code': 'DISMISSED'
            }), 403
        
    # Check if student should be dismissed due to reaching max_probation_total
    if check_and_update_dismissal_status(student_id):
        current_app.logger.warning(f"Global restriction: Student {student_id} has been dismissed due to reaching max probation total")
        session.clear()  # Clear session for dismissed student
        return jsonify({
            'success': False,
            'message': 'Your account has been dismissed due to reaching maximum probation limit. Please contact the administration.',
            'code': 'DISMISSED'
        }), 403
    
    # Use cached result if available for board decision check
    if hasattr(g, 'awaiting_board_decision'):
        is_restricted = g.awaiting_board_decision
    else:
        is_restricted = is_awaiting_board_decision(student_id)
        g.awaiting_board_decision = is_restricted
    
    if is_restricted:
        current_app.logger.warning(f"Global restriction applied for student {student_id}: Awaiting board decision")
        return jsonify({
            'success': False,
            'message': 'Awaiting Scientific Board decision whether to grant an extension semester or not',
            'code': 'AWAITING_BOARD_DECISION'
        }), 403

@student_bp.route('/course-registration', methods=['GET'])
@login_required
def course_registration():
    try:
        student = session.get('student')
        if not student:
            current_app.logger.error("No student in session")
            return jsonify({
                'success': False,
                'message': 'User not logged in',
                'code': 'UNAUTHORIZED'
            }), 401
            
        # Double-check board decision status here for extra safety
        student_id = student['student_id']
        if is_awaiting_board_decision(student_id):
            current_app.logger.warning(f"Access restricted in course_registration for student {student_id}")
            return jsonify({
                'success': False,
                'message': 'Awaiting Scientific Board Decision',
                'code': 'AWAITING_BOARD_DECISION'
            }), 403

        current_app.logger.info(f"Loading course registration for student {student_id}")
        
        # Calculate and store semester summaries to ensure data is up-to-date
        # This is the same logic used in enrollment_history() function
        # Get all semesters for the student
        semesters = get_student_semesters(student_id)
        
        # Calculate and store semester summaries
        calculate_semester_summaries(student_id, semesters)
        
        # Get registration status information
        registration_info = get_registration_status_and_courses(student_id)
        
        try:
            # Get registration data from course_select module
            data = get_course_registration_data(student_id)
            if not data:
                raise ValueError("No data")
            
            # Add registration status information to the response
            data['registration_status'] = registration_info['status']
            
            # Convert datetime objects to ISO format strings for JSON serialization
            if registration_info['start_date']:
                data['registration_start_date'] = registration_info['start_date'].isoformat()
                current_app.logger.info(f"Start date set to: {data['registration_start_date']}")
            else:
                data['registration_start_date'] = None
                
            if registration_info['end_date']:
                data['registration_end_date'] = registration_info['end_date'].isoformat()
                current_app.logger.info(f"End date set to: {data['registration_end_date']}")
            else:
                data['registration_end_date'] = None
            
            # Use enrolled courses from registration info (for consistent format)
            if registration_info['courses']:
                data['enrolled_courses'] = registration_info['courses']
                data['has_existing_submissions'] = True
            else:
                # Get currently enrolled courses for this semester (as backup)
                cursor = current_app.mysql.connection.cursor()
                cursor.execute("""
                    SELECT ac.course_code, c.course_name, c.coefficient as credits, ac.forgiveness, 
                           ac.lecture_study_group, ac.tutorial_study_group
                    FROM add_course ac
                    JOIN courses c ON ac.course_code = c.course_code
                    WHERE ac.student_id = %s 
                    AND ac.year = %s 
                    AND ac.semester = %s 
                    AND ac.status = 'enrolled'
                    ORDER BY ac.id DESC
                """, (student_id, data['current_year'], data['current_semester']))
                
                enrolled_courses = [dict(zip([col[0] for col in cursor.description], row)) 
                                for row in cursor.fetchall()]
                data['enrolled_courses'] = enrolled_courses
                data['has_existing_submissions'] = len(enrolled_courses) > 0
            
            data['max_courses'] = get_max_courses()
            
            # Log the registration status details
            current_app.logger.info(f"Sending registration data: status={data['registration_status']}, " + 
                                   f"start_date={data['registration_start_date']}, " +
                                   f"end_date={data['registration_end_date']}")
            
            # Get forgiveness counter information
            cursor = current_app.mysql.connection.cursor()
            cursor.execute("""
                SELECT forgiveness_counter 
                FROM student_semester_summary
                WHERE student_id = %s AND year = %s AND semester = %s
            """, (student_id, data['current_year'], data['current_semester']))
            
            forgiveness_result = cursor.fetchone()
            forgiveness_counter = forgiveness_result[0] if forgiveness_result and forgiveness_result[0] is not None else 0
            
            # Get max forgiveness uses from system parameters
            # We no longer need to get max_forgiveness_uses as there's no limit on retakes
            # The forgiveness logic will be handled separately through requests
            
            data['forgiveness_counter'] = forgiveness_counter
            data['max_forgiveness'] = None  # Set to None as it's not used anymore
            
            # Get probation counter information
            cursor.execute("""
                SELECT probation_counter 
                FROM student_semester_summary
                WHERE student_id = %s
                ORDER BY year DESC, semester DESC
                LIMIT 1
            """, (student_id,))
            
            probation_result = cursor.fetchone()
            probation_counter = probation_result[0] if probation_result and probation_result[0] is not None else 0
            
            # Only include probation counter if it's greater than 0
            if probation_counter > 0:
                data['probation_counter'] = probation_counter
                
                # Get max probation limits from system parameters
                cursor.execute("""
                    SELECT max_probation_board, max_probation_total, min_cumulative_gpa
                    FROM system_parameters 
                    ORDER BY last_updated DESC LIMIT 1
                """)
                probation_params = cursor.fetchone()
                
                if probation_params:
                    data['max_probation_board'] = probation_params[0]
                    data['max_probation_total'] = probation_params[1]
                    data['min_cumulative_gpa'] = float(probation_params[2]) if probation_params[2] else None
                
                # Check if student has overrides
                cursor.execute("""
                    SELECT max_probation_board, max_probation_total
                    FROM student_parameters_overrides
                    WHERE student_id = %s
                """, (student_id,))
                
                probation_override = cursor.fetchone()
                if probation_override:
                    if probation_override[0] is not None:
                        data['max_probation_board'] = probation_override[0]
                    if probation_override[1] is not None:
                        data['max_probation_total'] = probation_override[1]
                
                # Get student's current cumulative GPA
                cursor.execute("""
                    SELECT cumulative_gpa
                    FROM student_semester_summary
                    WHERE student_id = %s
                    ORDER BY year DESC, semester DESC
                    LIMIT 1
                """, (student_id,))
                
                gpa_result = cursor.fetchone()
                if gpa_result and gpa_result[0] is not None:
                    data['current_cumulative_gpa'] = float(gpa_result[0])
                
                # Add ordinal suffix for probation counter
                if probation_counter == 1:
                    data['probation_ordinal'] = 'First'
                elif probation_counter == 2:
                    data['probation_ordinal'] = 'Second'
                elif probation_counter == 3:
                    data['probation_ordinal'] = 'Third'
                else:
                    data['probation_ordinal'] = f'{probation_counter}th'
            
            return jsonify({
                'success': True,
                'data': data
            })
        
        except Exception as e:
            current_app.logger.error(f"Error loading course registration data: {str(e)}")
            import traceback
            current_app.logger.error(traceback.format_exc())
            return jsonify({
                'success': False,
                'message': 'Failed to load course registration data',
                'error': str(e),
                'code': 'DATA_LOAD_ERROR'
            }), 500
    
    except Exception as e:
        current_app.logger.error(f"Unexpected error in course_registration route: {str(e)}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'message': 'An unexpected error occurred',
            'error': str(e),
            'code': 'UNEXPECTED_ERROR'
        }), 500

def get_max_courses():
    """Returns the current max courses allowed per semester"""
    cursor = current_app.mysql.connection.cursor()
    try:
        cursor.execute("SELECT max_courses_per_semester FROM system_parameters LIMIT 1")
        result = cursor.fetchone()
        return result[0]
    except Exception as e:
        current_app.logger.error(f"Error fetching max courses: {str(e)}")
    finally:
        cursor.close()


@student_bp.route('/enrollment-history')
@login_required
def enrollment_history():
    try:
        student = session.get('student')
        if not student:
            return handle_unauthorized()
            
        student_id = student['student_id']
        current_app.logger.info(f"Loading enrollment history for student {student_id}")
        
        try:
            # Get all semesters for the student
            semesters = get_student_semesters(student_id)
            
            # Calculate and store semester summaries
            calculate_semester_summaries(student_id, semesters)
            
            # Build the enrollment data structure for response
            enrollment_data = build_enrollment_data(student_id, semesters)
            
            # Calculate remaining forgiveness uses for the student
            cursor = current_app.mysql.connection.cursor()
            try:
                # 1) Determine the maximum forgiveness uses (override takes precedence over system default)
                cursor.execute("""
                    SELECT max_forgiveness_uses
                    FROM student_parameters_overrides
                    WHERE student_id = %s
                """, (student_id,))
                override_row = cursor.fetchone()
                if override_row and override_row[0] is not None:
                    max_forgiveness_uses = int(override_row[0])
                else:
                    cursor.execute("""
                        SELECT max_forgiveness_uses
                        FROM system_parameters
                        ORDER BY last_updated DESC
                        LIMIT 1
                    """)
                    system_row = cursor.fetchone()
                    max_forgiveness_uses = int(system_row[0]) if system_row and system_row[0] is not None else None

                # 2) Count the number of forgiveness policies already used by the student
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM add_course
                    WHERE student_id = %s AND forgiveness = 1
                """, (student_id,))
                used_row = cursor.fetchone()
                used_count = int(used_row[0]) if used_row and used_row[0] is not None else 0

                # 3) Calculate remaining uses (ensure it is not negative)
                remaining_uses = None
                if max_forgiveness_uses is not None:
                    remaining_uses = max(max_forgiveness_uses - used_count, 0)

                # 4) Attach to response payload
                enrollment_data['max_forgiveness_uses'] = max_forgiveness_uses
                enrollment_data['remaining_forgiveness_uses'] = remaining_uses
            finally:
                cursor.close()
            
            # Get forgiveness requests status
            cursor = current_app.mysql.connection.cursor()
            try:
                cursor.execute("""
                    SELECT course_code, status, request_date, handling_date
                    FROM forgiveness_requests
                    WHERE student_id = %s
                """, (student_id,))
                
                forgiveness_status = {}
                for req in cursor.fetchall():
                    course_code, status, request_date, handling_date = req
                    forgiveness_status[course_code] = {
                        'status': status,
                        'request_date': request_date.strftime('%Y-%m-%d %H:%M:%S') if request_date else None,
                        'handling_date': handling_date.strftime('%Y-%m-%d %H:%M:%S') if handling_date else None
                    }
                
                enrollment_data['forgiveness_status'] = forgiveness_status
            finally:
                cursor.close()
            
            current_app.logger.debug(f"Enrollment history data loaded for student {student_id}")
            return jsonify({
                'success': True,
                'section': 'enrollment-history',
                'title': 'Enrollment History',
                'data': enrollment_data
            })
            
        except Exception as e:
            return handle_data_load_error(e)
            
    except Exception as e:
        return handle_unexpected_error(e)

def handle_unauthorized():
    current_app.logger.error("No student in session")
    return jsonify({
        'success': False,
        'message': 'User not logged in',
        'code': 'UNAUTHORIZED'
    }), 401

def handle_data_load_error(e):
    current_app.logger.error(f"Error loading enrollment history: {str(e)}", exc_info=True)
    return jsonify({
        'success': False,
        'message': 'Failed to load enrollment history',
        'code': 'DATA_LOAD_ERROR',
        'error': str(e)
    }), 500

def handle_unexpected_error(e):
    current_app.logger.error(f"Unexpected error in enrollment_history: {str(e)}", exc_info=True)
    return jsonify({
        'success': False,
        'message': 'An unexpected error occurred',
        'code': 'INTERNAL_ERROR',
        'error': str(e)
    }), 500

def get_student_semesters(student_id):
    """Get all semesters the student has attended (including current enrollment)"""
    cursor = current_app.mysql.connection.cursor()
    cursor.execute("""
        SELECT DISTINCT year, semester 
        FROM add_course 
        WHERE student_id = %s 
        AND status IN ('passed', 'failed', 'enrolled')  # Include enrolled courses
        ORDER BY year DESC, semester DESC
    """, (student_id,))
    return [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]

def calculate_semester_summaries(student_id, semesters):
    """Calculate and store semester summaries in database"""
    cursor = current_app.mysql.connection.cursor()
    
    # Get all courses the student has taken with grades for forgiveness processing
    cursor.execute("""
        SELECT 
            ac.course_code,
            ac.grade_point, 
            c.coefficient,
            ac.forgiveness
        FROM add_course ac
        JOIN courses c ON ac.course_code = c.course_code
        WHERE ac.student_id = %s
        AND ac.status IN ('passed', 'failed')
        AND ac.grade_point IS NOT NULL
    """, (student_id,))
    
    all_graded_courses = cursor.fetchall()
    
    # Process forgiveness - for each course, find if it has multiple attempts with forgiveness
    forgiveness_courses = {}
    for course in all_graded_courses:
        course_code = course[0]
        grade_point = course[1]
        coefficient = course[2]
        has_forgiveness = course[3]
        
        if has_forgiveness:
            if course_code not in forgiveness_courses:
                forgiveness_courses[course_code] = {'best_grade': grade_point, 'coefficient': coefficient}
            elif grade_point > forgiveness_courses[course_code]['best_grade']:
                forgiveness_courses[course_code]['best_grade'] = grade_point
    
    semesters_chronological = sorted(semesters, key=lambda x: (x['year'], x['semester']))
    cumulative_registered = 0
    cumulative_earned = 0
    cumulative_grade_points = 0
    cumulative_coefficients = 0  
    
    # Track courses we've already seen for forgiveness handling
    processed_forgiveness_courses = set()
    
    for semester in semesters_chronological:
        year = semester['year']
        semester_num = semester['semester']
        
        stats = calculate_semester_stats(cursor, student_id, year, semester_num)
        
        # Handle forgiveness for this semester
        cursor.execute("""
            SELECT 
                ac.course_code, 
                ac.grade_point, 
                c.coefficient,
                ac.forgiveness
            FROM add_course ac
            JOIN courses c ON ac.course_code = c.course_code
            WHERE ac.student_id = %s 
            AND ac.year = %s 
            AND ac.semester = %s
            AND ac.status IN ('passed', 'failed')
            AND ac.grade_point IS NOT NULL
        """, (student_id, year, semester_num))
        
        semester_courses = cursor.fetchall()
        
        # Update cumulative registered and earned credits
        cumulative_registered += stats['registered_credits']
        cumulative_earned += stats['earned_credits']
        
        # Special handling for grade points to apply forgiveness policy
        for course in semester_courses:
            course_code = course[0]
            grade_point = course[1]
            coefficient = course[2]
            has_forgiveness = course[3]
            
            # Handle normal courses normally
            if not has_forgiveness:
                cumulative_grade_points += grade_point * coefficient
                cumulative_coefficients += coefficient
            else:
                # Special handling for forgiveness courses
                if course_code in forgiveness_courses:
                    best_grade = forgiveness_courses[course_code]['best_grade']
                    course_coefficient = forgiveness_courses[course_code]['coefficient']
                    
                    if course_code not in processed_forgiveness_courses:
                        # First time seeing this forgiveness course, add with best grade
                        cumulative_grade_points += best_grade * course_coefficient
                        cumulative_coefficients += course_coefficient
                        processed_forgiveness_courses.add(course_code)
                else:
                    # Shouldn't happen, but handle as normal course
                    cumulative_grade_points += grade_point * coefficient
                    cumulative_coefficients += coefficient
        
        # Calculate GPAs
        semester_gpa = stats['grade_points'] / stats['total_coefficients'] if stats['total_coefficients'] > 0 else None
        cumulative_gpa = cumulative_grade_points / cumulative_coefficients if cumulative_coefficients > 0 else None
        
        # Store summary in database
        store_semester_summary(
            cursor, student_id, year, semester_num,
            stats['registered_credits'], stats['earned_credits'], semester_gpa,
            cumulative_registered, cumulative_earned, cumulative_gpa
        )
    
    current_app.mysql.connection.commit()

def calculate_semester_stats(cursor, student_id, year, semester_num):
    """Calculate statistics for a single semester"""
    # First get ALL registered credits (including enrolled courses)
    cursor.execute("""
        SELECT 
            SUM(c.coefficient) as registered_credits,
            SUM(CASE WHEN ac.status = 'passed' THEN c.coefficient ELSE 0 END) as earned_credits
        FROM add_course ac
        JOIN courses c ON ac.course_code = c.course_code
        WHERE ac.student_id = %s AND ac.year = %s AND ac.semester = %s
        AND ac.status IN ('passed', 'failed', 'enrolled')  # Include enrolled in registered count
    """, (student_id, year, semester_num))
    
    credits_result = cursor.fetchone()
    
    # Then get GPA-related stats (excluding enrolled courses)
    cursor.execute("""
        SELECT 
            SUM(ac.grade_point * c.coefficient) as grade_points,
            SUM(c.coefficient) as total_coefficients
        FROM add_course ac
        JOIN courses c ON ac.course_code = c.course_code
        WHERE ac.student_id = %s AND ac.year = %s AND ac.semester = %s
        AND ac.status IN ('passed', 'failed')  # Exclude enrolled from GPA
    """, (student_id, year, semester_num))
    
    gpa_result = cursor.fetchone()
    
    return {
        'registered_credits': credits_result[0] or 0,
        'earned_credits': credits_result[1] or 0,
        'grade_points': gpa_result[0] or 0,
        'total_coefficients': gpa_result[1] or 0
    }

def store_semester_summary(cursor, student_id, year, semester_num, 
                          registered_credits, earned_credits, semester_gpa,
                          cumulative_registered, cumulative_earned, cumulative_gpa):
    """Store semester summary in database"""
    # Check if student is dismissed - if so, don't create a semester summary
    cursor.execute("""
        SELECT enrollment_status FROM student
        WHERE student_id = %s
    """, (student_id,))
    
    student_status = cursor.fetchone()
    if student_status and student_status[0] == 'dismissed':
        current_app.logger.info(f"Not storing semester summary for dismissed student {student_id}")
        return
        
    cursor.execute("""
        INSERT INTO student_semester_summary (
            student_id, year, semester, 
            registered_credits, earned_credits, semester_gpa,
            cumulative_registered_credits, cumulative_earned_credits, cumulative_gpa
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            registered_credits = VALUES(registered_credits),
            earned_credits = VALUES(earned_credits),
            semester_gpa = VALUES(semester_gpa),
            cumulative_registered_credits = VALUES(cumulative_registered_credits),
            cumulative_earned_credits = VALUES(cumulative_earned_credits),
            cumulative_gpa = VALUES(cumulative_gpa)
            -- probation_counter and forgiveness_counter preserved
    """, (
        student_id, year, semester_num,
        registered_credits, earned_credits, semester_gpa,
        cumulative_registered, cumulative_earned, cumulative_gpa
    ))

def build_enrollment_data(student_id, semesters):
    """Build the enrollment data structure for the response"""
    cursor = current_app.mysql.connection.cursor()
    enrollment_data = {'semesters': []}
    
    for semester in semesters:
        year = semester['year']
        semester_num = semester['semester']
        
        # Get semester summary
        summary = get_semester_summary(cursor, student_id, year, semester_num)
        
        # Get semester courses
        courses = get_semester_courses(cursor, student_id, year, semester_num)
        
        enrollment_data['semesters'].append({
            'year': year,
            'semester': semester_num,
            'registered_credits': float(summary['registered_credits']),
            'earned_credits': float(summary['earned_credits']),
            'semester_gpa': float(summary['semester_gpa']) if summary['semester_gpa'] is not None else None,
            'cumulative_registered_credits': float(summary['cumulative_registered_credits']),
            'cumulative_earned_credits': float(summary['cumulative_earned_credits']),
            'cumulative_gpa': float(summary['cumulative_gpa']) if summary['cumulative_gpa'] is not None else None,
            'courses': courses
        })
    
    return enrollment_data

def get_semester_summary(cursor, student_id, year, semester_num):
    """Get stored semester summary from database"""
    cursor.execute("""
        SELECT 
            registered_credits,
            earned_credits,
            semester_gpa,
            cumulative_registered_credits,
            cumulative_earned_credits,
            cumulative_gpa
        FROM student_semester_summary
        WHERE student_id = %s AND year = %s AND semester = %s
    """, (student_id, year, semester_num))
    
    result = cursor.fetchone()
    if result:
        return dict(zip([col[0] for col in cursor.description], result))
    return {
        'registered_credits': 0,
        'earned_credits': 0,
        'semester_gpa': None,
        'cumulative_registered_credits': 0,
        'cumulative_earned_credits': 0,
        'cumulative_gpa': None
    }

def get_semester_courses(cursor, student_id, year, semester_num):
    """Get all courses for a semester"""
    cursor.execute("""
        SELECT 
            ac.course_code, 
            c.course_name, 
            c.coefficient,
            ac.status,
            ac.letter_grade,
            ac.grade_point,
            ac.forgiveness
        FROM add_course ac
        JOIN courses c ON ac.course_code = c.course_code
        WHERE ac.student_id = %s 
        AND ac.year = %s 
        AND ac.semester = %s
        AND ac.status IN ('passed', 'failed', 'enrolled')
        ORDER BY ac.course_code
    """, (student_id, year, semester_num))
    
    courses = []
    for row in cursor.fetchall():
        course = dict(zip([col[0] for col in cursor.description], row))
        course['coefficient'] = float(course['coefficient'])
        if course['grade_point'] is not None:
            course['grade_point'] = float(course['grade_point'])
        courses.append(course)
    
    return courses


@student_bp.route('/submit-courses', methods=['POST'])
@login_required
def submit_courses():
    cursor = None
    connection_created = False
    db_connection = None
    transaction_successful = False
    
    try:
        student = session.get('student')
        if not student:
            return jsonify({
                'success': False,
                'message': 'User not logged in',
                'code': 'UNAUTHORIZED'
            }), 401

        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided',
                'code': 'NO_DATA'
            }), 400

        current_app.logger.debug(f"Course submission data received: {data}")
        
        selected_courses = data.get('selected_courses', [])
        current_semester = data.get('current_semester')
        current_year = data.get('current_year')
        eligible_current_courses = data.get('eligible_current_courses', [])
        not_met_courses = data.get('not_met_courses', [])
        retake_courses = data.get('retake_courses', [])
        elective_selections = data.get('elective_selections', {})

        if not all([current_semester, current_year]):
            return jsonify({
                'success': False,
                'message': 'Missing semester or year information',
                'code': 'MISSING_DATA'
            }), 400

        if len(selected_courses) > 7:
            return jsonify({
                'success': False,
                'message': 'Cannot select more than 7 courses',
                'code': 'MAX_COURSES_EXCEEDED'
            }), 400

        # Create a set of retake course codes for faster lookup
        retake_course_codes = {course['course_code'] for course in retake_courses}
        
        cursor = current_app.mysql.connection.cursor()
        
        # Check if student is restricted due to credit requirements
        student_year = get_student_year(student['student_id'])
        is_restricted = False
        
        if student_year and student_year >= 3:
            # Get student's French status
            cursor.execute("SELECT non_french FROM student WHERE student_id = %s", (student['student_id'],))
            is_non_french = cursor.fetchone()[0] == 1
            
            # Get min_credit_percentage_major from system_parameters
            cursor.execute("SELECT min_credit_percentage_major FROM system_parameters ORDER BY last_updated DESC LIMIT 1")
            min_percentage_row = cursor.fetchone()
            min_percentage = float(min_percentage_row[0]) if min_percentage_row and min_percentage_row[0] is not None else None
            
            # Calculate total weights for year 1 and 2 courses
            total_weights_query = """
                SELECT SUM(coefficient) as total_weights
                FROM courses
                WHERE year IN (1, 2)
                {french_clause}
            """.format(
                french_clause="AND (requires_french = 0 OR requires_french IS NULL)" if is_non_french else ""
            )
            cursor.execute(total_weights_query)
            total_weights_row = cursor.fetchone()
            total_weights = float(total_weights_row[0]) if total_weights_row and total_weights_row[0] is not None else 0.0
            
            # Calculate earned credits for year 1 and 2 courses
            earned_credits_query = """
                SELECT SUM(c.coefficient) as earned_credits
                FROM add_course ac
                JOIN courses c ON ac.course_code = c.course_code
                WHERE ac.student_id = %s 
                AND ac.status = 'passed'
                AND c.year IN (1, 2)
                {french_clause}
            """.format(
                french_clause="AND (c.requires_french = 0 OR c.requires_french IS NULL)" if is_non_french else ""
            )
            cursor.execute(earned_credits_query, (student['student_id'],))
            earned_credits_row = cursor.fetchone()
            earned_credits = 0.0
            if earned_credits_row and earned_credits_row[0] is not None:
                try:
                    earned_credits = float(earned_credits_row[0])
                except (TypeError, ValueError):
                    earned_credits = 0.0
            
            # Calculate required credits based on min_percentage
            required_credits = None
            if min_percentage and total_weights:
                required_credits = total_weights * (min_percentage / 100)
                # Check if student meets credit requirements
                is_restricted = earned_credits < required_credits
        
        # Validate elective selections
        if elective_selections:
            # Get elective group requirements
            cursor.execute("""
                SELECT elective_group_number, required_picks
                FROM elective_group_requirements
            """)
            requirements = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Validate each elective group
            for group_number, selected_codes in elective_selections.items():
                group_number = int(group_number)  # Convert string key to int
                required_picks = requirements.get(group_number, 0)
                
                # Check if the required number of courses are selected
                if len(selected_codes) < required_picks:
                    return jsonify({
                        'success': False,
                        'message': f'Group {group_number} requires at least {required_picks} course selections',
                        'code': 'ELECTIVE_REQUIREMENT_NOT_MET'
                    }), 400
        
        # Count retake courses, but no longer limit them
        # The forgiveness logic will be handled separately through requests
        forgiveness_count = len(retake_course_codes)
        
        # We no longer need to check max_forgiveness_uses as there's no limit on retakes
        
        # Check if student has at least 2 specializations
        cursor.execute("""
            SELECT major, second_major, minor, second_minor
            FROM student
            WHERE student_id = %s
        """, (student['student_id'],))
        
        specialization_row = cursor.fetchone()
        specialization_count = 0
        if specialization_row:
            for spec in specialization_row:
                if spec:  # Count non-null specializations
                    specialization_count += 1
        
        # Check if any of the selected courses are year 3 or 4 courses
        has_year_3_4_courses = False
        if specialization_count < 2:
            # Only check if we need to (when specialization count is less than 2)
            selected_course_codes = tuple(selected_courses)
            if selected_course_codes:  # Make sure it's not empty
                cursor.execute("""
                    SELECT 1 FROM courses
                    WHERE course_code IN %s AND year IN (3, 4)
                    LIMIT 1
                """, (selected_course_codes,))
                has_year_3_4_courses = cursor.fetchone() is not None
        
        # First delete all existing enrollments for this semester
        cursor.execute("""
            DELETE FROM add_course 
            WHERE student_id = %s 
            AND year = %s 
            AND semester = %s
            AND status IN ('enrolled', 'notenrolled')
        """, (student['student_id'], current_year, current_semester))
        current_app.logger.debug("Deleted existing enrollments for edit mode")
        
        # First, get all previously enrolled courses with their study groups
        cursor.execute("""
            SELECT course_code, lecture_study_group, tutorial_study_group
            FROM add_course 
            WHERE student_id = %s 
            AND year = %s 
            AND semester = %s
            AND (lecture_study_group IS NOT NULL OR tutorial_study_group IS NOT NULL)
        """, (student['student_id'], current_year, current_semester))
        
        previous_study_groups = {}
        for row in cursor.fetchall():
            course_code, lecture_group, tutorial_group = row
            previous_study_groups[course_code] = {
                'lecture': lecture_group,
                'tutorial': tutorial_group
            }
    
        # Add selected courses as 'enrolled'
        for course_code in selected_courses:
            # Check if this is a retake course by looking in the set
            is_retake = course_code in retake_course_codes
            
            # Check if this course was previously enrolled with study groups
            groups = previous_study_groups.get(course_code, None)
            
            if groups:
                # If the course was previously enrolled with study groups, preserve them
                lecture_group = groups.get('lecture')
                tutorial_group = groups.get('tutorial')
                
                if is_retake:
                    cursor.execute("""
                        INSERT INTO add_course 
                        (student_id, course_code, year, semester, status, date, retake, 
                         lecture_study_group, tutorial_study_group)
                        VALUES (%s, %s, %s, %s, 'enrolled', CURDATE(), 1, %s, %s)
                    """, (student['student_id'], course_code, current_year, current_semester, 
                          lecture_group, tutorial_group))
                else:
                    cursor.execute("""
                        INSERT INTO add_course 
                        (student_id, course_code, year, semester, status, date, retake,
                         lecture_study_group, tutorial_study_group)
                        VALUES (%s, %s, %s, %s, 'enrolled', CURDATE(), 0, %s, %s)
                    """, (student['student_id'], course_code, current_year, current_semester,
                          lecture_group, tutorial_group))
            else:
                # For courses without previous study group
                if is_retake:
                    cursor.execute("""
                        INSERT INTO add_course 
                        (student_id, course_code, year, semester, status, date, retake)
                        VALUES (%s, %s, %s, %s, 'enrolled', CURDATE(), 1)
                    """, (student['student_id'], course_code, current_year, current_semester))
                    current_app.logger.debug(f"Added enrolled retake course: {course_code} (retake=1)")
                else:
                    cursor.execute("""
                        INSERT INTO add_course 
                        (student_id, course_code, year, semester, status, date, retake)
                        VALUES (%s, %s, %s, %s, 'enrolled', CURDATE(), 0)
                    """, (student['student_id'], course_code, current_year, current_semester))
                    current_app.logger.debug(f"Added enrolled regular course: {course_code} (retake=0)")
        
        # Add selected elective courses as 'enrolled'
        if elective_selections:
            # Create a set of already enrolled course codes for faster lookup
            already_enrolled_codes = set(selected_courses)
            
            for group_number, selected_codes in elective_selections.items():
                for course_code in selected_codes:
                    # Skip if already enrolled through selected_courses
                    if course_code in already_enrolled_codes:
                        current_app.logger.debug(f"Skipping duplicate elective course: {course_code} (already in selected_courses)")
                        continue
                        
                    cursor.execute("""
                        INSERT INTO add_course 
                        (student_id, course_code, year, semester, status, date, retake)
                        VALUES (%s, %s, %s, %s, 'enrolled', CURDATE(), 0)
                    """, (student['student_id'], course_code, current_year, current_semester))
                    current_app.logger.debug(f"Added enrolled elective course: {course_code} from group {group_number}")
        
        # Skip adding notenrolled courses if student has fewer than 2 specializations and is taking year 3-4 courses
        if not (specialization_count < 2 and has_year_3_4_courses):
            # Add unchecked eligible current courses as 'notenrolled' (no forgiveness column)
            eligible_codes = [c['course_code'] for c in eligible_current_courses]
            unchecked_current = [code for code in eligible_codes if code not in selected_courses]
            
            for course_code in unchecked_current:
                cursor.execute("""
                    INSERT INTO add_course 
                    (student_id, course_code, year, semester, status, date, lecture_study_group, tutorial_study_group)
                    VALUES (%s, %s, %s, %s, 'notenrolled', CURDATE(), NULL, NULL)
                """, (student['student_id'], course_code, current_year, current_semester))
                current_app.logger.debug(f"Added notenrolled course: {course_code}")
            
            # Add not_met_requirements courses as 'notenrolled' (no forgiveness column)
            for course in not_met_courses:
                if course['course_code'] not in selected_courses:
                    cursor.execute("""
                        INSERT INTO add_course 
                        (student_id, course_code, year, semester, status, date, lecture_study_group, tutorial_study_group)
                        VALUES (%s, %s, %s, %s, 'notenrolled', CURDATE(), NULL, NULL)
                    """, (student['student_id'], course['course_code'], current_year, current_semester))
                    current_app.logger.debug(f"Added notenrolled for unmet requirements: {course['course_code']}")
        else:
            current_app.logger.debug("Skipping notenrolled courses: student has fewer than 2 specializations and is taking year 3-4 courses")
            unchecked_current = []
        
        # If student is restricted due to credit requirements, add current semester courses as 'notenrolled'
        if is_restricted:
            current_app.logger.debug(f"Student {student['student_id']} is restricted due to credit requirements")
            
            # Get current semester courses for the student's year
            current_semester_courses = get_current_courses(current_semester, current_year, student['student_id'])
            
            # Create a set of already processed courses
            processed_courses = set(selected_courses)
            processed_courses.update(unchecked_current)
            processed_courses.update([course['course_code'] for course in not_met_courses if course['course_code'] not in selected_courses])
            
            # Add any courses not already processed as 'notenrolled'
            for course in current_semester_courses['courses']:
                course_code = course['course_code']
                if course_code not in processed_courses:
                    cursor.execute("""
                        INSERT INTO add_course 
                        (student_id, course_code, year, semester, status, date, lecture_study_group, tutorial_study_group)
                        VALUES (%s, %s, %s, %s, 'notenrolled', CURDATE(), NULL, NULL)
                    """, (student['student_id'], course_code, current_year, current_semester))
                    current_app.logger.debug(f"Added notenrolled for restricted student: {course_code}")
                    unchecked_current.append(course_code)
        
        # Update forgiveness_counter in student_semester_summary based on the number of retake courses
        forgiveness_count = len(retake_course_codes)
        current_app.logger.debug(f"Updating forgiveness counter to {forgiveness_count} for student {student['student_id']}")
        
        # Ensure semester summary exists
        ensure_semester_summary_exists(cursor, student['student_id'], current_year, current_semester)
        
        # Update forgiveness counter
        cursor.execute("""
            UPDATE student_semester_summary
            SET forgiveness_counter = %s
            WHERE student_id = %s AND year = %s AND semester = %s
        """, (forgiveness_count, student['student_id'], current_year, current_semester))
        
        # Check schedule_validation parameter
        cursor.execute("""
            SELECT schedule_validation FROM schedule_parameters LIMIT 1
        """)
        schedule_validation_row = cursor.fetchone()
        schedule_validation = schedule_validation_row[0] if schedule_validation_row else 0
        
        if schedule_validation == 1:
            # Run the schedule optimizer to check if a feasible schedule can be created
            current_app.logger.info(f"Running schedule optimizer to check for feasible solutions for student {student['student_id']}")
            
            # Use the existing MySQL connection for the optimizer
            db_connection = current_app.mysql.connection
            connection_created = True
            
            # Run the optimizer with a single solution - just checking for feasibility
            schedule_result = optimize_student_schedule(student['student_id'], db_connection)
            
            # Check if a feasible solution was found
            if not schedule_result['success']:
                # If no feasible solution, roll back the transaction
                current_app.mysql.connection.rollback()
                current_app.logger.warning(f"No feasible schedule found for student {student['student_id']}. Rolling back course enrollment.")
                
                return jsonify({
                    'success': False,
                    'message': 'There is a scheduling conflict between the courses you selected. Please adjust your selection.',
                    'code': 'SCHEDULING_CONFLICT',
                    'details': schedule_result.get('message', 'Unable to create a schedule with these courses')
                }), 400
        else:
            # Skip optimization step when schedule_validation is disabled
            current_app.logger.info(f"Schedule validation disabled. Skipping optimizer for student {student['student_id']}")
            connection_created = True
            db_connection = current_app.mysql.connection
        
        # If we reach here, commit the transaction
        current_app.mysql.connection.commit()
        transaction_successful = True
        
        return jsonify({
            'success': True,
            'message': 'Courses submitted successfully',
            'selected_courses': selected_courses,
            'unchecked_current': unchecked_current,
            'current_semester': current_semester,
            'current_year': current_year,
            'has_existing_submissions': True
        })

    except Exception as e:
        if not transaction_successful:
            # Rollback if an error occurred and we haven't already committed
            current_app.mysql.connection.rollback()
        current_app.logger.error(f"Error in submit_courses: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': 'An error occurred during course submission',
            'code': 'SUBMISSION_ERROR',
            'error': str(e)
        }), 500
    finally:
        if cursor:
            cursor.close()

def get_student_data(student_id):
    """Get complete student data including profile picture, level, and enrollment status"""
    cursor = current_app.mysql.connection.cursor()
    try:
        cursor.execute(
            """SELECT student_id, first_name, last_name, year_of_study, 
                  level, profile_picture, email_address, enrollment_status FROM student 
               WHERE student_id = %s""",
            (student_id,)
        )
        result = cursor.fetchone()
        if result:
            columns = [col[0] for col in cursor.description]
            student_data = dict(zip(columns, result))
            if student_data.get('profile_picture'):
                student_data['profile_picture'] = base64.b64encode(
                    student_data['profile_picture']).decode('utf-8')
            return student_data
        return None
    except Exception as e:
        current_app.logger.error(f"Error in get_student_data: {str(e)}", exc_info=True)
        return None
    finally:
        cursor.close()



@student_bp.route('/major_minor/major_requirements')
@login_required
def get_major_gpa():
    try:
        student = session.get('student')
        if not student:
            return unauthorized_response()

        student_id = student['student_id']
        cursor = current_app.mysql.connection.cursor()

        # 1. Get basic student info
        cumulative_gpa, is_non_french = get_student_basic_info(cursor, student_id)
        
        # 2. Get system parameters
        min_percentage, min_cumulative_gpa = get_system_parameters(cursor)
        
        # 3. Calculate credit status
        credit_status = calculate_credit_status(cursor, student_id, is_non_french, min_percentage)
        
        # 4. Check cumulative GPA requirement
        meets_cumulative_gpa = check_cumulative_gpa_requirement(cumulative_gpa, min_cumulative_gpa)
        
        # 5. Get GPA requirements (system defaults + overrides)
        min_gpa_map = get_gpa_requirements(cursor, student_id)
        
        # 6. Get all majors data
        majors, majors_order = get_majors_data(cursor)
        
        # 7. Get student grades
        student_grades = get_student_grades(cursor, student_id)
        
        # 8. Calculate major-specific data & update table student
        major_data, specialized_gpas = calculate_major_data(
            cursor, majors, student_grades, min_gpa_map,
            credit_status['meets_requirement'], meets_cumulative_gpa
        )

        eligible_majors = [m for m in major_data if major_data[m]['is_eligible']]
        eligible_status = 1 if len(eligible_majors) > 0 else 0
        
        cursor.execute("""
            UPDATE student 
            SET eligible_for_major = %s 
            WHERE student_id = %s
        """, (eligible_status, student_id))
        
                    # 9. Store specialized GPAs in the database
        # Get student's year_of_study from student table
        cursor.execute("""
            SELECT year_of_study FROM student
            WHERE student_id = %s
        """, (student_id,))
        
        student_year_result = cursor.fetchone()
        if not student_year_result:
            current_app.logger.error(f"Could not find student with ID {student_id}")
            return error_response("Student not found")
            
        student_year = student_year_result[0]
        
        # Get current active semester
        _, current_semester = get_current_semester()
        if student_year and current_semester:
            # Always ensure a semester summary exists first
            ensure_semester_summary_exists(cursor, student_id, student_year, current_semester)
            
            # Now update the specialized GPAs
            update_fields = []
            params = []
            
            # Get current values to check if they've changed
            cursor.execute("""
                SELECT acct_gpa, ba_gpa, fin_gpa, it_gpa, mrk_gpa 
                FROM student_semester_summary
                WHERE student_id = %s AND year = %s AND semester = %s
            """, (student_id, student_year, current_semester))
            
            current_values = cursor.fetchone()
            
            # Map DB column indexes to specialized_gpas keys
            field_map = {
                0: 'acct_gpa',
                1: 'ba_gpa',
                2: 'fin_gpa',
                3: 'it_gpa',
                4: 'mrk_gpa'
            }
            
            # Check if values have changed or are NULL
            for idx, field in field_map.items():
                new_value = specialized_gpas[field]
                current_value = current_values[idx] if current_values else None
                
                # Update if:
                # 1. New value exists AND
                # 2. Either current value is NULL or values are different
                if new_value is not None and (current_value is None or abs(float(current_value) - new_value) > 0.0001):
                    update_fields.append(f"{field} = %s")
                    params.append(new_value)
                    current_app.logger.info(f"Updating {field} from {current_value} to {new_value}")
            
            if update_fields:  # Only update if there are values to update
                query = f"""
                    UPDATE student_semester_summary
                    SET {", ".join(update_fields)}
                    WHERE student_id = %s AND year = %s AND semester = %s
                """
                params.extend([student_id, student_year, current_semester])
                cursor.execute(query, params)
                current_app.logger.info(f"Updated specialized GPAs for student {student_id}, year {student_year}, semester {current_semester}")
            else:
                current_app.logger.info(f"No changes needed for specialized GPAs for student {student_id}")
        
        current_app.mysql.connection.commit()

        return jsonify({
            'success': True,
            'data': build_response_data(
                cumulative_gpa,
                min_cumulative_gpa,
                meets_cumulative_gpa,
                credit_status,
                major_data,
                majors_order,
                is_non_french
            )
        })

    except Exception as e:
        current_app.logger.error(f"Error calculating major GPAs: {str(e)}", exc_info=True)
        return error_response(str(e))
    finally:
        if 'cursor' in locals():
            cursor.close()

def unauthorized_response():
    return jsonify({
        'success': False,
        'message': 'User not logged in',
        'code': 'UNAUTHORIZED'
    }), 401

def error_response(error_msg):
    return jsonify({
        'success': False,
        'message': 'Failed to calculate major GPAs',
        'error': error_msg
    }), 500

def get_student_basic_info(cursor, student_id):
    cursor.execute("""
        SELECT cumulative_gpa, non_french 
        FROM student_semester_summary
        JOIN student ON student_semester_summary.student_id = student.student_id
        WHERE student_semester_summary.student_id = %s
        ORDER BY year DESC, semester DESC
        LIMIT 1
    """, (student_id,))
    result = cursor.fetchone()
    cumulative_gpa = float(result[0]) if result and result[0] is not None else None
    is_non_french = bool(result[1]) if result and result[1] is not None else False
    return cumulative_gpa, is_non_french

def get_system_parameters(cursor):
    cursor.execute("""
        SELECT min_credit_percentage_major, min_cumulative_gpa
        FROM system_parameters
        ORDER BY last_updated DESC
        LIMIT 1
    """)
    min_percentage_row = cursor.fetchone()
    min_percentage = float(min_percentage_row[0]) if min_percentage_row else None
    min_cumulative_gpa = float(min_percentage_row[1]) if min_percentage_row else None
    return min_percentage, min_cumulative_gpa

def calculate_credit_status(cursor, student_id, is_non_french, min_percentage):
    # Calculate total weights
    total_weights_query = """
        SELECT SUM(coefficient) as total_weights
        FROM courses
        WHERE year IN (1, 2)
        {french_clause}
    """.format(
        french_clause="AND (requires_french = 0 OR requires_french IS NULL)" if is_non_french else ""
    )
    cursor.execute(total_weights_query)
    total_weights_row = cursor.fetchone()
    total_weights = float(total_weights_row[0]) if total_weights_row and total_weights_row[0] is not None else 0.0

    # Calculate earned credits - use DISTINCT to count each course only once
    earned_credits_query = """
        SELECT SUM(c.coefficient) as earned_credits
        FROM (
            SELECT DISTINCT ac.course_code
            FROM add_course ac
            JOIN courses c ON ac.course_code = c.course_code
            WHERE ac.student_id = %s 
            AND ac.status = 'passed'
            AND c.year IN (1, 2)
            {french_clause}
        ) as distinct_courses
        JOIN courses c ON distinct_courses.course_code = c.course_code
    """.format(
        french_clause="AND (c.requires_french = 0 OR c.requires_french IS NULL)" if is_non_french else ""
    )
    cursor.execute(earned_credits_query, (student_id,))
    earned_credits_row = cursor.fetchone()
    earned_credits = 0.0  # Default value
    if earned_credits_row and earned_credits_row[0] is not None:
        try:
            earned_credits = float(earned_credits_row[0])
        except (TypeError, ValueError):
            earned_credits = 0.0

    # Check if meets requirement
    meets_requirement = False
    required_credits = None
    if min_percentage and total_weights and earned_credits is not None:
        required_credits = total_weights * (min_percentage / 100)
        meets_requirement = earned_credits >= total_weights

    return {
        'earned_credits': earned_credits,
        'required_credits': required_credits,
        'meets_requirement': meets_requirement,
        'min_percentage': min_percentage,
        'total_weights': total_weights
    }

def check_cumulative_gpa_requirement(cumulative_gpa, min_cumulative_gpa):
    return (cumulative_gpa is not None and 
            min_cumulative_gpa is not None and 
            cumulative_gpa >= min_cumulative_gpa)

def get_gpa_requirements(cursor, student_id):
    # Get system defaults
    cursor.execute("""
        SELECT 
            COALESCE(min_gpa_acct, 0) as min_gpa_acct,
            COALESCE(min_gpa_ba, 0) as min_gpa_ba,
            COALESCE(min_gpa_fin, 0) as min_gpa_fin,
            COALESCE(min_gpa_it, 0) as min_gpa_it,
            COALESCE(min_gpa_mrk, 0) as min_gpa_mrk
        FROM system_parameters
        ORDER BY last_updated DESC LIMIT 1
    """)
    system_defaults = cursor.fetchone()
    
    min_gpa_map = {
        'ACCT': float(system_defaults[0]),
        'BA': float(system_defaults[1]),
        'FIN': float(system_defaults[2]),
        'IT': float(system_defaults[3]),
        'MRK': float(system_defaults[4])
    }

    # Check for overrides
    cursor.execute("""
        SELECT 
            min_gpa_acct, min_gpa_ba, min_gpa_fin, min_gpa_it, min_gpa_mrk
        FROM student_parameters_overrides
        WHERE student_id = %s
    """, (student_id,))
    override_row = cursor.fetchone()
    
    if override_row:
        if override_row[0] is not None: min_gpa_map['ACCT'] = float(override_row[0])
        if override_row[1] is not None: min_gpa_map['BA'] = float(override_row[1])
        if override_row[2] is not None: min_gpa_map['FIN'] = float(override_row[2])
        if override_row[3] is not None: min_gpa_map['IT'] = float(override_row[3])
        if override_row[4] is not None: min_gpa_map['MRK'] = float(override_row[4])

    return min_gpa_map

def get_majors_data(cursor):
    cursor.execute("SELECT id, major, full_name FROM majors")
    majors = {row[0]: {'major': row[1], 'full_name': row[2]} for row in cursor.fetchall()}
    majors_order = [major_info['major'] for major_id, major_info in sorted(majors.items())]
    return majors, majors_order

def get_student_grades(cursor, student_id):
    cursor.execute("""
        SELECT course_code, COALESCE(grade_point, 0), letter_grade
        FROM add_course 
        WHERE student_id = %s AND status = 'passed'
    """, (student_id,))
    return {
        row[0]: {
            'grade_point': float(row[1]), 
            'letter_grade': row[2]
        } 
        for row in cursor.fetchall()
    }

def calculate_major_data(cursor, majors, student_grades, min_gpa_map,
                      meets_credit_req, meets_cumulative_gpa):
    """Calculate major data including specialized GPAs for each major"""
    major_data = {}
    # Dictionary to store specialized GPAs for database update
    specialized_gpas = {
        'acct_gpa': None,
        'ba_gpa': None,
        'fin_gpa': None,
        'it_gpa': None,
        'mrk_gpa': None
    }

    for major_id, major_info in majors.items():
        cursor.execute("""
            SELECT course_code, course_name, weight, COALESCE(minimum_grade_point, 0)
            FROM major_course_requirements
            WHERE major_id = %s
        """, (major_id,))

        requirements = []
        total_weighted = 0.0
        total_weights = 0.0
        all_completed_courses_meet_minimum = True
        minimum_grade_exists = False  # Track if any courses have minimum grades
        total_major_requirements_weight = 0.0  # Total weight of all requirements for this major
        has_minimum_requirements = False  # Flag to track if any course has minimum requirements

        # First, calculate the total weight of all requirements for this major
        for row in cursor.fetchall():
            course_code, course_name, weight, min_grade = row
            weight = float(weight)
            total_major_requirements_weight += weight
            if min_grade and float(min_grade) > 0:
                has_minimum_requirements = True
        
        # Reset cursor position to get requirements again
        cursor.execute("""
            SELECT course_code, course_name, weight, COALESCE(minimum_grade_point, 0)
            FROM major_course_requirements
            WHERE major_id = %s
        """, (major_id,))

        for row in cursor.fetchall():
            course_code, course_name, weight, min_grade = row
            weight = float(weight)
            min_grade = float(min_grade) if min_grade is not None else None

            # Check if this course has a minimum grade requirement
            if min_grade and min_grade > 0:
                minimum_grade_exists = True

            grade_data = student_grades.get(course_code)

            if grade_data:
                grade_point = grade_data['grade_point']
                letter_grade = grade_data['letter_grade']
                weighted_grade = grade_point * weight
                has_passed = True

                # Only check minimum if required and grade exists
                if min_grade and min_grade > 0:
                    meets_minimum = grade_point is not None and grade_point >= min_grade
                    if not meets_minimum:
                        all_completed_courses_meet_minimum = False
                else:
                    meets_minimum = True
                
                # Add to total weighted and total weights for GPA calculation
                total_weighted += weighted_grade
                total_weights += weight
            else:
                grade_point = None
                letter_grade = None
                weighted_grade = None
                has_passed = False
                # Only consider minimum requirements if the course has been taken
                meets_minimum = None  # No grade yet, so we can't say it doesn't meet minimum
                
                # If course has minimum requirement but not taken, mark as not meeting requirements
                if min_grade and min_grade > 0:
                    all_completed_courses_meet_minimum = False

            requirements.append({
                'course_code': course_code,
                'course_name': course_name,
                'weight': weight,
                'grade_point': grade_point,
                'letter_grade': letter_grade,
                'weighted_grade': weighted_grade,
                'has_passed': has_passed,
                'meets_minimum': meets_minimum,  # Will be None for untaken courses
                'minimum_grade_point': min_grade if min_grade != 0 else None
            })

        # Calculate specialized GPA using total weighted points divided by total major requirements weight
        # This ensures we consider all required courses in the denominator
        specialized_gpa = (total_weighted / total_major_requirements_weight) if total_major_requirements_weight > 0 else None
        required_gpa = min_gpa_map[major_info['major']]

        # Only consider minimum grades for courses that have been taken
        # For the major to be eligible, all taken courses with minimums must meet requirements
        meets_specialized_reqs = (
            specialized_gpa is not None and 
            specialized_gpa >= required_gpa and 
            all_completed_courses_meet_minimum
        )

        is_eligible = (
            meets_specialized_reqs and
            meets_credit_req and
            meets_cumulative_gpa
        )

        # Store the specialized GPA in the dictionary for database update
        major_code = major_info['major'].lower()
        if major_code in ['acct', 'ba', 'fin', 'it', 'mrk']:
            specialized_gpas[f'{major_code}_gpa'] = specialized_gpa

        major_data[major_info['major']] = {
            'gpa': specialized_gpa,
            'required_gpa': required_gpa,
            'is_eligible': is_eligible,
            'meets_specialized_reqs': meets_specialized_reqs,
            'all_completed_courses_meet_minimum': all_completed_courses_meet_minimum,
            'minimum_grade_exists': minimum_grade_exists,
            'has_minimum_requirements': has_minimum_requirements,
            'requirements': requirements,
            'full_name': major_info['full_name']
        }

    return major_data, specialized_gpas

def build_response_data(cumulative_gpa, min_cumulative_gpa, meets_cumulative_gpa,
                      credit_status, major_data, majors_order, is_non_french):
    return {
        'cumulative_gpa': cumulative_gpa,
        'min_cumulative_gpa': min_cumulative_gpa,
        'meets_cumulative_gpa': meets_cumulative_gpa,
        'credit_status': credit_status,
        'major_data': major_data,
        'majors_order': majors_order,
        'eligible_majors': [m for m in major_data if major_data[m]['is_eligible']],
        'is_non_french': is_non_french
    }


@student_bp.route('/major_minor/select', methods=['POST'])
@login_required
def select_major_minor():
    try:
        student = session.get('student')
        if not student:
            return unauthorized_response()

        data = request.get_json()
        if not data or 'choices' not in data:
            return invalid_data_response()

        choices = data['choices']
        student_id = student['student_id']

        cursor = current_app.mysql.connection.cursor()

        # Check if the selection window is open
        cursor.execute("""
            SELECT status
            FROM major_minor_selection_window
            WHERE status = 'open'
            ORDER BY id DESC
            LIMIT 1
        """)
        
        selection_window = cursor.fetchone()
        if not selection_window:
            return jsonify({
                'success': False,
                'message': 'Major/Minor selection is currently closed',
                'code': 'SELECTION_CLOSED'
            }), 403

        all_majors = fetch_all_majors(cursor)
        all_minors = fetch_all_minors(cursor)
        eligible_majors = fetch_eligible_majors()

        validation_error = validate_choices(choices, all_majors, all_minors, eligible_majors)
        if validation_error:
            return validation_error
            
        # Check if this combination is in the rejected_combinations table
        cursor.execute("""
            SELECT id FROM rejected_combinations
            WHERE major = %s
            AND (second_major = %s OR (second_major IS NULL AND %s IS NULL))
            AND (minor = %s OR (minor IS NULL AND %s IS NULL))
        """, (
            choices.get('major'),
            choices.get('second_major'), choices.get('second_major'),
            choices.get('minor'), choices.get('minor')
        ))
        
        rejected_combination = cursor.fetchone()
        if rejected_combination:
            # If the combination is in rejected_combinations, automatically set status to 'rejected'
            status = 'rejected'
            # Update the request or create a new one with rejected status
            upsert_request(cursor, student_id, choices, existing_request_id, status)
            current_app.mysql.connection.commit()
            
            return jsonify({
                'success': False,
                'message': 'This combination has been rejected by the administration and cannot be selected',
                'code': 'REJECTED_COMBINATION'
            }), 400

        # Get any existing request for this student (pending, accepted, or rejected)
        cursor.execute("""
            SELECT id FROM major_minor_requests
            WHERE student_id = %s
            ORDER BY submission_date DESC
            LIMIT 1
        """, (student_id,))
        existing = cursor.fetchone()
        existing_request_id = existing[0] if existing else None
        
        # Special handling for "NONE" selection
        if choices.get('major') == 'NONE':
            # For "NONE" selection, automatically set status to 'accepted'
            status = 'accepted'
            
            # Update student record to clear major, second_major, minor, and second_minor fields
            cursor.execute("""
                UPDATE student 
                SET major = NULL, second_major = NULL, minor = NULL, second_minor = NULL
                WHERE student_id = %s
            """, (student_id,))
            
            current_app.logger.info(f"Cleared major/minor fields for student {student_id} due to NONE selection")
        else:
            # For normal selections, check if there's an existing decision for this combination
            cursor.execute("""
                SELECT status FROM major_minor_requests
                WHERE major = %s 
                AND (second_major = %s OR (second_major IS NULL AND %s IS NULL))
                AND (minor = %s OR (minor IS NULL AND %s IS NULL))
                AND status IN ('accepted', 'rejected')
                LIMIT 1
            """, (
                choices.get('major'),
                choices.get('second_major'), choices.get('second_major'),
                choices.get('minor'), choices.get('minor')
            ))
            
            existing_decision = cursor.fetchone()
            status = existing_decision[0] if existing_decision else 'pending'
        
        # Update the request or create a new one with the appropriate status
        upsert_request(cursor, student_id, choices, existing_request_id, status)

        current_app.mysql.connection.commit()

        return jsonify({
            'success': True,
            'message': f'Major/Minor selection submitted successfully',
            'status': status  # Return the actual status (pending, accepted, or rejected)
        })

    except Exception as e:
        current_app.logger.error(f"Error submitting Major/Minor selection: {str(e)}", exc_info=True)
        return error_response(str(e))
    finally:
        if 'cursor' in locals():
            cursor.close()

def invalid_data_response():
    return jsonify({
        'success': False,
        'message': 'Invalid request data',
        'code': 'INVALID_DATA'
    }), 400

def fetch_all_majors(cursor):
    cursor.execute("SELECT major, full_name FROM majors")
    return {row[0]: row[1] for row in cursor.fetchall()}

def fetch_all_minors(cursor):
    cursor.execute("SELECT minor, full_name FROM minors")
    return {row[0]: row[1] for row in cursor.fetchall()}

def fetch_eligible_majors():
    gpa_data = get_major_gpa().get_json()
    if not gpa_data['success']:
        return None
    return gpa_data['data']['eligible_majors']

def validate_choices(choices, all_majors, all_minors, eligible_majors):
    if eligible_majors is None:
        return jsonify({
            'success': False,
            'message': 'Failed to verify eligibility',
            'code': 'ELIGIBILITY_CHECK_FAILED'
        }), 400

    # Validate that user has selected either a second major or a minor when major is not NONE
    if 'major' in choices and choices['major'] and choices['major'] != 'NONE':
        if not ('second_major' in choices and choices['second_major']) and not ('minor' in choices and choices['minor']):
            return jsonify({
                'success': False,
                'message': 'You must select either a second major or a minor to complete your selection',
                'code': 'INCOMPLETE_SELECTION'
            }), 400
    # For NONE selection, no second major or minor is required

    # Validate major
    if 'major' in choices and choices['major']:
        if choices['major'] != 'NONE' and choices['major'] not in eligible_majors:
            return jsonify({
                'success': False,
                'message': 'Not eligible for selected major',
                'code': 'NOT_ELIGIBLE'
            }), 400
            
    # This validation is already done above

    # Validate second major
    if 'second_major' in choices and choices['second_major']:
        if choices['second_major'] not in eligible_majors:
            return jsonify({
                'success': False,
                'message': 'Not eligible for second major',
                'code': 'NOT_ELIGIBLE'
            }), 400
        if 'major' in choices and choices['major'] == choices['second_major']:
            return jsonify({
                'success': False,
                'message': 'Second major must be different from first',
                'code': 'DUPLICATE_MAJOR'
            }), 400

    # Validate minor
    if 'minor' in choices and choices['minor']:
        if choices['minor'] not in all_minors:
            return jsonify({
                'success': False,
                'message': 'Invalid minor selected',
                'code': 'INVALID_MINOR'
            }), 400
        if 'major' in choices and choices['major'] == choices['minor']:
            return jsonify({
                'success': False,
                'message': 'Minor cannot match major',
                'code': 'MAJOR_MINOR_CONFLICT'
            }), 400

    return None

def get_existing_pending_request(cursor, student_id):
    cursor.execute("""
        SELECT id FROM major_minor_requests
        WHERE student_id = %s AND status = 'pending'
    """, (student_id,))
    existing = cursor.fetchone()
    return existing[0] if existing else None

def upsert_request(cursor, student_id, choices, existing_request_id, status):
    if existing_request_id:
        cursor.execute("""
            UPDATE major_minor_requests
            SET major = %s,
                second_major = %s,
                minor = %s,
                second_minor = NULL,
                submission_date = CURRENT_DATE,
                status = %s
            WHERE id = %s
        """, (
            choices.get('major'),
            choices.get('second_major'),
            choices.get('minor'),
            status,
            existing_request_id
        ))
    else:
        cursor.execute("""
            INSERT INTO major_minor_requests 
            (student_id, major, second_major, minor, second_minor, status)
            VALUES (%s, %s, %s, %s, NULL, %s)
        """, (
            student_id,
            choices.get('major'),
            choices.get('second_major'),
            choices.get('minor'),
            status
        ))


@student_bp.route('/major_minor/rejected_combinations')
@login_required
def get_rejected_combinations():
    try:
        cursor = current_app.mysql.connection.cursor()
        
        # Get all rejected combinations
        cursor.execute("""
            SELECT major, second_major, minor, second_minor, rejection_date
            FROM rejected_combinations
            ORDER BY rejection_date DESC
        """)
        
        combinations = []
        for row in cursor.fetchall():
            combinations.append({
                'major': row[0],
                'second_major': row[1],
                'minor': row[2],
                'second_minor': row[3],
                'rejection_date': row[4].strftime('%Y-%m-%d') if row[4] else None
            })
        
        return jsonify({
            'success': True,
            'rejected_combinations': combinations
        })
        
    except Exception as e:
        current_app.logger.error(f"Error fetching rejected combinations: {str(e)}", exc_info=True)
        return error_response(str(e))
    finally:
        if 'cursor' in locals():
            cursor.close()

@student_bp.route('/major_minor/options')
@login_required
def get_major_minor_options():
    try:
        cursor = current_app.mysql.connection.cursor()
        
        # Get all majors and minors with their full names
        cursor.execute("SELECT major, full_name FROM majors")
        majors = {row[0]: row[1] for row in cursor.fetchall()}
        
        cursor.execute("SELECT minor, full_name FROM minors")
        minors = {row[0]: row[1] for row in cursor.fetchall()}
        
        return jsonify({
            'success': True,
            'majors': majors,
            'minors': minors
        })
        
    except Exception as e:
        current_app.logger.error(f"Error fetching major/minor options: {str(e)}", exc_info=True)
        return error_response(str(e))
    finally:
        if 'cursor' in locals():
            cursor.close()


@student_bp.route('/major_minor/selection_status')
@login_required
def get_major_minor_selection_status():
    """Get the current status of major/minor selection period"""
    try:
        cursor = current_app.mysql.connection.cursor()
        
        # Check for scheduled periods that should be activated
        cursor.execute("""
            UPDATE major_minor_selection_window 
            SET status = 'open'
            WHERE status = 'scheduled' 
            AND start_date <= NOW()
        """)
        current_app.mysql.connection.commit()
        
        # Check for open periods that should be auto-closed
        cursor.execute("""
            UPDATE major_minor_selection_window 
            SET status = 'closed',
                closed_at = NOW(),
                closed_by_admin = NULL
            WHERE status = 'open' 
            AND end_date <= NOW()
        """)
        current_app.mysql.connection.commit()
        
        # Get current active period
        cursor.execute("""
            SELECT status, start_date, end_date 
            FROM major_minor_selection_window 
            WHERE status IN ('open', 'scheduled')
            ORDER BY end_date DESC
            LIMIT 1
        """)
        
        result = cursor.fetchone()
        
        if result:
            status, start_date, end_date = result
            return jsonify({
                'success': True,
                'is_open': status == 'open',
                'is_scheduled': status == 'scheduled',
                'start_date': start_date.strftime('%Y-%m-%d %H:%M:%S') if start_date else None,
                'end_date': end_date.strftime('%Y-%m-%d %H:%M:%S') if end_date else None
            })
        else:
            return jsonify({
                'success': True,
                'is_open': False,
                'is_scheduled': False
            })
            
    except Exception as e:
        current_app.logger.error(f"Error checking major/minor selection status: {str(e)}", exc_info=True)
        return error_response(str(e))
    finally:
        if 'cursor' in locals():
            cursor.close()


@student_bp.route('/major_minor/current')
@login_required
def get_current_choices():
    try:
        student = session.get('student')
        if not student:
            return unauthorized_response()

        cursor = current_app.mysql.connection.cursor()
        student_id = student['student_id']
        
        cursor.execute("""
            SELECT major, second_major, minor, second_minor, status, submission_date
            FROM major_minor_requests
            WHERE student_id = %s AND (status = 'pending' OR status = 'accepted' OR status = 'rejected')
            ORDER BY submission_date DESC
            LIMIT 1
        """, (student_id,))
        
        result = cursor.fetchone()
        
        if result:
            choices = {
                'major': result[0],
                'second_major': result[1],
                'minor': result[2],
                'second_minor': result[3],
                'status': result[4],
                'submission_date': result[5].strftime('%Y-%m-%d') if result[5] else None
            }
            return jsonify({
                'success': True,
                'choices': choices
            })
        else:
            return jsonify({
                'success': True,
                'choices': None
            })
            
    except Exception as e:
        current_app.logger.error(f"Error fetching current choices: {str(e)}", exc_info=True)
        return error_response(str(e))
    finally:
        if 'cursor' in locals():
            cursor.close()

@student_bp.route('/course-registration/course_info/<course_code>', methods=['GET'])
@login_required
def get_course_info(course_code):
    """Get course information including prerequisites and courses that have this course as prerequisite"""
    cursor = current_app.mysql.connection.cursor()
    try:
        # Get student ID for logging
        student_id = session['student']['student_id']
        current_app.logger.info(f"Course info request for {course_code} by student {student_id}")
        
        # Get course details
        cursor.execute("""
            SELECT c.course_code, c.course_name, c.description, c.has_tutorial, c.has_lecture, c.coefficient
            FROM courses c
            WHERE c.course_code = %s
        """, (course_code,))
        course = cursor.fetchone()
        
        if not course:
            return jsonify({
                'success': False,
                'message': 'Course not found'
            }), 404
        
        # Get prerequisites for this course
        cursor.execute("""
            SELECT c.course_code, c.course_name
            FROM courses c
            JOIN course_prerequisites cp ON c.id = cp.prerequisite_id
            JOIN courses c2 ON cp.course_id = c2.id
            WHERE c2.course_code = %s
        """, (course_code,))
        prerequisites = [{'code': row[0], 'name': row[1]} for row in cursor.fetchall()]
        
        # Get courses that have this course as a prerequisite
        cursor.execute("""
            SELECT c.course_code, c.course_name
            FROM courses c
            JOIN course_prerequisites cp ON c.id = cp.course_id
            JOIN courses c2 ON cp.prerequisite_id = c2.id
            WHERE c2.course_code = %s
        """, (course_code,))
        is_prerequisite_for = [{'code': row[0], 'name': row[1]} for row in cursor.fetchall()]
        
        return jsonify({
            'success': True,
            'course_code': course[0],
            'course_name': course[1],
            'description': course[2],
            'has_tutorial': bool(course[3]),
            'has_lecture': bool(course[4]),
            'coefficient': course[5],
            'prerequisites': prerequisites,
            'is_prerequisite_for': is_prerequisite_for
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in get_course_info: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error fetching course information: {str(e)}'
        }), 500
    finally:
        cursor.close()

@student_bp.route('/course-registration/courses_info', methods=['POST'])
@login_required
def get_multiple_courses_info():
    """Get information for multiple courses in a single request"""
    cursor = current_app.mysql.connection.cursor()
    try:
        # Get student ID for logging
        student_id = session['student']['student_id']
        
        # Get course codes from request
        data = request.get_json()
        if not data or 'course_codes' not in data:
            return jsonify({
                'success': False,
                'message': 'No course codes provided'
            }), 400
            
        course_codes = data['course_codes']
        if not course_codes:
            return jsonify({
                'success': False,
                'message': 'Empty course codes list'
            }), 400
            
        current_app.logger.info(f"Bulk course info request for {len(course_codes)} courses by student {student_id}")
        
        # Create result dictionary
        courses_info = {}
        
        # Use a parameterized query with IN clause
        if course_codes:
            # Create placeholders for SQL query
            placeholders = ', '.join(['%s'] * len(course_codes))
            
            # Get basic course info for all requested courses
            cursor.execute(f"""
                SELECT c.course_code, c.course_name, c.description, c.has_tutorial, c.has_lecture, c.coefficient
                FROM courses c
                WHERE c.course_code IN ({placeholders})
            """, course_codes)
            
            # Store basic course info
            for row in cursor.fetchall():
                course_code = row[0]
                courses_info[course_code] = {
                    'course_code': course_code,
                    'course_name': row[1],
                    'description': row[2],
                    'has_tutorial': bool(row[3]),
                    'has_lecture': bool(row[4]),
                    'coefficient': row[5],
                    'prerequisites': [],
                    'is_prerequisite_for': []
                }
            
            # Get prerequisites for all courses
            cursor.execute(f"""
                SELECT c2.course_code, c.course_code as prereq_code, c.course_name as prereq_name
                FROM courses c2
                JOIN course_prerequisites cp ON cp.course_id = c2.id
                JOIN courses c ON c.id = cp.prerequisite_id
                WHERE c2.course_code IN ({placeholders})
            """, course_codes)
            
            # Add prerequisites to the corresponding courses
            for row in cursor.fetchall():
                course_code = row[0]
                prereq_code = row[1]
                prereq_name = row[2]
                
                if course_code in courses_info:
                    courses_info[course_code]['prerequisites'].append({
                        'code': prereq_code,
                        'name': prereq_name
                    })
            
            # Get "is prerequisite for" info
            cursor.execute(f"""
                SELECT c2.course_code, c.course_code as required_code, c.course_name as required_name
                FROM courses c2
                JOIN course_prerequisites cp ON cp.prerequisite_id = c2.id
                JOIN courses c ON c.id = cp.course_id
                WHERE c2.course_code IN ({placeholders})
            """, course_codes)
            
            # Add "is prerequisite for" to the corresponding courses
            for row in cursor.fetchall():
                course_code = row[0]
                required_code = row[1]
                required_name = row[2]
                
                if course_code in courses_info:
                    courses_info[course_code]['is_prerequisite_for'].append({
                        'code': required_code,
                        'name': required_name
                    })
        
        return jsonify({
            'success': True,
            'courses_info': courses_info
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in get_multiple_courses_info: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error fetching course information: {str(e)}'
        }), 500
    finally:
        cursor.close()

@student_bp.route('/schedule', methods=['GET'])
@login_required
def get_student_schedule():
    """Get the student's enrolled courses for the current semester"""
    try:
        student = session.get('student')
        if not student:
            return jsonify({
                'success': False,
                'message': 'User not logged in',
                'code': 'UNAUTHORIZED'
            }), 401

        student_id = student['student_id']
        cursor = current_app.mysql.connection.cursor()
        
        try:
            # Get current semester info from academic_calendar where is_current=1
            cursor.execute("""
                SELECT semester, academic_year
                FROM academic_calendar
                WHERE is_current = 1
                LIMIT 1
            """)
            
            calendar_info = cursor.fetchone()
            if not calendar_info:
                return jsonify({
                    'success': False,
                    'message': 'No active semester found',
                    'code': 'NO_SEMESTER'
                }), 404
            
            current_semester = calendar_info[0]
            academic_year = calendar_info[1]
            
            # Get student's year of study from student table
            cursor.execute("""
                SELECT year_of_study
                FROM student
                WHERE student_id = %s
            """, (student_id,))
            
            student_info = cursor.fetchone()
            if not student_info:
                return jsonify({
                    'success': False,
                    'message': 'Student information not found',
                    'code': 'NO_STUDENT_INFO'
                }), 404
            
            student_year = student_info[0]
            
            # Check for saved schedule in student_schedules table
            cursor.execute("""
                SELECT schedule_data, created_at
                FROM student_schedules
                WHERE student_id = %s AND semester = %s AND year = %s
                LIMIT 1
            """, (student_id, current_semester, academic_year))
            
            saved_schedule = cursor.fetchone()
            
            # Log what we're about to query
            current_app.logger.info(f"Fetching enrolled courses for student_id={student_id}, year={academic_year}, semester={current_semester}")
            
            # Get enrolled courses for current semester - use status='enrolled' only
            cursor.execute("""
                SELECT ac.course_code, c.course_name, c.coefficient as credits, 
                       ac.lecture_study_group, ac.tutorial_study_group
                FROM add_course ac
                JOIN courses c ON ac.course_code = c.course_code
                WHERE ac.student_id = %s 
                AND ac.status = 'enrolled'
                AND ac.semester = %s
            """, (student_id, current_semester))
            
            enrolled_courses = []
            for row in cursor.fetchall():
                course_code, course_name, credits, lecture_group, tutorial_group = row
                enrolled_courses.append({
                    "course_code": course_code,
                    "course_name": course_name,
                    "credits": credits,
                    "lecture_study_group": lecture_group,
                    "tutorial_study_group": tutorial_group
                })
            
            # Log what we found
            current_app.logger.info(f"Found {len(enrolled_courses)} enrolled courses for student {student_id} in semester {current_semester}")
            
            response_data = {
                'success': True,
                'semester': current_semester,
                'year': academic_year,
                'student_year': student_year,
                'enrolled_courses': enrolled_courses
            }
            
            # Add saved schedule to response if it exists
            if saved_schedule:
                import json
                schedule_data = json.loads(saved_schedule[0])
                created_at = saved_schedule[1].strftime('%Y-%m-%d %H:%M:%S') if saved_schedule[1] else None
                
                response_data['saved_schedule'] = {
                    'schedule': schedule_data,
                    'created_at': created_at
                }
                current_app.logger.info(f"Found saved schedule for student {student_id}, created at {created_at}")
            
            # Always return success, even if no courses found
            return jsonify(response_data)
            
        finally:
            cursor.close()
        
    except Exception as e:
        current_app.logger.error(f"Error getting student schedule: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Error retrieving schedule: {str(e)}',
            'code': 'SCHEDULE_ERROR'
        }), 500

@student_bp.route('/schedule/regenerate', methods=['POST'])
@login_required
def regenerate_schedule():
    """Force regeneration of the student's schedule"""
    try:
        student = session.get('student')
        if not student:
            return jsonify({
                'success': False,
                'message': 'User not logged in',
                'code': 'UNAUTHORIZED'
            }), 401

        student_id = student['student_id']
        cursor = current_app.mysql.connection.cursor()
        
        # Get preferences from request body
        preferences = None
        clear_preferences = False
        try:
            data = request.get_json()
            if data:
                if 'preferences' in data:
                    preferences = data['preferences']
                    current_app.logger.info(f"Received preferences: {preferences}")
                if 'clear_preferences' in data and data['clear_preferences']:
                    clear_preferences = True
                    current_app.logger.info("Clearing preferences")
        except Exception as e:
            current_app.logger.error(f"Error parsing preferences: {str(e)}")
            # Continue without preferences
        
        try:
            # First ensure the student_schedules table exists
            try:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS student_schedules (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        student_id INT NOT NULL,
                        enrolled_courses_key VARCHAR(500) NOT NULL,
                        schedule_data MEDIUMTEXT NOT NULL,
                        semester INT,
                        year INT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        INDEX (student_id, enrolled_courses_key)
                    )
                """)
                current_app.mysql.connection.commit()
            except Exception as e:
                current_app.logger.error(f"Error creating student_schedules table: {str(e)}")
                # Continue execution - we'll handle missing table errors below
            
            # Get the enrolled course codes
            cursor.execute("""
                SELECT course_code FROM add_course 
                WHERE student_id = %s AND status = 'enrolled'
                ORDER BY course_code
            """, (student_id,))
            
            enrolled_courses = [row[0] for row in cursor.fetchall()]
            
            if not enrolled_courses:
                return jsonify({
                    'success': False,
                    'message': 'You have no enrolled courses. Please enroll in courses before generating a schedule.',
                    'code': 'NO_COURSES'
                }), 404
            
            enrolled_courses_key = ','.join(sorted(enrolled_courses))
            
            # Delete any existing saved schedules for these courses
            try:
                cursor.execute("""
                    DELETE FROM student_schedules
                    WHERE student_id = %s AND enrolled_courses_key = %s
                """, (student_id, enrolled_courses_key))
                current_app.mysql.connection.commit()
                current_app.logger.info(f"Deleted existing schedules for student {student_id}")
            except Exception as e:
                current_app.logger.error(f"Error deleting existing schedules: {str(e)}")
                # Continue execution - we'll generate a new schedule anyway
            
            # Generate a new schedule with a random seed to ensure different results
            import random
            seed = random.randint(1, 10000)
            current_app.logger.info(f"Generating new schedule with seed {seed}")
            
            result = optimize_student_schedule(
                student_id=student_id,
                db_connection=current_app.mysql.connection,
                random_seed=seed,
                preferences=None if clear_preferences else preferences
            )
            
            # Check if optimization was successful
            if not result['success']:
                # If preferences were specified and optimization failed, try again without preferences
                if preferences and not clear_preferences:
                    current_app.logger.warning("Optimization with preferences failed, trying without preferences")
                    
                    # Store the error message
                    error_message = result.get('message', 'Could not find a valid schedule with your preferences')
                    
                    # Try again without preferences
                    result = optimize_student_schedule(
                        student_id=student_id,
                        db_connection=current_app.mysql.connection,
                        random_seed=seed
                    )
                    
                    if result['success']:
                        # Add detailed error message about which preferences couldn't be satisfied
                        preference_details = []
                        if preferences.get('max_days'):
                            preference_details.append(f"maximum of {preferences['max_days']} days")
                        
                        if preferences.get('preferred_days') and len(preferences['preferred_days']) > 0:
                            preference_details.append(f"preferred days ({', '.join(preferences['preferred_days'])})")
                        
                        if preferences.get('course_preferences'):
                            prof_prefs = []
                            for course, prefs in preferences['course_preferences'].items():
                                if prefs.get('preferred_professor'):
                                    prof_prefs.append(f"{course}: {prefs['preferred_professor']}")
                            
                            if prof_prefs:
                                preference_details.append(f"professor preferences ({', '.join(prof_prefs)})")
                        
                        result['preferences_error'] = "Could not find a valid schedule with your preferences, generated a default schedule"
                    else:
                        return jsonify({
                            'success': False,
                            'message': 'Could not generate a valid schedule with or without preferences.',
                            'code': 'OPTIMIZATION_FAILED',
                            'details': error_message
                        }), 500
            
            # If optimization was successful, save the schedule
            if result['success'] and 'schedule' in result and result['schedule']:
                # Get semester and year
                semester = result.get('semester')
                year = result.get('year')
                
                # Add course details
                course_details = {}
                for item in result['schedule']:
                    course_code = item['course_code']
                    if course_code not in course_details:
                        cursor.execute("""
                            SELECT course_name, coefficient
                            FROM courses
                            WHERE course_code = %s
                        """, (course_code,))
                        course_info = cursor.fetchone()
                        if course_info:
                            course_details[course_code] = {
                                'course_name': course_info[0],
                                'coefficient': course_info[1]
                            }
                
                result['course_details'] = course_details
                
                # Save the schedule to the database
                try:
                    # Prepare data to save
                    import json
                    # Remove course_details before saving (we'll add them back when retrieving)
                    save_result = {k: v for k, v in result.items() if k != 'course_details'}
                    schedule_data = json.dumps(save_result)
                    
                    # Save to database
                    cursor.execute("""
                        INSERT INTO student_schedules 
                        (student_id, enrolled_courses_key, schedule_data, semester, year)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (student_id, enrolled_courses_key, schedule_data, semester, year))
                    current_app.mysql.connection.commit()
                    
                    current_app.logger.info(f"Saved regenerated schedule for student {student_id}")
                except Exception as e:
                    current_app.logger.error(f"Error saving regenerated schedule: {str(e)}")
                    # Continue anyway, just don't save the schedule
            
            return jsonify(result)
        
        finally:
            cursor.close()
        
    except Exception as e:
        current_app.logger.error(f"Error regenerating schedule: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Error regenerating schedule: {str(e)}',
            'code': 'SCHEDULE_ERROR'
        }), 500

@student_bp.route('/schedule/professors', methods=['POST'])
@login_required
def get_course_professors():
    """Get professors teaching specific courses"""
    try:
        student = session.get('student')
        if not student:
            return jsonify({
                'success': False,
                'message': 'User not logged in',
                'code': 'UNAUTHORIZED'
            }), 401

        # Get course codes from request
        data = request.get_json()
        if not data or 'course_codes' not in data or not data['course_codes']:
            return jsonify({
                'success': False,
                'message': 'No course codes provided',
                'code': 'INVALID_REQUEST'
            }), 400

        course_codes = data['course_codes']
        
        # Get professors for these courses
        cursor = current_app.mysql.connection.cursor()
        
        try:
            professors_data = {}
            
            for course_code in course_codes:
                # Get course name
                cursor.execute("""
                    SELECT course_name FROM courses
                    WHERE course_code = %s
                """, (course_code,))
                
                course_result = cursor.fetchone()
                if not course_result:
                    continue
                
                course_name = course_result[0]
                professors_data[course_code] = {
                    'course_name': course_name,
                    'lecture_professors': [],
                    'tutorial_professors': []
                }
                
                # Get lecture professors
                cursor.execute("""
                    SELECT DISTINCT professor
                    FROM schedule
                    WHERE course_code = %s AND session_type = 'lecture'
                    ORDER BY professor
                """, (course_code,))
                
                lecture_professors = [row[0] for row in cursor.fetchall()]
                professors_data[course_code]['lecture_professors'] = lecture_professors
                
                # Get tutorial professors
                cursor.execute("""
                    SELECT DISTINCT professor
                    FROM schedule
                    WHERE course_code = %s AND session_type = 'tutorial'
                    ORDER BY professor
                """, (course_code,))
                
                tutorial_professors = [row[0] for row in cursor.fetchall()]
                professors_data[course_code]['tutorial_professors'] = tutorial_professors
            
            return jsonify({
                'success': True,
                'professors_data': professors_data
            })
            
        finally:
            cursor.close()
            
    except Exception as e:
        current_app.logger.error(f"Error getting course professors: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Error retrieving professors data: {str(e)}',
            'code': 'PROFESSORS_ERROR'
        }), 500

@student_bp.route('/schedule/tutorial_professors', methods=['POST'])
@login_required
def get_tutorial_professors():
    """Get tutorial professors and valid lecture-tutorial combinations for courses"""
    try:
        data = request.get_json()
        if not data or 'courses' not in data:
            return jsonify({
                'success': False,
                'message': 'No courses provided'
            }), 400
        
        courses = data['courses']
        if not courses:
            return jsonify({
                'success': False,
                'message': 'Empty course list'
            }), 400
            
        # Get tutorial professors for each course
        cursor = current_app.mysql.connection.cursor()
        tutorial_professors = {}
        lecture_tutorial_combinations = {}
        
        # Create placeholders for SQL query
        placeholders = ', '.join(['%s'] * len(courses))
        
        # First, get all tutorial professors for these courses
        query = f"""
            SELECT DISTINCT course_code, professor
            FROM schedule 
            WHERE course_code IN ({placeholders}) 
            AND session_type = 'tutorial'
            ORDER BY course_code, professor
        """
        
        cursor.execute(query, courses)
        
        # Group tutorial professors by course
        for row in cursor.fetchall():
            course_code, professor = row
            if course_code not in tutorial_professors:
                tutorial_professors[course_code] = []
            if professor not in tutorial_professors[course_code]:
                tutorial_professors[course_code].append(professor)
        
        # Now get valid lecture-tutorial professor combinations by group
        query = f"""
            SELECT s1.course_code, s1.`group`, s1.professor AS lecture_professor, s2.professor AS tutorial_professor 
            FROM schedule s1
            JOIN schedule s2 ON s1.course_code = s2.course_code AND s1.`group` = s2.`group`
            WHERE s1.course_code IN ({placeholders})
            AND s1.session_type = 'lecture'
            AND s2.session_type = 'tutorial'
            ORDER BY s1.course_code, s1.professor, s2.professor
        """
        
        cursor.execute(query, courses)
        
        # Group combinations by course and lecture professor
        for row in cursor.fetchall():
            course_code, group, lecture_professor, tutorial_professor = row
            
            if course_code not in lecture_tutorial_combinations:
                lecture_tutorial_combinations[course_code] = {}
            
            if lecture_professor not in lecture_tutorial_combinations[course_code]:
                lecture_tutorial_combinations[course_code][lecture_professor] = []
            
            if tutorial_professor not in lecture_tutorial_combinations[course_code][lecture_professor]:
                lecture_tutorial_combinations[course_code][lecture_professor].append(tutorial_professor)
        
        # Make sure all requested courses are in the result, even if they have no tutorials
        for course in courses:
            if course not in tutorial_professors:
                tutorial_professors[course] = []
            if course not in lecture_tutorial_combinations:
                lecture_tutorial_combinations[course] = {}
        
        cursor.close()
        
        current_app.logger.info(f"Fetched tutorial professors for {len(courses)} courses")
        
        return jsonify({
            'success': True,
            'tutorial_professors': tutorial_professors,
            'lecture_tutorial_combinations': lecture_tutorial_combinations
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in get_tutorial_professors: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Error fetching tutorial professors: {str(e)}'
        }), 500

@student_bp.route('/save-study-groups', methods=['POST'])
@login_required
def save_study_groups():
    """Save study groups for enrolled courses"""
    try:
        student = session.get('student')
        if not student:
            return jsonify({
                'success': False,
                'message': 'User not logged in',
                'code': 'UNAUTHORIZED'
            }), 401

        data = request.get_json()
        if not data or 'course_groups' not in data:
            return jsonify({
                'success': False,
                'message': 'No course groups provided',
                'code': 'MISSING_DATA'
            }), 400
            
        course_groups = data.get('course_groups', {})
        semester = data.get('semester')
        year = data.get('year')
        
        if not course_groups:
            return jsonify({
                'success': False,
                'message': 'Empty course groups',
                'code': 'EMPTY_DATA'
            }), 400
            
        if not semester or not year:
            # Get current semester and year from the database
            cursor = current_app.mysql.connection.cursor()
            cursor.execute("""
                SELECT semester, year FROM current_semester
                ORDER BY id DESC LIMIT 1
            """)
            result = cursor.fetchone()
            if result:
                semester, year = result
                
        # Update add_course table with study groups
        cursor = current_app.mysql.connection.cursor()
        
        # Start a transaction
        try:
            student_id = student['student_id']
            updates = []
            
            for course_code, group in course_groups.items():
                # Check if the group is for lecture or tutorial or both
                lecture_group = None
                tutorial_group = None
                
                if isinstance(group, dict):
                    lecture_group = group.get('lecture')
                    tutorial_group = group.get('tutorial')
                else:
                    # For backward compatibility, assume it's a lecture group
                    lecture_group = group
                
                cursor.execute("""
                    UPDATE add_course
                    SET lecture_study_group = %s,
                        tutorial_study_group = %s
                    WHERE student_id = %s
                    AND course_code = %s
                    AND year = %s
                    AND semester = %s
                    AND status = 'enrolled'
                """, (lecture_group, tutorial_group, student_id, course_code, year, semester))
                
                if cursor.rowcount > 0:
                    updates.append(course_code)
            
            # Even if no courses were updated, we'll consider it a success
            # to avoid confusing the user
            
            # Commit the transaction
            current_app.mysql.connection.commit()
            
            current_app.logger.info(f"Updated study groups for student {student_id}, courses: {', '.join(updates) if updates else 'none'}")
            
            return jsonify({
                'success': True,
                'message': 'Study groups saved successfully',
                'updated_courses': updates
            })
            
        except Exception as e:
            current_app.logger.error(f"Error saving study groups: {str(e)}", exc_info=True)
            return jsonify({
                'success': False,
                'message': f'Error saving study groups: {str(e)}',
                'code': 'DB_ERROR'
            }), 500
            
    except Exception as e:
        current_app.logger.error(f"Error in save_study_groups: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Unexpected error: {str(e)}',
            'code': 'INTERNAL_ERROR'
        }), 500

def ensure_semester_summary_exists(cursor, student_id, year, semester):
    """Ensure a semester summary record exists, creating it if necessary"""
    # First check if the student is dismissed - if so, don't create a semester summary
    cursor.execute("""
        SELECT enrollment_status FROM student
        WHERE student_id = %s
    """, (student_id,))
    
    student_status = cursor.fetchone()
    if student_status and student_status[0] == 'dismissed':
        current_app.logger.info(f"Not creating semester summary for dismissed student {student_id}")
        return False
    
    cursor.execute("""
        SELECT record_id, acct_gpa, ba_gpa, fin_gpa, it_gpa, mrk_gpa 
        FROM student_semester_summary
        WHERE student_id = %s AND year = %s AND semester = %s
    """, (student_id, year, semester))
    
    result = cursor.fetchone()
    
    if not result:
        # No record exists, create a new one
        # Get previous semester's cumulative data
        cursor.execute("""
            SELECT 
                cumulative_registered_credits,
                cumulative_earned_credits,
                cumulative_gpa,
                probation_counter
            FROM student_semester_summary
            WHERE student_id = %s
            ORDER BY year DESC, semester DESC
            LIMIT 1
        """, (student_id,))
        
        prev = cursor.fetchone()
        
        if prev:
            cumulative_registered = prev[0] or 0
            cumulative_earned = prev[1] or 0
            cumulative_gpa = prev[2]
            probation_counter = prev[3] or 0
        else:
            cumulative_registered = 0
            cumulative_earned = 0
            cumulative_gpa = None
            probation_counter = 0
        
        # Create a new record with NULL specialized GPAs
        cursor.execute("""
            INSERT INTO student_semester_summary
            (student_id, year, semester, 
             cumulative_registered_credits, cumulative_earned_credits, cumulative_gpa,
             probation_counter, forgiveness_counter,
             acct_gpa, ba_gpa, fin_gpa, it_gpa, mrk_gpa)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 0, NULL, NULL, NULL, NULL, NULL)
        """, (
            student_id, year, semester,
            cumulative_registered, cumulative_earned, cumulative_gpa,
            probation_counter
        ))
        
        current_app.logger.info(f"Created new semester summary for student {student_id}, year {year}, semester {semester}")
        return True
    else:
        # Record exists, check if specialized GPAs are all NULL
        all_gpas_null = True
        for i in range(1, 6):  # Check all 5 specialized GPAs (indexes 1-5 in the result)
            if result[i] is not None:
                all_gpas_null = False
                break
                
        if all_gpas_null:
            current_app.logger.info(f"Found semester summary with NULL GPAs for student {student_id}, year {year}, semester {semester}")
            
        return False

# Helper function to get drop course requests for a student
def get_drop_course_requests(student_id):
    try:
        cursor = current_app.mysql.connection.cursor()
        
        # Fetch drop requests with more detail
        current_app.logger.info(f"Fetching drop course requests for student_id={student_id}")
        
        cursor.execute("""
            SELECT id, course_code, status, request_date, type
            FROM drop_course_requests
            WHERE student_id = %s AND status = 'pending'
        """, (student_id,))
        
        results = cursor.fetchall()
        current_app.logger.info(f"Found {len(results)} drop course requests for student_id={student_id}")
        
        requests = {}
        for row in results:
            request_id, course_code, status, request_date, request_type = row
            current_app.logger.info(f"Processing drop request: id={request_id}, course_code={course_code}, status={status}, type={request_type}")
            
            # Format the date to ISO format for JSON serialization
            formatted_date = request_date.isoformat() if request_date else None
            
            requests[course_code] = {
                'id': request_id,
                'status': status,
                'date': formatted_date,
                'type': request_type
            }
        
        cursor.close()
        current_app.logger.info(f"Returning drop requests dictionary with keys: {list(requests.keys())}")
        return requests
    except Exception as e:
        current_app.logger.error(f"Error getting drop course requests: {str(e)}")
        return {}

@student_bp.route('/drop-course-request', methods=['POST'])
@login_required
def create_drop_course_request():
    try:
        student = session.get('student')
        if not student:
            return jsonify({
                'success': False,
                'message': 'User not logged in',
                'code': 'UNAUTHORIZED'
            }), 401
        
        student_id = student['student_id']
        data = request.json
        
        if not data or 'course_code' not in data or 'confirmation' not in data:
            return jsonify({
                'success': False,
                'message': 'Missing required data',
                'code': 'INVALID_REQUEST'
            }), 400
        
        course_code = data['course_code']
        confirmation = data['confirmation']
        
        # Verify confirmation is "YES"
        if confirmation != "YES":
            return jsonify({
                'success': False,
                'message': 'Confirmation text must be "YES"',
                'code': 'INVALID_CONFIRMATION'
            }), 400
        
        # Check if a pending drop request already exists
        cursor = current_app.mysql.connection.cursor()
        cursor.execute("""
            SELECT id FROM drop_course_requests
            WHERE student_id = %s
            AND course_code = %s
            AND status = 'pending'
        """, (student_id, course_code))
        
        existing_request = cursor.fetchone()
        if existing_request:
            return jsonify({
                'success': False,
                'message': 'You already have a pending drop request for this course',
                'code': 'REQUEST_EXISTS'
            }), 400
        
        # Get current semester info
        current_year, current_semester = get_current_semester()
        
        # NEW CHECK 1: Check if the course is a failed course that the student is retaking
        cursor.execute("""
            SELECT ac1.status
            FROM add_course ac1
            WHERE ac1.student_id = %s 
            AND ac1.course_code = %s
            AND ac1.year < %s
            AND ac1.status = 'failed'
            ORDER BY ac1.id DESC
            LIMIT 1
        """, (student_id, course_code, current_year))
        
        failed_course = cursor.fetchone()
        if failed_course:
            return jsonify({
                'success': False,
                'message': 'You cannot drop a failed course that you are retaking.',
                'code': 'FAILED_COURSE_RETAKE'
            }), 400
            
        # NEW CHECK 2: Check if student has ANY courses with 'notenrolled' or 'failed' status
        # If they don't, then all courses are autochecked
        cursor.execute("""
            SELECT COUNT(*)
            FROM (
                SELECT ac.course_code, ac.status
                FROM add_course ac
                WHERE ac.student_id = %s
                AND NOT (ac.year = %s AND ac.semester = %s AND ac.status = 'enrolled')
                AND ac.status IN ('notenrolled', 'failed')
                ORDER BY ac.id DESC
                LIMIT 1
            ) AS subquery
        """, (student_id, current_year, current_semester))
        
        has_notenrolled_or_failed = cursor.fetchone()[0] > 0
        
        # If student has no 'notenrolled' or 'failed' courses, all current courses are autochecked
        if not has_notenrolled_or_failed:
            current_app.logger.info(f"Student {student_id} has no 'notenrolled' or 'failed' courses, all courses are autochecked")
            return jsonify({
                'success': False,
                'message': 'This is a required course for your program and cannot be dropped.',
                'code': 'REQUIRED_COURSE'
            }), 400
        
        # Determine the course type
        course_type = 'Current'  # Default type
        
        # Check if it's a retake under forgiveness policy
        cursor.execute("""
            SELECT COUNT(*) 
            FROM add_course 
            WHERE student_id = %s 
            AND course_code = %s 
            AND forgiveness = 1
        """, (student_id, course_code))
        
        is_forgiveness_retake = cursor.fetchone()[0] > 0
        if is_forgiveness_retake:
            course_type = 'Retake'
        else:
            # Check if it's an extra course
            cursor.execute("""
                SELECT COUNT(*) 
                FROM add_course 
                WHERE student_id = %s 
                AND course_code = %s 
                AND year = %s 
                AND semester = %s 
                AND status = 'enrolled'
            """, (student_id, course_code, current_year, current_semester))
            
            is_current_semester = cursor.fetchone()[0] > 0
            
            if is_current_semester:
                # Check if this course is from the "extra courses" section
                # This would require checking if the course is not part of the student's required curriculum
                # For simplicity, we'll check if it's not a core course for their major
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM major_courses mc
                    JOIN student_majors sm ON mc.major_id = sm.major_id
                    WHERE sm.student_id = %s 
                    AND mc.course_code = %s 
                    AND mc.is_core = 1
                """, (student_id, course_code))
                
                is_core_course = cursor.fetchone()[0] > 0
                
                if not is_core_course:
                    course_type = 'Extra'
                else:
                    course_type = 'Current'
            else:
                # Check if it's a previously dropped course
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM add_course 
                    WHERE student_id = %s 
                    AND course_code = %s 
                    AND status = 'notenrolled'
                """, (student_id, course_code))
                
                is_previously_dropped = cursor.fetchone()[0] > 0
                
                if is_previously_dropped:
                    course_type = 'Skipped'
        
        current_app.logger.info(f"Determined course type for {course_code}: {course_type}")
        
        # Create the drop request with the determined type
        cursor.execute("""
            INSERT INTO drop_course_requests 
            (student_id, course_code, status, request_date, type)
            VALUES (%s, %s, 'pending', NOW(), %s)
        """, (student_id, course_code, course_type))
        
        current_app.mysql.connection.commit()
        
        request_id = cursor.lastrowid
        cursor.close()
        
        return jsonify({
            'success': True,
            'message': 'Drop course request submitted successfully',
            'data': {
                'request_id': request_id,
                'type': course_type
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error creating drop course request: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred while processing your request',
            'error': str(e),
            'code': 'SERVER_ERROR'
        }), 500

@student_bp.route('/drop-course-request/<int:request_id>', methods=['DELETE'])
@login_required
def cancel_drop_course_request(request_id):
    try:
        student = session.get('student')
        if not student:
            return jsonify({
                'success': False,
                'message': 'User not logged in',
                'code': 'UNAUTHORIZED'
            }), 401
        
        student_id = student['student_id']
        
        # Verify the request exists and belongs to this student
        cursor = current_app.mysql.connection.cursor()
        cursor.execute("""
            SELECT id FROM drop_course_requests
            WHERE id = %s
            AND student_id = %s
            AND status = 'pending'
        """, (request_id, student_id))
        
        request_record = cursor.fetchone()
        if not request_record:
            return jsonify({
                'success': False,
                'message': 'Drop request not found or cannot be canceled',
                'code': 'REQUEST_NOT_FOUND'
            }), 404
        
        # Delete the request
        cursor.execute("""
            DELETE FROM drop_course_requests
            WHERE id = %s
        """, (request_id,))
        
        current_app.mysql.connection.commit()
        cursor.close()
        
        return jsonify({
            'success': True,
            'message': 'Drop course request canceled successfully'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error canceling drop course request: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred while processing your request',
            'error': str(e),
            'code': 'SERVER_ERROR'
        }), 500

@student_bp.route('/get-drop-requests', methods=['GET'])
@login_required
def get_drop_course_requests_endpoint():
    """API endpoint to get all pending drop course requests for the student"""
    try:
        student = session.get('student')
        if not student:
            return jsonify({
                'success': False,
                'message': 'User not logged in',
                'code': 'UNAUTHORIZED'
            }), 401
        
        student_id = student['student_id']
        
        # Get drop course requests
        requests = get_drop_course_requests(student_id)
        current_app.logger.info(f"Fetched {len(requests)} drop requests for student {student_id}")
        
        return jsonify({
            'success': True,
            'requests': requests
        })
        
    except Exception as e:
        current_app.logger.error(f"Error fetching drop requests: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred while fetching drop requests',
            'error': str(e)
        }), 500

@student_bp.route('/makeup-session', methods=['GET'])
@login_required
def makeup_session():
    """Get information about makeup session and check eligibility for the student"""
    try:
        student = session.get('student')
        if not student:
            return jsonify({
                'success': False,
                'message': 'User not logged in',
                'code': 'UNAUTHORIZED'
            }), 401

        student_id = student['student_id']
        cursor = current_app.mysql.connection.cursor()
        
        try:
            # Check condition 1: Makeup session is open or scheduled
            cursor.execute("""
                SELECT id, status, open_date, close_date
                FROM makeup_session 
                ORDER BY id DESC LIMIT 1
            """)
            
            makeup_session_result = cursor.fetchone()
            
            if not makeup_session_result or makeup_session_result[1] not in ['open', 'scheduled']:
                return jsonify({
                    "success": False,
                    "message": "No active makeup session is available at this time",
                    "eligible": False
                })
            
            # Get session details for the response
            session_details = {
                "id": makeup_session_result[0],
                "status": makeup_session_result[1],
                "open_date": makeup_session_result[2],
                "close_date": makeup_session_result[3]
            }
            
            # Check condition 2: Student has 115+ cumulative earned credits
            cursor.execute("""
                SELECT cumulative_earned_credits 
                FROM student_semester_summary 
                WHERE student_id = %s 
                ORDER BY year DESC, semester DESC 
                LIMIT 1
            """, (student_id,))
            
            credit_result = cursor.fetchone()
            if not credit_result or credit_result[0] < 115:
                return jsonify({
                    "success": False,
                    "message": "You need at least 115 earned credits to be eligible for makeup sessions",
                    "eligible": False,
                    "sessionDetails": session_details,
                    "credits": credit_result[0] if credit_result else 0
                })
            
            # Check condition 3: Student has at most 2 eligible failed/notenrolled courses
            # First get failed/notenrolled courses eligible for makeup that are NOT already registered
            cursor.execute("""
                SELECT c.course_code, c.course_name, c.coefficient, a.status, a.forgiveness, c.eligible_for_makeup
                FROM add_course a 
                JOIN courses c ON a.course_code = c.course_code
                WHERE a.student_id = %s 
                AND a.id IN (
                    SELECT MAX(id) 
                    FROM add_course 
                    WHERE student_id = %s 
                    GROUP BY course_code
                )
                AND a.status IN ('failed', 'notenrolled')
                AND c.eligible_for_makeup = 1
                AND (a.forgiveness IS NULL OR a.forgiveness = 0)
                AND NOT EXISTS (
                    SELECT 1 FROM add_course ac
                    WHERE ac.student_id = %s
                    AND ac.course_code = a.course_code
                    AND ac.semester = 3  -- Check if already registered for makeup
                )
            """, (student_id, student_id, student_id))
            
            failed_courses = cursor.fetchall()
            
            if len(failed_courses) > 2:
                return jsonify({
                    "success": False,
                    "message": "You have more than 2 courses eligible for makeup",
                    "eligible": False,
                    "sessionDetails": session_details,
                    "credits": credit_result[0] if credit_result else 0
                })
            
            # Check condition 4: Check for eligible_for_makeup=0 courses based on major count
            # First, get the major count from student table
            cursor.execute("""
                SELECT major, second_major
                FROM student
                WHERE student_id = %s
            """, (student_id,))
            
            major_result = cursor.fetchone()
            major_count = 0
            if major_result:
                # Count non-null major values
                if major_result[0] is not None and major_result[0] != '':
                    major_count += 1
                if major_result[1] is not None and major_result[1] != '':
                    major_count += 1
            
            # Check courses with eligible_for_makeup=0
            cursor.execute("""
                SELECT a.course_code, c.course_name, a.status
                FROM add_course a
                JOIN courses c ON a.course_code = c.course_code
                WHERE a.student_id = %s 
                AND a.status IN ('enrolled', 'passed')
                AND c.eligible_for_makeup = 0
                AND a.id IN (
                    SELECT MAX(id) 
                    FROM add_course 
                    WHERE student_id = %s 
                    GROUP BY course_code
                )
            """, (student_id, student_id))
            
            eligible_courses = cursor.fetchall()
            
            # If 0-1 majors, need at least 1 eligible course
            # If 2 majors, need at least 2 different eligible courses
            if (major_count < 2 and len(eligible_courses) < 1) or \
               (major_count >= 2 and len(eligible_courses) < 2):
                return jsonify({
                    "success": False,
                    "message": f"You need {'at least 2 qualifying courses for your dual major' if major_count >= 2 else 'at least 1 qualifying course'}",
                    "eligible": False,
                    "sessionDetails": session_details,
                    "credits": credit_result[0] if credit_result else 0
                })
            
            # If all conditions are met, gather the relevant data
            # Get failed and notenrolled courses eligible for makeup
            cursor.execute("""
                SELECT c.course_code, c.course_name, c.coefficient, a.status
                FROM add_course a 
                JOIN courses c ON a.course_code = c.course_code
                WHERE a.student_id = %s 
                AND a.id IN (
                    SELECT MAX(id) 
                    FROM add_course 
                    WHERE student_id = %s 
                    GROUP BY course_code
                )
                AND a.status IN ('failed', 'notenrolled')
                AND c.eligible_for_makeup = 1
                AND (a.forgiveness IS NULL OR a.forgiveness = 0)
                AND NOT EXISTS (
                    SELECT 1 FROM add_course ac
                    WHERE ac.student_id = %s
                    AND ac.course_code = a.course_code
                    AND ac.semester = 3  -- Check if already registered for makeup
                )
            """, (student_id, student_id, student_id))
            
            eligible_makeup_courses = []
            for row in cursor.fetchall():
                eligible_makeup_courses.append({
                    "course_code": row[0],
                    "course_name": row[1],
                    "coefficient": row[2],
                    "status": row[3],
                    "registered": False
                })
            
            # Get already registered makeup courses (semester = 3)
            cursor.execute("""
                SELECT c.course_code, c.course_name, c.coefficient, a.status
                FROM add_course a 
                JOIN courses c ON a.course_code = c.course_code
                WHERE a.student_id = %s 
                AND a.semester = 3 
                AND a.status = 'enrolled'
            """, (student_id,))
            
            for row in cursor.fetchall():
                eligible_makeup_courses.append({
                    "course_code": row[0],
                    "course_name": row[1],
                    "coefficient": row[2],
                    "status": row[3],
                    "registered": True
                })
            
            # Return success with all required data
            return jsonify({
                "success": True,
                "eligible": True,
                "makeupCourses": eligible_makeup_courses,
                "sessionDetails": session_details,
                "credits": credit_result[0] if credit_result else 0
            })
            
        finally:
            cursor.close()
            
    except Exception as e:
        current_app.logger.error(f"Error in makeup session check: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"An unexpected error occurred: {str(e)}"
        }), 500


@student_bp.route('/makeup-session/register', methods=['POST'])
@login_required
def register_makeup_courses():
    """Register student for makeup courses"""
    try:
        student = session.get('student')
        if not student:
            return jsonify({
                'success': False,
                'message': 'User not logged in',
                'code': 'UNAUTHORIZED'
            }), 401
            
        student_id = student['student_id']
        
        # Get course codes from request
        data = request.get_json()
        
        if not data or 'courses' not in data:
            return jsonify({"success": False, "message": "Invalid request: missing course data"}), 400
        
        course_codes = data.get('courses', [])
        
        if not course_codes or len(course_codes) > 2:
            return jsonify({
                "success": False, 
                "message": f"Invalid course selection: You must select 1-2 courses, but selected {len(course_codes)}"
            }), 400
        
        cursor = current_app.mysql.connection.cursor()
        
        try:
            # Check if a makeup session is active
            cursor.execute("""
                SELECT status FROM makeup_session 
                ORDER BY id DESC LIMIT 1
            """)
            
            makeup_session_result = cursor.fetchone()
            
            if not makeup_session_result or makeup_session_result[0] not in ['open', 'scheduled']:
                return jsonify({
                    "success": False,
                    "message": "No active makeup session is available"
                }), 400
            
            # Verify student eligibility again for security
            # This repeats the checks from the GET route to ensure valid submission
            
            # Check credits
            cursor.execute("""
                SELECT cumulative_earned_credits 
                FROM student_semester_summary 
                WHERE student_id = %s 
                ORDER BY year DESC, semester DESC 
                LIMIT 1
            """, (student_id,))
            
            credit_result = cursor.fetchone()
            if not credit_result or credit_result[0] < 115:
                return jsonify({
                    "success": False,
                    "message": "You need at least 115 earned credits to be eligible for makeup sessions"
                }), 403
            
            # Verify the selected courses are valid and eligible
            placeholders = ', '.join(['%s'] * len(course_codes))
            query = f"""
                SELECT c.course_code, c.course_name, a.status, a.forgiveness, c.eligible_for_makeup
                FROM add_course a 
                JOIN courses c ON a.course_code = c.course_code
                WHERE a.student_id = %s 
                AND a.course_code IN ({placeholders})
                AND a.id IN (
                    SELECT MAX(id) 
                    FROM add_course 
                    WHERE student_id = %s 
                    GROUP BY course_code
                )
                AND a.status IN ('failed', 'notenrolled')
                AND c.eligible_for_makeup = 1
                AND (a.forgiveness IS NULL OR a.forgiveness = 0)
            """
            params = [student_id] + course_codes + [student_id]
            cursor.execute(query, params)
            
            eligible_courses = cursor.fetchall()
            
            if len(eligible_courses) != len(course_codes):
                return jsonify({
                    "success": False,
                    "message": "One or more selected courses are not eligible for makeup"
                }), 400
            
            # Get student's year of study from student table
            cursor.execute("""
                SELECT year_of_study FROM student WHERE student_id = %s
            """, (student_id,))
            
            student_result = cursor.fetchone()
            if not student_result:
                return jsonify({
                    "success": False,
                    "message": "Could not determine student's year of study"
                }), 500
                
            current_year = student_result[0]
            
            # Define makeup semester as 3
            makeup_semester = 3
            
            # Get current semester from academic_calendar
            cursor.execute("""
                SELECT semester FROM academic_calendar WHERE is_current = 1 LIMIT 1
            """)
            academic_calendar_result = cursor.fetchone()
            current_semester = academic_calendar_result[0] if academic_calendar_result else 1
            
            # Insert registration records for each course into add_course table
            for course_code in course_codes:
                # First check if there's already a registration for this course in the current term
                cursor.execute("""
                    SELECT id FROM add_course
                    WHERE student_id = %s AND course_code = %s
                    AND year = %s AND semester = %s
                """, (student_id, course_code, current_year, makeup_semester))
                
                if cursor.fetchone():
                    continue  # Skip if already registered
                
                # Insert the registration into add_course
                cursor.execute("""
                    INSERT INTO add_course 
                    (student_id, course_code, semester, year, status, date)
                    VALUES (%s, %s, %s, %s, 'enrolled', NOW())
                """, (student_id, course_code, makeup_semester, current_year))
            
            current_app.mysql.connection.commit()
            
            return jsonify({
                "success": True,
                "message": "Successfully registered for makeup courses",
                "registeredCourses": course_codes
            })
            
        finally:
            cursor.close()
            
    except Exception as e:
        current_app.logger.error(f"Error in makeup course registration: {str(e)}")
        return jsonify({
            "success": False, 
            "message": f"An unexpected error occurred: {str(e)}"
        }), 500

@student_bp.route('/profile-info', methods=['GET', 'POST'])
@login_required
def profile_info():
    """Get or update student profile information"""
    try:
        student = session.get('student')
        if not student:
            return jsonify({
                'success': False,
                'message': 'User not logged in',
                'code': 'UNAUTHORIZED'
            }), 401
            
        student_id = student['student_id']
        cursor = current_app.mysql.connection.cursor()
        
        # GET request: Return current profile information
        if request.method == 'GET':
            try:
                cursor.execute("""
                    SELECT 
                        student_id, first_name, last_name, national_id, 
                        email_address, phone, profile_picture, secondary_email_address,
                        enrollment_status
                    FROM student 
                    WHERE student_id = %s
                """, (student_id,))
                
                result = cursor.fetchone()
                if not result:
                    return jsonify({
                        'success': False,
                        'message': 'Student not found',
                        'code': 'NOT_FOUND'
                    }), 404
                
                # Convert profile picture to base64 if exists
                profile_data = None
                if result[6]:  # index 6 is profile_picture
                    profile_data = base64.b64encode(result[6]).decode('utf-8')
                
                # Check if student is graduated
                is_graduated = result[8] == 'graduated'
                
                # Update session with graduation status
                if is_graduated:
                    session['student']['is_graduated'] = True
                
                profile_info = {
                    'student_id': result[0],
                    'first_name': result[1],
                    'last_name': result[2],
                    'national_id': result[3],
                    'email_address': result[4],
                    'phone': result[5] or '',
                    'profile_picture': profile_data,
                    'secondary_email_address': result[7] or '',
                    'enrollment_status': result[8],
                    'is_graduated': is_graduated
                }
                
                return jsonify({
                    'success': True,
                    'data': profile_info
                })
                
            except Exception as e:
                current_app.logger.error(f"Error fetching profile info: {str(e)}")
                return jsonify({
                    'success': False,
                    'message': f'Error fetching profile information: {str(e)}',
                    'code': 'DB_ERROR'
                }), 500
                
        # POST request: Update profile information
        elif request.method == 'POST':
            try:
                data = request.get_json()
                if not data:
                    return jsonify({
                        'success': False,
                        'message': 'No data provided',
                        'code': 'NO_DATA'
                    }), 400
                
                # Extract fields that can be updated
                first_name = data.get('first_name')
                last_name = data.get('last_name')
                phone = data.get('phone')
                secondary_email_address = data.get('secondary_email_address')
                profile_picture = data.get('profile_picture')
                
                # Validate required fields
                if not first_name or not last_name:
                    return jsonify({
                        'success': False,
                        'message': 'First name and last name are required',
                        'code': 'MISSING_REQUIRED'
                    }), 400
                
                # Start building the update query
                query_parts = []
                params = []
                
                if first_name:
                    query_parts.append("first_name = %s")
                    params.append(first_name)
                    
                if last_name:
                    query_parts.append("last_name = %s")
                    params.append(last_name)
                    
                if phone is not None:
                    query_parts.append("phone = %s")
                    params.append(phone)
                    
                if secondary_email_address is not None:
                    query_parts.append("secondary_email_address = %s")
                    params.append(secondary_email_address)
                
                # Handle profile picture update if provided
                if profile_picture:
                    # Remove data URL prefix if present
                    if profile_picture.startswith('data:image'):
                        image_data = profile_picture.split(',')[1]
                    else:
                        image_data = profile_picture
                    
                    try:
                        binary_data = base64.b64decode(image_data)
                        query_parts.append("profile_picture = %s")
                        params.append(binary_data)
                    except Exception as e:
                        current_app.logger.error(f"Error decoding profile picture: {str(e)}")
                        return jsonify({
                            'success': False,
                            'message': 'Invalid profile picture format',
                            'code': 'INVALID_IMAGE'
                        }), 400
                
                # If no fields to update, return early
                if not query_parts:
                    return jsonify({
                        'success': False,
                        'message': 'No fields to update',
                        'code': 'NO_CHANGES'
                    }), 400
                
                # Build and execute the update query
                query = f"UPDATE student SET {', '.join(query_parts)} WHERE student_id = %s"
                params.append(student_id)
                
                cursor.execute(query, params)
                current_app.mysql.connection.commit()
                
                # Update session info
                if first_name:
                    session['student']['first_name'] = first_name
                if last_name:
                    session['student']['last_name'] = last_name
                if profile_picture:
                    # Update profile picture in session
                    session['student']['profile_picture'] = image_data
                
                return jsonify({
                    'success': True,
                    'message': 'Profile updated successfully'
                })
                
            except Exception as e:
                current_app.logger.error(f"Error updating profile: {str(e)}")
                return jsonify({
                    'success': False,
                    'message': f'Error updating profile: {str(e)}',
                    'code': 'UPDATE_ERROR'
                }), 500
                
    except Exception as e:
        current_app.logger.error(f"Unexpected error in profile_info: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'An unexpected error occurred: {str(e)}',
            'code': 'UNEXPECTED_ERROR'
        }), 500
    finally:
        if 'cursor' in locals():
            cursor.close()

@student_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Change student password"""
    try:
        student = session.get('student')
        if not student:
            return jsonify({
                'success': False,
                'message': 'User not logged in',
                'code': 'UNAUTHORIZED'
            }), 401
            
        student_id = student['student_id']
        data = request.get_json()
        
        if not data or 'current_password' not in data or 'new_password' not in data:
            return jsonify({
                'success': False,
                'message': 'Missing required fields',
                'code': 'MISSING_FIELDS'
            }), 400
            
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        # Validate new password
        if len(new_password) < 8:
            return jsonify({
                'success': False,
                'message': 'New password must be at least 8 characters',
                'code': 'WEAK_PASSWORD'
            }), 400
            
        cursor = current_app.mysql.connection.cursor()
        
        # Verify current password
        cursor.execute("SELECT password FROM student WHERE student_id = %s", (student_id,))
        result = cursor.fetchone()
        
        if not result:
            return jsonify({
                'success': False,
                'message': 'Student not found',
                'code': 'NOT_FOUND'
            }), 404
            
        stored_password = result[0]
        
        # Verify current password using Werkzeug's check_password_hash
        if not check_password_hash(stored_password, current_password):
            return jsonify({
                'success': False,
                'message': 'Current password is incorrect',
                'code': 'INCORRECT_PASSWORD'
            }), 401
            
        # Update password with a secure hash
        hashed_password = generate_password_hash(new_password)
        cursor.execute(
            "UPDATE student SET password = %s WHERE student_id = %s",
            (hashed_password, student_id)
        )
        
        current_app.mysql.connection.commit()
        cursor.close()
        
        return jsonify({
            'success': True,
            'message': 'Password changed successfully'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in change_password: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'An error occurred: {str(e)}',
            'code': 'UNEXPECTED_ERROR'
        }), 500

@student_bp.route('/schedule/professors/preferences', methods=['GET', 'POST'])
@login_required
def handle_professor_preferences():
    # Get student info from session
    student = session.get('student')
    if not student:
        current_app.logger.error("No student found in session")
        return jsonify({
            'success': False,
            'message': 'User not logged in',
            'code': 'UNAUTHORIZED'
        }), 401
        
    # Extract student_id from student info
    student_id = student.get('student_id')
    if not student_id:
        current_app.logger.error("No student_id found in session data")
        return jsonify({
            'success': False,
            'message': 'Invalid session data',
            'code': 'INVALID_SESSION'
        }), 400
    
    # Log the student_id for debugging
    current_app.logger.info(f"Professor preferences request for student_id: {student_id}")
    
    # Handle GET request - retrieve existing preferences
    if request.method == 'GET':
        try:
            cursor = current_app.mysql.connection.cursor(dictionary=True)
            
            # Get all course IDs and professor preferences for this student
            cursor.execute("""
                                SELECT pp.course_code, pp.session_type, pp.professor_index, pp.ranked 
                FROM professor_preferences pp
                WHERE pp.student_id = %s
                ORDER BY pp.course_code, pp.session_type, pp.ranked
            """, (student_id,))
            
            preferences = cursor.fetchall()
            cursor.close()
            
            # Group preferences by course_code and session_type
            preference_dict = {}
            for pref in preferences:
                course_code = pref['course_code']
                session_type = 'lecture' if pref['session_type'] == 1 else 'tutorial'
                
                if course_code not in preference_dict:
                    preference_dict[course_code] = {}
                
                if session_type not in preference_dict[course_code]:
                    preference_dict[course_code][session_type] = []
                
                preference_dict[course_code][session_type].append({
                    'professor_index': pref['professor_index'],
                    'rank': pref['ranked']  # Using ranked from DB but keeping name as rank for frontend consistency
                })
            
            return jsonify({
                'success': True,
                'preferences': preference_dict
            })
            
        except Exception as e:
            current_app.logger.error(f"Error retrieving professor preferences: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Failed to retrieve professor preferences'
            }), 500
    
    # Handle POST request - save preferences
    elif request.method == 'POST':
        try:
            current_app.logger.info(f"Received POST request to save professor preferences")
            data = request.json
            current_app.logger.debug(f"Request data: {data}")
            
            if not data or 'preferences' not in data:
                current_app.logger.error("No preferences data found in request")
                return jsonify({
                    'success': False,
                    'message': 'No preference data provided'
                }), 400
            
            preferences = data.get('preferences', {})
            current_app.logger.info(f"Processing preferences for {len(preferences)} courses")
            
            cursor = current_app.mysql.connection.cursor()
            
            # Delete existing preferences for this student
            cursor.execute(
                "DELETE FROM professor_preferences WHERE student_id = %s",
                (student_id,)
            )
            
            # Get current timestamp for created_at and updated_at
            current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Process preferences by course and session type
            for course_code, course_prefs in preferences.items():
                # Use course_code directly since that's what we store in the table
                # No need to get course_id from courses table
                
                # Process lecture preferences
                if 'lecture' in course_prefs:
                    session_type = 1  # 1 for lecture
                    current_app.logger.info(f"Processing lecture preferences for course {course_code}")
                    
                    # Get all possible professors for this course and session type
                    cursor.execute("""
                        SELECT DISTINCT professor, professor_index 
                        FROM schedule 
                        WHERE course_code = %s 
                        AND session_type = 'lecture'
                    """, (course_code,))
                    current_app.logger.debug(f"Looking for professors in schedule table for course {course_code}, lecture")
                    
                    professors_result = cursor.fetchall()
                    professor_map = {professor[0]: professor[1] for professor in professors_result}
                    
                    for prof_data in course_prefs['lecture']:
                        professor_name = prof_data.get('professor')
                        rank_value = prof_data.get('rank', 0)  # Get rank or default to 0
                        
                        # Find the professor_index for this professor
                        if professor_name in professor_map:
                            professor_index = professor_map[professor_name]
                            
                            # Log for debugging
                            current_app.logger.info(f"Inserting professor preference: {professor_name}, index={professor_index}, rank={rank_value}")
                            
                            # Insert preference into database
                            cursor.execute("""
                                INSERT INTO professor_preferences 
                                (student_id, course_code, session_type, professor_index, ranked, created_at, updated_at)
                                VALUES (%s, %s, %s, %s, %s, %s, %s)
                            """, (
                                student_id, course_code, session_type, professor_index, 
                                rank_value, current_timestamp, current_timestamp
                            ))
                
                # Process tutorial preferences
                if 'tutorial' in course_prefs:
                    session_type = 2  # 2 for tutorial
                    
                    # Get all possible professors for this course and session type
                    cursor.execute("""
                        SELECT DISTINCT professor, professor_index 
                        FROM schedule 
                        WHERE course_code = %s 
                        AND session_type = 'tutorial'
                    """, (course_code,))
                    
                    professors_result = cursor.fetchall()
                    professor_map = {professor[0]: professor[1] for professor in professors_result}
                    
                    for prof_data in course_prefs['tutorial']:
                        professor_name = prof_data.get('professor')
                        rank_value = prof_data.get('rank', 0)  # Get rank or default to 0
                        
                        # Find the professor_index for this professor
                        if professor_name in professor_map:
                            professor_index = professor_map[professor_name]
                            
                            # Log for debugging
                            current_app.logger.info(f"Inserting tutorial professor preference: {professor_name}, index={professor_index}, rank={rank_value}")
                            
                            # Insert preference into database
                            cursor.execute("""
                                INSERT INTO professor_preferences 
                                (student_id, course_code, session_type, professor_index, ranked, created_at, updated_at)
                                VALUES (%s, %s, %s, %s, %s, %s, %s)
                            """, (
                                student_id, course_code, session_type, professor_index,
                                rank_value, current_timestamp, current_timestamp
                            ))
            
            # Commit changes to database
            current_app.mysql.connection.commit()
            cursor.close()
            
            current_app.logger.info(f"Successfully saved professor preferences for student: {student_id}")
            return jsonify({
                'success': True,
                'message': 'Professor preferences saved successfully'
            })
            
        except Exception as e:
            if cursor:
                current_app.mysql.connection.rollback()
                cursor.close()
                
            current_app.logger.error(f"Error saving professor preferences: {str(e)}")
            import traceback
            current_app.logger.error(traceback.format_exc())
            return jsonify({
                'success': False,
                'message': f'Failed to save professor preferences: {str(e)}'
            }), 500

@student_bp.route('/schedule/time_slots', methods=['GET', 'POST'])
@login_required
def handle_time_slot_preferences():
    # Get student info from session
    student = session.get('student')
    if not student:
        current_app.logger.error("No student found in session")
        return jsonify({
            'success': False,
            'message': 'User not logged in',
            'code': 'UNAUTHORIZED'
        }), 401
        
    # Extract student_id from student info
    student_id = student.get('student_id')
    if not student_id:
        current_app.logger.error("No student_id found in session data")
        return jsonify({
            'success': False,
            'message': 'Invalid session data',
            'code': 'INVALID_SESSION'
        }), 400
        
    # Log the student_id for debugging
    current_app.logger.info(f"Time slot preferences request for student_id: {student_id}")
    
    # Handle GET request - retrieve existing preferences
    if request.method == 'GET':
        try:
            cursor = current_app.mysql.connection.cursor(dictionary=True)
            
            # Get current preferences
            cursor.execute(
                """
                SELECT time_slot_number, is_preferred 
                FROM time_slot_preferences 
                WHERE student_id = %s
                """, 
                (student_id,)
            )
            
            preferences = cursor.fetchall()
            cursor.close()
            
            # Convert to a simple dictionary for easier frontend use
            preference_dict = {pref['time_slot_number']: pref['is_preferred'] for pref in preferences}
            
            return jsonify({
                'success': True,
                'preferences': preference_dict
            })
            
        except Exception as e:
            current_app.logger.error(f"Error retrieving time slot preferences: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Failed to retrieve time slot preferences'
            }), 500
    
    # Handle POST request - save preferences
    elif request.method == 'POST':
        try:
            data = request.json
            if not data or 'preferences' not in data:
                return jsonify({
                    'success': False,
                    'message': 'No preference data provided'
                }), 400
            
            # preferences should be a list of time slot numbers that are preferred
            preferred_slots = data.get('preferences', [])
            
            cursor = current_app.mysql.connection.cursor()
            
            # First, delete existing preferences for this student
            cursor.execute(
                "DELETE FROM time_slot_preferences WHERE student_id = %s",
                (student_id,)
            )
            
            # Then insert new preferences for all 30 slots
            current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            for slot_number in range(1, 31):
                is_preferred = 1 if slot_number in preferred_slots else 0
                
                cursor.execute(
                    """
                    INSERT INTO time_slot_preferences 
                    (student_id, time_slot_number, is_preferred, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (student_id, slot_number, is_preferred, current_timestamp, current_timestamp)
                )
            
            current_app.mysql.connection.commit()
            cursor.close()
            
            return jsonify({
                'success': True,
                'message': 'Time slot preferences saved successfully'
            })
            
        except Exception as e:
            current_app.logger.error(f"Error saving time slot preferences: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Failed to save time slot preferences'
            }), 500

@student_bp.route('/schedule/generate', methods=['POST'])
@login_required
def generate_optimized_schedule():
    """Generate an optimized schedule using the new model based on student preferences"""
    try:
        student = session.get('student')
        if not student:
            return jsonify({
                'success': False,
                'message': 'User not logged in',
                'code': 'UNAUTHORIZED'
            }), 401

        student_id = student['student_id']
        cursor = current_app.mysql.connection.cursor()
        
        try:
            # Get the enrolled course codes
            cursor.execute("""
                SELECT course_code FROM add_course 
                WHERE student_id = %s AND status = 'enrolled'
                ORDER BY course_code
            """, (student_id,))
            
            enrolled_courses = [row[0] for row in cursor.fetchall()]
            
            if not enrolled_courses:
                return jsonify({
                    'success': False,
                    'message': 'You have no enrolled courses. Please enroll in courses before generating a schedule.',
                    'code': 'NO_COURSES'
                }), 404
            
            # Load preferences from database
            preferences = {}
            
            # Load professor preferences
            cursor.execute("""
                SELECT course_code, session_type, professor_index, ranked
                FROM professor_preferences
                WHERE student_id = %s
            """, (student_id,))
            
            professor_preferences = {}
            for row in cursor.fetchall():
                course_code, session_type, professor_index, rank = row
                if course_code not in professor_preferences:
                    professor_preferences[course_code] = {}
                if session_type not in professor_preferences[course_code]:
                    professor_preferences[course_code][session_type] = {}
                professor_preferences[course_code][session_type][professor_index] = rank
            
            if professor_preferences:
                preferences['professor_preferences'] = professor_preferences
            
            # Load timeslot preferences
            cursor.execute("""
                SELECT time_slot_number, is_preferred
                FROM time_slot_preferences
                WHERE student_id = %s
            """, (student_id,))
            
            timeslot_preferences = {}
            for row in cursor.fetchall():
                time_slot_number, is_preferred = row
                timeslot_preferences[time_slot_number] = bool(is_preferred)
            
            if timeslot_preferences:
                preferences['timeslot_preferences'] = timeslot_preferences
            
            current_app.logger.info(f"Generating optimized schedule for student {student_id} with preferences: {preferences}")
            
            # Check if there are any additional preferences from the request
            try:
                data = request.get_json()
                if data and 'preferences' in data:
                    req_preferences = data['preferences']
                    
                    # Check if priority_mode is specified
                    if 'priority_mode' in req_preferences:
                        priority_mode = req_preferences['priority_mode']
                        current_app.logger.info(f"Using priority mode for schedule generation: {priority_mode}")
                        
                        # Add priority_mode to preferences - the optimizer will load the appropriate weight
                        preferences['priority_mode'] = priority_mode
                    else:
                        # If no priority_mode specified, check the database for the current mode
                        cursor.execute(
                            "SELECT priority FROM priority_preferences WHERE student_id = %s",
                            (student_id,)
                        )
                        mode_result = cursor.fetchone()
                        if mode_result and mode_result[0]:
                            stored_mode = mode_result[0]
                            # Convert 'a'/'b' to 'timeslots'/'professors'
                            stored_priority_mode = (
                                'timeslots' if stored_mode == 'a' else 'professors'
                            )
                            preferences['priority_mode'] = stored_priority_mode
                            current_app.logger.info(
                                f"Using stored priority mode from DB: {stored_priority_mode}"
                            )
                        else:
                            # Default to timeslots priority if nothing is stored
                            preferences['priority_mode'] = 'timeslots'
                            current_app.logger.info(
                                "No stored priority found – defaulting to 'timeslots'"
                            )
                    
                    # Merge any other preferences
                    for key, value in req_preferences.items():
                        if key != 'priority_mode':  # We've already handled this
                            preferences[key] = value
            except Exception as e:
                current_app.logger.error(f"Error parsing request preferences: {str(e)}")
                # Continue with existing preferences
            
            # Import the optimize_student_schedule function
            from schedule_optimizer import optimize_student_schedule
            
            current_app.logger.debug(f"Calling optimize_student_schedule with student_id={student_id} and preferences: {preferences}")
            
            # Generate the schedule
            result = optimize_student_schedule(
                student_id=student_id,
                db_connection=current_app.mysql.connection,
                random_seed=None,  # Let the optimizer use a default seed
                preferences=preferences
            )
            
            # Log the result
            current_app.logger.debug(f"Optimization result: success={result.get('success')}, has_schedule={('schedule' in result)}, schedule_length={len(result.get('schedule', []))})")
            
            if not result['success']:
                return jsonify({
                    'success': False,
                    'message': result.get('message', 'Failed to generate schedule'),
                    'code': 'OPTIMIZATION_FAILED'
                }), 500
            
            # Add course details to the result
            if 'schedule' in result:
                # Check for course_name in schedule items
                for item in result['schedule']:
                    if 'course_name' not in item or not item['course_name'] or item['course_name'] == 'Unknown Course':
                        # Need to populate course names
                        break
                else:
                    # All items have course names, skip database query
                    current_app.logger.debug("Schedule items already have course names, skipping query")
                    result['course_details'] = {}
                    return jsonify(result)
                
                # Need to query course details
                course_details = {}
                for item in result['schedule']:
                    course_code = item['course_code']
                    if course_code not in course_details:
                        cursor.execute("""
                            SELECT course_name, coefficient
                            FROM courses
                            WHERE course_code = %s
                        """, (course_code,))
                        course_info = cursor.fetchone()
                        if course_info:
                            course_details[course_code] = {
                                'course_name': course_info[0],
                                'coefficient': course_info[1]
                            }
                            # Update item directly for better display
                            item['course_name'] = course_info[0]
                        else:
                            # Create default if no info found
                            course_details[course_code] = {
                                'course_name': f"{course_code} Course",
                                'coefficient': 3  # Default credits
                            }
                            item['course_name'] = f"{course_code} Course"
                
                result['course_details'] = course_details
            
            # Save the schedule to the database
            try:
                # Get semester and year
                cursor.execute("""
                    SELECT semester, year
                    FROM academic_calendar
                    WHERE is_current = 1
                    LIMIT 1
                """)
                calendar_info = cursor.fetchone()
                if calendar_info:
                    result['semester'] = calendar_info[0]
                    result['year'] = calendar_info[1]
                
                # Prepare data to save
                import json
                enrolled_courses_key = ','.join(sorted(enrolled_courses))
                save_result = {k: v for k, v in result.items() if k != 'course_details'}
                schedule_data = json.dumps(save_result)
                
                # First delete any existing schedules
                cursor.execute("""
                    DELETE FROM student_schedules
                    WHERE student_id = %s AND enrolled_courses_key = %s
                """, (student_id, enrolled_courses_key))
                
                # Check if the student_schedules table has semester and year columns
                try:
                    # First check table structure
                    cursor.execute("SHOW COLUMNS FROM student_schedules")
                    columns = [column[0] for column in cursor.fetchall()]
                    
                    if 'semester' in columns and 'year' in columns:
                        # If columns exist, use them
                        cursor.execute("""
                            INSERT INTO student_schedules 
                            (student_id, enrolled_courses_key, schedule_data, semester, year)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (student_id, enrolled_courses_key, schedule_data, result['semester'], result['year']))
                    else:
                        # If columns don't exist, don't include them
                        cursor.execute("""
                            INSERT INTO student_schedules 
                            (student_id, enrolled_courses_key, schedule_data)
                            VALUES (%s, %s, %s)
                        """, (student_id, enrolled_courses_key, schedule_data))
                except Exception as e:
                    current_app.logger.error(f"Error checking table structure: {str(e)}")
                    # Fallback to simpler query
                    cursor.execute("""
                        INSERT INTO student_schedules 
                        (student_id, enrolled_courses_key, schedule_data)
                        VALUES (%s, %s, %s)
                    """, (student_id, enrolled_courses_key, schedule_data))
                current_app.mysql.connection.commit()
                
                current_app.logger.info(f"Saved optimized schedule for student {student_id}")
            except Exception as e:
                current_app.logger.error(f"Error saving optimized schedule: {str(e)}")
                # Continue anyway, just don't save the schedule
            
            return jsonify(result)
        
        finally:
            cursor.close()
        
    except Exception as e:
        current_app.logger.error(f"Error generating optimized schedule: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Error generating schedule: {str(e)}',
            'code': 'SCHEDULE_ERROR'
        }), 500

@student_bp.route('/major_minor/specialized_gpas')
@login_required
def get_specialized_gpas():
    """Get the specialized GPAs for the student from the database"""
    try:
        student = session.get('student')
        if not student:
            return unauthorized_response()

        student_id = student['student_id']
        cursor = current_app.mysql.connection.cursor()
        
        try:
            # Get student's year_of_study from student table
            cursor.execute("""
                SELECT year_of_study FROM student
                WHERE student_id = %s
            """, (student_id,))
            
            student_year_result = cursor.fetchone()
            if not student_year_result:
                return jsonify({
                    'success': False,
                    'message': 'Student not found',
                    'code': 'NOT_FOUND'
                }), 404
                
            student_year = student_year_result[0]
            
            # Get current active semester
            _, current_semester = get_current_semester()
            
            if not student_year or not current_semester:
                return jsonify({
                    'success': False,
                    'message': 'No active semester or student year found',
                    'code': 'NO_SEMESTER'
                }), 404
            
            # Get specialized GPAs from the database
            cursor.execute("""
                SELECT acct_gpa, ba_gpa, fin_gpa, it_gpa, mrk_gpa
                FROM student_semester_summary
                WHERE student_id = %s AND year = %s AND semester = %s
            """, (student_id, student_year, current_semester))
            
            result = cursor.fetchone()
            
            if not result:
                return jsonify({
                    'success': False,
                    'message': 'No specialized GPAs found',
                    'code': 'NO_DATA'
                }), 404
            
            # Convert to dictionary with proper names
            specialized_gpas = {
                'ACCT': float(result[0]) if result[0] is not None else None,
                'BA': float(result[1]) if result[1] is not None else None,
                'FIN': float(result[2]) if result[2] is not None else None,
                'IT': float(result[3]) if result[3] is not None else None,
                'MRK': float(result[4]) if result[4] is not None else None
            }
            
            return jsonify({
                'success': True,
                'specialized_gpas': specialized_gpas
            })
            
        except Exception as e:
            current_app.logger.error(f"Error fetching specialized GPAs: {str(e)}", exc_info=True)
            return jsonify({
                'success': False,
                'message': f'Error fetching specialized GPAs: {str(e)}',
                'code': 'DB_ERROR'
            }), 500
        finally:
            cursor.close()
            
    except Exception as e:
        current_app.logger.error(f"Unexpected error in get_specialized_gpas: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'An unexpected error occurred: {str(e)}',
            'code': 'UNEXPECTED_ERROR'
        }), 500

@student_bp.route('/enrollment-history/forgiveness', methods=['POST'])
@login_required
def apply_forgiveness():
    """Apply grade forgiveness for a specific course"""
    try:
        student = session.get('student')
        if not student:
            return handle_unauthorized()
            
        student_id = student['student_id']
        data = request.get_json()
        
        if not data or not all(key in data for key in ['course_code', 'year', 'semester']):
            return jsonify({
                'success': False,
                'message': 'Missing required data'
            }), 400
        
        course_code = data['course_code']
        year = data['year']
        semester = data['semester']
        
        current_app.logger.info(f"Processing forgiveness request for student {student_id}, course {course_code}")
        
        cursor = current_app.mysql.connection.cursor()
        
        try:
            # Check if there's already a pending or approved request for this course
            cursor.execute("""
                SELECT id, status
                FROM forgiveness_requests
                WHERE student_id = %s AND course_code = %s AND status IN ('pending', 'approved')
            """, (student_id, course_code))
            
            existing_request = cursor.fetchone()
            if existing_request:
                status = existing_request[1]
                return jsonify({
                    'success': False,
                    'message': f'A forgiveness request for this course is already {status}',
                    'status': status
                }), 400
            
            # Get the course coefficient to validate
            cursor.execute("""
                SELECT coefficient 
                FROM courses 
                WHERE course_code = %s
            """, (course_code,))
            
            course_row = cursor.fetchone()
            if not course_row:
                return jsonify({
                    'success': False,
                    'message': 'Course not found'
                }), 404
            
            # Check if the current attempt is a passing grade
            cursor.execute("""
                SELECT status, grade_point, letter_grade
                FROM add_course 
                WHERE student_id = %s 
                AND course_code = %s 
                AND year = %s 
                AND semester = %s
            """, (student_id, course_code, year, semester))
            
            current_attempt = cursor.fetchone()
            if not current_attempt or current_attempt[0] != 'passed':
                return jsonify({
                    'success': False,
                    'message': 'Forgiveness can only be applied to passing grades'
                }), 400
                
            current_grade = current_attempt[1]
            current_letter_grade = current_attempt[2]
            
            # Find the lowest grade for this course (to be forgiven)
            cursor.execute("""
                SELECT id, grade_point, letter_grade
                FROM add_course
                WHERE student_id = %s
                AND course_code = %s
                AND NOT (year = %s AND semester = %s)
                AND grade_point IS NOT NULL
                ORDER BY grade_point ASC
                LIMIT 1
            """, (student_id, course_code, year, semester))
            
            lowest_grade_row = cursor.fetchone()
            if not lowest_grade_row:
                return jsonify({
                    'success': False,
                    'message': 'No previous attempts found to forgive'
                }), 404
                
            add_id = lowest_grade_row[0]
            forgiven_grade = lowest_grade_row[1]
            forgiven_letter_grade = lowest_grade_row[2]
            
            # Get current academic year from academic_calendar
            cursor.execute("""
                SELECT academic_year 
                FROM academic_calendar 
                WHERE is_current = 1 
                LIMIT 1
            """)
            
            current_academic_year = cursor.fetchone()
            if not current_academic_year:
                current_academic_year = [year]  # Default to the year from the request
            
            # Create a forgiveness request in the database
            cursor.execute("""
                INSERT INTO forgiveness_requests 
                (student_id, course_code, status, request_date, forgiven_grade, new_grade, academic_year, add_id) 
                VALUES (%s, %s, 'pending', NOW(), %s, %s, %s, %s)
            """, (student_id, course_code, forgiven_grade, current_grade, current_academic_year[0], add_id))
            
            request_id = cursor.lastrowid
            
            # Commit the changes
            current_app.mysql.connection.commit()
            
            # Log the successful forgiveness request
            current_app.logger.info(f"Forgiveness request created for student {student_id}, course {course_code}, request ID {request_id}")
            
            return jsonify({
                'success': True,
                'message': 'Forgiveness request submitted successfully',
                'request_id': request_id,
                'status': 'pending'
            })
            
        except Exception as e:
            current_app.mysql.connection.rollback()
            current_app.logger.error(f"Error applying forgiveness: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Failed to apply forgiveness',
                'error': str(e)
            }), 500
        finally:
            cursor.close()
            
    except Exception as e:
        current_app.logger.error(f"Unexpected error in apply_forgiveness: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An unexpected error occurred',
            'error': str(e)
        }), 500

@student_bp.route('/enrollment-history/forgiveness-impact', methods=['POST'])
@login_required
def calculate_forgiveness_impact():
    """Calculate the impact of grade forgiveness on CGPA"""
    try:
        student = session.get('student')
        if not student:
            return handle_unauthorized()
            
        student_id = student['student_id']
        data = request.get_json()
        
        if not data or not all(key in data for key in ['course_code', 'year', 'semester']):
            return jsonify({
                'success': False,
                'message': 'Missing required data'
            }), 400
        
        course_code = data['course_code']
        year = data['year']
        semester = data['semester']
        
        current_app.logger.info(f"Calculating forgiveness impact for student {student_id}, course {course_code}")
        
        cursor = current_app.mysql.connection.cursor()
        
        try:
            # Get the current CGPA from the most recent semester summary
            cursor.execute("""
                SELECT cumulative_gpa, cumulative_registered_credits
                FROM student_semester_summary
                WHERE student_id = %s
                ORDER BY year DESC, semester DESC
                LIMIT 1
            """, (student_id,))
            
            summary_row = cursor.fetchone()
            if not summary_row:
                return jsonify({
                    'success': False,
                    'message': 'No semester summary found'
                }), 404
                
            current_cgpa = float(summary_row[0])
            total_credits = float(summary_row[1])
            
            # Get the course coefficient
            cursor.execute("""
                SELECT coefficient
                FROM courses
                WHERE course_code = %s
            """, (course_code,))
            
            course_row = cursor.fetchone()
            if not course_row:
                return jsonify({
                    'success': False,
                    'message': 'Course not found'
                }), 404
                
            course_credits = float(course_row[0])
            
            # Find the lowest grade point for this course (excluding the current attempt)
            cursor.execute("""
                SELECT id, letter_grade, grade_point
                FROM add_course
                WHERE student_id = %s
                AND course_code = %s
                AND NOT (year = %s AND semester = %s)
                AND grade_point IS NOT NULL
                ORDER BY grade_point ASC
                LIMIT 1
            """, (student_id, course_code, year, semester))
            
            lowest_grade_row = cursor.fetchone()
            if not lowest_grade_row:
                return jsonify({
                    'success': False,
                    'message': 'No previous attempts found'
                }), 404
                
            add_id = lowest_grade_row[0]
            lowest_letter_grade = lowest_grade_row[1]
            lowest_grade_point = float(lowest_grade_row[2])
            
            # Get the current attempt's grade
            cursor.execute("""
                SELECT letter_grade, grade_point
                FROM add_course
                WHERE student_id = %s
                AND course_code = %s
                AND year = %s
                AND semester = %s
            """, (student_id, course_code, year, semester))
            
            current_grade_row = cursor.fetchone()
            current_letter_grade = current_grade_row[0] if current_grade_row else None
            current_grade_point = float(current_grade_row[1]) if current_grade_row and current_grade_row[1] is not None else None
            
            # Calculate the impact on CGPA
            # Formula: (current_cgpa * total_credits - lowest_grade_point * course_credits) / (total_credits - course_credits)
            if total_credits > course_credits:  # Avoid division by zero
                new_cgpa = (current_cgpa * total_credits - lowest_grade_point * course_credits) / (total_credits - course_credits)
                # Round to 2 decimal places and ensure it's between 0 and 4.0
                new_cgpa = round(min(4.0, max(0, new_cgpa)), 2)
            else:
                # If we can't calculate properly, just show a slight improvement
                new_cgpa = min(4.0, current_cgpa + 0.1)
            
            return jsonify({
                'success': True,
                'current_cgpa': current_cgpa,
                'new_cgpa': new_cgpa,
                'lowest_grade': {
                    'letter': lowest_letter_grade,
                    'point': lowest_grade_point,
                    'add_id': add_id
                },
                'current_grade': {
                    'letter': current_letter_grade,
                    'point': current_grade_point
                }
            })
            
        except Exception as e:
            current_app.logger.error(f"Error calculating forgiveness impact: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Failed to calculate forgiveness impact',
                'error': str(e)
            }), 500
        finally:
            cursor.close()
            
    except Exception as e:
        current_app.logger.error(f"Unexpected error in calculate_forgiveness_impact: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An unexpected error occurred',
            'error': str(e)
        }), 500

@student_bp.route('/enrollment-history/forgiveness-status', methods=['GET'])
@login_required
def check_forgiveness_status():
    """Check forgiveness request status for all courses"""
    try:
        student = session.get('student')
        if not student:
            return handle_unauthorized()
            
        student_id = student['student_id']
        
        cursor = current_app.mysql.connection.cursor()
        
        try:
            # Get all forgiveness requests for this student
            cursor.execute("""
                SELECT course_code, status, request_date, handling_date
                FROM forgiveness_requests
                WHERE student_id = %s
            """, (student_id,))
            
            requests = cursor.fetchall()
            
            # Format the results
            forgiveness_status = {}
            for req in requests:
                course_code, status, request_date, handling_date = req
                forgiveness_status[course_code] = {
                    'status': status,
                    'request_date': request_date.strftime('%Y-%m-%d %H:%M:%S') if request_date else None,
                    'handling_date': handling_date.strftime('%Y-%m-%d %H:%M:%S') if handling_date else None
                }
            
            return jsonify({
                'success': True,
                'forgiveness_status': forgiveness_status
            })
            
        except Exception as e:
            current_app.logger.error(f"Error checking forgiveness status: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Failed to check forgiveness status',
                'error': str(e)
            }), 500
        finally:
            cursor.close()
            
    except Exception as e:
        current_app.logger.error(f"Unexpected error in check_forgiveness_status: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An unexpected error occurred',
            'error': str(e)
        }), 500

@student_bp.route('/schedule/all-optimal', methods=['POST'])
@login_required
def find_all_optimal_schedules():
    """Find all optimal schedules for the student"""
    try:
        student = session.get('student')
        if not student:
            return jsonify({
                'success': False,
                'message': 'User not logged in',
                'code': 'UNAUTHORIZED'
            }), 401

        student_id = student['student_id']
        cursor = current_app.mysql.connection.cursor()
        
        try:
            # Get preferences from request body
            preferences = None
            try:
                data = request.get_json()
                if data and 'preferences' in data:
                    preferences = data['preferences']
                    current_app.logger.info(f"Received preferences: {preferences}")
            except Exception as e:
                current_app.logger.error(f"Error parsing preferences: {str(e)}")
                # Continue without preferences
            
            # Get the enrolled course codes
            cursor.execute("""
                SELECT course_code FROM add_course 
                WHERE student_id = %s AND status = 'enrolled'
                ORDER BY course_code
            """, (student_id,))
            
            enrolled_courses = [row[0] for row in cursor.fetchall()]
            
            if not enrolled_courses:
                return jsonify({
                    'success': False,
                    'message': 'You have no enrolled courses. Please enroll in courses before generating a schedule.',
                    'code': 'NO_COURSES'
                }), 404
            
            # Generate all optimal schedules
            current_app.logger.info(f"Finding all optimal schedules for student {student_id}")
            
            result = optimize_student_schedule(
                student_id=student_id,
                db_connection=current_app.mysql.connection,
                preferences=preferences,
                find_all=True  # This is the key parameter to find all optimal solutions
            )
            
            # Add course details to each solution
            if result['success'] and 'solutions' in result and result['solutions']:
                try:
                    # Get all unique course codes from all solutions
                    all_course_codes = set()
                    for solution in result['solutions']:
                        if 'schedule' in solution:
                            for item in solution['schedule']:
                                all_course_codes.add(item['course_code'])
                    
                    # Get course details for all courses
                    course_details = {}
                    for course_code in all_course_codes:
                        cursor.execute("""
                            SELECT course_name, coefficient
                            FROM courses
                            WHERE course_code = %s
                        """, (course_code,))
                        course_info = cursor.fetchone()
                        if course_info:
                            course_details[course_code] = {
                                'course_name': course_info[0],
                                'coefficient': course_info[1]
                            }
                    
                    # Add course details to each solution
                    for solution in result['solutions']:
                        solution['course_details'] = course_details
                except Exception as e:
                    current_app.logger.error(f"Error processing solutions: {str(e)}")
                    # Continue anyway, we'll return what we have
            
            return jsonify(result)
        
        finally:
            cursor.close()
        
    except Exception as e:
        current_app.logger.error(f"Error finding all optimal schedules: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Error finding all optimal schedules: {str(e)}',
            'code': 'SCHEDULE_ERROR'
        }), 500

@student_bp.route('/schedule/confirm_choice', methods=['POST'])
@login_required
def confirm_schedule_choice():
    """Save a confirmed schedule and update study groups in add_course table"""
    cursor = None  # Initialize cursor to None
    try:
        # Use Flask's session explicitly to avoid any shadowing
        from flask import session as flask_session  
        student = flask_session.get('student')
        if not student:
            return jsonify({
                'success': False,
                'message': 'User not logged in',
                'code': 'UNAUTHORIZED'
            }), 401

        student_id = student['student_id']
        cursor = current_app.mysql.connection.cursor()
        
        # Check if registration is open
        cursor.execute("""
            SELECT status FROM registration_config 
            ORDER BY id DESC LIMIT 1
        """)
        reg_status = cursor.fetchone()
        if not reg_status or reg_status[0] != 'open':
            return jsonify({
                'success': False,
                'message': 'Course registration is not currently open',
                'code': 'REGISTRATION_CLOSED'
            }), 403
            
        # Get request data
        data = request.get_json()
        if not data or 'schedule' not in data:
            return jsonify({
                'success': False,
                'message': 'No schedule data provided',
                'code': 'INVALID_REQUEST'
            }), 400
            
        schedule = data['schedule']
        if not schedule or not isinstance(schedule, list):
            return jsonify({
                'success': False,
                'message': 'Invalid schedule format',
                'code': 'INVALID_FORMAT'
            }), 400
            
        # Get current semester info from academic_calendar
        cursor.execute("""
            SELECT academic_year, semester
            FROM academic_calendar
            WHERE is_current = 1
            LIMIT 1
        """)
        
        semester_info = cursor.fetchone()
        if not semester_info:
            return jsonify({
                'success': False,
                'message': 'No active semester found',
                'code': 'NO_SEMESTER'
            }), 404
            
        academic_year, semester = semester_info
        
        # Group sessions by course and type
        course_groups = {}
        for session in schedule:
            course_code = session['course_code']
            session_type = session['session_type']
            group = session.get('group', None)
            
            if course_code not in course_groups:
                course_groups[course_code] = {
                    'lecture': None,
                    'tutorial': None
                }
                
            # Only set the group if it's not already set (use first occurrence)
            if group and course_groups[course_code][session_type] is None:
                course_groups[course_code][session_type] = group
        
        # Update the add_course table with the study groups
        for course_code, groups in course_groups.items():
            lecture_group = groups['lecture']
            tutorial_group = groups['tutorial']
            
            cursor.execute("""
                UPDATE add_course
                SET lecture_study_group = %s,
                    tutorial_study_group = %s
                WHERE student_id = %s
                AND course_code = %s
                AND year = %s
                AND semester = %s
                AND status = 'enrolled'
            """, (lecture_group, tutorial_group, student_id, course_code, academic_year, semester))
        
        # Get all enrolled courses for creating a unique key
        cursor.execute("""
            SELECT course_code 
            FROM add_course 
            WHERE student_id = %s 
            AND year = %s 
            AND semester = %s 
            AND status = 'enrolled'
            ORDER BY course_code
        """, (student_id, academic_year, semester))
        
        enrolled_courses = [row[0] for row in cursor.fetchall()]
        enrolled_courses_key = ",".join(enrolled_courses)
        
        # Convert schedule data to JSON string
        import json
        schedule_data = json.dumps(schedule)
        
        # Check if student already has a saved schedule for this semester
        cursor.execute("""
            SELECT id 
            FROM student_schedules 
            WHERE student_id = %s AND year = %s AND semester = %s
        """, (student_id, academic_year, semester))
        
        existing_schedule = cursor.fetchone()
        
        if existing_schedule:
            # Update existing schedule
            cursor.execute("""
                UPDATE student_schedules
                SET enrolled_courses_key = %s,
                    schedule_data = %s,
                    created_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (enrolled_courses_key, schedule_data, existing_schedule[0]))
            current_app.logger.info(f"Updated existing schedule for student {student_id} (id: {existing_schedule[0]})")
        else:
            # Create new schedule entry
            cursor.execute("""
                INSERT INTO student_schedules 
                (student_id, enrolled_courses_key, schedule_data, semester, year, created_at)
                VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            """, (student_id, enrolled_courses_key, schedule_data, semester, academic_year))
            current_app.logger.info(f"Created new schedule entry for student {student_id}")
        
        current_app.mysql.connection.commit()
        
        return jsonify({
            'success': True,
            'message': 'Schedule confirmed and study groups saved successfully'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error confirming schedule: {str(e)}", exc_info=True)
        if cursor:
            current_app.mysql.connection.rollback()
        return jsonify({
            'success': False,
            'message': f'Error confirming schedule: {str(e)}',
            'code': 'CONFIRM_ERROR'
        }), 500
    finally:
        if cursor:
            cursor.close()

@student_bp.route('/schedule/delete-saved', methods=['DELETE'])
@login_required
def delete_saved_schedule():
    """Delete a student's saved schedule for the current semester"""
    try:
        # Use Flask's session explicitly to avoid any shadowing
        from flask import session as flask_session  
        student = flask_session.get('student')
        if not student:
            return jsonify({
                'success': False,
                'message': 'User not logged in',
                'code': 'UNAUTHORIZED'
            }), 401

        student_id = student['student_id']
        cursor = None
        
        try:
            cursor = current_app.mysql.connection.cursor()
            
            # Get current semester info
            cursor.execute("""
                SELECT semester, academic_year
                FROM academic_calendar
                WHERE is_current = 1
                LIMIT 1
            """)
            
            semester_info = cursor.fetchone()
            if not semester_info:
                return jsonify({
                    'success': False,
                    'message': 'No active semester found',
                    'code': 'NO_SEMESTER'
                }), 404
                
            current_semester, academic_year = semester_info
            
            # Delete the saved schedule
            cursor.execute("""
                DELETE FROM student_schedules
                WHERE student_id = %s AND semester = %s AND year = %s
            """, (student_id, current_semester, academic_year))
            
            current_app.mysql.connection.commit()
            
            if cursor.rowcount > 0:
                current_app.logger.info(f"Deleted saved schedule for student {student_id}")
                return jsonify({
                    'success': True,
                    'message': 'Saved schedule deleted successfully'
                })
            else:
                current_app.logger.info(f"No saved schedule found to delete for student {student_id}")
                return jsonify({
                    'success': False,
                    'message': 'No saved schedule found to delete',
                    'code': 'NO_SAVED_SCHEDULE'
                }), 404
                
        finally:
            if cursor:
                cursor.close()
                
    except Exception as e:
        current_app.logger.error(f"Error deleting saved schedule: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Error deleting saved schedule: {str(e)}',
            'code': 'DELETE_ERROR'
        }), 500

@student_bp.route('/schedule/update-mode', methods=['POST', 'GET'])
@login_required
def update_priority_mode_in_db():
    """Update or retrieve the priority mode directly from the database"""
    try:
        student = session.get('student')
        if not student:
            return jsonify({
                'success': False,
                'message': 'User not logged in',
                'code': 'UNAUTHORIZED'
            }), 401
        
        cursor = current_app.mysql.connection.cursor()
        
        try:
            # Handle GET request - retrieve current mode
            if request.method == 'GET':
                cursor.execute(
                    "SELECT priority FROM priority_preferences WHERE student_id = %s",
                    (student['student_id'],)
                )
                result = cursor.fetchone()
                if result and result[0]:
                    mode = result[0]
                    return jsonify({
                        'success': True,
                        'mode': mode
                    })
                else:
                    return jsonify({
                        'success': False,
                        'message': 'No priority mode found in database',
                        'code': 'NO_MODE'
                    }), 404
            
            # Handle POST request - update mode
            # Get the mode from the request
            data = request.get_json()
            if not data or 'mode' not in data:
                return jsonify({
                    'success': False,
                    'message': 'No mode provided',
                    'code': 'INVALID_REQUEST'
                }), 400
            
            mode = data['mode']
            
            # Validate mode
            if mode not in ['a', 'b']:
                return jsonify({
                    'success': False,
                    'message': 'Invalid mode. Mode must be either "a" or "b"',
                    'code': 'INVALID_MODE'
                }), 400
            
            # Check if an entry already exists for this student
            cursor.execute(
                "SELECT 1 FROM priority_preferences WHERE student_id = %s", (student['student_id'],)
            )
            exists = cursor.fetchone()
            if exists:
                # Update existing row
                cursor.execute(
                    "UPDATE priority_preferences SET priority = %s WHERE student_id = %s",
                    (mode, student['student_id']),
                )
            else:
                # Insert new row
                cursor.execute(
                    "INSERT INTO priority_preferences (student_id, priority) VALUES (%s, %s)",
                    (student['student_id'], mode),
                )
            current_app.mysql.connection.commit()
            
            current_app.logger.info(
                f"Updated priority preference for student {student['student_id']} to '{mode}'"
            )
            
            return jsonify({
                'success': True,
                'message': 'Priority mode updated successfully',
                'mode': mode
            })
        finally:
            cursor.close()
    
    except Exception as e:
        current_app.logger.error(f"Error handling priority mode: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Error handling priority mode: {str(e)}',
            'code': 'MODE_ERROR'
        }), 500

def build_prerequisite_chains(cursor, course_code, visited=None, depth=0):
    """
    Recursively build prerequisite chains for a given course.
    
    Args:
        cursor: Database cursor
        course_code: The course code to check prerequisites for
        visited: Set of already visited course codes (to prevent cycles)
        depth: Current recursion depth
        
    Returns:
        List of chains, where each chain is a list of dictionaries with course info
    """
    if visited is None:
        visited = set()
    
    # Prevent cycles in prerequisite graph
    if course_code in visited or depth > 10:  # Limit recursion depth
        return []
    
    visited.add(course_code)
    
    # Get course info
    cursor.execute("""
        SELECT c.course_code, c.course_name, c.year, c.semester, c.id
        FROM courses c
        WHERE c.course_code = %s
    """, (course_code,))
    
    course_info = cursor.fetchone()
    if not course_info:
        current_app.logger.warning(f"Course {course_code} not found in database")
        return []
    
    course_code, course_name, year, semester, course_id = course_info
    
    # Create current course node
    current_course = {
        "code": course_code,
        "name": course_name,
        "year": year,
        "semester": semester
    }
    
    # Find courses that have this course as a prerequisite
    cursor.execute("""
        SELECT c.course_code, c.course_name, c.year, c.semester, c.id
        FROM course_prerequisites cp
        JOIN courses c ON cp.course_id = c.id
        WHERE cp.prerequisite_id = %s
    """, (course_id,))
    
    dependent_courses = cursor.fetchall()
    current_app.logger.info(f"Course {course_code} is a prerequisite for {len(dependent_courses)} courses")
    
    # If this course is not a prerequisite for any other course, return empty list
    if not dependent_courses:
        return []
    
    # Build chains for each dependent course
    chains = []
    for dep_course in dependent_courses:
        dep_code, dep_name, dep_year, dep_semester, dep_id = dep_course
        current_app.logger.info(f"Course {course_code} is a prerequisite for {dep_code}")
        
        # Create dependent course node
        dependent_course = {
            "code": dep_code,
            "name": dep_name,
            "year": dep_year,
            "semester": dep_semester
        }
        
        # Create a chain with this course and the dependent one
        current_chain = [current_course, dependent_course]
        
        # Recursively get chains for the dependent course
        next_chains = build_prerequisite_chains(cursor, dep_code, visited.copy(), depth + 1)
        
        if next_chains:
            # If there are further dependencies, extend each chain
            for next_chain in next_chains:
                # Skip the first element in next_chain as it's already included as dependent_course
                extended_chain = current_chain + next_chain[1:]
                chains.append(extended_chain)
        else:
            # If no further dependencies, use the current chain
            chains.append(current_chain)
    
    return chains

@student_bp.route('/course-registration/check', methods=['POST'])
@login_required
def check_course_selection():
  
    try:
        student = session.get('student')
        if not student:
            return jsonify({
                'success': False,
                'message': 'User not logged in',
                'code': 'UNAUTHORIZED'
            }), 401

        student_id = student.get('student_id') or student.get('id')
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No course selection data provided',
                'code': 'NO_DATA'
            }), 400

        # Handle case where no courses are selected yet
        selected_courses = data.get('selected_courses', [])
        if not isinstance(selected_courses, list):
            selected_courses = []
            
        current_app.logger.info(f"Received selected courses: {selected_courses}")
        
        # Get student's year of study and current semester from database
        cursor = current_app.mysql.connection.cursor()
        try:
            # Get student's year of study and non_french status
            cursor.execute("SELECT year_of_study, non_french FROM student WHERE student_id = %s", (student_id,))
            student_result = cursor.fetchone()
            
            if not student_result:
                raise ValueError(f"Student with ID {student_id} not found")
                
            student_year = student_result[0]
            is_non_french = bool(student_result[1])
            
            current_app.logger.info(f"Student {student_id} is in year {student_year}, non_french: {is_non_french}")
            
            # Get current semester from academic_calendar
            cursor.execute("""
                SELECT academic_year, semester
                FROM academic_calendar
                WHERE is_current = 1
                ORDER BY calendar_id DESC
                LIMIT 1
            """)
            calendar_result = cursor.fetchone()
            
            if not calendar_result:
                return jsonify({
                    'success': False,
                    'message': 'Could not determine current semester',
                    'code': 'NO_CURRENT_SEMESTER'
                }), 400
                
            current_year = calendar_result[0]
            current_semester = calendar_result[1]
            
            current_app.logger.info(f"Student {student_id} is in year {student_year}, current semester {current_semester} of year {current_year}")
        finally:
            cursor.close()
        
        # Get all available courses for this student - ONLY current semester courses and skipped courses
        available_courses = []
        
        try:
            # STEP 1: Get current semester courses using get_current_courses from course_select.py
            current_courses = get_current_courses(current_semester, student_year, student_id)
            current_app.logger.info(f"Current courses from get_current_courses: {current_courses}")
            
            # Extract course codes from the returned course dictionaries
            for course in current_courses['courses']:
                if isinstance(course, dict) and 'course_code' in course:
                    course_code = course['course_code']
                    if course_code not in available_courses:
                        available_courses.append(course_code)
            
            # STEP 2: Get skipped courses (not enrolled) using get_notenrolled_courses from course_select.py
            skipped_courses = get_notenrolled_courses(student_id, current_semester, student_year)
            current_app.logger.info(f"Skipped courses from get_notenrolled_courses: {skipped_courses}")
            
            # Extract course codes from the returned course dictionaries
            skipped_course_codes = [course['course_code'] for course in skipped_courses]
            
            # Add skipped courses to available courses
            for course_code in skipped_course_codes:
                if course_code not in available_courses:
                    available_courses.append(course_code)
                    
            # If we still don't have any courses, log an error but don't use hardcoded values
            if not available_courses:
                current_app.logger.error("No courses found from functions. Database may be missing course data.")
            
        except Exception as e:
            current_app.logger.error(f"Error getting available courses: {str(e)}", exc_info=True)
            # Log error but don't use hardcoded values
            available_courses = []  # Return empty list instead of hardcoded values
            
        current_app.logger.info(f"Total available courses: {available_courses}")
        
        # Calculate unselected courses - only consider current semester courses including retake courses
        unselected_courses = list(set(available_courses) - set(selected_courses))
        current_app.logger.info(f"Selected courses: {selected_courses}")
        current_app.logger.info(f"Available courses (current semester): {available_courses}")
        current_app.logger.info(f"Calculated unselected courses (current semester): {unselected_courses}")
        
        # TEMPORARY ENROLLMENT FOR SCHEDULE VALIDATION
        # Create a new database connection for transaction
        db_connection = current_app.mysql.connection
        cursor = db_connection.cursor()
        
        try:
            # Begin transaction
            cursor.execute("START TRANSACTION")
            
            # First delete all existing enrollments for this semester
            cursor.execute("""
                DELETE FROM add_course 
                WHERE student_id = %s 
                AND year = %s 
                AND semester = %s
                AND status IN ('enrolled', 'notenrolled')
            """, (student_id, current_year, current_semester))
            
            # Add selected courses as 'enrolled'
            for course_code in selected_courses:
                cursor.execute("""
                    INSERT INTO add_course (student_id, course_code, year, semester, status)
                    VALUES (%s, %s, %s, %s, 'enrolled')
                """, (student_id, course_code, current_year, current_semester))
            
            # Add unselected courses as 'notenrolled'
            for course_code in unselected_courses:
                cursor.execute("""
                    INSERT INTO add_course (student_id, course_code, year, semester, status)
                    VALUES (%s, %s, %s, %s, 'notenrolled')
                """, (student_id, course_code, current_year, current_semester))
            
            # Check if schedule validation is enabled in the system parameters
            cursor.execute("SELECT schedule_validation FROM schedule_parameters LIMIT 1")
            validation_result = cursor.fetchone()
            schedule_validation_enabled = validation_result and validation_result[0] == 1
            
            if schedule_validation_enabled:
                # Check if a feasible schedule can be created
                schedule_result = optimize_student_schedule(student_id, db_connection)
                
                # Check if schedule optimization was successful
                if not schedule_result['success']:
                    # Always rollback the temporary enrollments
                    cursor.execute("ROLLBACK")
                    return jsonify({
                        'success': False,
                        'message': 'There is a scheduling conflict between the courses you selected. Please adjust your selection.',
                        'code': 'SCHEDULE_CONFLICT'
                    }), 400
            else:
                # Skip schedule validation, assume it's successful
                schedule_result = {'success': True}
            
            # Always rollback the temporary enrollments
            cursor.execute("ROLLBACK")
            
        except Exception as e:
            # Ensure rollback on any error
            cursor.execute("ROLLBACK")
            current_app.logger.error(f"Error during temporary enrollment: {str(e)}", exc_info=True)
            return jsonify({
                'success': False,
                'message': f'Error checking schedule feasibility: {str(e)}',
                'code': 'SCHEDULE_CHECK_ERROR'
            }), 500
        finally:
            cursor.close()
        
        # Generate warnings
        warnings = []
        prerequisite_chains = []
        selected_course_chains = []
        
        try:
            # Create a new database connection for warnings analysis
            cursor = current_app.mysql.connection.cursor()
            
            # Build prerequisite chains for unselected courses
            for course_code in unselected_courses:
                chains = build_prerequisite_chains(cursor, course_code)
                if chains:
                    for chain in chains:
                        formatted_chain = []
                        for course in chain:
                            formatted_chain.append({
                                "code": course["code"],
                                "name": course["name"],
                                "year": course["year"],
                                "semester": course["semester"]
                            })
                        prerequisite_chains.append(formatted_chain)
            
            # Build prerequisite chains for selected courses (failed, current semester, and skipped)
            selected_course_codes = []
            
            # Get failed courses
            cursor.execute("""
                SELECT course_code FROM add_course 
                WHERE student_id = %s AND status = 'failed'
            """, (student_id,))
            failed_courses = [row[0] for row in cursor.fetchall()]
            selected_course_codes.extend([code for code in failed_courses if code in selected_courses])
            
            # Get current semester courses
            cursor.execute("""
                SELECT course_code FROM courses 
                WHERE semester = %s AND year <= %s
            """, (current_semester, student_year))
            current_semester_courses = [row[0] for row in cursor.fetchall()]
            selected_course_codes.extend([code for code in current_semester_courses if code in selected_courses])
            
            # Get skipped courses
            cursor.execute("""
                SELECT course_code FROM add_course 
                WHERE student_id = %s AND status = 'notenrolled'
            """, (student_id,))
            skipped_courses = [row[0] for row in cursor.fetchall()]
            selected_course_codes.extend([code for code in skipped_courses if code in selected_courses])
            
            # Remove duplicates
            selected_course_codes = list(set(selected_course_codes))
            
            # Build chains for selected courses
            for course_code in selected_course_codes:
                chains = build_prerequisite_chains(cursor, course_code)
                if chains:
                    for chain in chains:
                        formatted_chain = []
                        for course in chain:
                            formatted_chain.append({
                                "code": course["code"],
                                "name": course["name"],
                                "year": course["year"],
                                "semester": course["semester"]
                            })
                        # Add to selected course chains
                        selected_course_chains.append({
                            "root_course": course_code,
                            "chain": " --> ".join([f"{course['code']} ({course['year']}/{course['semester']})" for course in chain])
                        })
            
            # Get specialized GPAs for the student
            cursor.execute("""
                SELECT acct_gpa, ba_gpa, fin_gpa, it_gpa, mrk_gpa 
                FROM student_semester_summary 
                WHERE student_id = %s
                ORDER BY year DESC, semester DESC
                LIMIT 1
            """, (student_id,))
            
            specialized_gpas = cursor.fetchone()
            current_app.logger.info(f"Specialized GPAs for student {student_id}: {specialized_gpas}")
            
            # Get system parameters for minimum GPA requirements
            cursor.execute("""
                SELECT min_gpa_acct, min_gpa_ba, min_gpa_fin, min_gpa_it, min_gpa_mrk
                FROM system_parameters
                LIMIT 1
            """)
            
            min_gpa_requirements = cursor.fetchone()
            current_app.logger.info(f"Minimum GPA requirements: {min_gpa_requirements}")
            
            # If we have both specialized GPAs and minimum requirements
            if specialized_gpas and min_gpa_requirements:
                # Map major IDs to their names and GPA fields
                major_mapping = {
                    1: {'name': 'Accounting', 'gpa_index': 0, 'min_gpa_index': 0},
                    2: {'name': 'Business Administration', 'gpa_index': 1, 'min_gpa_index': 1},
                    3: {'name': 'Finance', 'gpa_index': 2, 'min_gpa_index': 2},
                    4: {'name': 'Information Technology', 'gpa_index': 3, 'min_gpa_index': 3},
                    5: {'name': 'Marketing', 'gpa_index': 4, 'min_gpa_index': 4}
                }
                
                current_app.logger.info(f"Analyzing {len(unselected_courses)} unselected courses: {unselected_courses}")
                
                # First, group unselected courses by major
                major_unselected_courses = {}
                
                # For each unselected course, check if it's required for any major
                for course_code in unselected_courses:
                    # Query to find which majors require this course
                    cursor.execute("""
                        SELECT mcr.major_id, m.major, m.full_name, mcr.weight, mcr.minimum_grade_point
                        FROM major_course_requirements mcr
                        JOIN majors m ON mcr.major_id = m.id
                        WHERE mcr.course_code = %s
                    """, (course_code,))
                    
                    required_for_majors = cursor.fetchall()
                    current_app.logger.info(f"Course {course_code} is required for {len(required_for_majors)} majors")
                    
                    # If this course is required for any major
                    if required_for_majors:
                        for major_data in required_for_majors:
                            major_id, major_code, major_name, course_weight, min_grade = major_data
                            
                            # Skip if major is not in our mapping
                            if major_id not in major_mapping:
                                continue
                            
                            # Add to the major's unselected courses
                            if major_id not in major_unselected_courses:
                                major_unselected_courses[major_id] = {
                                    'major_code': major_code,
                                    'major_name': major_name,
                                    'courses': []
                                }
                            
                            major_unselected_courses[major_id]['courses'].append({
                                'course_code': course_code,
                                'weight': float(course_weight),
                                'min_grade': min_grade
                            })
                
                # Get courses the student has already taken, including multiple attempts
                cursor.execute("""
                    SELECT course_code, status, grade_point, forgiveness, id
                    FROM add_course
                    WHERE student_id = %s
                    ORDER BY id ASC
                """, (student_id,))
                
                taken_courses = {}
                course_attempts = {}
                
                # First pass: collect all attempts for each course
                for row in cursor.fetchall():
                    taken_course_code, status, grade_point, forgiveness, entry_id = row
                    
                    if taken_course_code not in course_attempts:
                        course_attempts[taken_course_code] = []
                    
                    course_attempts[taken_course_code].append({
                        'id': entry_id,
                        'status': status,
                        'grade_point': grade_point,
                        'forgiveness': forgiveness
                    })
                
                # Second pass: process each course based on its attempts
                for course_code, attempts in course_attempts.items():
                    # Check if any attempt has forgiveness applied
                    forgiveness_applied = any(attempt.get('forgiveness') == 1 for attempt in attempts)
                    
                    if forgiveness_applied:
                        # If forgiveness is applied, only consider the attempt with highest grade
                        valid_attempts = [a for a in attempts if a['status'] in ('passed', 'failed') and a['grade_point'] is not None]
                        if valid_attempts:
                            # Sort by grade point (highest first)
                            valid_attempts.sort(key=lambda x: float(x['grade_point']) if x['grade_point'] is not None else 0, reverse=True)
                            best_attempt = valid_attempts[0]
                            
                            taken_courses[course_code] = {
                                'status': best_attempt['status'],
                                'grade_point': best_attempt['grade_point'],
                                'attempts': [best_attempt],
                                'forgiveness_applied': True
                            }
                    else:
                        # If no forgiveness, consider all valid attempts
                        valid_attempts = [a for a in attempts if a['status'] in ('passed', 'failed') and a['grade_point'] is not None]
                        
                        if valid_attempts:
                            # Store all valid attempts for this course
                            taken_courses[course_code] = {
                                'status': valid_attempts[-1]['status'],  # Use most recent status
                                'grade_point': valid_attempts[-1]['grade_point'],  # Use most recent grade
                                'attempts': valid_attempts,
                                'forgiveness_applied': False
                            }
                
                current_app.logger.info(f"Student has taken {len(taken_courses)} courses")
                
                # Now analyze each major's unselected courses as a group
                for major_id, major_data in major_unselected_courses.items():
                    major_code = major_data['major_code']
                    major_name = major_data['major_name']
                    unselected_major_courses = major_data['courses']
                    
                    # Skip if no courses are unselected for this major
                    if not unselected_major_courses:
                        continue
                    
                    # Get mapping for this major
                    mapping = major_mapping[major_id]
                    current_gpa = specialized_gpas[mapping['gpa_index']]
                    min_required_gpa = min_gpa_requirements[mapping['min_gpa_index']]
                    
                    current_app.logger.info(f"Analyzing {len(unselected_major_courses)} unselected courses for major {major_code}")
                    current_app.logger.info(f"Current GPA={current_gpa}, Min GPA={min_required_gpa}")
                    
                    # Get all required courses for this major
                    cursor.execute("""
                        SELECT mcr.course_code, mcr.weight, mcr.minimum_grade_point
                        FROM major_course_requirements mcr
                        WHERE mcr.major_id = %s
                    """, (major_id,))
                    
                    all_required_courses = cursor.fetchall()
                    current_app.logger.info(f"Found {len(all_required_courses)} required courses for major {major_code}")
                    
                    # Get the current specialized GPA for this major
                    current_gpa_value = float(current_gpa) if current_gpa is not None else 0.0
                    
                    # Calculate total weights of ALL required courses for this major
                    total_major_weights = 0
                    for req_course in all_required_courses:
                        req_course_code, req_weight, min_grade = req_course
                        
                        # If the course has been taken multiple times without forgiveness,
                        # we need to count its weight multiple times
                        if req_course_code in taken_courses and 'attempts' in taken_courses[req_course_code]:
                            course_data = taken_courses[req_course_code]
                            if not course_data.get('forgiveness_applied', False) and len(course_data['attempts']) > 1:
                                # Count weight for each valid attempt
                                valid_attempts = [a for a in course_data['attempts'] if a['status'] in ('passed', 'failed')]
                                total_major_weights += float(req_weight) * len(valid_attempts)
                                current_app.logger.info(f"Course {req_course_code} has {len(valid_attempts)} attempts, counting weight {float(req_weight)} {len(valid_attempts)} times")
                            else:
                                total_major_weights += float(req_weight)
                        else:
                            total_major_weights += float(req_weight)
                    
                    # Calculate current total grade points
                    # If we're using specialized GPA from student_semester_summary, it already includes all attempts
                    # So we need to use that value multiplied by the adjusted total weights
                    current_total_grade_points = current_gpa_value * total_major_weights
                    
                    # For debugging, let's calculate the grade points directly from the taken courses
                    # to verify that our specialized GPA calculation is correct
                    calculated_grade_points = 0
                    calculated_weights = 0
                    
                    for req_course in all_required_courses:
                        req_course_code, req_weight, min_grade = req_course
                        if req_course_code in taken_courses:
                            course_data = taken_courses[req_course_code]
                            
                            if 'attempts' in course_data:
                                # Handle multiple attempts
                                if course_data.get('forgiveness_applied', False):
                                    # For forgiveness, only count the best attempt
                                    if course_data['grade_point'] is not None:
                                        grade_point = float(course_data['grade_point'])
                                        calculated_grade_points += grade_point * float(req_weight)
                                        calculated_weights += float(req_weight)
                                        current_app.logger.info(f"Forgiveness: Course {req_course_code} best grade {grade_point}, weight {float(req_weight)}")
                                else:
                                    # For no forgiveness, count all attempts
                                    for attempt in course_data['attempts']:
                                        if attempt['grade_point'] is not None:
                                            grade_point = float(attempt['grade_point'])
                                            calculated_grade_points += grade_point * float(req_weight)
                                            calculated_weights += float(req_weight)
                                            current_app.logger.info(f"No forgiveness: Course {req_course_code} attempt grade {grade_point}, weight {float(req_weight)}")
                    
                    # Calculate our own GPA for debugging
                    calculated_gpa = calculated_weights > 0 and calculated_grade_points / calculated_weights or 0
                    current_app.logger.info(f"Calculated GPA: {calculated_gpa}, Specialized GPA: {current_gpa_value}")
                    current_app.logger.info(f"Calculated weights: {calculated_weights}, Total weights: {total_major_weights}")
                    
                    # For now, we'll continue using the specialized GPA from the database
                    # But we have the calculation in place if we need to use it
                    
                    # Extract codes and weights of unselected courses
                    unselected_course_codes = [c['course_code'] for c in unselected_major_courses]
                    unselected_course_weights_sum = sum(c['weight'] for c in unselected_major_courses)
                    
                    # Check if any unselected course has a minimum grade requirement
                    courses_with_min_grade = []
                    for course in unselected_major_courses:
                        if course['min_grade'] is not None and float(course['min_grade']) > 0:
                            min_grade_value = float(course['min_grade'])
                            
                            # Convert grade point to letter grade
                            letter_grade = "F"
                            if min_grade_value >= 3.7:
                                letter_grade = "A-"
                            elif min_grade_value >= 3.3:
                                letter_grade = "B+"
                            elif min_grade_value >= 3.0:
                                letter_grade = "B"
                            elif min_grade_value >= 2.7:
                                letter_grade = "B-"
                            elif min_grade_value >= 2.3:
                                letter_grade = "C+"
                            elif min_grade_value >= 2.0:
                                letter_grade = "C"
                            elif min_grade_value >= 1.7:
                                letter_grade = "C-"
                            elif min_grade_value >= 1.3:
                                letter_grade = "D+"
                            elif min_grade_value >= 1.0:
                                letter_grade = "D"
                                
                            courses_with_min_grade.append({
                                'course_code': course['course_code'],
                                'min_grade_value': min_grade_value,
                                'letter_grade': letter_grade
                            })
                            
                            # Check if student has previously taken this course with a grade below the minimum
                            if course['course_code'] in taken_courses:
                                course_data = taken_courses[course['course_code']]
                                
                                # Check most recent attempt
                                if course_data['status'] in ['passed', 'failed'] and course_data['grade_point'] is not None:
                                    # If there are multiple attempts and no forgiveness, check all attempts
                                    if 'attempts' in course_data and len(course_data['attempts']) > 1 and not course_data.get('forgiveness_applied', False):
                                        # Check if any attempt is below minimum
                                        below_min_attempts = []
                                        for attempt in course_data['attempts']:
                                            if attempt['grade_point'] is not None and float(attempt['grade_point']) < min_grade_value:
                                                below_min_attempts.append(float(attempt['grade_point']))
                                        
                                        if below_min_attempts:
                                            course['previous_attempt_below_min'] = True
                                            course['previous_grade'] = below_min_attempts[-1]  # Most recent below-min grade
                                            course['multiple_attempts'] = True
                                            course['below_min_attempts'] = below_min_attempts
                                    else:
                                        # Single attempt or forgiveness applied
                                        previous_grade = float(course_data['grade_point'])
                                        if previous_grade < min_grade_value:
                                            course['previous_attempt_below_min'] = True
                                            course['previous_grade'] = previous_grade
                    
                    # Identify remaining courses (excluding all unselected courses)
                    remaining_courses = []
                    remaining_weights_sum = 0
                    other_required_courses = []  # Track other required courses for display
                    
                    for req_course in all_required_courses:
                        req_course_code, req_weight, min_grade = req_course
                        
                        if req_course_code not in taken_courses and req_course_code not in unselected_course_codes:
                            # Course not yet taken and not in the unselected courses
                            req_weight_float = float(req_weight)
                            remaining_courses.append((req_course_code, req_weight_float))
                            remaining_weights_sum += req_weight_float
                            other_required_courses.append(req_course_code)
                    
                    # Calculate minimum required total grade points to meet minimum GPA
                    # IMPORTANT: We always use total_major_weights in the denominator
                    min_required = float(min_required_gpa)
                    min_total_grade_points = min_required * total_major_weights
                    
                    # Calculate how many grade points we need from remaining courses
                    # We need to reach min_total_grade_points, and we already have current_total_grade_points
                    needed_grade_points = min_total_grade_points - current_total_grade_points
                    
                    # Calculate minimum average grade needed in remaining courses
                    min_avg_grade_needed = 0
                    
                    # Check if there are any remaining courses
                    if remaining_weights_sum > 0:
                        min_avg_grade_needed = needed_grade_points / remaining_weights_sum
                    else:
                        # If there are no remaining courses (this is the last course)
                        # Check if current GPA meets the minimum requirement
                        if current_gpa_value < min_required:
                            # If current GPA is below minimum, it's impossible to meet without this course
                            min_avg_grade_needed = 9999  # Use a large number instead of infinity for JSON compatibility
                        else:
                            # Current GPA already meets minimum
                            min_avg_grade_needed = 0
                    
                    # Check if the minimum average grade needed is achievable (max is 4.0)
                    impossible_to_meet_min = min_avg_grade_needed > 4.0
                    
                    # Calculate best possible GPA (assuming 4.0 in all remaining courses)
                    # IMPORTANT: The denominator is always total_major_weights
                    best_possible_grade_points = current_total_grade_points + (4.0 * remaining_weights_sum)
                    best_possible_gpa = best_possible_grade_points / total_major_weights
                    
                    # For the case where this is the last course, check if skipping it would still meet requirements
                    if remaining_weights_sum == 0 and unselected_course_weights_sum > 0:
                        # Calculate GPA without the unselected course(s)
                        adjusted_total_weights = total_major_weights - unselected_course_weights_sum
                        if adjusted_total_weights > 0:
                            adjusted_gpa = current_total_grade_points / adjusted_total_weights
                            # Update the impossible flag based on this calculation
                            impossible_to_meet_min = adjusted_gpa < min_required
                    
                    current_app.logger.info(f"Group analysis for {len(unselected_course_codes)} courses in major {major_code}:")
                    current_app.logger.info(f"  - Unselected courses: {unselected_course_codes}")
                    current_app.logger.info(f"  - Current specialized GPA: {current_gpa_value}")
                    current_app.logger.info(f"  - Total major weights: {total_major_weights}")
                    current_app.logger.info(f"  - Current total grade points: {current_total_grade_points}")
                    current_app.logger.info(f"  - Unselected courses weights sum: {unselected_course_weights_sum}")
                    current_app.logger.info(f"  - Remaining weights (excl. unselected): {remaining_weights_sum}")
                    current_app.logger.info(f"  - Min required GPA: {min_required}")
                    current_app.logger.info(f"  - Min total grade points needed: {min_total_grade_points}")
                    current_app.logger.info(f"  - Needed grade points from remaining courses: {needed_grade_points}")
                    current_app.logger.info(f"  - Min avg grade needed in other courses: {min_avg_grade_needed}")
                    current_app.logger.info(f"  - Best possible GPA: {best_possible_gpa}")
                    current_app.logger.info(f"  - Impossible to meet min GPA: {impossible_to_meet_min}")
                            
                    # Generate appropriate message for the group of unselected courses
                    message = ""
                    
                    # Format the other required courses text
                    other_courses_text = ""
                    if other_required_courses:
                        other_courses_text = f" ({', '.join(other_required_courses)})"
                    
                    # Format the unselected courses text
                    unselected_courses_text = ", ".join(unselected_course_codes)
                    
                    # Case 1: Courses with minimum grade requirements
                    if courses_with_min_grade:
                        # If there are multiple courses with min grade requirements
                        if len(courses_with_min_grade) > 1:
                            course_codes = [c['course_code'] for c in courses_with_min_grade]
                            courses_with_grades = [f"{c['course_code']} (min: {c['letter_grade']})" for c in courses_with_min_grade]
                            message = f"{', '.join(course_codes)}: These courses are required for {major_name} major with minimum grades as shown: {', '.join(courses_with_grades)}. If you skip these courses, you will not be eligible for this major."
                        else:
                            # Single course with min grade requirement
                            c = courses_with_min_grade[0]
                            message = f"This course is required for {major_name} major with a minimum grade of {c['letter_grade']}. If you skip this course, you will not be eligible for this major."
                            
                            # Add info about previous attempt if applicable
                            for course in unselected_major_courses:
                                if course['course_code'] == c['course_code'] and 'previous_attempt_below_min' in course and course['previous_attempt_below_min']:
                                    if 'multiple_attempts' in course and course.get('multiple_attempts'):
                                        # Multiple attempts without forgiveness
                                        attempts_str = ", ".join([f"{grade:.2f}" for grade in course['below_min_attempts']])
                                        message += f" Note: You previously took this course multiple times and received grades below the minimum requirement ({attempts_str} < {c['min_grade_value']:.2f})."
                                    else:
                                        # Single attempt or forgiveness applied
                                        message += f" Note: You previously took this course and received a grade below the minimum requirement ({course['previous_grade']:.2f} < {c['min_grade_value']:.2f})."
                    
                    # Format min_required to remove trailing zeros - do this once for all cases
                    if min_required is None:
                        formatted_min = "2.0"  # Default value if min_required is None
                    else:
                        formatted_min = f"{min_required:.1f}".rstrip('0').rstrip('.') if min_required == int(min_required) else f"{min_required:.3f}".rstrip('0').rstrip('.')
                    
                    # Case 2: Courses don't have min grade but GPA impact is impossible
                    if impossible_to_meet_min:
                        
                        if remaining_weights_sum == 0:
                            # No other required courses remaining
                            if len(unselected_course_codes) > 1:
                                message = f"{', '.join(unselected_course_codes)}: These courses are required for {major_name} major. If you skip these courses, it will be IMPOSSIBLE to meet the minimum specialized GPA requirement of {formatted_min} for this major by the end of your second year. Consider retaking courses and/or applying for forgiveness policy to increase your specialized GPA."
                            else:
                                message = f"This course is required for {major_name} major. If you skip this course, it will be IMPOSSIBLE to meet the minimum specialized GPA requirement of {formatted_min} for this major by the end of your second year. Consider retaking courses and/or applying for forgiveness policy to increase your specialized GPA."
                        else:
                            # There are other required courses remaining
                            if len(unselected_course_codes) > 1:
                                message = f"{', '.join(unselected_course_codes)}: These courses are required for {major_name} major. If you skip these courses, it will be IMPOSSIBLE to meet the minimum specialized GPA requirement of {formatted_min} for this major by the end of your second year, even with perfect grades in all other courses{other_courses_text} that you have yet to enroll in."
                            else:
                                message = f"This course is required for {major_name} major. If you skip this course, it will be IMPOSSIBLE to meet the minimum specialized GPA requirement of {formatted_min} for this major by the end of your second year, even with perfect grades in all other courses{other_courses_text} that you have yet to enroll in."
                    
                    # Case 3: Courses don't have min grade but GPA impact is challenging
                    elif not impossible_to_meet_min and min_avg_grade_needed is not None and min_avg_grade_needed > 3.5:
                        if len(unselected_course_codes) > 1:
                            message = f"{', '.join(unselected_course_codes)}: These courses are required for {major_name} major. If you skip these courses, you would need to average at least {min_avg_grade_needed:.2f} in all other required courses{other_courses_text} to meet the minimum specialized GPA requirement of {formatted_min} by the end of your second year, which is very challenging."
                        else:
                            message = f"This course is required for {major_name} major. If you skip this course, you would need to average at least {min_avg_grade_needed:.2f} in all other required courses{other_courses_text} to meet the minimum specialized GPA requirement of {formatted_min} by the end of your second year, which is very challenging."
                    
                    # Case 4: Courses don't have min grade but GPA impact is moderate
                    elif not impossible_to_meet_min and min_avg_grade_needed is not None and min_avg_grade_needed > 3.0:
                        if len(unselected_course_codes) > 1:
                            message = f"{', '.join(unselected_course_codes)}: These courses are required for {major_name} major. If you skip these courses, you would need to average at least {min_avg_grade_needed:.2f} in all other required courses{other_courses_text} to meet the minimum specialized GPA requirement of {formatted_min}."
                        else:
                            message = f"This course is required for {major_name} major. If you skip this course, you would need to average at least {min_avg_grade_needed:.2f} in all other required courses{other_courses_text} to meet the minimum specialized GPA requirement of {formatted_min}."
                    
                    # Case 5: Courses don't have min grade and GPA impact is achievable
                    else:
                        
                        # Check if this is the last required course
                        if remaining_weights_sum == 0:
                            # This is the last required course
                            if len(unselected_course_codes) > 1:
                                # Format the course codes first, then add the rest of the message
                                message = f"{', '.join(unselected_course_codes)}: These are the last required courses for {major_name} major. You need to achieve at least a {min_required:.2f} average grade in these courses to meet the minimum specialized GPA requirement of {formatted_min} by the end of your second year."
                            else:
                                message = f"This course is required for {major_name} major. This is the last required course for this major. Your current specialized GPA is {current_gpa_value:.2f}, and the minimum required is {formatted_min}."
                            
                            # Add whether they meet the requirement without this course
                            adjusted_total_weights = total_major_weights - unselected_course_weights_sum
                            if adjusted_total_weights > 0:
                                adjusted_gpa = current_total_grade_points / adjusted_total_weights
                                if adjusted_gpa >= min_required:
                                    message += f" If you skip this course, your specialized GPA would be {adjusted_gpa:.2f}, which meets the minimum requirement."
                                else:
                                    message += f" If you skip this course, your specialized GPA would be {adjusted_gpa:.2f}, which does NOT meet the minimum requirement of {formatted_min}."
                        else:
                            # Normal case with other courses remaining
                            if len(unselected_course_codes) > 1:
                                message = f"{', '.join(unselected_course_codes)}: These courses are required for {major_name} major. If you skip these courses, you would need to average at least {min_avg_grade_needed:.2f} in all other required courses{other_courses_text} to meet the minimum specialized GPA requirement of {formatted_min} by the end of your second year, which is achievable but not recommended."
                            else:
                                message = f"This course is required for {major_name} major. If you skip this course, you would need to average at least {min_avg_grade_needed:.2f} in all other required courses{other_courses_text} to meet the minimum specialized GPA requirement of {formatted_min} by the end of your second year, which is achievable but not recommended."
                    
                    # Create a warning for each unselected course
                    for course in unselected_major_courses:
                        course_code = course['course_code']
                        course_weight = course['weight']
                        
                        # Ensure all values are JSON serializable
                        if isinstance(min_avg_grade_needed, float) and (math.isinf(min_avg_grade_needed) or math.isnan(min_avg_grade_needed)):
                            min_avg_grade_needed = 9999
                            
                        warnings.append({
                            'course_code': course_code,
                            'message': message,
                            'major': major_code,
                            'major_name': major_name,
                            'current_gpa': current_gpa,
                            'min_gpa': min_required_gpa,
                            'course_weight': course_weight,
                            'best_possible_gpa': best_possible_gpa,
                            'min_avg_grade_needed': min_avg_grade_needed,
                            'impossible': impossible_to_meet_min,
                            'other_required_courses': other_required_courses,
                            'unselected_course_group': unselected_course_codes
                        })
                        
                        current_app.logger.info(f"Added warning for course {course_code} for major {major_code}")
            
            cursor.close()
            
        except Exception as e:
            current_app.logger.error(f"Error analyzing major requirements: {str(e)}", exc_info=True)
            # Continue without adding warnings if there's a database error
        
        # Check if student is on probation and if selected courses can help
        probation_analysis = check_probation_impact(student_id, selected_courses)
        
        # Analyze selected courses that are the last required courses for a major
        selected_course_analysis = []
        
        try:
            cursor = current_app.mysql.connection.cursor()
            
            # Get specialized GPAs for this student
            cursor.execute("""
                SELECT acct_gpa, ba_gpa, fin_gpa, it_gpa, mrk_gpa
                FROM student_semester_summary
                WHERE student_id = %s
                ORDER BY year DESC, semester DESC
                LIMIT 1
            """, (student_id,))
            
            specialized_gpas = cursor.fetchone()
            
            # Get minimum GPA requirements
            cursor.execute("""
                SELECT min_gpa_acct, min_gpa_ba, min_gpa_fin, min_gpa_it, min_gpa_mrk
                FROM system_parameters
                ORDER BY last_updated DESC
                LIMIT 1
            """)
            
            min_gpas = cursor.fetchone()
            
            if specialized_gpas and min_gpas:
                # Map of major codes to indices
                major_indices = {
                    'ACCT': 0,
                    'BA': 1,
                    'FIN': 2,
                    'IT': 3,
                    'MRK': 4
                }
                
                # For each major, check if the selected courses are the last required courses
                for major_code, idx in major_indices.items():
                    current_gpa = specialized_gpas[idx] if specialized_gpas[idx] is not None else 0
                    min_required_gpa = min_gpas[idx] if min_gpas[idx] is not None else 2.0
                    
                    # Skip if already meeting requirements
                    if current_gpa >= min_required_gpa:
                        continue
                    
                    # Get all required courses for this major
                    cursor.execute("""
                        SELECT mcr.course_code, mcr.weight, mcr.minimum_grade_point
                        FROM major_course_requirements mcr
                        WHERE mcr.major_id = (SELECT id FROM majors WHERE major = %s)
                    """, (major_code,))
                    
                    all_required_courses = cursor.fetchall()
                    
                    # Get courses the student has already taken
                    cursor.execute("""
                        SELECT course_code, status, grade_point, forgiveness
                        FROM add_course
                        WHERE student_id = %s AND status IN ('passed', 'failed')
                        ORDER BY id DESC
                    """, (student_id,))
                    
                    taken_courses = {}
                    for row in cursor.fetchall():
                        course_code, status, grade_point, forgiveness = row
                        if course_code not in taken_courses:
                            taken_courses[course_code] = {
                                'status': status,
                                'grade_point': grade_point,
                                'forgiveness': forgiveness
                            }
                    
                    # Calculate current grade points and weights
                    current_total_grade_points = 0
                    total_major_weights = 0
                    
                    for course in all_required_courses:
                        course_code, weight, _ = course
                        weight_float = float(weight)
                        total_major_weights += weight_float
                        
                        if course_code in taken_courses:
                            course_data = taken_courses[course_code]
                            if course_data['grade_point'] is not None:
                                current_total_grade_points += float(course_data['grade_point']) * weight_float
                    
                    # Find required courses that haven't been taken yet
                    remaining_required = []
                    for course in all_required_courses:
                        course_code, weight, _ = course
                        if course_code not in taken_courses:
                            remaining_required.append(course_code)
                    
                    # Check if selected courses are the only remaining required courses
                    if remaining_required and all(course in selected_courses for course in remaining_required):
                        # These selected courses are the last required courses for this major
                        
                        # Calculate how many grade points we need to reach the minimum GPA
                        min_total_grade_points = float(min_required_gpa) * total_major_weights
                        needed_grade_points = min_total_grade_points - current_total_grade_points
                        
                        # Calculate the minimum average grade needed in these courses
                        remaining_weights_sum = 0
                        for course in all_required_courses:
                            course_code, weight, _ = course
                            if course_code in remaining_required:
                                remaining_weights_sum += float(weight)
                        
                        if remaining_weights_sum > 0:
                            min_avg_grade_needed = needed_grade_points / remaining_weights_sum
                            
                            # Check if it's possible to meet the requirement
                            if min_avg_grade_needed <= 4.0:
                                # It's possible to meet the requirement
                                major_name = major_code
                                cursor.execute("SELECT full_name FROM majors WHERE major = %s", (major_code,))
                                major_result = cursor.fetchone()
                                if major_result:
                                    major_name = major_result[0]
                                
                                # Get course names for the courses
                                cursor.execute(f"""
                                    SELECT course_code, course_name
                                    FROM courses 
                                    WHERE course_code IN ({', '.join(['%s'] * len(remaining_required))})
                                """, remaining_required)
                                
                                course_names = {row[0]: row[1] for row in cursor.fetchall()}
                                course_list = [f"{code} ({course_names.get(code, 'Unknown')})" for code in remaining_required]
                                courses_text = ", ".join(course_list)
                                
                                # Format min_required_gpa to remove trailing zeros
                                formatted_min_gpa = f"{float(min_required_gpa):.1f}".rstrip('0').rstrip('.') if float(min_required_gpa) == int(float(min_required_gpa)) else f"{float(min_required_gpa):.3f}".rstrip('0').rstrip('.')
                                
                                selected_course_analysis.append({
                                    'major_code': major_code,
                                    'major_name': major_name,
                                    'current_gpa': float(current_gpa),
                                    'min_required_gpa': float(min_required_gpa),
                                    'courses': remaining_required,
                                    'min_avg_grade_needed': min_avg_grade_needed,
                                    'message': f"These are the last required courses for {major_name} major: {courses_text}. You need to achieve at least a {min_avg_grade_needed:.2f} average grade in these courses to meet the minimum specialized GPA requirement of {formatted_min_gpa} by the end of your second year."
                                })
                            else:
                                # It's not possible to meet the requirement
                                major_name = major_code
                                cursor.execute("SELECT full_name FROM majors WHERE major = %s", (major_code,))
                                major_result = cursor.fetchone()
                                if major_result:
                                    major_name = major_result[0]
                                
                                # Get course names for the courses
                                cursor.execute(f"""
                                    SELECT course_code, course_name
                                    FROM courses 
                                    WHERE course_code IN ({', '.join(['%s'] * len(remaining_required))})
                                """, remaining_required)
                                
                                course_names = {row[0]: row[1] for row in cursor.fetchall()}
                                course_list = [f"{code} ({course_names.get(code, 'Unknown')})" for code in remaining_required]
                                courses_text = ", ".join(course_list)
                                
                                # Format min_required_gpa to remove trailing zeros
                                formatted_min_gpa = f"{float(min_required_gpa):.1f}".rstrip('0').rstrip('.') if float(min_required_gpa) == int(float(min_required_gpa)) else f"{float(min_required_gpa):.3f}".rstrip('0').rstrip('.')
                                
                                selected_course_analysis.append({
                                    'major_code': major_code,
                                    'major_name': major_name,
                                    'current_gpa': float(current_gpa),
                                    'min_required_gpa': float(min_required_gpa),
                                    'courses': remaining_required,
                                    'min_avg_grade_needed': 9999,  # Use 9999 instead of infinity for JSON compatibility
                                    'message': f"These are the last required courses for {major_name} major: {courses_text}. Even with perfect grades in these courses, you cannot meet the minimum GPA requirement of {formatted_min_gpa}. Consider retaking courses and/or applying for forgiveness policy to increase your specialized GPA."
                                })
            
            cursor.close()
        except Exception as e:
            current_app.logger.error(f"Error analyzing selected courses: {str(e)}", exc_info=True)
            # Continue without adding analysis if there's an error
        
        # Format prerequisite chains for display
        formatted_chains = []
        processed_chains = set()  # To avoid duplicate chains
        
        current_app.logger.info(f"Formatting {len(prerequisite_chains)} prerequisite chains")
        
        for chain in prerequisite_chains:
            if len(chain) < 2:  # Skip chains with only one course
                continue
                
            chain_text = ""
            for i, course in enumerate(chain):
                course_info = f"{course['code']} - {course['name']} (Year {course['year']}, Semester {course['semester']})"
                if i < len(chain) - 1:
                    chain_text += f"{course_info} --> "
                else:
                    chain_text += course_info
            
            # Only add unique chains
            if chain_text not in processed_chains:
                processed_chains.add(chain_text)
                
                # Add explanatory message
                if len(chain) > 0:
                    first_course = chain[0]
                    message = f"Not selecting {first_course['code']} will prevent you from taking the following course sequence:"
                    formatted_chains.append({
                        "root_course": first_course['code'],
                        "chain": chain_text,
                        "message": message,
                        "courses": chain  # Include full course objects for frontend flexibility
                    })
        
        current_app.logger.info(f"Found {len(formatted_chains)} unique prerequisite chains")
        
        # Sort chains by root course for better organization
        formatted_chains.sort(key=lambda x: x["root_course"])
        
        # Format selected course chains for display
        formatted_selected_chains = []
        processed_selected_chains = set()  # To avoid duplicate chains
        
        current_app.logger.info(f"Formatting {len(selected_course_chains)} selected course prerequisite chains")
        
        for chain in selected_course_chains:
            chain_text = chain["chain"]
            
            # Only add unique chains
            if chain_text not in processed_selected_chains:
                processed_selected_chains.add(chain_text)
                formatted_selected_chains.append(chain)
        
        current_app.logger.info(f"Found {len(formatted_selected_chains)} unique selected course prerequisite chains")
        
        # Return the debug info along with any warnings and prerequisite chains
        return jsonify({
            'success': True,
            'warnings': warnings,
            'probation_analysis': probation_analysis,
            'selected_course_analysis': selected_course_analysis,
            'prerequisite_chains': formatted_chains,
            'selected_course_chains': formatted_selected_chains,
            'debug_info': {
                'selected_courses': selected_courses,
                'available_courses': available_courses,
                'unselected_courses': unselected_courses
            }
        })
    
    except Exception as e:
        current_app.logger.error(f"Error in check_course_selection: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred while checking course selection',
            'error': str(e)
        }), 500

def check_probation_impact(student_id, selected_courses):
    """
    Check if the student's current course selection can help them get out of probation.
    
    Args:
        student_id: The student's ID
        selected_courses: List of course codes selected by the student
        
    Returns:
        Dictionary with probation analysis results
    """
    try:
        # Create database connection
        cursor = current_app.mysql.connection.cursor()
        
        # Check if student is on probation
        cursor.execute("""
            SELECT probation_counter, cumulative_gpa, cumulative_registered_credits
            FROM student_semester_summary
            WHERE student_id = %s
            ORDER BY record_id DESC
            LIMIT 1
        """, (student_id,))
        
        probation_result = cursor.fetchone()
        if not probation_result:
            # No semester summary found, student is not on probation
            return {
                'on_probation': False,
                'message': 'You are not currently on probation.'
            }
            
        probation_counter, current_cumulative_gpa, current_registered_credits = probation_result
        
        # If probation counter is 0, student is not on probation
        if probation_counter == 0:
            return {
                'on_probation': False,
                'message': 'You are not currently on probation.'
            }
        
        # Get minimum required GPA to get out of probation
        cursor.execute("""
            SELECT min_cumulative_gpa
            FROM system_parameters
            LIMIT 1
        """)
        
        min_gpa_result = cursor.fetchone()
        if not min_gpa_result:
            # No system parameters found
            return {
                'on_probation': True,
                'probation_counter': probation_counter,
                'error': 'Could not determine minimum GPA requirement.'
            }
            
        min_required_gpa = float(min_gpa_result[0])
        
        # Get weights for selected courses
        if not selected_courses:
            return {
                'on_probation': True,
                'probation_counter': probation_counter,
                'current_cumulative_gpa': float(current_cumulative_gpa),
                'min_required_gpa': min_required_gpa,
                'message': 'No courses selected. Please select courses to see if they can help you get out of probation.'
            }
        
        # Create placeholders for SQL query
        placeholders = ', '.join(['%s'] * len(selected_courses))
        
        # Get course weights
        cursor.execute(f"""
            SELECT course_code, coefficient
            FROM courses
            WHERE course_code IN ({placeholders})
        """, selected_courses)
        
        course_weights = {}
        for row in cursor.fetchall():
            course_code, coefficient = row
            course_weights[course_code] = float(coefficient)
        
        # Calculate total weight of selected courses
        total_selected_weight = 0
        for course_code in selected_courses:
            if course_code in course_weights:
                total_selected_weight += course_weights[course_code]
        
        # Calculate current total grade points
        current_grade_points = float(current_cumulative_gpa) * float(current_registered_credits)
        
        # Calculate new total registered credits
        new_total_credits = float(current_registered_credits) + total_selected_weight
        
        # Calculate best case scenario (4.0 in all selected courses)
        best_case_new_points = current_grade_points + (4.0 * total_selected_weight)
        best_case_new_gpa = best_case_new_points / new_total_credits
        
        # Calculate minimum term GPA needed to reach minimum required GPA
        min_required_total_points = min_required_gpa * new_total_credits
        points_needed = min_required_total_points - current_grade_points
        min_term_gpa_needed = points_needed / total_selected_weight if total_selected_weight > 0 else 0
        
        # Check if it's possible to get out of probation
        can_get_out_of_probation = best_case_new_gpa >= min_required_gpa
        
        # Prepare result
        result = {
            'on_probation': True,
            'probation_counter': probation_counter,
            'current_cumulative_gpa': float(current_cumulative_gpa),
            'min_required_gpa': min_required_gpa,
            'can_get_out_of_probation': can_get_out_of_probation,
            'best_case_new_gpa': float(best_case_new_gpa),
            'min_term_gpa_needed': float(min_term_gpa_needed) if min_term_gpa_needed <= 4.0 else None
        }
        
        # Add appropriate message
        if can_get_out_of_probation:
            if min_term_gpa_needed <= 4.0:
                result['message'] = f"Your current selection can help you get out of probation if you achieve a term GPA of at least {min_term_gpa_needed:.2f} in these courses."
            else:
                result['message'] = f"Your current selection can help you get out of probation, but you would need to achieve a term GPA higher than 4.0, which is not possible. Consider taking more courses or using grade forgiveness if available."
        else:
            result['message'] = f"Your current selection is not enough to get you out of probation, even with perfect grades (4.0 GPA). The best you can achieve is a cumulative GPA of {best_case_new_gpa:.2f}, which is below the required {min_required_gpa:.2f}."
        
        return result
        
    except Exception as e:
        current_app.logger.error(f"Error in check_probation_impact: {str(e)}", exc_info=True)
        return {
            'on_probation': None,
            'error': f"An error occurred while analyzing probation impact: {str(e)}"
        }
    finally:
        if 'cursor' in locals():
            cursor.close()

@student_bp.route('/schedule/check-preferences', methods=['GET'])
@login_required
def check_preferences():
    """Check if the student has preferences in all three required tables."""
    try:
        # Get student ID from session
        student_id = session.get('student', {}).get('student_id')
        if not student_id:
            current_app.logger.error(f"Student ID not found in session: {session}")
            return jsonify({
                'success': False,
                'message': 'Student ID not found in session'
            }), 401

        current_app.logger.info(f"Checking preferences for student {student_id}")
        
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Check for priority preference
            cursor.execute(
                "SELECT COUNT(*) as count FROM priority_preferences WHERE student_id = %s",
                (student_id,)
            )
            result = cursor.fetchone()
            has_priority = result[0] > 0 if result else False
            current_app.logger.info(f"Priority preferences check: {has_priority}")

            # Check for professor preferences
            cursor.execute(
                "SELECT COUNT(*) as count FROM professor_preferences WHERE student_id = %s",
                (student_id,)
            )
            result = cursor.fetchone()
            has_professors = result[0] > 0 if result else False
            current_app.logger.info(f"Professor preferences check: {has_professors}")

            # Check for time slot preferences
            cursor.execute(
                "SELECT COUNT(*) as count FROM time_slot_preferences WHERE student_id = %s",
                (student_id,)
            )
            result = cursor.fetchone()
            has_timeslots = result[0] > 0 if result else False
            current_app.logger.info(f"Time slot preferences check: {has_timeslots}")

            # Return the results
            result = {
                'success': True,
                'has_all_preferences': has_priority and has_professors and has_timeslots,
                'preferences': {
                    'priority': has_priority,
                    'professors': has_professors,
                    'timeslots': has_timeslots
                }
            }
            current_app.logger.info(f"Preferences check result: {result}")
            return jsonify(result)

        finally:
            cursor.close()

    except Exception as e:
        current_app.logger.error(f"Error checking preferences: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

