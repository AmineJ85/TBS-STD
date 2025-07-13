from flask import Blueprint, jsonify, session, request, current_app
from datetime import datetime, date
import base64
from werkzeug.security import check_password_hash, generate_password_hash
from auth import admin_required
from functools import wraps
import re

admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin')

def check_admin_auth():
    """Check if admin is logged in"""
    admin = session.get('admin')
    if not admin:
        return None, jsonify({'success': False, 'message': 'Admin not logged in'}), 401
    return admin, None

def get_db_cursor():
    """Get database cursor"""
    return current_app.mysql.connection.cursor()

def handle_db_error(e, error_message):
    """Handle database errors"""
    current_app.logger.error(f"{error_message}: {str(e)}")
    return jsonify({
        'success': False,
        'message': error_message,
        'details': str(e)
    }), 500

def get_semester_name(semester_number):
    """Get semester name from number"""
    return 'Fall' if semester_number == 1 else 'Spring'

def check_active_semester(cursor):
    """Check if there's an active semester"""
    cursor.execute("""
        SELECT 1 FROM academic_calendar 
        WHERE is_current = 1 AND end_date IS NULL
    """)
    return cursor.fetchone() is not None

def validate_registration_dates(start_date, end_date):
    """Validate registration start and end dates"""
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
        end_date = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')

        now = datetime.now()
        if end_date < now:
            return None, jsonify({'success': False, 'message': 'End date must be in the future'}), 400

        if start_date >= end_date:
            return None, jsonify({'success': False, 'message': 'Start date must be before end date'}), 400

        return (start_date, end_date), None

    except ValueError as e:
        current_app.logger.error(f"Invalid date format: {str(e)}")
        return None, jsonify({'success': False, 'message': 'Invalid date format. Use YYYY-MM-DD HH:MM:SS'}), 400

def get_registration_status(cursor):
    """Get current registration status"""
    # Check for scheduled registrations that should be activated
    cursor.execute("""
        UPDATE registration_config 
        SET status = 'open'
        WHERE status = 'scheduled' 
        AND start_date <= NOW()
    """)
    current_app.mysql.connection.commit()
    
    # Check for open registrations that should be auto-closed
    cursor.execute("""
        UPDATE registration_config 
        SET status = 'closed',
            closed_at = NOW(),
            closed_by_admin = NULL
        WHERE status = 'open' 
        AND end_date <= NOW()
    """)
    current_app.mysql.connection.commit()
    
    # Get current active registration
    cursor.execute("""
        SELECT status, start_date, end_date 
        FROM registration_config 
        WHERE status IN ('open', 'scheduled')
        ORDER BY end_date DESC
        LIMIT 1
    """)
    
    result = cursor.fetchone()
    
    if result:
        status, start_date, end_date = result
        return {
            'success': True,
            'is_open': status == 'open',
            'is_scheduled': status == 'scheduled',
            'start_date': start_date.strftime('%Y-%m-%d %H:%M:%S') if start_date else None,
            'end_date': end_date.strftime('%Y-%m-%d %H:%M:%S') if end_date else None
        }
    else:
        return {
            'success': True,
            'is_open': False,
            'is_scheduled': False
        }

def start_registration(cursor, admin_id, start_date, end_date):
    """Start a new registration period"""
    cursor.execute("UPDATE registration_config SET status = 'closed' WHERE status IN ('open', 'scheduled')")
    
    status = 'scheduled' if start_date > datetime.now() else 'open'
    
    cursor.execute("""
        INSERT INTO registration_config (start_date, end_date, status, opened_by_admin, opened_at)
        VALUES (%s, %s, %s, %s, NOW())
    """, (start_date, end_date, status, admin_id))
    
    current_app.mysql.connection.commit()
    
    return {
        'success': True,
        'message': f'Registration {"scheduled" if status == "scheduled" else "opened"} successfully',
        'start_date': start_date.strftime('%Y-%m-%d %H:%M:%S'),
        'end_date': end_date.strftime('%Y-%m-%d %H:%M:%S'),
        'is_scheduled': status == 'scheduled'
    }

def activate_registration(cursor):
    """Activate a scheduled registration"""
    cursor.execute("""
        UPDATE registration_config
        SET status = 'open'
        WHERE status = 'scheduled'
        AND start_date <= NOW()
    """)
    
    affected = cursor.rowcount
    current_app.mysql.connection.commit()
    
    if affected == 0:
        return None, jsonify({'success': False, 'message': 'No scheduled registration to activate'}), 400
    
    cursor.execute("""
        SELECT start_date, end_date 
        FROM registration_config 
        WHERE status = 'open'
        ORDER BY end_date DESC
        LIMIT 1
    """)
    result = cursor.fetchone()
    
    if result:
        start_date, end_date = result
        return {
            'success': True,
            'message': 'Scheduled registration activated successfully',
            'start_date': start_date.strftime('%Y-%m-%d %H:%M:%S'),
            'end_date': end_date.strftime('%Y-%m-%d %H:%M:%S')
        }
    else:
        return {'success': True, 'message': 'Scheduled registration activated successfully'}

def close_registration(cursor, admin_id):
    """Close an active registration"""
    # Add logging to help diagnose the issue
    current_app.logger.info(f"Closing registration with admin_id={admin_id}")
    
    cursor.execute("""
        UPDATE registration_config
        SET status = 'closed',
            closed_at = NOW(),
            closed_by_admin = %s
        WHERE status = 'open'
    """, (admin_id,))
    
    affected = cursor.rowcount
    current_app.logger.info(f"Rows affected by close_registration: {affected}")
    current_app.mysql.connection.commit()
    
    if affected == 0:
        current_app.logger.warning("No active registration to close")
        return None, jsonify({'success': False, 'message': 'No active registration to close'}), 400
    
    current_app.logger.info("Registration closed successfully")
    return {'success': True, 'message': 'Registration closed successfully'}

def cancel_registration(cursor, admin_id):
    """Cancel a scheduled registration"""
    # Add logging to help diagnose the issue
    current_app.logger.info(f"Canceling scheduled registration with admin_id={admin_id}")
    
    cursor.execute("""
        UPDATE registration_config
        SET status = 'closed',
            closed_at = NOW(),
            closed_by_admin = %s
        WHERE status = 'scheduled'
    """, (admin_id,))
    
    affected = cursor.rowcount
    current_app.logger.info(f"Rows affected by cancel_registration: {affected}")
    current_app.mysql.connection.commit()
    
    if affected == 0:
        current_app.logger.warning("No scheduled registration to cancel")
        return None, jsonify({'success': False, 'message': 'No scheduled registration to cancel'}), 400
    
    current_app.logger.info("Scheduled registration cancelled successfully")
    return {'success': True, 'message': 'Scheduled registration cancelled successfully'}

def check_incomplete_grades(cursor):
    """
    Check if there are students with:
    1. Courses with status 'enrolled'
    2. Courses with status 'passed' or 'failed' but missing letter_grade or grade_point
       (except for courses with letter_grade 'P' or 'TC' which are allowed)
    
    Returns:
    - If issues found: list of dictionaries with student information
    - If no issues: empty list
    """
    cursor.execute("""
        SELECT DISTINCT s.student_id, s.first_name, s.last_name, s.national_id, a.status, a.course_code,
            a.letter_grade, a.grade_point
        FROM add_course a
        JOIN student s ON a.student_id = s.student_id
        WHERE 
            (a.status = 'enrolled')
            OR
            (a.status IN ('passed', 'failed') 
             AND (a.letter_grade IS NULL OR a.letter_grade = '' OR 
                 (a.grade_point IS NULL AND (a.letter_grade != 'P' AND a.letter_grade != 'TC'))))
        ORDER BY s.student_id
    """)
    
    results = cursor.fetchall()
    
    if not results:
        return []
    
    students_with_issues = []
    for row in results:
        student_id, first_name, last_name, national_id, status, course_code, letter_grade, grade_point = row
        issue_type = "enrolled status" if status == "enrolled" else "missing grade"
        
        students_with_issues.append({
            "student_id": student_id,
            "first_name": first_name,
            "last_name": last_name,
            "national_id": national_id,
            "issue_type": issue_type,
            "course_code": course_code
        })
    
    return students_with_issues

def check_for_graduates(cursor):
    """
    Check for students who meet graduation requirements:
    1. No more 'notenrolled' courses
    2. No failed courses (except those taken under forgiveness)
    3. Cumulative earned credits >= minimum_grad_credit
    4. Cumulative GPA >= minimum_grad_cgpa
    5. Has a declared major
    6. Is at least in year 4 of study
    7. Has at least one course with coefficient >= 6 if single major
    8. Has at least two distinct courses with coefficient >= 6 if double major
    
    Returns:
    - List of student IDs who meet graduation requirements
    """
    # Get graduation requirements from system parameters
    cursor.execute("""
        SELECT minimum_grad_credit, minimum_grad_cgpa
        FROM system_parameters
        LIMIT 1
    """)
    
    params = cursor.fetchone()
    if not params:
        current_app.logger.error("Failed to retrieve system parameters for graduation check")
        return []
    
    min_credits, min_cgpa = params
    
    # Find students who meet graduation requirements
    cursor.execute("""
        WITH LastCourseStatus AS (
            -- Get the last status for each course for each student
            SELECT 
                ac1.student_id,
                ac1.course_code,
                ac1.status,
                ac1.forgiveness
            FROM add_course ac1
            INNER JOIN (
                SELECT student_id, course_code, MAX(id) as max_id
                FROM add_course
                GROUP BY student_id, course_code
            ) ac2 ON ac1.id = ac2.max_id
        ),
        FailedCourses AS (
            -- Find students with failed courses (excluding forgiveness)
            SELECT DISTINCT student_id
            FROM LastCourseStatus
            WHERE status = 'failed' AND forgiveness = 0
        ),
        NotEnrolledCourses AS (
            -- Find students with 'notenrolled' courses
            SELECT DISTINCT student_id
            FROM LastCourseStatus
            WHERE status = 'notenrolled'
        ),
        HighCoefficientCourses AS (
            -- Find passed courses with coefficient >= 6 for each student
            SELECT 
                ac.student_id,
                ac.course_code,
                c.coefficient
            FROM LastCourseStatus ac
            JOIN courses c ON ac.course_code = c.course_code
            WHERE 
                ac.status = 'passed' AND 
                c.coefficient >= 6
        ),
        HighCoefficientCounts AS (
            -- Count high coefficient courses per student
            SELECT 
                student_id,
                COUNT(DISTINCT course_code) AS high_coef_course_count
            FROM HighCoefficientCourses
            GROUP BY student_id
        ),
        EligibleStudents AS (
            -- Find students who meet all academic requirements
            SELECT 
                s.student_id,
                s.first_name,
                s.last_name
            FROM student s
            JOIN student_semester_summary sss ON s.student_id = sss.student_id
            LEFT JOIN HighCoefficientCounts hcc ON s.student_id = hcc.student_id
            WHERE 
                -- Must have a major
                s.major IS NOT NULL AND s.major != '' AND
                -- Must be at least in year 4
                s.year_of_study >= 4 AND
                -- Must have enrollment status 'enrolled'
                s.enrollment_status = 'enrolled' AND
                -- Get the latest semester summary record for each student
                sss.record_id = (
                    SELECT MAX(record_id) 
                    FROM student_semester_summary 
                    WHERE student_id = s.student_id
                ) AND
                -- Must meet minimum credits requirement
                sss.cumulative_earned_credits >= %s AND
                -- Must meet minimum CGPA requirement
                sss.cumulative_gpa >= %s AND
                -- Must not have failed courses (except forgiveness)
                s.student_id NOT IN (SELECT student_id FROM FailedCourses) AND
                -- Must not have 'notenrolled' courses
                s.student_id NOT IN (SELECT student_id FROM NotEnrolledCourses) AND
                -- Must have enough high coefficient courses based on major count
                (
                    -- If single major: at least 1 high coefficient course
                    (s.second_major IS NULL OR s.second_major = '' AND COALESCE(hcc.high_coef_course_count, 0) >= 1)
                    OR
                    -- If double major: at least 2 high coefficient courses
                    (s.second_major IS NOT NULL AND s.second_major != '' AND COALESCE(hcc.high_coef_course_count, 0) >= 2)
                )
        )
        SELECT student_id, first_name, last_name
        FROM EligibleStudents
    """, (min_credits, min_cgpa))
    
    graduates = cursor.fetchall()
    
    # Update student status to 'graduated' for eligible students
    if graduates:
        graduate_ids = [g[0] for g in graduates]
        
        # Update student enrollment status to 'graduated'
        placeholders = ', '.join(['%s'] * len(graduate_ids))
        cursor.execute(f"""
            UPDATE student
            SET enrollment_status = 'graduated'
            WHERE student_id IN ({placeholders})
        """, graduate_ids)
        
        current_app.mysql.connection.commit()
        
        # Log the graduates
        graduate_info = [{'student_id': g[0], 'name': f"{g[1]} {g[2]}"} for g in graduates]
        current_app.logger.info(f"Updated {len(graduate_ids)} students to graduated status: {graduate_info}")
        
        return graduate_info
    
    return []

@admin_bp.route('/course_registration', methods=['GET', 'POST'])
def course_registration():
    """Single endpoint handling ALL admin operations"""
    admin = session.get('admin')
    if not admin:
        return jsonify({'success': False, 'message': 'Admin not logged in'}), 401

    cursor = None
    try:
        cursor = current_app.mysql.connection.cursor()

        if request.method == 'GET':
            section = request.args.get('section')
            
            if section == 'semester_status':
                # Get current semester
                cursor.execute("""
                    SELECT calendar_id, academic_year, semester, start_date, end_date, is_current
                    FROM academic_calendar
                    WHERE is_current = 1
                    ORDER BY start_date DESC
                    LIMIT 1
                """)
                
                current_semester = cursor.fetchone()
                
                if current_semester:
                    calendar_id, academic_year, semester, start_date, end_date, is_current = current_semester
                    current_semester_data = {
                        'calendar_id': calendar_id,
                        'academic_year': academic_year,
                        'semester': semester,
                        'start_date': start_date.strftime('%Y-%m-%d') if start_date else None,
                        'end_date': end_date.strftime('%Y-%m-%d') if end_date else None,
                        'is_current': bool(is_current)
                    }
                else:
                    current_semester_data = None
                
                # Get last semester to determine next semester number
                cursor.execute("""
                    SELECT academic_year, semester 
                    FROM academic_calendar 
                    ORDER BY academic_year DESC, semester DESC 
                    LIMIT 1
                """)
                last_semester = cursor.fetchone()
                
                next_semester = 1
                
                if last_semester:
                    last_year, last_semester_num = last_semester
                    next_semester = 2 if last_semester_num == 1 else 1
                    current_year = last_year
                    
                    # If we're ending semester 2, next semester should be 1 of next year
                    if last_semester_num == 2 and current_semester_data and current_semester_data['end_date']:
                        current_year += 1
                
                return jsonify({
                    'success': True,
                    'current_semester': current_semester_data,
                    'next_semester': next_semester,
                    'next_year': current_year
                })

            elif section == 'course-registration':
                # Check for scheduled registrations that should be activated
                cursor.execute("""
                    UPDATE registration_config 
                    SET status = 'open'
                    WHERE status = 'scheduled' 
                    AND start_date <= NOW()
                """)
                current_app.mysql.connection.commit()
                
                # Check for open registrations that should be auto-closed
                cursor.execute("""
                    UPDATE registration_config 
                    SET status = 'closed',
                        closed_at = NOW(),
                        closed_by_admin = NULL
                    WHERE status = 'open' 
                    AND end_date <= NOW()
                """)
                current_app.mysql.connection.commit()
                
                # Get current active registration
                cursor.execute("""
                    SELECT status, start_date, end_date 
                    FROM registration_config 
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
            
            elif section == 'major-minor-validation':
                return jsonify({
                    'success': True,
                    'section': 'major-minor-validation',
                    'title': 'Major/Minor Validation'
                })
            
            elif section == 'system-adjustments':
                return jsonify({
                    'success': True,
                    'section': 'system-adjustments',
                    'title': 'System Adjustments'
                })
            
            elif section == 'statistics':
                return jsonify({
                    'success': True,
                    'section': 'statistics',
                    'title': 'Statistics'
                })
            
            else:
                return jsonify({
                    'success': True,
                    'section': section,
                    'title': section.replace('-', ' ').title() if section else 'Admin Dashboard',
                    'content': f'This is placeholder content for {section.replace("-", " ").title() if section else "Admin Dashboard"}.'
                })

        elif request.method == 'POST':
            data = request.json
            action = data.get('action')

            if not action:
                return jsonify({'success': False, 'message': 'Action is required'}), 400

            if action == 'set_current_section':
                section = data.get('section')
                if section:
                    session['current_section'] = section
                    return jsonify({'success': True})
                return jsonify({'success': False, 'message': 'No section provided'}), 400

            elif action == 'manage_semester':
                action_type = data.get('type')  # 'start' or 'end'
                admin_id = admin.get('admin_id')


                if action_type == 'start':
                    # First check if there's already an active semester
                    cursor.execute("""
                        SELECT 1 FROM academic_calendar 
                        WHERE is_current = 1 AND end_date IS NULL
                    """)
                    if cursor.fetchone():
                        return jsonify({
                            'success': False,
                            'message': 'There is already an active semester'
                        }), 400

                    # Get the most recent semester (regardless of status)
                    cursor.execute("""
                        SELECT academic_year, semester 
                        FROM academic_calendar 
                        ORDER BY academic_year DESC, semester DESC 
                        LIMIT 1
                    """)
                    last_semester = cursor.fetchone()
                    
                    if last_semester:
                        last_year, last_semester_num = last_semester
                        # Determine next semester and year
                        if last_semester_num == 1:
                            next_semester = 2
                            next_year = last_year
                        else:  # last_semester_num == 2
                            next_semester = 1
                            next_year = last_year + 1
                    else:
                        # No semesters exist yet, start with Fall (1) of current year
                        next_semester = 1
                        next_year = date.today().year

                    # Verify this semester doesn't already exist
                    cursor.execute("""
                        SELECT 1 FROM academic_calendar 
                        WHERE academic_year = %s AND semester = %s
                    """, (next_year, next_semester))
                    if cursor.fetchone():
                        return jsonify({
                            'success': False,
                            'message': f'Semester {get_semester_name(next_semester)}, {next_year} already exists'
                        }), 400

                    # Mark all other semesters as not current
                    cursor.execute("UPDATE academic_calendar SET is_current = 0")
                    
                    # Start new semester
                    cursor.execute("""
                        INSERT INTO academic_calendar 
                        (academic_year, semester, start_date, is_current)
                        VALUES (%s, %s, CURDATE(), 1)
                    """, (next_year, next_semester))
                    current_app.mysql.connection.commit()
                    
                    # If transitioning from Spring to Fall, increment student years
                    if last_semester and last_semester_num == 2 and next_semester == 1:
                        # Don't increment students who are in their first year AND have no grades yet
                        # Also don't increment graduated students
                        cursor.execute("""
                            UPDATE student 
                            SET year_of_study = year_of_study + 1
                            WHERE year_of_study IS NOT NULL 
                            AND enrollment_status != 'dismissed'
                            AND enrollment_status != 'graduated'
                            AND (
                                -- Either not a first-year student
                                year_of_study > 1
                                OR 
                                -- OR a first-year with actual grades
                                (year_of_study = 1 AND student_id IN (
                                    SELECT student_id 
                                    FROM student_semester_summary 
                                    WHERE cumulative_gpa IS NOT NULL
                                ))
                            )
                        """)
                        
                        rows_updated = cursor.rowcount
                        current_app.mysql.connection.commit()
                        
                        # Log the year increment
                        current_app.logger.info(
                            f"Incremented academic year for {rows_updated} students (new year: {next_year})"
                        )
                    
                    # Create new student_semester_summary entries for all students
                    current_app.logger.info("Creating new student_semester_summary entries for all students")
                    
                    # First, get the min_cumulative_gpa value for logging
                    cursor.execute("SELECT min_cumulative_gpa FROM system_parameters ORDER BY last_updated DESC LIMIT 1")
                    min_gpa_result = cursor.fetchone()
                    min_cumulative_gpa = min_gpa_result[0] if min_gpa_result else None
                    current_app.logger.info(f"Current min_cumulative_gpa threshold: {min_cumulative_gpa}")
                    
                    # Log academic years for some students
                    cursor.execute("SELECT student_id, year_of_study FROM student LIMIT 5")
                    sample_students = cursor.fetchall()
                    current_app.logger.info(f"Sample student academic years: {sample_students}")
                    
                    cursor.execute("""
                        INSERT INTO student_semester_summary 
                        (student_id, year, semester, 
                        cumulative_registered_credits, cumulative_earned_credits, cumulative_gpa,
                        probation_counter, forgiveness_counter,
                        acct_gpa, ba_gpa, fin_gpa, it_gpa, mrk_gpa)
                        SELECT 
                            s.student_id,
                            s.year_of_study AS year,
                            %s AS semester,
                            COALESCE(prev.cumulative_registered_credits, 0) AS cumulative_registered_credits,
                            COALESCE(prev.cumulative_earned_credits, 0) AS cumulative_earned_credits,
                            prev.cumulative_gpa,
                            CASE
                                WHEN prev.cumulative_gpa IS NULL THEN 0
                                WHEN prev.cumulative_gpa < (SELECT min_cumulative_gpa FROM system_parameters ORDER BY last_updated DESC LIMIT 1)
                                    THEN COALESCE(prev.probation_counter, 0) + 1
                                ELSE 0
                            END AS probation_counter,
                            COALESCE(prev.forgiveness_counter, 0) AS forgiveness_counter,
                            NULL AS acct_gpa,
                            NULL AS ba_gpa,
                            NULL AS fin_gpa,
                            NULL AS it_gpa,
                            NULL AS mrk_gpa
                        FROM 
                            student s
                        LEFT JOIN (
                            SELECT 
                                sss.student_id,
                                sss.cumulative_registered_credits,
                                sss.cumulative_earned_credits,
                                sss.cumulative_gpa,
                                sss.probation_counter,
                                sss.forgiveness_counter
                            FROM 
                                student_semester_summary sss
                            INNER JOIN (
                                SELECT 
                                    student_id,
                                    MAX(year * 10 + semester) AS max_year_sem
                                FROM 
                                    student_semester_summary
                                GROUP BY 
                                    student_id
                            ) latest ON sss.student_id = latest.student_id 
                              AND (sss.year * 10 + sss.semester) = latest.max_year_sem
                        ) AS prev ON s.student_id = prev.student_id
                        WHERE s.year_of_study IS NOT NULL
                        AND s.enrollment_status != 'dismissed'
                        AND s.enrollment_status != 'graduated'
                        ON DUPLICATE KEY UPDATE
                            cumulative_registered_credits = VALUES(cumulative_registered_credits),
                            cumulative_earned_credits = VALUES(cumulative_earned_credits),
                            cumulative_gpa = VALUES(cumulative_gpa),
                            probation_counter = VALUES(probation_counter),
                            forgiveness_counter = COALESCE(student_semester_summary.forgiveness_counter, VALUES(forgiveness_counter))
                    """, (next_semester,))
                    
                    records_inserted = cursor.rowcount
                    current_app.mysql.connection.commit()
                    
                    # Log some of the inserted records to verify correct years
                    cursor.execute("""
                        SELECT student_id, year, semester FROM student_semester_summary
                        WHERE semester = %s
                        ORDER BY student_id
                        LIMIT 5
                    """, (next_semester,))
                    sample_records = cursor.fetchall()
                    current_app.logger.info(f"Sample inserted records (student_id, year, semester): {sample_records}")
                    
                    # Log students who got probation increments
                    cursor.execute("""
                        SELECT COUNT(*) FROM student_semester_summary 
                        WHERE year = %s AND semester = %s AND probation_counter > 0
                    """, (next_year, next_semester))
                    probation_count = cursor.fetchone()[0]
                    
                    current_app.logger.info(f"Created {records_inserted} student_semester_summary entries for semester {next_semester}, year {next_year}")
                    current_app.logger.info(f"Students on probation this semester: {probation_count}")
                    
                    # Check for students who reached max probation limit and need board review
                    # Note: This check also happens in student.py:is_awaiting_board_decision for real-time checks
                    current_app.logger.info("Checking for students who reached max probation limit...")
                    cursor.execute("""
                        WITH MaxProbationValues AS (
                            SELECT 
                                s.student_id,
                                COALESCE(spo.max_probation_board, sp.max_probation_board) AS max_probation_board
                            FROM 
                                student s
                            CROSS JOIN (
                                SELECT * FROM system_parameters ORDER BY last_updated DESC LIMIT 1
                            ) sp
                            LEFT JOIN 
                                student_parameters_overrides spo ON s.student_id = spo.student_id
                        )
                        SELECT 
                            sss.student_id,
                            sss.probation_counter,
                            mpv.max_probation_board
                        FROM 
                            student_semester_summary sss
                        JOIN 
                            MaxProbationValues mpv ON sss.student_id = mpv.student_id
                        WHERE 
                            sss.year = %s 
                            AND sss.semester = %s
                            AND sss.probation_counter >= mpv.max_probation_board
                            AND NOT EXISTS (
                                SELECT 1 FROM board_probation_extension bpe
                                WHERE bpe.student_id = sss.student_id
                                AND bpe.status = 'pending'
                            )
                    """, (next_year, next_semester))
                    
                    students_at_max_probation = cursor.fetchall()
                    
                    if students_at_max_probation:
                        current_app.logger.info(f"Found {len(students_at_max_probation)} students who reached max probation limit")
                        
                        # Create board_probation_extension entries for these students
                        for student in students_at_max_probation:
                            student_id = student[0]
                            
                            # First delete any existing pending requests for this student
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
                        current_app.logger.info(f"Created {len(students_at_max_probation)} board_probation_extension entries")
                    else:
                        current_app.logger.info("No students found who reached max probation limit")
                    
                    # Get the newly created semester
                    cursor.execute("""
                        SELECT calendar_id, academic_year, semester, start_date, end_date, is_current
                        FROM academic_calendar
                        WHERE is_current = 1
                        ORDER BY start_date DESC
                        LIMIT 1
                    """)
                    new_semester = cursor.fetchone()
                    
                    calendar_id, academic_year, semester, start_date, end_date, is_current = new_semester
                    
                    return jsonify({
                        'success': True,
                        'message': f'Semester: {get_semester_name(semester)}, {academic_year} has started successfully',
                        'data': {
                            'current_semester': {
                                'calendar_id': calendar_id,
                                'academic_year': academic_year,
                                'semester': semester,
                                'start_date': start_date.strftime('%Y-%m-%d'),
                                'end_date': end_date.strftime('%Y-%m-%d') if end_date else None,
                                'is_current': bool(is_current)
                            }
                        }
                    })
                    
                elif action_type == 'end':
                    # Get current semester
                    cursor.execute("""
                        SELECT calendar_id, academic_year, semester, start_date
                        FROM academic_calendar 
                        WHERE is_current = 1 
                        AND end_date IS NULL
                        ORDER BY start_date DESC 
                        LIMIT 1
                    """)
                    
                    current_semester = cursor.fetchone()
                    
                    if not current_semester:
                        return jsonify({'success': False, 'message': 'No active semester to end'}), 400
                        
                    calendar_id, academic_year, semester, start_date = current_semester
                    
                    # Check for students with incomplete grades or enrolled courses
                    students_with_issues = check_incomplete_grades(cursor)
                    if students_with_issues:
                        # If there are issues, return an error with the students list
                        return jsonify({
                            'success': False, 
                            'message': 'Cannot end semester - students with incomplete grades or enrolled courses',
                            'error_type': 'incomplete_grades',
                            'students': students_with_issues
                        }), 400
                    
                    # Close any active registration periods
                    cursor.execute("""
                        UPDATE registration_config 
                        SET status = 'closed',
                            closed_at = NOW(),
                            closed_by_admin = %s
                        WHERE status IN ('open', 'scheduled')
                    """, (admin_id,))
                    
                    # End current semester
                    cursor.execute("""
                        UPDATE academic_calendar 
                        SET end_date = CURDATE(),
                            is_current = 0
                        WHERE calendar_id = %s
                    """, (calendar_id,))
                    
                    # Check for graduates and update their status
                    graduates = check_for_graduates(cursor)
                    
                    # Update student levels based on completed courses
                    cursor.execute("""
                        WITH PassedCourses AS (
                            SELECT DISTINCT student_id, course_code
                            FROM add_course
                            WHERE status = 'passed'
                        ),
                        Year1NonFrenchCourses AS (
                            SELECT course_code
                            FROM courses
                            WHERE year = 1
                            AND course_code NOT IN ('NBC 110', 'NBC 130')
                        ),
                        Year1AllCourses AS (
                            SELECT course_code
                            FROM courses
                            WHERE year = 1
                        ),
                        Year2NonFrenchCourses AS (
                            SELECT course_code
                            FROM courses
                            WHERE year = 2
                            AND course_code NOT IN ('NBC 110', 'NBC 130')
                        ),
                        Year2AllCourses AS (
                            SELECT course_code
                            FROM courses
                            WHERE year = 2
                        ),
                        EligibleStudents AS (
                            SELECT 
                                student.student_id,
                                CASE
                                    WHEN (
                                        student.non_french = 1 
                                        AND NOT EXISTS (
                                            SELECT 1 FROM Year1NonFrenchCourses y1
                                            WHERE NOT EXISTS (
                                                SELECT 1 FROM PassedCourses pc
                                                WHERE pc.student_id = student.student_id 
                                                AND pc.course_code = y1.course_code
                                            )
                                        )
                                        AND NOT EXISTS (
                                            SELECT 1 FROM Year2NonFrenchCourses y2
                                            WHERE NOT EXISTS (
                                                SELECT 1 FROM PassedCourses pc
                                                WHERE pc.student_id = student.student_id 
                                                AND pc.course_code = y2.course_code
                                            )
                                        )
                                    ) THEN 'Junior'
                                    WHEN (
                                        student.non_french = 0 
                                        AND NOT EXISTS (
                                            SELECT 1 FROM Year1AllCourses y1
                                            WHERE NOT EXISTS (
                                                SELECT 1 FROM PassedCourses pc
                                                WHERE pc.student_id = student.student_id 
                                                AND pc.course_code = y1.course_code
                                            )
                                        )
                                        AND NOT EXISTS (
                                            SELECT 1 FROM Year2AllCourses y2
                                            WHERE NOT EXISTS (
                                                SELECT 1 FROM PassedCourses pc
                                                WHERE pc.student_id = student.student_id 
                                                AND pc.course_code = y2.course_code
                                            )
                                        )
                                    ) THEN 'Junior'
                                    WHEN (
                                        student.non_french = 1 
                                        AND NOT EXISTS (
                                            SELECT 1 FROM Year1NonFrenchCourses y1
                                            WHERE NOT EXISTS (
                                                SELECT 1 FROM PassedCourses pc
                                                WHERE pc.student_id = student.student_id 
                                                AND pc.course_code = y1.course_code
                                            )
                                        )
                                    ) THEN 'Sophomore'
                                    WHEN (
                                        student.non_french = 0 
                                        AND NOT EXISTS (
                                            SELECT 1 FROM Year1AllCourses y1
                                            WHERE NOT EXISTS (
                                                SELECT 1 FROM PassedCourses pc
                                                WHERE pc.student_id = student.student_id 
                                                AND pc.course_code = y1.course_code
                                            )
                                        )
                                    ) THEN 'Sophomore'
                                    ELSE 'Freshman'
                                END as new_level
                            FROM student
                        )
                        UPDATE student
                        JOIN EligibleStudents ON student.student_id = EligibleStudents.student_id
                        SET student.level = EligibleStudents.new_level
                    """)
                    
                    current_app.mysql.connection.commit()
                    
                    return jsonify({
                        'success': True,
                        'message': f'Semester: {get_semester_name(semester)}, {academic_year} has ended successfully',
                        'data': {
                            'current_semester': {
                                'calendar_id': calendar_id,
                                'academic_year': academic_year,
                                'semester': semester,
                                'start_date': start_date.strftime('%Y-%m-%d'),
                                'end_date': date.today().strftime('%Y-%m-%d')
                            },
                            'graduates': graduates if graduates else None
                        }
                    })

            elif action == 'start_registration':
                # Check if there's an active semester
                cursor.execute("""
                    SELECT 1 FROM academic_calendar 
                    WHERE is_current = 1 AND end_date IS NULL
                """)
                if not cursor.fetchone():
                    return jsonify({'success': False, 'message': 'Cannot open registration - no active semester'}), 400

                start_date = data.get('start_date')
                end_date = data.get('end_date')

                if not start_date or not end_date:
                    return jsonify({'success': False, 'message': 'Start date and end date are required'}), 400

                try:
                    start_date = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
                    end_date = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')

                    now = datetime.now()
                    if end_date < now:
                        return jsonify({'success': False, 'message': 'End date must be in the future'}), 400

                    if start_date >= end_date:
                        return jsonify({'success': False, 'message': 'Start date must be before end date'}), 400

                except ValueError as e:
                    current_app.logger.error(f"Invalid date format: {str(e)}")
                    return jsonify({'success': False, 'message': 'Invalid date format. Use YYYY-MM-DD HH:MM:SS'}), 400

                cursor.execute("UPDATE registration_config SET status = 'closed' WHERE status IN ('open', 'scheduled')")
                
                status = 'scheduled' if start_date > datetime.now() else 'open'
                
                cursor.execute("""
                    INSERT INTO registration_config (start_date, end_date, status, opened_by_admin, opened_at)
                    VALUES (%s, %s, %s, %s, NOW())
                """, (start_date, end_date, status, admin['admin_id']))
                
                current_app.mysql.connection.commit()
                
                return jsonify({
                    'success': True,
                    'message': f'Registration {"scheduled" if status == "scheduled" else "opened"} successfully',
                    'start_date': start_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'end_date': end_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'is_scheduled': status == 'scheduled'
                })

            elif action == 'activate_registration':
                cursor.execute("""
                    UPDATE registration_config
                    SET status = 'open'
                    WHERE status = 'scheduled'
                    AND start_date <= NOW()
                """)
                
                affected = cursor.rowcount
                current_app.mysql.connection.commit()
                
                if affected == 0:
                    return jsonify({'success': False, 'message': 'No scheduled registration to activate'}), 400
                
                cursor.execute("""
                    SELECT start_date, end_date 
                    FROM registration_config 
                    WHERE status = 'open'
                    ORDER BY end_date DESC
                    LIMIT 1
                """)
                result = cursor.fetchone()
                
                if result:
                    start_date, end_date = result
                    return jsonify({
                        'success': True,
                        'message': 'Scheduled registration activated successfully',
                        'start_date': start_date.strftime('%Y-%m-%d %H:%M:%S'),
                        'end_date': end_date.strftime('%Y-%m-%d %H:%M:%S')
                    })
                else:
                    return jsonify({'success': True, 'message': 'Scheduled registration activated successfully'})

            elif action == 'close_registration':
                result = close_registration(cursor, admin['admin_id'])
                if isinstance(result, tuple) and len(result) == 3:
                    # This means an error was returned
                    return result[1]  # Return the jsonify response
                return jsonify(result)

            elif action == 'cancel_registration':
                result = cancel_registration(cursor, admin['admin_id'])
                if isinstance(result, tuple) and len(result) == 3:
                    # This means an error was returned
                    return result[1]  # Return the jsonify response
                return jsonify(result)

            elif action == 'end_semester':
                # Check if there's an active semester
                cursor.execute("""
                    SELECT calendar_id, academic_year, semester, start_date 
                    FROM academic_calendar 
                    WHERE is_current = 1 AND end_date IS NULL
                """)
                
                current_semester = cursor.fetchone()
                
                if not current_semester:
                    return jsonify({'success': False, 'message': 'No active semester to end'}), 400
                    
                calendar_id, academic_year, semester, start_date = current_semester
                
                # Check for students with incomplete grades or enrolled courses
                students_with_issues = check_incomplete_grades(cursor)
                if students_with_issues:
                    # If there are issues, return an error with the students list
                    return jsonify({
                        'success': False, 
                        'message': 'Cannot end semester - students with incomplete grades or enrolled courses',
                        'error_type': 'incomplete_grades',
                        'students': students_with_issues
                    }), 400
                
                # Close any active registration periods
                cursor.execute("""
                    UPDATE registration_config 
                    SET status = 'closed',
                        closed_at = NOW(),
                        closed_by_admin = %s
                    WHERE status IN ('open', 'scheduled')
                """, (admin_id,))
                
                # End current semester
                cursor.execute("""
                    UPDATE academic_calendar 
                    SET end_date = CURDATE(),
                        is_current = 0
                    WHERE calendar_id = %s
                """, (calendar_id,))
                
                # Check for graduates and update their status
                graduates = check_for_graduates(cursor)
                
                # Update student levels based on completed courses
                cursor.execute("""
                    WITH PassedCourses AS (
                        SELECT DISTINCT student_id, course_code
                        FROM add_course
                        WHERE status = 'passed'
                    ),
                    Year1NonFrenchCourses AS (
                        SELECT course_code
                        FROM courses
                        WHERE year = 1
                        AND course_code NOT IN ('NBC 110', 'NBC 130')
                    ),
                    Year1AllCourses AS (
                        SELECT course_code
                        FROM courses
                        WHERE year = 1
                    ),
                    Year2NonFrenchCourses AS (
                        SELECT course_code
                        FROM courses
                        WHERE year = 2
                        AND course_code NOT IN ('NBC 110', 'NBC 130')
                    ),
                    Year2AllCourses AS (
                        SELECT course_code
                        FROM courses
                        WHERE year = 2
                    ),
                    EligibleStudents AS (
                        SELECT 
                            student.student_id,
                            CASE
                                WHEN (
                                    student.non_french = 1 
                                    AND NOT EXISTS (
                                        SELECT 1 FROM Year1NonFrenchCourses y1
                                        WHERE NOT EXISTS (
                                            SELECT 1 FROM PassedCourses pc
                                            WHERE pc.student_id = student.student_id 
                                            AND pc.course_code = y1.course_code
                                        )
                                    )
                                    AND NOT EXISTS (
                                        SELECT 1 FROM Year2NonFrenchCourses y2
                                        WHERE NOT EXISTS (
                                            SELECT 1 FROM PassedCourses pc
                                            WHERE pc.student_id = student.student_id 
                                            AND pc.course_code = y2.course_code
                                        )
                                    )
                                ) THEN 'Junior'
                                WHEN (
                                    student.non_french = 0 
                                    AND NOT EXISTS (
                                        SELECT 1 FROM Year1AllCourses y1
                                        WHERE NOT EXISTS (
                                            SELECT 1 FROM PassedCourses pc
                                            WHERE pc.student_id = student.student_id 
                                            AND pc.course_code = y1.course_code
                                        )
                                    )
                                    AND NOT EXISTS (
                                        SELECT 1 FROM Year2AllCourses y2
                                        WHERE NOT EXISTS (
                                            SELECT 1 FROM PassedCourses pc
                                            WHERE pc.student_id = student.student_id 
                                            AND pc.course_code = y2.course_code
                                        )
                                    )
                                ) THEN 'Junior'
                                WHEN (
                                    student.non_french = 1 
                                    AND NOT EXISTS (
                                        SELECT 1 FROM Year1NonFrenchCourses y1
                                        WHERE NOT EXISTS (
                                            SELECT 1 FROM PassedCourses pc
                                            WHERE pc.student_id = student.student_id 
                                            AND pc.course_code = y1.course_code
                                        )
                                    )
                                ) THEN 'Sophomore'
                                WHEN (
                                    student.non_french = 0 
                                    AND NOT EXISTS (
                                        SELECT 1 FROM Year1AllCourses y1
                                        WHERE NOT EXISTS (
                                            SELECT 1 FROM PassedCourses pc
                                            WHERE pc.student_id = student.student_id 
                                            AND pc.course_code = y1.course_code
                                        )
                                    )
                                ) THEN 'Sophomore'
                                ELSE 'Freshman'
                            END as new_level
                        FROM student
                    )
                    UPDATE student
                    JOIN EligibleStudents ON student.student_id = EligibleStudents.student_id
                    SET student.level = EligibleStudents.new_level
                """)
                
                current_app.mysql.connection.commit()
                
                return jsonify({
                    'success': True,
                    'message': f'Semester: {get_semester_name(semester)}, {academic_year} has ended successfully',
                    'data': {
                        'current_semester': {
                            'calendar_id': calendar_id,
                            'academic_year': academic_year,
                            'semester': semester,
                            'start_date': start_date.strftime('%Y-%m-%d'),
                            'end_date': date.today().strftime('%Y-%m-%d')
                        },
                        'graduates': graduates if graduates else None
                    }
                })

            else:
                return jsonify({'success': False, 'message': 'Invalid action'}), 400

    except Exception as e:
        current_app.mysql.connection.rollback()
        current_app.logger.error(f"Error in admin operation: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error processing request',
            'details': str(e)
        }), 500

    finally:
        if cursor:
            cursor.close()

@admin_bp.route('/major_minor_validation', methods=['GET', 'POST'])
def major_minor_validation():
    """Handle major/minor validation statistics and requests"""
    admin = session.get('admin')
    if not admin:
        return jsonify({'success': False, 'message': 'Admin not logged in'}), 401

    cursor = None
    try:
        cursor = current_app.mysql.connection.cursor()

        if request.method == 'POST':
            data = request.get_json()
            combination = data.get('combination')
            action = data.get('action')

            if not combination or action not in ['accepted', 'rejected']:
                return jsonify({
                    'success': False,
                    'message': 'Invalid request parameters'
                }), 400

            # Split the combination string
            parts = combination.split('-')
            if len(parts) < 2:
                return jsonify({'success': False, 'message': 'Invalid combination format'}), 400

            # Get the actual data from the database to determine the combination type
            cursor.execute("""
                SELECT 
                    major, second_major, minor, second_minor
                FROM major_minor_requests
                WHERE (major = %s AND (second_major = %s OR minor = %s))
            """, (parts[0], parts[1], parts[1]))
            
            results = cursor.fetchall()
            if not results:
                current_app.logger.error(f"No matching combination found in database: {combination}")
                return jsonify({'success': False, 'message': 'No matching combination found'}), 404
                
            # Determine combination type based on the combination string format and database results
            is_major_major = False
            is_major_minor = False
            
            # Use the combination_type from the frontend if provided
            combination_type = data.get('combination_type', '')
            if combination_type:
                is_major_major = combination_type == 'major-major'
                is_major_minor = combination_type == 'major-minor'
                current_app.logger.info(f"Using frontend-provided combination type: {combination_type}")
            else:
                # Fallback to detection if combination_type not provided
                # First, check if the combination format matches what we're looking for
                if len(parts) == 2:
                    # This could be either major/major or major/minor
                    # Check if parts[1] is a valid major
                    if parts[1] in ['ACCT', 'BA', 'FIN', 'IT', 'MRK']:
                        # Look for a matching major/major record
                        for row in results:
                            major, second_major, minor, second_minor = row
                            if second_major == parts[1]:
                                is_major_major = True
                                combination_type = 'major-major'
                                break
                
                    # If not found as major/major, check for major/minor
                    if not is_major_major:
                        for row in results:
                            major, second_major, minor, second_minor = row
                            if minor == parts[1] and not second_major:
                                is_major_minor = True
                                combination_type = 'major-minor'
                                break
                # Major-Minor-Minor combinations are no longer supported
            
            # If we couldn't determine the type, return an error
            if not (is_major_major or is_major_minor):
                current_app.logger.error(f"Unknown combination type for: {combination}")
                return jsonify({'success': False, 'message': 'Unknown combination type'}), 400
            
            current_app.logger.info(f"Detected combination type: {combination_type}")
            
            # Set the parts based on the determined combination type
            if is_major_major:
                # Find the matching row
                for row in results:
                    major, second_major, minor, second_minor = row
                    if second_major == parts[1]:
                        parts[0] = major
                        parts[1] = second_major
                        current_app.logger.info(f"Major/Major: {major}/{second_major}")
                        break
            elif is_major_minor:
                # Find the matching row
                for row in results:
                    major, second_major, minor, second_minor = row
                    if minor == parts[1] and not second_major:
                        parts[0] = major
                        parts[1] = minor
                        current_app.logger.info(f"Major/Minor: {major}/{minor}")
                        break
            # Major-Minor-Minor combinations are no longer supported
            
            if is_major_major:
                current_app.logger.info(f"Processing major/major combination: {parts[0]}-{parts[1]}")
                cursor.execute("""
                    UPDATE major_minor_requests 
                    SET status = %s 
                    WHERE major = %s AND second_major = %s
                      AND (minor IS NULL OR minor = '')
                      AND (second_minor IS NULL OR second_minor = '')
                """, (action, parts[0], parts[1]))
                
                affected_rows = cursor.rowcount
                current_app.logger.info(f"Updated {affected_rows} rows in major_minor_requests table")
            # Major-Minor-Minor combinations are no longer supported
            else:  # Major-Minor
                current_app.logger.info(f"Processing major/minor combination: {parts[0]}-{parts[1]}")
                cursor.execute("""
                    UPDATE major_minor_requests 
                    SET status = %s 
                    WHERE major = %s AND minor = %s
                      AND (second_minor IS NULL OR second_minor = '')
                      AND (second_major IS NULL OR second_major = '')
                """, (action, parts[0], parts[1]))
                
                affected_rows = cursor.rowcount
                current_app.logger.info(f"Updated {affected_rows} rows in major_minor_requests table")
            
            current_app.mysql.connection.commit()
            
            return jsonify({
                'success': True,
                'message': f'Combination {action} successfully'
            })

        # GET request handling
        # Get total eligible students
        cursor.execute("""
            SELECT COUNT(*) 
            FROM student 
            WHERE eligible_for_major = 1
        """)
        total_eligible = cursor.fetchone()[0]

        # Get students who haven't submitted requests
        cursor.execute("""
            SELECT COUNT(*) 
            FROM major_minor_requests 
            WHERE status = 'pending'
        """)
        pending_choices = cursor.fetchone()[0]

        # Get total submitted requests
        cursor.execute("""
            SELECT COUNT(*) 
            FROM major_minor_requests
        """)
        submitted_requests = cursor.fetchone()[0]

        # Get counts for each major (from both major and second_major columns)
        cursor.execute("""
            SELECT 
                major AS m, 
                COUNT(*) AS count 
            FROM major_minor_requests 
            WHERE major != 'NONE' 
            GROUP BY major
            
            UNION ALL
            
            SELECT 
                second_major AS m, 
                COUNT(*) AS count 
            FROM major_minor_requests 
            WHERE second_major != 'NONE' 
            GROUP BY second_major
        """)
        major_counts_raw = cursor.fetchall()

        # Process the counts into a dictionary
        major_counts = {}
        for major, count in major_counts_raw:
            if major in major_counts:
                major_counts[major] += count
            else:
                major_counts[major] = count

        # Get all requests with student details
        cursor.execute("""
            SELECT 
                mmr.id,
                mmr.major,
                mmr.second_major,
                mmr.minor,
                mmr.second_minor,
                mmr.status,
                mmr.submission_date,
                s.first_name,
                s.last_name,
                s.national_id
            FROM major_minor_requests mmr
            JOIN student s ON mmr.student_id = s.student_id
            ORDER BY mmr.submission_date DESC
        """)
        requests = cursor.fetchall()

        # Initialize empty dictionaries for each category
        major_minor = {}
        major_major = {}
        
        # Process requests into two categories - second_minor is no longer supported
        for req in requests:
            if not req:  # Skip if request is None
                continue

            major = req[1] or 'NONE'
            second_major = req[2] or 'NONE'
            minor = req[3] or 'NONE'
            # second_minor is no longer used
            
            # Create combination key based on category
            if second_major != 'NONE':
                combo_key = f"{major}-{second_major}"
                category = major_major
            else:
                combo_key = f"{major}-{minor}"
                category = major_minor

            # Initialize category if it doesn't exist
            if combo_key not in category:
                category[combo_key] = {
                    'count': 0,
                    'students': [],
                    'status': 'pending'  # Default status for the combination
                }
            
            # Add student to the combination
            student_data = {
                'id': req[0],
                'first_name': req[7],
                'last_name': req[8],
                'national_id': req[9],
                'submission_date': req[6].strftime('%Y-%m-%d %H:%M:%S') if req[6] else None
            }
            
            category[combo_key]['count'] += 1
            category[combo_key]['students'].append(student_data)

            # Update combination status if any student is accepted/rejected
            if req[5] == 'accepted':
                category[combo_key]['status'] = 'accepted'
            elif req[5] == 'rejected':
                category[combo_key]['status'] = 'rejected'

        return jsonify({
            'success': True,
            'statistics': {
                'total_eligible': total_eligible,
                'pending_choices': pending_choices,
                'submitted_requests': submitted_requests,
                'major_counts': major_counts  # Added major counts
            },
            'combinations': {
                'major_minor': major_minor,
                'major_major': major_major
            }
        })

    except Exception as e:
        current_app.logger.error(f"Error in major/minor validation: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error processing request',
            'details': str(e)
        }), 500

    finally:
        if cursor:
            cursor.close()

@admin_bp.route('/major_minor_validation/<student_id>')
def get_student_details(student_id):
    """Get detailed student information including cumulative GPA"""
    admin = session.get('admin')
    if not admin:
        return jsonify({'success': False, 'message': 'Admin not logged in'}), 401

    cursor = None
    try:
        cursor = current_app.mysql.connection.cursor()

        # Get student details
        cursor.execute("""
            SELECT 
                s.student_id,
                s.first_name,
                s.last_name,
                s.national_id,
                s.email_address,
                s.year_of_study,
                s.group,
                s.phone,
                s.profile_picture,
                s.level,
                sss.cumulative_gpa
            FROM student s
            LEFT JOIN student_semester_summary sss ON s.student_id = sss.student_id
            WHERE s.national_id = %s
            ORDER BY sss.year DESC, sss.semester DESC
            LIMIT 1
        """, (student_id,))
        
        student_data = cursor.fetchone()
        
        if not student_data:
            # Try searching by student_id if national_id search failed
            cursor.execute("""
                SELECT 
                    s.student_id,
                    s.first_name,
                    s.last_name,
                    s.national_id,
                    s.email_address,
                    s.year_of_study,
                    s.group,
                    s.phone,
                    s.profile_picture,
                    s.level,
                    sss.cumulative_gpa
                FROM student s
                LEFT JOIN student_semester_summary sss ON s.student_id = sss.student_id
                WHERE s.student_id = %s
                ORDER BY sss.year DESC, sss.semester DESC
                LIMIT 1
            """, (student_id,))
            
            student_data = cursor.fetchone()
            
            if not student_data:
                return jsonify({'success': False, 'message': 'Student not found'}), 404

        # Format the response
        student = {
            'student_id': student_data[0],
            'first_name': student_data[1],
            'last_name': student_data[2],
            'national_id': student_data[3],
            'email_address': student_data[4],
            'year_of_study': student_data[5],
            'group': student_data[6],
            'phone': student_data[7],
            'level': student_data[9],
            'profile_picture': student_data[8] if student_data[8] else '/static/images/default-profile.png'
        }
        
        cumulative_gpa = float(student_data[10]) if student_data[10] is not None else None

        return jsonify({
            'success': True,
            'student': student,
            'cumulative_gpa': cumulative_gpa
        })

    except Exception as e:
        current_app.logger.error(f"Error fetching student details: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error fetching student details',
            'details': str(e)
        }), 500

    finally:
        if cursor:
            cursor.close()

@admin_bp.route('/major_minor_validation/submitted_requests', methods=['GET'])
def get_submitted_requests():
    """Get list of students who have NOT submitted major/minor requests but are eligible"""
    admin = session.get('admin')
    if not admin:
        return jsonify({'success': False, 'message': 'Admin not logged in'}), 401

    cursor = None
    try:
        cursor = current_app.mysql.connection.cursor()
        
        # Get eligible students who have NOT submitted requests
        cursor.execute("""
            SELECT DISTINCT 
                s.first_name,
                s.last_name,
                s.national_id,
                s.email_address,
                s.year_of_study,
                s.group,
                s.phone
            FROM student s
            LEFT JOIN major_minor_requests mmr ON s.student_id = mmr.student_id
            WHERE s.eligible_for_major = 1
            AND mmr.id IS NULL
            ORDER BY s.last_name, s.first_name
        """)
        
        students = []
        for row in cursor.fetchall():
            students.append({
                'first_name': row[0],
                'last_name': row[1],
                'national_id': row[2],
                'email_address': row[3],
                'year_of_study': row[4],
                'group': row[5],
                'phone': row[6]
            })
        
        return jsonify({
            'success': True,
            'students': students
        })

    except Exception as e:
        current_app.logger.error(f"Error fetching submitted requests: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error fetching submitted requests',
            'details': str(e)
        }), 500

    finally:
        if cursor:
            cursor.close()

@admin_bp.route('/major_minor_validation/validate', methods=['POST'])
def validate_major_minor():
    """Endpoint to validate major/minor combinations and update student records"""
    admin = session.get('admin')
    if not admin:
        return jsonify({'success': False, 'message': 'Admin not logged in'}), 401

    data = request.get_json()
    if not data or 'combination' not in data or 'action' not in data:
        return jsonify({'success': False, 'message': 'Invalid request data'}), 400

    combination = data['combination']
    action = data['action']  # 'accepted', 'rejected', or 'pending'
    
    # New parameter to specifically mark as "no longer rejected"
    remove_rejection = data.get('remove_rejection', False)
    
    # Get combination type directly from the frontend
    combination_type = data.get('combination_type', '')

    if action not in ['accepted', 'rejected', 'pending']:
        return jsonify({'success': False, 'message': 'Invalid action'}), 400

    cursor = None
    try:
        cursor = current_app.mysql.connection.cursor()

        # Split the combination string
        parts = combination.split('-')
        if len(parts) < 2:
            return jsonify({'success': False, 'message': 'Invalid combination format'}), 400

        # Get the actual data from the database to determine the combination type
        cursor.execute("""
            SELECT 
                major, second_major, minor, second_minor
            FROM major_minor_requests
            WHERE (major = %s AND (second_major = %s OR minor = %s))
        """, (parts[0], parts[1], parts[1]))
        
        results = cursor.fetchall()
        if not results:
            current_app.logger.error(f"No matching combination found in database: {combination}")
            return jsonify({'success': False, 'message': 'No matching combination found'}), 404
            
        # Determine combination type based on the combination string format and database results
        is_major_major = False
        is_major_minor = False
        
        # Use the combination_type from the frontend if provided
        if combination_type:
            is_major_major = combination_type == 'major-major'
            is_major_minor = combination_type == 'major-minor'
            current_app.logger.info(f"Using frontend-provided combination type: {combination_type}")
        else:
            # Fallback to detection if combination_type not provided
            # First, check if the combination format matches what we're looking for
            if len(parts) == 2:
                # This could be either major/major or major/minor
                # Check if parts[1] is a valid major
                if parts[1] in ['ACCT', 'BA', 'FIN', 'IT', 'MRK']:
                    # Look for a matching major/major record
                    for row in results:
                        major, second_major, minor, second_minor = row
                        if second_major == parts[1]:
                            is_major_major = True
                            combination_type = 'major-major'
                            break
                
                # If not found as major/major, check for major/minor
                if not is_major_major:
                    for row in results:
                        major, second_major, minor, second_minor = row
                        if minor == parts[1] and not second_major:
                            is_major_minor = True
                            combination_type = 'major-minor'
                            break
            # Major-Minor-Minor combinations are no longer supported
        
        # If we couldn't determine the type, return an error
        if not (is_major_major or is_major_minor):
            current_app.logger.error(f"Unknown combination type for: {combination}")
            return jsonify({'success': False, 'message': 'Unknown combination type'}), 400
        
        current_app.logger.info(f"Detected combination type: {combination_type}")
        
        # Set the parts based on the determined combination type
        if is_major_major:
            # Find the matching row
            for row in results:
                major, second_major, minor, second_minor = row
                if second_major == parts[1]:
                    parts[0] = major
                    parts[1] = second_major
                    current_app.logger.info(f"Major/Major: {major}/{second_major}")
                    break
        elif is_major_minor:
            # Find the matching row
            for row in results:
                major, second_major, minor, second_minor = row
                if minor == parts[1] and not second_major:
                    parts[0] = major
                    parts[1] = minor
                    current_app.logger.info(f"Major/Minor: {major}/{minor}")
                    break
        # Major-Minor-Minor combinations are no longer supported
        
        if is_major_major:
            current_app.logger.info(f"Processing major/major combination: {parts[0]}-{parts[1]}")
            
            # Get all students who have requested this major/major combination
            cursor.execute("""
                SELECT mmr.id, mmr.student_id, mmr.status
                FROM major_minor_requests mmr
                WHERE mmr.major = %s AND mmr.second_major = %s
                   AND (mmr.minor IS NULL OR mmr.minor = '')
                   AND (mmr.second_minor IS NULL OR mmr.second_minor = '')
            """, (parts[0], parts[1]))
            
            requests = cursor.fetchall()
            current_app.logger.info(f"Found {len(requests)} requests for major/major combination")
            
            # Log each request for debugging
            for req in requests:
                current_app.logger.info(f"Request ID: {req[0]}, Student ID: {req[1]}, Status: {req[2]}")
        # Major-Minor-Minor combinations are no longer supported
        elif is_major_minor:
            cursor.execute("""
                SELECT mmr.id, mmr.student_id, mmr.status
                FROM major_minor_requests mmr
                WHERE mmr.major = %s AND mmr.minor = %s
                  AND (mmr.second_minor IS NULL OR mmr.second_minor = '')
                  AND (mmr.second_major IS NULL OR mmr.second_major = '')
            """, (parts[0], parts[1]))
        else:  # Major-Minor
            current_app.logger.info(f"Processing major/minor combination: {parts[0]}-{parts[1]}")
            cursor.execute("""
                SELECT mmr.id, mmr.student_id, mmr.status
                FROM major_minor_requests mmr
                WHERE mmr.major = %s  
                AND (mmr.second_minor IS NULL OR mmr.second_minor = '')
            """, (parts[0], parts[1]))
        
        requests = cursor.fetchall()
        if not requests:
            if is_major_major:
                # Try the reverse order if no results were found
                current_app.logger.warning(f"No requests found for {parts[0]}-{parts[1]}, trying reverse order")
                temp = parts[0]
                parts[0] = parts[1]
                parts[1] = temp
                cursor.execute("""
                    SELECT mmr.id, mmr.student_id, mmr.status, mmr.major, mmr.second_major
                    FROM major_minor_requests mmr
                    WHERE ((mmr.major = %s AND mmr.second_major = %s)
                       OR (mmr.major = %s AND mmr.second_major = %s))
                       AND mmr.minor IS NULL
                       AND mmr.second_minor IS NULL
                """, (parts[0], parts[1], parts[1], parts[0]))
                requests = cursor.fetchall()
                current_app.logger.info(f"Found {len(requests)} requests with reverse order")
                
                # Log each request for debugging
                for req in requests:
                    current_app.logger.info(f"Request ID: {req[0]}, Student ID: {req[1]}, Status: {req[2]}, Major: {req[3]}, Second Major: {req[4]}")
            
            if not requests:
                # Try a more lenient search for major/major combinations
                if is_major_major:
                    current_app.logger.warning(f"Still no requests found, trying more lenient search")
                    cursor.execute("""
                        SELECT mmr.id, mmr.student_id, mmr.status, mmr.major, mmr.second_major
                        FROM major_minor_requests mmr
                        WHERE (mmr.major = %s AND mmr.second_major = %s)
                           OR (mmr.major = %s AND mmr.second_major = %s)
                    """, (parts[0], parts[1], parts[1], parts[0]))
                    requests = cursor.fetchall()
                    current_app.logger.info(f"Found {len(requests)} requests with lenient search")
                
                if not requests:
                    current_app.logger.error(f"No matching combination found: {combination}")
                    return jsonify({'success': False, 'message': 'No matching combination found'}), 404
        
        # Get all student IDs affected by this combination
        student_ids = []
        request_ids = []
        has_rejected = False
        
        for req in requests:
            student_ids.append(req[1])  # student_id is at index 1
            request_ids.append(req[0])  # request id is at index 0
            if req[2] == 'rejected':  # Check if any request is currently rejected
                has_rejected = True
        
        # Handle the case where we want to remove rejections
        if remove_rejection:
            current_app.logger.info(f"Removing rejection for combination: {combination}")
            
            # Delete from rejected_combinations table
            if is_major_major:
                current_app.logger.info(f"Removing major/major rejection: {parts[0]}-{parts[1]}")
                # Remove from rejected_combinations table
                cursor.execute("""
                    DELETE FROM rejected_combinations
                    WHERE major = %s AND second_major = %s
                """, (parts[0], parts[1]))
                
                affected_rows = cursor.rowcount
                current_app.logger.info(f"Removed {affected_rows} rows from rejected_combinations")
                
                # Update status in major_minor_requests
                cursor.execute("""
                    UPDATE major_minor_requests
                    SET status = 'pending'
                    WHERE major = %s AND second_major = %s
                      AND (minor IS NULL OR minor = '')
                      AND (second_minor IS NULL OR second_minor = '')
                """, (parts[0], parts[1]))
                
                affected_rows = cursor.rowcount
                current_app.logger.info(f"Updated {affected_rows} rows in major_minor_requests")
            # Major-Minor-Minor combinations are no longer supported
            else:  # Major-Minor
                current_app.logger.info(f"Removing major/minor rejection: {parts[0]}-{parts[1]}")
                # Remove from rejected_combinations table
                cursor.execute("""
                    DELETE FROM rejected_combinations
                    WHERE major = %s AND minor = %s
                      AND (second_minor IS NULL OR second_minor = '')
                """, (parts[0], parts[1]))
                
                affected_rows = cursor.rowcount
                current_app.logger.info(f"Removed {affected_rows} rows from rejected_combinations")
                
                # Update status in major_minor_requests
                cursor.execute("""
                    UPDATE major_minor_requests
                    SET status = 'pending'
                    WHERE major = %s AND minor = %s
                      AND (second_minor IS NULL OR second_minor = '')
                      AND (second_major IS NULL OR second_major = '')
                """, (parts[0], parts[1]))
                
                affected_rows = cursor.rowcount
                current_app.logger.info(f"Updated {affected_rows} rows in major_minor_requests")
                
            current_app.mysql.connection.commit()
            return jsonify({
                'success': True,
                'message': f'Successfully removed rejection for combination {combination}'
            })
        
        # Update status for all affected students based on action
        if action == 'rejected':
            # If rejecting the combination, update all related records to 'rejected'
            if is_major_major:
                current_app.logger.info(f"Rejecting major/major combination: {parts[0]}-{parts[1]}")
                cursor.execute("""
                    UPDATE major_minor_requests
                    SET status = 'rejected'
                    WHERE major = %s AND second_major = %s
                       AND (minor IS NULL OR minor = '')
                       AND (second_minor IS NULL OR second_minor = '')
                """, (parts[0], parts[1]))
                
                updated_rows = cursor.rowcount
                current_app.logger.info(f"Updated {updated_rows} rows in major_minor_requests table")
                
                # Insert into rejected_combinations table
                cursor.execute("""
                    INSERT INTO rejected_combinations
                    (major, second_major)
                    VALUES (%s, %s)
                    ON DUPLICATE KEY UPDATE rejection_date = CURRENT_TIMESTAMP
                """, (parts[0], parts[1]))
                
                # Clear the student's choices in student table
                if student_ids:
                    cursor.execute("""
                        UPDATE student s
                        SET s.major = NULL,
                            s.second_major = NULL,
                            s.minor = NULL,
                            s.second_minor = NULL
                        WHERE s.student_id IN (%s)
                    """ % ','.join(['%s'] * len(student_ids)), student_ids)
                    
                    affected_rows = cursor.rowcount
                    current_app.logger.info(f"Cleared {affected_rows} student records for rejected major/major combination")
            # Major-Minor-Minor combinations are no longer supported
            else:  # Major-Minor
                current_app.logger.info(f"Rejecting major/minor combination: {parts[0]}-{parts[1]}")
                cursor.execute("""
                    UPDATE major_minor_requests
                    SET status = 'rejected'
                    WHERE major = %s AND minor = %s
                       AND (second_minor IS NULL OR second_minor = '')
                       AND (second_major IS NULL OR second_major = '')
                """, (parts[0], parts[1]))
                
                updated_rows = cursor.rowcount
                current_app.logger.info(f"Updated {updated_rows} rows in major_minor_requests table")
                
                # Insert into rejected_combinations table
                cursor.execute("""
                    INSERT INTO rejected_combinations
                    (major, minor)
                    VALUES (%s, %s)
                    ON DUPLICATE KEY UPDATE rejection_date = CURRENT_TIMESTAMP
                """, (parts[0], parts[1]))
                
                # Clear the student's choices in student table
                if student_ids:
                    cursor.execute("""
                        UPDATE student s
                        SET s.major = NULL,
                            s.second_major = NULL,
                            s.minor = NULL,
                            s.second_minor = NULL
                        WHERE s.student_id IN (%s)
                    """ % ','.join(['%s'] * len(student_ids)), student_ids)
                    
                    affected_rows = cursor.rowcount
                    current_app.logger.info(f"Cleared {affected_rows} student records for rejected major/minor combination")
        else:
            # If accepting or setting to pending, update the status
            if is_major_major:
                current_app.logger.info(f"Updating major/major combination status to {action}")
                cursor.execute("""
                    UPDATE major_minor_requests
                    SET status = %s
                    WHERE ((major = %s AND second_major = %s)
                       OR (major = %s AND second_major = %s))
                       AND (minor IS NULL OR minor = '')
                       AND (second_minor IS NULL OR second_minor = '')
                """, (action, parts[0], parts[1], parts[1], parts[0]))
                
                updated_rows = cursor.rowcount
                current_app.logger.info(f"Updated {updated_rows} rows in major_minor_requests table")
                
                # If no longer rejected, remove from rejected_combinations
                cursor.execute("""
                    DELETE FROM rejected_combinations
                    WHERE (major = %s AND second_major = %s)
                       OR (major = %s AND second_major = %s)
                """, (parts[0], parts[1], parts[1], parts[0]))
            # Major-Minor-Minor combinations are no longer supported
            else:  # Major-Minor
                cursor.execute("""
                    UPDATE major_minor_requests
                    SET status = %s
                    WHERE major = %s AND minor = %s 
                    AND (second_minor IS NULL OR second_minor = '')
                """, (action, parts[0], parts[1]))
                
                # If no longer rejected, remove from rejected_combinations
                cursor.execute("""
                    DELETE FROM rejected_combinations
                    WHERE major = %s AND minor = %s 
                    AND (second_minor IS NULL OR second_minor = '')
                """, (parts[0], parts[1]))
            
            # If accepting, copy the values from major_minor_requests to student table
            if action == 'accepted' and student_ids:
                current_app.logger.info(f"Accepting combination: {combination}, is_major_major={is_major_major}")
                current_app.logger.info(f"Student IDs: {student_ids}")
                
                if is_major_major:
                    # For major-major combinations, explicitly set the fields correctly
                    current_app.logger.info(f"Updating student table for major/major combination: {parts[0]}-{parts[1]}")
                    
                    # Now perform the update
                    cursor.execute("""
                        UPDATE student s
                        JOIN major_minor_requests mmr ON s.student_id = mmr.student_id
                        SET s.major = mmr.major,
                            s.second_major = mmr.second_major,
                            s.minor = NULL,
                            s.second_minor = NULL
                        WHERE mmr.student_id IN (%s)
                          AND mmr.status = 'accepted'
                    """ % ','.join(['%s'] * len(student_ids)), student_ids)
                    
                    affected_rows = cursor.rowcount
                    current_app.logger.info(f"Updated {affected_rows} student records for major/major combination")
                    
                # Major-Minor-Minor combinations are no longer supported
                    
                else:  # Major-Minor
                    # For major/minor combinations
                    current_app.logger.info(f"Updating student table for major/minor combination: {parts[0]}-{parts[1]}")
                    
                    cursor.execute("""
                        UPDATE student s
                        JOIN major_minor_requests mmr ON s.student_id = mmr.student_id
                        SET s.major = mmr.major,
                            s.second_major = NULL,
                            s.minor = mmr.minor,
                            s.second_minor = NULL
                        WHERE mmr.student_id IN (%s)
                          AND mmr.status = 'accepted'
                           
                          
                    """ % ','.join(['%s'] * len(student_ids)), student_ids)
                    
                    affected_rows = cursor.rowcount
                    current_app.logger.info(f"Updated {affected_rows} student records for major/minor combination")
                    
            elif action == 'rejected' and student_ids:
                # For rejected, clear student choices
                cursor.execute("""
                    UPDATE student s
                    SET s.major = NULL,
                        s.second_major = NULL,
                        s.minor = NULL,
                        s.second_minor = NULL
                    WHERE s.student_id IN (%s)
                """ % ','.join(['%s'] * len(student_ids)), student_ids)
                
                affected_rows = cursor.rowcount
                current_app.logger.info(f"Cleared {affected_rows} student records for rejected combination")
            elif action == 'pending' and student_ids:
                # For pending (undoing an acceptance), also clear student choices
                cursor.execute("""
                    UPDATE student s
                    SET s.major = NULL,
                        s.second_major = NULL,
                        s.minor = NULL,
                        s.second_minor = NULL
                    WHERE s.student_id IN (%s)
                """ % ','.join(['%s'] * len(student_ids)), student_ids)
                
                affected_rows = cursor.rowcount
                current_app.logger.info(f"Cleared {affected_rows} student records when setting back to pending")
        
        current_app.mysql.connection.commit()
        affected_rows = cursor.rowcount
        
        return jsonify({
            'success': True,
            'message': f'Successfully {action} {affected_rows} student(s) for combination {combination}'
        })

    except Exception as e:
        current_app.mysql.connection.rollback()
        current_app.logger.error(f"Error validating combination: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error processing validation',
            'details': str(e)
        }), 500
    finally:
        if cursor:
            cursor.close()

@admin_bp.route('/system_adjustments', methods=['GET', 'POST', 'PUT', 'DELETE'])
@admin_required
def system_adjustments():
    """Handle system adjustments page load"""
    admin = session.get('admin')
    cursor = None
    try:
        cursor = current_app.mysql.connection.cursor()
        
        if request.method == 'GET':
            section = request.args.get('section', 'overview')
            
            if section == 'overview':
                return jsonify({
                    'success': True,
                    'section': 'system-adjustments',
                    'title': 'System Adjustments',
                    'subsections': [
                        {'id': 'courses', 'name': 'Course Settings'},
                        {'id': 'major-minor', 'name': 'Major Settings'},
                        {'id': 'general', 'name': 'General Settings'},
                        {'id': 'schedule', 'name': 'Schedule Settings'},
                        {'id': 'special-cases', 'name': 'Special Cases'}
                    ]
                })
            
            return jsonify({
                'success': True,
                'section': section,
                'title': section.replace('-', ' ').title()
            })
        
        elif request.method == 'POST' or request.method == 'PUT':
            data = request.json
            admin_id = admin.get('admin_id')
            
            # Check if we're updating system-wide settings or student overrides
            if 'student_id' in data:
                # Update student parameter overrides
                student_id = data.get('student_id')
                
                # Verify student exists
                cursor.execute("SELECT 1 FROM student WHERE student_id = %s", (student_id,))
                if not cursor.fetchone():
                    return jsonify({'success': False, 'message': 'Student not found'}), 404
                
                # Extract GPA values, handling None/empty values
                min_gpa_acct = data.get('min_gpa_acct')
                min_gpa_ba = data.get('min_gpa_ba')
                min_gpa_fin = data.get('min_gpa_fin')
                min_gpa_it = data.get('min_gpa_it')
                min_gpa_mrk = data.get('min_gpa_mrk')
                min_credit_percentage_major = data.get('min_credit_percentage_major')
                
                # Check if all values are null - if so, don't create an override
                if (min_gpa_acct is None and min_gpa_ba is None and min_gpa_fin is None and 
                    min_gpa_it is None and min_gpa_mrk is None and min_credit_percentage_major is None):
                    return jsonify({
                        'success': False,
                        'message': 'At least one override value must be provided'
                    }), 400
                
                # Check if student already has overrides
                cursor.execute("SELECT min_gpa_acct, min_gpa_ba, min_gpa_fin, min_gpa_it, min_gpa_mrk, min_credit_percentage_major FROM student_parameters_overrides WHERE student_id = %s", (student_id,))
                old_values = cursor.fetchone()
                has_overrides = old_values is not None
                
                # Create dictionaries for old and new values for logging
                columns = ['min_gpa_acct', 'min_gpa_ba', 'min_gpa_fin', 'min_gpa_it', 'min_gpa_mrk', 'min_credit_percentage_major']
                old_values_dict = {}
                if has_overrides:
                    for i, col in enumerate(columns):
                        old_values_dict[col] = float(old_values[i]) if old_values[i] is not None else None
                
                new_values_dict = {
                    'min_gpa_acct': min_gpa_acct,
                    'min_gpa_ba': min_gpa_ba,
                    'min_gpa_fin': min_gpa_fin,
                    'min_gpa_it': min_gpa_it,
                    'min_gpa_mrk': min_gpa_mrk,
                    'min_credit_percentage_major': min_credit_percentage_major
                }
                
                if has_overrides:
                    # Update existing overrides
                    cursor.execute("""
                        UPDATE student_parameters_overrides
                        SET min_gpa_acct = %s,
                            min_gpa_ba = %s,
                            min_gpa_fin = %s,
                            min_gpa_it = %s,
                            min_gpa_mrk = %s,
                            min_credit_percentage_major = %s
                        WHERE student_id = %s
                    """, (
                        min_gpa_acct,
                        min_gpa_ba,
                        min_gpa_fin,
                        min_gpa_it,
                        min_gpa_mrk,
                        min_credit_percentage_major,
                        student_id
                    ))
                else:
                    # Insert new overrides
                    cursor.execute("""
                        INSERT INTO student_parameters_overrides
                        (student_id, min_gpa_acct, min_gpa_ba, min_gpa_fin, min_gpa_it, min_gpa_mrk, min_credit_percentage_major)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        student_id,
                        min_gpa_acct,
                        min_gpa_ba,
                        min_gpa_fin,
                        min_gpa_it,
                        min_gpa_mrk,
                        min_credit_percentage_major
                    ))
                
                # Log changes to parameter_changes_log
                for column_name, new_value in new_values_dict.items():
                    # Only log if the value has changed or it's a new override
                    old_value = old_values_dict.get(column_name) if has_overrides else None
                    if new_value != old_value:
                        cursor.execute("""
                            INSERT INTO parameter_changes_log
                            (changed_at, changed_by_admin, change_type, student_id, column_name, old_value, new_value)
                            VALUES (NOW(), %s, 'student', %s, %s, %s, %s)
                        """, (
                            admin_id,
                            student_id,
                            column_name,
                            str(old_value) if old_value is not None else None,
                            str(new_value) if new_value is not None else None
                        ))
                
                current_app.mysql.connection.commit()
                
                return jsonify({
                    'success': True,
                    'message': 'Student parameter overrides updated successfully'
                })
            
            else:
                # Update system-wide parameters
                min_gpa_acct = data.get('min_gpa_acct')
                min_gpa_ba = data.get('min_gpa_ba')
                min_gpa_fin = data.get('min_gpa_fin')
                min_gpa_it = data.get('min_gpa_it')
                min_gpa_mrk = data.get('min_gpa_mrk')
                min_cumulative_gpa = data.get('min_cumulative_gpa')
                min_credit_percentage_major = data.get('min_credit_percentage_major')
                
                # Get current values for logging
                cursor.execute("""
                    SELECT 
                        min_gpa_acct, 
                        min_gpa_ba, 
                        min_gpa_fin, 
                        min_gpa_it, 
                        min_gpa_mrk,
                        min_cumulative_gpa,
                        min_credit_percentage_major
                    FROM system_parameters
                    LIMIT 1
                """)
                
                old_values = cursor.fetchone()
                has_params = old_values is not None
                
                # Create dictionaries for old and new values for logging
                columns = ['min_gpa_acct', 'min_gpa_ba', 'min_gpa_fin', 'min_gpa_it', 'min_gpa_mrk', 
                           'min_cumulative_gpa', 'min_credit_percentage_major']
                old_values_dict = {}
                if has_params:
                    for i, col in enumerate(columns):
                        old_values_dict[col] = float(old_values[i]) if old_values[i] is not None else None
                
                new_values_dict = {
                    'min_gpa_acct': min_gpa_acct,
                    'min_gpa_ba': min_gpa_ba,
                    'min_gpa_fin': min_gpa_fin,
                    'min_gpa_it': min_gpa_it,
                    'min_gpa_mrk': min_gpa_mrk,
                    'min_cumulative_gpa': min_cumulative_gpa,
                    'min_credit_percentage_major': min_credit_percentage_major
                }
                
                if has_params:
                    # Update existing parameters
                    cursor.execute("""
                        UPDATE system_parameters
                        SET min_gpa_acct = %s,
                            min_gpa_ba = %s,
                            min_gpa_fin = %s,
                            min_gpa_it = %s,
                            min_gpa_mrk = %s,
                            min_cumulative_gpa = %s,
                            min_credit_percentage_major = %s,
                            last_updated = NOW()
                    """, (
                        min_gpa_acct,
                        min_gpa_ba,
                        min_gpa_fin,
                        min_gpa_it,
                        min_gpa_mrk,
                        min_cumulative_gpa,
                        min_credit_percentage_major
                    ))
                else:
                    # Insert new parameters
                    cursor.execute("""
                        INSERT INTO system_parameters
                        (min_gpa_acct, min_gpa_ba, min_gpa_fin, min_gpa_it, min_gpa_mrk, min_cumulative_gpa, min_credit_percentage_major, last_updated)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                    """, (
                        min_gpa_acct,
                        min_gpa_ba,
                        min_gpa_fin,
                        min_gpa_it,
                        min_gpa_mrk,
                        min_cumulative_gpa,
                        min_credit_percentage_major
                    ))
                
                # Log changes to parameter_changes_log
                for column_name, new_value in new_values_dict.items():
                    # Only log if the value has changed or it's a new parameter
                    old_value = old_values_dict.get(column_name) if has_params else None
                    if new_value != old_value:
                        cursor.execute("""
                            INSERT INTO parameter_changes_log
                            (changed_at, changed_by_admin, change_type, column_name, old_value, new_value)
                            VALUES (NOW(), %s, 'system', %s, %s, %s)
                        """, (
                            admin_id,
                            column_name,
                            str(old_value) if old_value is not None else None,
                            str(new_value) if new_value is not None else None
                        ))
                
                current_app.mysql.connection.commit()
                
                return jsonify({
                    'success': True,
                    'message': 'System parameters updated successfully'
                })
        
        elif request.method == 'DELETE':
            # Remove student parameter overrides
            student_id = request.args.get('student_id')
            if not student_id:
                return jsonify({'success': False, 'message': 'Student ID is required'}), 400
            
            # Verify student exists
            cursor.execute("SELECT 1 FROM student WHERE student_id = %s", (student_id,))
            if not cursor.fetchone():
                return jsonify({'success': False, 'message': 'Student not found'}), 404
            
            # Get current values for logging
            cursor.execute("""
                SELECT min_gpa_acct, min_gpa_ba, min_gpa_fin, min_gpa_it, min_gpa_mrk, min_credit_percentage_major
                FROM student_parameters_overrides
                WHERE student_id = %s
            """, (student_id,))
            
            old_values = cursor.fetchone()
            if not old_values:
                return jsonify({'success': False, 'message': 'No overrides found for this student'}), 404
            
            # Log removal of each parameter
            columns = ['min_gpa_acct', 'min_gpa_ba', 'min_gpa_fin', 'min_gpa_it', 'min_gpa_mrk', 'min_credit_percentage_major']
            for i, column_name in enumerate(columns):
                if old_values[i] is not None:
                    cursor.execute("""
                        INSERT INTO parameter_changes_log
                        (changed_at, changed_by_admin, change_type, student_id, column_name, old_value, new_value)
                        VALUES (NOW(), %s, 'student', %s, %s, %s, NULL)
                    """, (
                        admin.get('admin_id'),
                        student_id,
                        column_name,
                        str(float(old_values[i])) if old_values[i] else None
                    ))
            
            # Delete overrides for this student
            cursor.execute("DELETE FROM student_parameters_overrides WHERE student_id = %s", (student_id,))
            current_app.mysql.connection.commit()
            
            return jsonify({
                'success': True,
                'message': 'Student parameter overrides removed successfully'
            })
    
    except Exception as e:
        current_app.mysql.connection.rollback()
        current_app.logger.error(f"Error in system adjustments major: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error processing request',
            'details': str(e)
        }), 500
    
    finally:
        if cursor:
            cursor.close()

@admin_bp.route('/system_adjustments/courses', methods=['GET', 'POST', 'PUT', 'DELETE'])
@admin_required
def system_adjustments_courses():
    """Handle course settings adjustments"""
    admin = session.get('admin')
    cursor = None
    try:
        cursor = current_app.mysql.connection.cursor()
        
        if request.method == 'GET':
            # If course_code is provided, return specific course details
            course_code = request.args.get('course_code')
            if course_code:
                cursor.execute("""
                    SELECT * FROM courses 
                    WHERE course_code = %s
                """, (course_code,))
                
                course = cursor.fetchone()
                if not course:
                    return jsonify({'success': False, 'message': 'Course not found'}), 404
                
                # Get all majors and minors for advanced settings
                cursor.execute("SELECT major, full_name FROM majors ORDER BY major")
                majors = [{'code': row[0], 'name': row[1]} for row in cursor.fetchall()]
                
                cursor.execute("SELECT minor, full_name FROM minors ORDER BY minor")
                minors = [{'code': row[0], 'name': row[1]} for row in cursor.fetchall()]
                
                # Convert course to dictionary with appropriate column names
                course_columns = [
                    'id', 'course_code', 'course_name', 'coefficient', 'semester', 
                    'year', 'for_major', 'for_minor', 'for_minor_if_major_is', 
                    'minor_study_year', 'description', 'has_lecture', 'has_tutorial', 
                    'in_curriculum', 'requires_french'
                ]
                
                course_data = dict(zip(course_columns, course))
                
                # Split comma-separated values into lists for multiselect fields
                if course_data['for_major']:
                    course_data['for_major'] = course_data['for_major'].split(',')
                else:
                    course_data['for_major'] = []
                    
                if course_data['for_minor']:
                    course_data['for_minor'] = course_data['for_minor'].split(',')
                else:
                    course_data['for_minor'] = []
                    
                if course_data['for_minor_if_major_is']:
                    course_data['for_minor_if_major_is'] = course_data['for_minor_if_major_is'].split(',')
                else:
                    course_data['for_minor_if_major_is'] = []
                
                # Convert tinyint to boolean for checkbox fields
                course_data['has_lecture'] = bool(course_data['has_lecture'])
                course_data['has_tutorial'] = bool(course_data['has_tutorial'])
                course_data['in_curriculum'] = bool(course_data['in_curriculum'])
                course_data['requires_french'] = bool(course_data['requires_french'])
                
                return jsonify({
                    'success': True,
                    'course': course_data,
                    'majors': majors,
                    'minors': minors
                })
            
            # Otherwise return all courses grouped by year and semester
            cursor.execute("""
                SELECT course_code, course_name, coefficient, semester, year, in_curriculum
                FROM courses
                ORDER BY year, semester, course_code
            """)
            
            all_courses = cursor.fetchall()
            grouped_courses = {}
            
            for course in all_courses:
                course_code, course_name, coefficient, semester, year, in_curriculum = course
                year_key = f"{year}XX"
                semester_name = 'Fall' if semester == 1 else 'Spring'
                group_key = f"{year_key} {semester_name}"
                
                if group_key not in grouped_courses:
                    grouped_courses[group_key] = []
                
                grouped_courses[group_key].append({
                    'course_code': course_code,
                    'course_name': course_name,
                    'coefficient': coefficient,
                    'semester': semester,
                    'year': year,
                    'in_curriculum': bool(in_curriculum)
                })
            
            # Get all majors and minors for the UI
            cursor.execute("SELECT major, full_name FROM majors ORDER BY major")
            majors = [{'code': row[0], 'name': row[1]} for row in cursor.fetchall()]
            
            cursor.execute("SELECT minor, full_name FROM minors ORDER BY minor")
            minors = [{'code': row[0], 'name': row[1]} for row in cursor.fetchall()]
            
            return jsonify({
                'success': True,
                'grouped_courses': grouped_courses,
                'majors': majors,
                'minors': minors
            })
            
        elif request.method == 'POST':
            # Add a new course
            data = request.json
            
            # Basic validation
            required_fields = ['course_code', 'course_name']
            for field in required_fields:
                if field not in data or not data[field]:
                    return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400
            
            # Prepare for_major, for_minor, for_minor_if_major_is as comma-separated strings
            for_major = ','.join(data.get('for_major', []))
            for_minor = ','.join(data.get('for_minor', []))
            for_minor_if_major_is = ','.join(data.get('for_minor_if_major_is', []))
            
            # Convert empty strings to None for nullable fields
            for_major = for_major if for_major else None
            for_minor = for_minor if for_minor else None
            for_minor_if_major_is = for_minor_if_major_is if for_minor_if_major_is else None
            
            # Check if course already exists
            cursor.execute("SELECT 1 FROM courses WHERE course_code = %s", (data['course_code'],))
            if cursor.fetchone():
                return jsonify({'success': False, 'message': 'Course code already exists'}), 400
            
            # Insert the new course
            cursor.execute("""
                INSERT INTO courses (
                    course_code, course_name, coefficient, semester, year, 
                    for_major, for_minor, for_minor_if_major_is, minor_study_year,
                    description, has_lecture, has_tutorial, in_curriculum, requires_french
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                data['course_code'], data['course_name'], data.get('coefficient'),
                data.get('semester'), data.get('year'),
                for_major, for_minor, for_minor_if_major_is, 
                data.get('minor_study_year'),
                data.get('description'), 
                data.get('has_lecture', False), data.get('has_tutorial', False),
                data.get('in_curriculum', True), data.get('requires_french', False)
            ))
            
            current_app.mysql.connection.commit()
            
            return jsonify({
                'success': True, 
                'message': f"Course {data['course_code']} added successfully"
            })
            
        elif request.method == 'PUT':
            # Update an existing course
            data = request.json
            
            # Basic validation
            if 'course_code' not in data or not data['course_code']:
                return jsonify({'success': False, 'message': 'Missing required field: course_code'}), 400
            
            if 'course_name' not in data or not data['course_name']:
                return jsonify({'success': False, 'message': 'Missing required field: course_name'}), 400
            
            # Check if course exists
            cursor.execute("SELECT 1 FROM courses WHERE course_code = %s", (data['course_code'],))
            if not cursor.fetchone():
                return jsonify({'success': False, 'message': 'Course not found'}), 404
            
            # Prepare for_major, for_minor, for_minor_if_major_is as comma-separated strings
            for_major = ','.join(data.get('for_major', []))
            for_minor = ','.join(data.get('for_minor', []))
            for_minor_if_major_is = ','.join(data.get('for_minor_if_major_is', []))
            
            # Convert empty strings to None for nullable fields
            for_major = for_major if for_major else None
            for_minor = for_minor if for_minor else None
            for_minor_if_major_is = for_minor_if_major_is if for_minor_if_major_is else None
            
            # Update the course
            cursor.execute("""
                UPDATE courses SET
                    course_name = %s,
                    coefficient = %s,
                    semester = %s,
                    year = %s,
                    for_major = %s,
                    for_minor = %s,
                    for_minor_if_major_is = %s,
                    minor_study_year = %s,
                    description = %s,
                    has_lecture = %s,
                    has_tutorial = %s,
                    in_curriculum = %s,
                    requires_french = %s
                WHERE course_code = %s
            """, (
                data['course_name'], data.get('coefficient'),
                data.get('semester'), data.get('year'),
                for_major, for_minor, for_minor_if_major_is,
                data.get('minor_study_year'),
                data.get('description'),
                data.get('has_lecture', False), data.get('has_tutorial', False),
                data.get('in_curriculum', True), data.get('requires_french', False),
                data['course_code']
            ))
            
            current_app.mysql.connection.commit()
            
            return jsonify({
                'success': True, 
                'message': f"Course {data['course_code']} updated successfully"
            })
        
        elif request.method == 'DELETE':
            # Delete a course
            course_code = request.args.get('course_code')
            if not course_code:
                return jsonify({'success': False, 'message': 'Course code is required'}), 400
            
            # Check if course exists
            cursor.execute("SELECT 1 FROM courses WHERE course_code = %s", (course_code,))
            if not cursor.fetchone():
                return jsonify({'success': False, 'message': 'Course not found'}), 404
            
            # Delete the course
            cursor.execute("DELETE FROM courses WHERE course_code = %s", (course_code,))
            current_app.mysql.connection.commit()
            
            return jsonify({
                'success': True,
                'message': f"Course {course_code} deleted successfully"
            })
        
    except Exception as e:
        current_app.mysql.connection.rollback()
        current_app.logger.error(f"Error in system adjustments courses: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error processing request',
            'details': str(e)
        }), 500
        
    finally:
        if cursor:
            cursor.close()

@admin_bp.route('/system_adjustments/major', methods=['GET', 'POST', 'PUT', 'DELETE'])
@admin_required
def system_adjustments_major():
    """Handle major settings adjustments including GPA requirements"""
    admin = session.get('admin')
    
    cursor = None
    try:
        cursor = current_app.mysql.connection.cursor()
        
        if request.method == 'GET':
            # Check if we're searching for a specific student
            student_search = request.args.get('student_search')
            student_id = request.args.get('student_id')
            
            # If searching for a student by national ID or name
            if student_search:
                cursor.execute("""
                    SELECT student_id, first_name, last_name, national_id
                    FROM student
                    WHERE national_id LIKE %s
                    OR CONCAT(first_name, ' ', last_name) LIKE %s
                    LIMIT 10
                """, (f'%{student_search}%', f'%{student_search}%'))
                
                students = []
                for row in cursor.fetchall():
                    students.append({
                        'student_id': row[0],
                        'first_name': row[1],
                        'last_name': row[2],
                        'national_id': row[3]
                    })
                
                return jsonify({
                    'success': True,
                    'students': students
                })
            
            # If requesting a specific student's override settings
            elif student_id:
                # Get student info
                cursor.execute("""
                    SELECT student_id, first_name, last_name, national_id, level
                    FROM student
                    WHERE student_id = %s
                """, (student_id,))
                
                student_info = cursor.fetchone()
                if not student_info:
                    return jsonify({'success': False, 'message': 'Student not found'}), 404
                
                student = {
                    'student_id': student_info[0],
                    'first_name': student_info[1],
                    'last_name': student_info[2],
                    'national_id': student_info[3],
                    'level': student_info[4] if student_info[4] else 'Not set'
                }
                
                # Get student parameter overrides if they exist
                cursor.execute("""
                    SELECT min_gpa_acct, min_gpa_ba, min_gpa_fin, min_gpa_it, min_gpa_mrk, min_credit_percentage_major
                    FROM student_parameters_overrides
                    WHERE student_id = %s
                """, (student_id,))
                
                overrides = cursor.fetchone()
                
                # Get last update timestamp for this student's parameters
                cursor.execute("""
                    SELECT MAX(changed_at) 
                    FROM parameter_changes_log 
                    WHERE student_id = %s AND change_type = 'student'
                """, (student_id,))
                
                last_updated = cursor.fetchone()[0]
                
                # If no overrides exist, return empty values
                if not overrides:
                    return jsonify({
                        'success': True,
                        'student': student,
                        'has_overrides': False,
                        'last_updated': last_updated.strftime('%Y-%m-%d %H:%M:%S') if last_updated else None,
                        'overrides': {
                            'min_gpa_acct': None,
                            'min_gpa_ba': None,
                            'min_gpa_fin': None,
                            'min_gpa_it': None,
                            'min_gpa_mrk': None,
                            'min_credit_percentage_major': None
                        }
                    })
                
                # Return student with overrides
                return jsonify({
                    'success': True,
                    'student': student,
                    'has_overrides': True,
                    'last_updated': last_updated.strftime('%Y-%m-%d %H:%M:%S') if last_updated else None,
                    'overrides': {
                        'min_gpa_acct': float(overrides[0]) if overrides[0] else None,
                        'min_gpa_ba': float(overrides[1]) if overrides[1] else None,
                        'min_gpa_fin': float(overrides[2]) if overrides[2] else None,
                        'min_gpa_it': float(overrides[3]) if overrides[3] else None,
                        'min_gpa_mrk': float(overrides[4]) if overrides[4] else None,
                        'min_credit_percentage_major': float(overrides[5]) if overrides[5] else None
                    }
                })
            
            # Otherwise return system-wide GPA settings
            cursor.execute("""
                SELECT 
                    min_gpa_acct, 
                    min_gpa_ba, 
                    min_gpa_fin, 
                    min_gpa_it, 
                    min_gpa_mrk,
                    min_cumulative_gpa,
                    min_credit_percentage_major,
                    last_updated
                FROM system_parameters
                LIMIT 1
            """)
            
            params = cursor.fetchone()
            if not params:
                return jsonify({'success': False, 'message': 'System parameters not found'}), 404
            
            # Get all majors for the UI
            cursor.execute("SELECT major, full_name FROM majors ORDER BY major")
            majors = [{'code': row[0], 'name': row[1]} for row in cursor.fetchall()]
            
            # Format the response
            return jsonify({
                'success': True,
                'parameters': {
                    'min_gpa_acct': float(params[0]) if params[0] else None,
                    'min_gpa_ba': float(params[1]) if params[1] else None,
                    'min_gpa_fin': float(params[2]) if params[2] else None,
                    'min_gpa_it': float(params[3]) if params[3] else None,
                    'min_gpa_mrk': float(params[4]) if params[4] else None,
                    'min_cumulative_gpa': float(params[5]) if params[5] else None,
                    'min_credit_percentage_major': float(params[6]) if params[6] else None,
                    'last_updated': params[7].strftime('%Y-%m-%d %H:%M:%S') if params[7] else None
                },
                'majors': majors
            })
        
        elif request.method == 'POST' or request.method == 'PUT':
            data = request.json
            admin_id = admin.get('admin_id')
            
            # Check if we're updating system-wide settings or student overrides
            if 'student_id' in data:
                # Update student parameter overrides
                student_id = data.get('student_id')
                
                # Verify student exists
                cursor.execute("SELECT 1 FROM student WHERE student_id = %s", (student_id,))
                if not cursor.fetchone():
                    return jsonify({'success': False, 'message': 'Student not found'}), 404
                
                # Extract GPA values, handling None/empty values
                min_gpa_acct = data.get('min_gpa_acct')
                min_gpa_ba = data.get('min_gpa_ba')
                min_gpa_fin = data.get('min_gpa_fin')
                min_gpa_it = data.get('min_gpa_it')
                min_gpa_mrk = data.get('min_gpa_mrk')
                min_credit_percentage_major = data.get('min_credit_percentage_major')
                
                # Check if all values are null - if so, don't create an override
                if (min_gpa_acct is None and min_gpa_ba is None and min_gpa_fin is None and 
                    min_gpa_it is None and min_gpa_mrk is None and min_credit_percentage_major is None):
                    return jsonify({
                        'success': False,
                        'message': 'At least one override value must be provided'
                    }), 400
                
                # Check if student already has overrides
                cursor.execute("SELECT min_gpa_acct, min_gpa_ba, min_gpa_fin, min_gpa_it, min_gpa_mrk, min_credit_percentage_major FROM student_parameters_overrides WHERE student_id = %s", (student_id,))
                old_values = cursor.fetchone()
                has_overrides = old_values is not None
                
                # Create dictionaries for old and new values for logging
                columns = ['min_gpa_acct', 'min_gpa_ba', 'min_gpa_fin', 'min_gpa_it', 'min_gpa_mrk', 'min_credit_percentage_major']
                old_values_dict = {}
                if has_overrides:
                    for i, col in enumerate(columns):
                        old_values_dict[col] = float(old_values[i]) if old_values[i] is not None else None
                
                new_values_dict = {
                    'min_gpa_acct': min_gpa_acct,
                    'min_gpa_ba': min_gpa_ba,
                    'min_gpa_fin': min_gpa_fin,
                    'min_gpa_it': min_gpa_it,
                    'min_gpa_mrk': min_gpa_mrk,
                    'min_credit_percentage_major': min_credit_percentage_major
                }
                
                if has_overrides:
                    # Update existing overrides
                    cursor.execute("""
                        UPDATE student_parameters_overrides
                        SET min_gpa_acct = %s,
                            min_gpa_ba = %s,
                            min_gpa_fin = %s,
                            min_gpa_it = %s,
                            min_gpa_mrk = %s,
                            min_credit_percentage_major = %s
                        WHERE student_id = %s
                    """, (
                        min_gpa_acct,
                        min_gpa_ba,
                        min_gpa_fin,
                        min_gpa_it,
                        min_gpa_mrk,
                        min_credit_percentage_major,
                        student_id
                    ))
                else:
                    # Insert new overrides
                    cursor.execute("""
                        INSERT INTO student_parameters_overrides
                        (student_id, min_gpa_acct, min_gpa_ba, min_gpa_fin, min_gpa_it, min_gpa_mrk, min_credit_percentage_major)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        student_id,
                        min_gpa_acct,
                        min_gpa_ba,
                        min_gpa_fin,
                        min_gpa_it,
                        min_gpa_mrk,
                        min_credit_percentage_major
                    ))
                
                # Log changes to parameter_changes_log
                for column_name, new_value in new_values_dict.items():
                    # Only log if the value has changed or it's a new override
                    old_value = old_values_dict.get(column_name) if has_overrides else None
                    if new_value != old_value:
                        cursor.execute("""
                            INSERT INTO parameter_changes_log
                            (changed_at, changed_by_admin, change_type, student_id, column_name, old_value, new_value)
                            VALUES (NOW(), %s, 'student', %s, %s, %s, %s)
                        """, (
                            admin_id,
                            student_id,
                            column_name,
                            str(old_value) if old_value is not None else None,
                            str(new_value) if new_value is not None else None
                        ))
                
                current_app.mysql.connection.commit()
                
                return jsonify({
                    'success': True,
                    'message': 'Student parameter overrides updated successfully'
                })
            
            else:
                # Update system-wide parameters
                min_gpa_acct = data.get('min_gpa_acct')
                min_gpa_ba = data.get('min_gpa_ba')
                min_gpa_fin = data.get('min_gpa_fin')
                min_gpa_it = data.get('min_gpa_it')
                min_gpa_mrk = data.get('min_gpa_mrk')
                min_cumulative_gpa = data.get('min_cumulative_gpa')
                min_credit_percentage_major = data.get('min_credit_percentage_major')
                
                # Get current values for logging
                cursor.execute("""
                    SELECT 
                        min_gpa_acct, 
                        min_gpa_ba, 
                        min_gpa_fin, 
                        min_gpa_it, 
                        min_gpa_mrk,
                        min_cumulative_gpa,
                        min_credit_percentage_major
                    FROM system_parameters
                    LIMIT 1
                """)
                
                old_values = cursor.fetchone()
                has_params = old_values is not None
                
                # Create dictionaries for old and new values for logging
                columns = ['min_gpa_acct', 'min_gpa_ba', 'min_gpa_fin', 'min_gpa_it', 'min_gpa_mrk', 
                           'min_cumulative_gpa', 'min_credit_percentage_major']
                old_values_dict = {}
                if has_params:
                    for i, col in enumerate(columns):
                        if i < 4:  # Integer values
                            old_values_dict[col] = int(old_values[i]) if old_values[i] is not None else None
                        elif i == 4:  # minimum_grad_credit is integer
                            old_values_dict[col] = int(old_values[i]) if old_values[i] is not None else None
                        else:  # Float values
                            old_values_dict[col] = float(old_values[i]) if old_values[i] is not None else None
                
                new_values_dict = {
                    'min_gpa_acct': min_gpa_acct,
                    'min_gpa_ba': min_gpa_ba,
                    'min_gpa_fin': min_gpa_fin,
                    'min_gpa_it': min_gpa_it,
                    'min_gpa_mrk': min_gpa_mrk,
                    'min_cumulative_gpa': min_cumulative_gpa,
                    'min_credit_percentage_major': min_credit_percentage_major
                }
                
                if has_params:
                    # Update existing parameters
                    cursor.execute("""
                        UPDATE system_parameters
                        SET min_gpa_acct = %s,
                            min_gpa_ba = %s,
                            min_gpa_fin = %s,
                            min_gpa_it = %s,
                            min_gpa_mrk = %s,
                            min_cumulative_gpa = %s,
                            min_credit_percentage_major = %s,
                            last_updated = NOW()
                    """, (
                        min_gpa_acct,
                        min_gpa_ba,
                        min_gpa_fin,
                        min_gpa_it,
                        min_gpa_mrk,
                        min_cumulative_gpa,
                        min_credit_percentage_major
                    ))
                else:
                    # Insert new parameters
                    cursor.execute("""
                        INSERT INTO system_parameters
                        (min_gpa_acct, min_gpa_ba, min_gpa_fin, min_gpa_it, min_gpa_mrk, min_cumulative_gpa, min_credit_percentage_major, last_updated)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                    """, (
                        min_gpa_acct,
                        min_gpa_ba,
                        min_gpa_fin,
                        min_gpa_it,
                        min_gpa_mrk,
                        min_cumulative_gpa,
                        min_credit_percentage_major
                    ))
                
                # Log changes to parameter_changes_log
                for column_name, new_value in new_values_dict.items():
                    # Only log if the value has changed or it's a new parameter
                    old_value = old_values_dict.get(column_name) if has_params else None
                    if new_value != old_value:
                        cursor.execute("""
                            INSERT INTO parameter_changes_log
                            (changed_at, changed_by_admin, change_type, column_name, old_value, new_value)
                            VALUES (NOW(), %s, 'system', %s, %s, %s)
                        """, (
                            admin_id,
                            column_name,
                            str(old_value) if old_value is not None else None,
                            str(new_value) if new_value is not None else None
                        ))
                
                current_app.mysql.connection.commit()
                
                return jsonify({
                    'success': True,
                    'message': 'System parameters updated successfully'
                })
        
        elif request.method == 'DELETE':
            # Remove student parameter overrides
            student_id = request.args.get('student_id')
            if not student_id:
                return jsonify({'success': False, 'message': 'Student ID is required'}), 400
            
            # Verify student exists
            cursor.execute("SELECT 1 FROM student WHERE student_id = %s", (student_id,))
            if not cursor.fetchone():
                return jsonify({'success': False, 'message': 'Student not found'}), 404
            
            # Get current values for logging
            cursor.execute("""
                SELECT min_gpa_acct, min_gpa_ba, min_gpa_fin, min_gpa_it, min_gpa_mrk, min_credit_percentage_major
                FROM student_parameters_overrides
                WHERE student_id = %s
            """, (student_id,))
            
            old_values = cursor.fetchone()
            if not old_values:
                return jsonify({'success': False, 'message': 'No overrides found for this student'}), 404
            
            # Log removal of each parameter
            columns = ['min_gpa_acct', 'min_gpa_ba', 'min_gpa_fin', 'min_gpa_it', 'min_gpa_mrk', 'min_credit_percentage_major']
            for i, column_name in enumerate(columns):
                if old_values[i] is not None:
                    cursor.execute("""
                        INSERT INTO parameter_changes_log
                        (changed_at, changed_by_admin, change_type, student_id, column_name, old_value, new_value)
                        VALUES (NOW(), %s, 'student', %s, %s, %s, NULL)
                    """, (
                        admin.get('admin_id'),
                        student_id,
                        column_name,
                        str(float(old_values[i])) if old_values[i] else None
                    ))
            
            # Delete overrides for this student
            cursor.execute("DELETE FROM student_parameters_overrides WHERE student_id = %s", (student_id,))
            current_app.mysql.connection.commit()
            
            return jsonify({
                'success': True,
                'message': 'Student parameter overrides removed successfully'
            })
    
    except Exception as e:
        current_app.mysql.connection.rollback()
        current_app.logger.error(f"Error in system adjustments major: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error processing request',
            'details': str(e)
        }), 500
    
    finally:
        if cursor:
            cursor.close()

@admin_bp.route('/system_adjustments/general', methods=['GET', 'POST', 'PUT', 'DELETE'])
@admin_required
def system_adjustments_general():
    """Handle general system settings adjustments including forgiveness, probation and course limits"""
    admin = session.get('admin')
    cursor = None
    try:
        cursor = current_app.mysql.connection.cursor()
        
        if request.method == 'GET':
            # Check if we're searching for a specific student
            student_search = request.args.get('student_search')
            student_id = request.args.get('student_id')
            
            # If searching for a student by national ID or name
            if student_search:
                cursor.execute("""
                    SELECT student_id, first_name, last_name, national_id
                    FROM student
                    WHERE national_id LIKE %s
                    OR CONCAT(first_name, ' ', last_name) LIKE %s
                    LIMIT 10
                """, (f'%{student_search}%', f'%{student_search}%'))
                
                students = []
                for row in cursor.fetchall():
                    students.append({
                        'student_id': row[0],
                        'first_name': row[1],
                        'last_name': row[2],
                        'national_id': row[3]
                    })
                
                return jsonify({
                    'success': True,
                    'students': students
                })
            
            # If requesting a specific student's override settings
            elif student_id:
                # Get student info
                cursor.execute("""
                    SELECT student_id, first_name, last_name, national_id, level
                    FROM student
                    WHERE student_id = %s
                """, (student_id,))
                
                student_info = cursor.fetchone()
                if not student_info:
                    return jsonify({'success': False, 'message': 'Student not found'}), 404
                
                student = {
                    'student_id': student_info[0],
                    'first_name': student_info[1],
                    'last_name': student_info[2],
                    'national_id': student_info[3],
                    'level': student_info[4] if student_info[4] else 'Not set'
                }
                
                # Get student parameter overrides if they exist
                cursor.execute("""
                    SELECT max_courses_per_semester, max_forgiveness_uses, max_probation_board, max_probation_total
                    FROM student_parameters_overrides
                    WHERE student_id = %s
                """, (student_id,))
                
                overrides = cursor.fetchone()
                
                # Get last update timestamp for this student's parameters
                cursor.execute("""
                    SELECT MAX(changed_at) 
                    FROM parameter_changes_log 
                    WHERE student_id = %s AND change_type = 'student'
                    AND column_name IN ('max_courses_per_semester', 'max_forgiveness_uses', 'max_probation_board', 'max_probation_total')
                """, (student_id,))
                
                last_updated = cursor.fetchone()[0]
                
                # If no overrides exist, return empty values
                if not overrides:
                    return jsonify({
                        'success': True,
                        'student': student,
                        'has_overrides': False,
                        'last_updated': last_updated.strftime('%Y-%m-%d %H:%M:%S') if last_updated else None,
                        'overrides': {
                            'max_courses_per_semester': None,
                            'max_forgiveness_uses': None,
                            'max_probation_board': None,
                            'max_probation_total': None
                        }
                    })
                
                # Return student with overrides
                return jsonify({
                    'success': True,
                    'student': student,
                    'has_overrides': True,
                    'last_updated': last_updated.strftime('%Y-%m-%d %H:%M:%S') if last_updated else None,
                    'overrides': {
                        'max_courses_per_semester': int(overrides[0]) if overrides[0] else None,
                        'max_forgiveness_uses': int(overrides[1]) if overrides[1] else None,
                        'max_probation_board': int(overrides[2]) if overrides[2] else None,
                        'max_probation_total': int(overrides[3]) if overrides[3] else None
                    }
                })
            
            # Otherwise return system-wide general settings
            cursor.execute("""
                SELECT 
                    max_courses_per_semester,
                    max_forgiveness_uses,
                    max_probation_board,
                    max_probation_total,
                    last_updated,
                    minimum_grad_credit,
                    minimum_grad_cgpa,
                    maximum_forgive_grade
                FROM system_parameters
                LIMIT 1
            """)
            
            params = cursor.fetchone()
            if not params:
                return jsonify({'success': False, 'message': 'System parameters not found'}), 404
            
            # Format the response
            return jsonify({
                'success': True,
                'parameters': {
                    'max_courses_per_semester': int(params[0]) if params[0] else None,
                    'max_forgiveness_uses': int(params[1]) if params[1] else None,
                    'max_probation_board': int(params[2]) if params[2] else None,
                    'max_probation_total': int(params[3]) if params[3] else None,
                    'last_updated': params[4].strftime('%Y-%m-%d %H:%M:%S') if params[4] else None,
                    'minimum_grad_credit': int(params[5]) if params[5] else None,
                    'minimum_grad_cgpa': float(params[6]) if params[6] else None,
                    'maximum_forgive_grade': float(params[7]) if params[7] else None
                }
            })
        
        elif request.method == 'POST' or request.method == 'PUT':
            data = request.json
            admin_id = admin.get('admin_id')
            
            # Check if we're updating system-wide settings or student overrides
            if 'student_id' in data:
                # Update student parameter overrides
                student_id = data.get('student_id')
                
                # Verify student exists
                cursor.execute("SELECT 1 FROM student WHERE student_id = %s", (student_id,))
                if not cursor.fetchone():
                    return jsonify({'success': False, 'message': 'Student not found'}), 404
                
                # Extract parameter values, handling None/empty values
                max_courses_per_semester = data.get('max_courses_per_semester')
                max_forgiveness_uses = data.get('max_forgiveness_uses')
                max_probation_board = data.get('max_probation_board')
                max_probation_total = data.get('max_probation_total')
                
                # Check if all values are null - if so, don't create an override
                if (max_courses_per_semester is None and max_forgiveness_uses is None and 
                    max_probation_board is None and max_probation_total is None):
                    return jsonify({
                        'success': False,
                        'message': 'At least one override value must be provided'
                    }), 400
                
                # Check if student already has overrides
                cursor.execute("""
                    SELECT max_courses_per_semester, max_forgiveness_uses, max_probation_board, max_probation_total 
                    FROM student_parameters_overrides 
                    WHERE student_id = %s
                """, (student_id,))
                old_values = cursor.fetchone()
                has_overrides = old_values is not None
                
                # Create dictionaries for old and new values for logging
                columns = ['max_courses_per_semester', 'max_forgiveness_uses', 'max_probation_board', 'max_probation_total']
                old_values_dict = {}
                if has_overrides:
                    for i, col in enumerate(columns):
                        old_values_dict[col] = int(old_values[i]) if old_values[i] is not None else None
                
                new_values_dict = {
                    'max_courses_per_semester': max_courses_per_semester,
                    'max_forgiveness_uses': max_forgiveness_uses,
                    'max_probation_board': max_probation_board,
                    'max_probation_total': max_probation_total
                }
                
                if has_overrides:
                    # Update existing overrides
                    cursor.execute("""
                        UPDATE student_parameters_overrides
                        SET max_courses_per_semester = %s,
                            max_forgiveness_uses = %s,
                            max_probation_board = %s,
                            max_probation_total = %s
                        WHERE student_id = %s
                    """, (
                        max_courses_per_semester,
                        max_forgiveness_uses,
                        max_probation_board,
                        max_probation_total,
                        student_id
                    ))
                else:
                    # Insert new overrides
                    cursor.execute("""
                        INSERT INTO student_parameters_overrides
                        (student_id, max_courses_per_semester, max_forgiveness_uses, max_probation_board, max_probation_total)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        student_id,
                        max_courses_per_semester,
                        max_forgiveness_uses,
                        max_probation_board,
                        max_probation_total
                    ))
                
                # Log changes to parameter_changes_log
                for column_name, new_value in new_values_dict.items():
                    # Only log if the value has changed or it's a new override
                    old_value = old_values_dict.get(column_name) if has_overrides else None
                    if new_value != old_value:
                        cursor.execute("""
                            INSERT INTO parameter_changes_log
                            (changed_at, changed_by_admin, change_type, student_id, column_name, old_value, new_value)
                            VALUES (NOW(), %s, 'student', %s, %s, %s, %s)
                        """, (
                            admin_id,
                            student_id,
                            column_name,
                            str(old_value) if old_value is not None else None,
                            str(new_value) if new_value is not None else None
                        ))
                
                current_app.mysql.connection.commit()
                
                return jsonify({
                    'success': True,
                    'message': 'Student parameter overrides updated successfully'
                })
            
            else:
                # Update system-wide parameters
                max_courses_per_semester = data.get('max_courses_per_semester')
                max_forgiveness_uses = data.get('max_forgiveness_uses')
                max_probation_board = data.get('max_probation_board')
                max_probation_total = data.get('max_probation_total')
                minimum_grad_credit = data.get('minimum_grad_credit')
                minimum_grad_cgpa = data.get('minimum_grad_cgpa')
                maximum_forgive_grade = data.get('maximum_forgive_grade')
                
                # Get current values for logging
                cursor.execute("""
                    SELECT 
                        max_courses_per_semester,
                        max_forgiveness_uses,
                        max_probation_board,
                        max_probation_total,
                        minimum_grad_credit,
                        minimum_grad_cgpa,
                        maximum_forgive_grade
                    FROM system_parameters
                    LIMIT 1
                """)
                
                old_values = cursor.fetchone()
                has_params = old_values is not None
                
                # Create dictionaries for old and new values for logging
                columns = ['max_courses_per_semester', 'max_forgiveness_uses', 'max_probation_board', 'max_probation_total',
                          'minimum_grad_credit', 'minimum_grad_cgpa', 'maximum_forgive_grade']
                old_values_dict = {}
                if has_params:
                    for i, col in enumerate(columns):
                        if i < 4:  # Integer values
                            old_values_dict[col] = int(old_values[i]) if old_values[i] is not None else None
                        elif i == 4:  # minimum_grad_credit is integer
                            old_values_dict[col] = int(old_values[i]) if old_values[i] is not None else None
                        else:  # Float values
                            old_values_dict[col] = float(old_values[i]) if old_values[i] is not None else None
                
                new_values_dict = {
                    'max_courses_per_semester': max_courses_per_semester,
                    'max_forgiveness_uses': max_forgiveness_uses,
                    'max_probation_board': max_probation_board,
                    'max_probation_total': max_probation_total,
                    'minimum_grad_credit': minimum_grad_credit,
                    'minimum_grad_cgpa': minimum_grad_cgpa,
                    'maximum_forgive_grade': maximum_forgive_grade
                }
                
                if has_params:
                    # Update existing parameters
                    cursor.execute("""
                        UPDATE system_parameters
                        SET max_courses_per_semester = %s,
                            max_forgiveness_uses = %s,
                            max_probation_board = %s,
                            max_probation_total = %s,
                                                minimum_grad_credit = %s,
                    minimum_grad_cgpa = %s,
                    maximum_forgive_grade = %s,
                            last_updated = NOW()
                    """, (
                        max_courses_per_semester,
                        max_forgiveness_uses,
                        max_probation_board,
                        max_probation_total,
                        minimum_grad_credit,
                        minimum_grad_cgpa,
                        maximum_forgive_grade
                    ))
                else:
                    # Insert new parameters
                    cursor.execute("""
                        INSERT INTO system_parameters
                        (max_courses_per_semester, max_forgiveness_uses, max_probation_board, max_probation_total, 
                        minimum_grad_credit, minimum_grad_cgpa, maximum_forgive_grade, last_updated)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                    """, (
                        max_courses_per_semester,
                        max_forgiveness_uses,
                        max_probation_board,
                        max_probation_total,
                        minimum_grad_credit,
                        minimum_grad_cgpa,
                        maximum_forgive_grade
                    ))
                
                # Log changes to parameter_changes_log
                for column_name, new_value in new_values_dict.items():
                    # Only log if the value has changed or it's a new parameter
                    old_value = old_values_dict.get(column_name) if has_params else None
                    if new_value != old_value:
                        cursor.execute("""
                            INSERT INTO parameter_changes_log
                            (changed_at, changed_by_admin, change_type, column_name, old_value, new_value)
                            VALUES (NOW(), %s, 'system', %s, %s, %s)
                        """, (
                            admin_id,
                            column_name,
                            str(old_value) if old_value is not None else None,
                            str(new_value) if new_value is not None else None
                        ))
                
                current_app.mysql.connection.commit()
                
                return jsonify({
                    'success': True,
                    'message': 'System parameters updated successfully'
                })
        
        elif request.method == 'DELETE':
            # Remove student parameter overrides
            student_id = request.args.get('student_id')
            if not student_id:
                return jsonify({'success': False, 'message': 'Student ID is required'}), 400
            
            # Verify student exists
            cursor.execute("SELECT 1 FROM student WHERE student_id = %s", (student_id,))
            if not cursor.fetchone():
                return jsonify({'success': False, 'message': 'Student not found'}), 404
            
            # Get current values for logging
            cursor.execute("""
                SELECT max_courses_per_semester, max_forgiveness_uses, max_probation_board, max_probation_total
                FROM student_parameters_overrides
                WHERE student_id = %s
            """, (student_id,))
            
            old_values = cursor.fetchone()
            if not old_values:
                return jsonify({'success': False, 'message': 'No overrides found for this student'}), 404
            
            # Log removal of each parameter
            columns = ['max_courses_per_semester', 'max_forgiveness_uses', 'max_probation_board', 'max_probation_total']
            for i, column_name in enumerate(columns):
                if old_values[i] is not None:
                    cursor.execute("""
                        INSERT INTO parameter_changes_log
                        (changed_at, changed_by_admin, change_type, student_id, column_name, old_value, new_value)
                        VALUES (NOW(), %s, 'student', %s, %s, %s, NULL)
                    """, (
                        admin.get('admin_id'),
                        student_id,
                        column_name,
                        str(int(old_values[i])) if old_values[i] else None
                    ))
            
            # Delete overrides for this student
            cursor.execute("""
                UPDATE student_parameters_overrides 
                SET max_courses_per_semester = NULL,
                    max_forgiveness_uses = NULL,
                    max_probation_board = NULL,
                    max_probation_total = NULL
                WHERE student_id = %s
            """, (student_id,))
            
            # Remove row if all values are NULL
            cursor.execute("""
                DELETE FROM student_parameters_overrides
                WHERE student_id = %s
                AND max_courses_per_semester IS NULL
                AND max_forgiveness_uses IS NULL
                AND max_probation_board IS NULL
                AND max_probation_total IS NULL
                AND min_gpa_acct IS NULL
                AND min_gpa_ba IS NULL
                AND min_gpa_fin IS NULL
                AND min_gpa_it IS NULL
                AND min_gpa_mrk IS NULL
                AND min_credit_percentage_major IS NULL
            """, (student_id,))
            
            current_app.mysql.connection.commit()
            
            return jsonify({
                'success': True,
                'message': 'Student parameter overrides removed successfully'
            })
    
    except Exception as e:
        current_app.mysql.connection.rollback()
        current_app.logger.error(f"Error in system adjustments general: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error processing request',
            'details': str(e)
        }), 500
    
    finally:
        if cursor:
            cursor.close()

@admin_bp.route('/system_adjustments/schedule', methods=['GET', 'POST', 'PUT'])
@admin_required
def system_adjustments_schedule():
    """Handle schedule optimization parameters adjustments"""
    admin = session.get('admin')
    cursor = None
    try:
        cursor = current_app.mysql.connection.cursor()
        if request.method == 'GET':
            cursor.execute("""
                SELECT weight_mode_a, weight_mode_b, maximum_solutions, time_limit, penalty_gap, schedule_validation
                FROM schedule_parameters
                LIMIT 1
            """)
            params = cursor.fetchone()
            if not params:
                return jsonify({'success': False, 'message': 'Schedule parameters not found'}), 404
            return jsonify({
                'success': True,
                'parameters': {
                    'weight_mode_a': float(params[0]) if params[0] is not None else None,
                    'weight_mode_b': int(params[1]) if params[1] is not None else None,
                    'maximum_solutions': int(params[2]) if params[2] is not None else None,
                    'time_limit': int(params[3]) if params[3] is not None else None,
                    'penalty_gap': int(params[4]) if params[4] is not None else None,
                    'schedule_validation': int(params[5]) if params[5] is not None else 0
                }
            })
        else:  # POST or PUT
            data = request.json or {}
            weight_mode_a = data.get('weight_mode_a')
            weight_mode_b = data.get('weight_mode_b')
            maximum_solutions = data.get('maximum_solutions')
            time_limit = data.get('time_limit')
            penalty_gap = data.get('penalty_gap')
            schedule_validation = data.get('schedule_validation', 0)

            # Basic validation (ensure not None)
            if any(v is None for v in [weight_mode_a, weight_mode_b, penalty_gap, maximum_solutions, time_limit]):
                return jsonify({'success': False, 'message': 'All parameters are required'}), 400

            # Update single row (assumes id=1)
            cursor.execute("""
                UPDATE schedule_parameters
                SET weight_mode_a = %s,
                    weight_mode_b = %s,
                    penalty_gap = %s,
                    maximum_solutions = %s,
                    time_limit = %s,
                    schedule_validation = %s
                WHERE id = 1
            """, (
                weight_mode_a,
                weight_mode_b,
                penalty_gap,
                maximum_solutions,
                time_limit,
                schedule_validation
            ))
            current_app.mysql.connection.commit()
            return jsonify({'success': True, 'message': 'Schedule parameters updated successfully'})

    except Exception as e:
        current_app.mysql.connection.rollback()
        current_app.logger.error(f"Error in system adjustments schedule: {str(e)}")
        return jsonify({'success': False, 'message': 'Error processing request', 'details': str(e)}), 500

    finally:
        if cursor:
            cursor.close()

@admin_bp.route('/system_adjustments/logs', methods=['GET'])
@admin_required
def get_parameter_logs():
    """Get parameter change logs with optional filtering"""
    admin = session.get('admin')
    cursor = None
    try:
        cursor = current_app.mysql.connection.cursor()
        
        # Get query parameters for filtering
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        change_type = request.args.get('change_type')  # 'system' or 'student'
        student_id = request.args.get('student_id')
        column_name = request.args.get('column_name')  # Filter by specific parameter
        
        # Build the query with optional filters
        query = """
            SELECT 
                pcl.log_id,
                pcl.changed_at,
                CONCAT(a.first_name, ' ', a.last_name) as admin_name,
                pcl.change_type,
                pcl.student_id,
                CASE 
                    WHEN pcl.student_id IS NOT NULL THEN CONCAT(s.first_name, ' ', s.last_name)
                    ELSE NULL
                END as student_name,
                pcl.column_name,
                pcl.old_value,
                pcl.new_value
            FROM parameter_changes_log pcl
            LEFT JOIN admin a ON pcl.changed_by_admin = a.admin_id
            LEFT JOIN student s ON pcl.student_id = s.student_id
            WHERE 1=1
        """
        
        params = []
        
        if start_date:
            query += " AND pcl.changed_at >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND pcl.changed_at <= %s"
            params.append(end_date)
        
        if change_type:
            query += " AND pcl.change_type = %s"
            params.append(change_type)
        
        if student_id:
            query += " AND pcl.student_id = %s"
            params.append(student_id)
        
        if column_name:
            # Check if column_name contains multiple values (comma-separated)
            if ',' in column_name:
                column_names = column_name.split(',')
                placeholders = ', '.join(['%s'] * len(column_names))
                query += f" AND pcl.column_name IN ({placeholders})"
                params.extend(column_names)
            else:
                query += " AND pcl.column_name = %s"
                params.append(column_name)
        
        # Order by most recent first
        query += " ORDER BY pcl.changed_at DESC LIMIT 500"
        
        # Execute the query
        cursor.execute(query, params)
        
        # Format the results
        logs = []
        for row in cursor.fetchall():
            logs.append({
                'log_id': row[0],
                'changed_at': row[1].strftime('%Y-%m-%d %H:%M:%S'),
                'admin_name': row[2],
                'change_type': row[3],
                'student_id': row[4],
                'student_name': row[5],
                'column_name': row[6],
                'old_value': row[7],
                'new_value': row[8]
            })
        
        return jsonify({
            'success': True,
            'logs': logs
        })
    
    except Exception as e:
        current_app.logger.error(f"Error fetching parameter logs: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error fetching parameter logs',
            'details': str(e)
        }), 500
    
    finally:
        if cursor:
            cursor.close()

def get_major_minor_status(cursor):
    """Get the current status of major/minor selection period"""
    current_app.logger.info("Checking major/minor selection status")
    
    # Check for scheduled periods that should be activated
    current_app.logger.info("Checking for scheduled periods that should be activated")
    cursor.execute("""
        UPDATE major_minor_selection_window 
        SET status = 'open'
        WHERE status = 'scheduled' 
        AND start_date <= NOW()
    """)
    activated_rows = cursor.rowcount
    current_app.logger.info(f"Activated {activated_rows} scheduled periods")
    current_app.mysql.connection.commit()
    
    # Check for open periods that should be auto-closed
    current_app.logger.info("Checking for open periods that should be auto-closed")
    cursor.execute("""
        UPDATE major_minor_selection_window 
        SET status = 'closed',
            closed_at = NOW(),
            closed_by_admin = NULL
        WHERE status = 'open' 
        AND end_date <= NOW()
    """)
    closed_rows = cursor.rowcount
    current_app.logger.info(f"Auto-closed {closed_rows} open periods")
    current_app.mysql.connection.commit()
    
    # Get current active period
    current_app.logger.info("Getting current active period")
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
        current_app.logger.info(f"Found active period: status={status}, start_date={start_date}, end_date={end_date}")
        return {
            'success': True,
            'is_open': status == 'open',
            'is_scheduled': status == 'scheduled',
            'start_date': start_date.strftime('%Y-%m-%d %H:%M:%S') if start_date else None,
            'end_date': end_date.strftime('%Y-%m-%d %H:%M:%S') if end_date else None
        }
    else:
        current_app.logger.info("No active period found")
        return {
            'success': True,
            'is_open': False,
            'is_scheduled': False
        }

def start_major_minor_selection(cursor, admin_id, start_date, end_date):
    """Start a new major/minor selection period"""
    try:
        current_app.logger.info(f"Starting major/minor selection with admin_id={admin_id}, start_date={start_date}, end_date={end_date}")
        
        # Close any existing open or scheduled periods
        cursor.execute("UPDATE major_minor_selection_window SET status = 'closed' WHERE status IN ('open', 'scheduled')")
        current_app.logger.info(f"Closed existing periods. Rows affected: {cursor.rowcount}")
        
        # Determine status based on start date
        status = 'scheduled' if start_date > datetime.now() else 'open'
        current_app.logger.info(f"New period status will be: {status}")
        
        # Insert new period
        current_app.logger.info("Inserting new period into major_minor_selection_window")
        cursor.execute("""
            INSERT INTO major_minor_selection_window (start_date, end_date, status, opened_by_admin, opened_at)
            VALUES (%s, %s, %s, %s, NOW())
        """, (start_date, end_date, status, admin_id))
        
        current_app.logger.info(f"Insert successful. Last row ID: {cursor.lastrowid}")
        current_app.mysql.connection.commit()
        current_app.logger.info("Transaction committed")
        
        return {
            'success': True,
            'message': f'Major/Minor selection period {"scheduled" if status == "scheduled" else "opened"} successfully',
            'start_date': start_date.strftime('%Y-%m-%d %H:%M:%S'),
            'end_date': end_date.strftime('%Y-%m-%d %H:%M:%S'),
            'is_scheduled': status == 'scheduled'
        }
    except Exception as e:
        current_app.logger.error(f"Error in start_major_minor_selection: {str(e)}")
        raise

def close_major_minor_selection(cursor, admin_id):
    """Close an active major/minor selection period"""
    # Add logging to help diagnose the issue
    current_app.logger.info(f"Closing major/minor selection with admin_id={admin_id}")
    
    cursor.execute("""
        UPDATE major_minor_selection_window 
        SET status = 'closed',
            closed_at = NOW(),
            closed_by_admin = %s
        WHERE status IN ('open', 'scheduled')
    """, (admin_id,))
    
    affected = cursor.rowcount
    current_app.logger.info(f"Rows affected by close_major_minor_selection: {affected}")
    current_app.mysql.connection.commit()
    
    if affected > 0:
        current_app.logger.info("Major/Minor selection period closed successfully")
        return {
            'success': True,
            'message': 'Major/Minor selection period closed successfully'
        }
    else:
        current_app.logger.warning("No active Major/Minor selection period found")
        return {
            'success': False,
            'message': 'No active Major/Minor selection period found'
        }

def cancel_major_minor_selection(cursor, admin_id):
    """Cancel a scheduled major/minor selection period"""
    # Add logging to help diagnose the issue
    current_app.logger.info(f"Canceling scheduled major/minor selection with admin_id={admin_id}")
    
    cursor.execute("""
        UPDATE major_minor_selection_window 
        SET status = 'closed',
            closed_at = NOW(),
            closed_by_admin = %s
        WHERE status = 'scheduled'
    """, (admin_id,))
    
    affected = cursor.rowcount
    current_app.logger.info(f"Rows affected by cancel_major_minor_selection: {affected}")
    current_app.mysql.connection.commit()
    
    if affected > 0:
        current_app.logger.info("Scheduled Major/Minor selection period cancelled successfully")
        return {
            'success': True,
            'message': 'Scheduled Major/Minor selection period cancelled successfully'
        }
    else:
        current_app.logger.warning("No scheduled Major/Minor selection period found")
        return {
            'success': False,
            'message': 'No scheduled Major/Minor selection period found'
        }

@admin_bp.route('/major_minor_selection', methods=['GET', 'POST'])
def major_minor_selection():
    """Endpoint for managing major/minor selection period"""
    admin = session.get('admin')
    if not admin:
        current_app.logger.error("Admin not logged in for major_minor_selection")
        return jsonify({'success': False, 'message': 'Admin not logged in'}), 401
    
    cursor = None
    try:
        cursor = current_app.mysql.connection.cursor()
        
        if request.method == 'GET':
            current_app.logger.info("GET request to major_minor_selection")
            return jsonify(get_major_minor_status(cursor))
        
        # POST method for actions
        current_app.logger.info("POST request to major_minor_selection")
        data = request.get_json()
        current_app.logger.info(f"Request data: {data}")
        
        if not data:
            current_app.logger.error("No data provided in request")
            return jsonify({'success': False, 'message': 'No data provided'}), 400
        
        action = data.get('action')
        admin_id = admin.get('admin_id')
        current_app.logger.info(f"Action: {action}, Admin ID: {admin_id}")
        
        if action == 'start_selection':
            start_date = data.get('start_date')
            end_date = data.get('end_date')
            current_app.logger.info(f"Start date: {start_date}, End date: {end_date}")
            
            if not start_date or not end_date:
                current_app.logger.error("Missing start_date or end_date")
                return jsonify({'success': False, 'message': 'Start date and end date are required'}), 400
            
            # Validate dates
            dates, error = validate_selection_dates(start_date, end_date)
            if error:
                current_app.logger.error(f"Date validation error: {error}")
                return error
                
            start_date, end_date = dates
            current_app.logger.info(f"Calling start_major_minor_selection with admin_id={admin_id}, start_date={start_date}, end_date={end_date}")
            return jsonify(start_major_minor_selection(cursor, admin_id, start_date, end_date))
            
        elif action == 'close_selection':
            return jsonify(close_major_minor_selection(cursor, admin_id))
            
        elif action == 'cancel_selection':
            return jsonify(cancel_major_minor_selection(cursor, admin_id))
            
        else:
            return jsonify({'success': False, 'message': 'Invalid action'}), 400
            
    except Exception as e:
        current_app.logger.error(f"Error in major/minor selection management: {str(e)}")
        current_app.logger.exception("Full exception details:")
        if cursor:
            current_app.mysql.connection.rollback()
        return jsonify({
            'success': False,
            'message': 'Error processing request',
            'details': str(e)
        }), 500
    finally:
        if cursor:
            cursor.close()

def validate_selection_dates(start_date, end_date):
    """Validate selection start and end dates"""
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
        end_date = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')

        now = datetime.now()
        if end_date < now:
            return None, jsonify({'success': False, 'message': 'End date must be in the future'}), 400

        if start_date >= end_date:
            return None, jsonify({'success': False, 'message': 'Start date must be before end date'}), 400

        return (start_date, end_date), None

    except ValueError as e:
        current_app.logger.error(f"Invalid date format: {str(e)}")
        return None, jsonify({'success': False, 'message': 'Invalid date format. Use YYYY-MM-DD HH:MM:SS'}), 400

@admin_bp.route('/statistics', methods=['GET'])
@admin_required
def get_statistics():
    """Get various statistics about courses, enrollments, and student performance"""
    admin = session.get('admin')
    
    # Get filter parameters from request
    year = request.args.get('year', 'all')
    semester = request.args.get('semester', 'all')
    
    # Check if this is a direct counting query
    count_type = request.args.get('count_type')
    query_type = request.args.get('query')
    chart_type = request.args.get('chart_type')
    
    # Handle chart data requests
    if chart_type == 'student_levels':
        return get_student_levels_data()
    elif chart_type == 'major_distribution':
        return get_major_distribution_data()
    elif chart_type == 'graduation_time':
        return get_graduation_time_data()
    
    if count_type == 'enrolled_students':
        # Count enrolled students
        return get_enrolled_students_count()
    
    if count_type == 'curriculum_courses':
        # Count courses in curriculum
        return get_curriculum_courses_count()
    
    if query_type == 'direct':
        # Handle direct database queries
        query_for = request.args.get('type')
        if query_for == 'students':
            status = request.args.get('status', 'enrolled')
            return get_direct_student_count(status)
        elif query_for == 'courses':
            in_curriculum = request.args.get('in_curriculum', '1')
            return get_direct_courses_count(in_curriculum)
    
    # Regular statistics query
    current_app.logger.info(f"Getting statistics with filters - year: {year}, semester: {semester}")
    
    cursor = None
    try:
        cursor = get_db_cursor()
        
        # Get all available years from date column (not year column)
        cursor.execute("SELECT DISTINCT YEAR(date) AS academic_year FROM add_course ORDER BY academic_year DESC")
        years = [str(row[0]) for row in cursor.fetchall()]
        
        cursor.execute("SELECT DISTINCT semester FROM add_course ORDER BY semester")
        semesters = [str(row[0]) for row in cursor.fetchall()]
        
        # Build the WHERE clause for filtering
        where_conditions = []
        params = []
        
        if year != 'all':
            try:
                year_int = int(year)
                where_conditions.append("YEAR(date) = %s")
                params.append(year_int)
                current_app.logger.info(f"Adding year filter: {year_int}")
            except (ValueError, TypeError) as e:
                current_app.logger.error(f"Invalid year parameter: {year}, error: {str(e)}")
                return jsonify({'success': False, 'message': f'Invalid year parameter: {year}'}), 400
        
        if semester != 'all':
            try:
                semester_int = int(semester)
                where_conditions.append("semester = %s")
                params.append(semester_int)
                current_app.logger.info(f"Adding semester filter: {semester_int}")
            except (ValueError, TypeError) as e:
                current_app.logger.error(f"Invalid semester parameter: {semester}, error: {str(e)}")
                return jsonify({'success': False, 'message': f'Invalid semester parameter: {semester}'}), 400
        
        # Default WHERE clause includes status filter
        base_where = "status IN ('passed', 'failed')"
        
        # Complete WHERE clause
        if where_conditions:
            where_clause = f"WHERE {base_where} AND {' AND '.join(where_conditions)}"
        else:
            where_clause = f"WHERE {base_where}"
            
        current_app.logger.info(f"Where clause: {where_clause}, params: {params}")
        
        try:
            # Query for first-time pass rates
            # For each student and course, find their first attempt by selecting the one with the smallest ID
            first_time_query = f"""
            WITH FirstAttempts AS (
                SELECT 
                    ac.*,
                    ROW_NUMBER() OVER (PARTITION BY student_id, course_code ORDER BY id ASC) as attempt_num
                FROM add_course ac
                {where_clause}
            ),
            FirstTimeResults AS (
                SELECT 
                    course_code,
                    COUNT(*) as total_first_attempts,
                    SUM(CASE WHEN status = 'passed' THEN 1 ELSE 0 END) as passed_first_time
                FROM FirstAttempts
                WHERE attempt_num = 1
                GROUP BY course_code
                HAVING COUNT(*) > 0
            )
            SELECT 
                course_code,
                total_first_attempts,
                passed_first_time,
                passed_first_time / total_first_attempts as first_time_pass_rate
            FROM FirstTimeResults
            """
            
            current_app.logger.debug(f"First time query: {first_time_query}")
            current_app.logger.debug(f"Params: {params}")
            cursor.execute(first_time_query, params)
            first_time_results = {}
            
            for row in cursor.fetchall():
                course_code, total_attempts, passed, pass_rate = row
                first_time_results[course_code] = {
                    'total_first_attempts': total_attempts,
                    'passed_first_time': passed,
                    'first_time_pass_rate': float(pass_rate) if pass_rate is not None else 0
                }
            
            # General stats WHERE clause includes status for enrolled/passed/failed
            if where_conditions:
                general_where = f"WHERE status IN ('passed', 'failed', 'enrolled') AND {' AND '.join(where_conditions)}"
            else:
                general_where = "WHERE status IN ('passed', 'failed', 'enrolled')"
                
            # Query for forgiveness usage and average grades
            general_query = f"""
            SELECT 
                course_code,
                COUNT(DISTINCT student_id) AS total_students,
                SUM(CASE WHEN forgiveness = 1 THEN 1 ELSE 0 END) AS forgiveness_count,
                COUNT(DISTINCT CASE WHEN forgiveness = 1 THEN student_id END) AS students_using_forgiveness,
                AVG(grade_point) AS average_grade
            FROM add_course
            {general_where}
            GROUP BY course_code
            """
            
            current_app.logger.debug(f"General query: {general_query}")
            current_app.logger.debug(f"Params: {params}")
            cursor.execute(general_query, params)
            
            # Create a dictionary to store all course statistics
            all_course_stats = {}
            
            # First, populate with first_time_results
            for course_code, data in first_time_results.items():
                all_course_stats[course_code] = {
                    'course_code': course_code,
                    'first_time_pass_rate': data['first_time_pass_rate'],
                    'total_students': 0,
                    'forgiveness_percentage': 0,
                    'average_grade': 0
                }
            
            # Then add the general statistics
            for row in cursor.fetchall():
                course_code = row[0]
                total_students = row[1] or 0
                students_using_forgiveness = row[3] or 0
                avg_grade = row[4]
                
                # Calculate forgiveness percentage (students who used forgiveness / total students)
                forgiveness_percentage = students_using_forgiveness / total_students if total_students > 0 else 0
                
                # Check if the course is already in our results
                if course_code in all_course_stats:
                    all_course_stats[course_code].update({
                        'total_students': total_students,
                        'forgiveness_percentage': forgiveness_percentage,
                        'average_grade': float(avg_grade) if avg_grade is not None else 0
                    })
                else:
                    all_course_stats[course_code] = {
                        'course_code': course_code,
                        'first_time_pass_rate': 0,  # Course wasn't in first_time_results
                        'total_students': total_students,
                        'forgiveness_percentage': forgiveness_percentage,
                        'average_grade': float(avg_grade) if avg_grade is not None else 0
                    }
            
            # Convert the dictionary to a list for the response
            course_statistics = list(all_course_stats.values())
            
            current_app.logger.info(f"Returning statistics for {len(course_statistics)} courses")
            return jsonify({
                'success': True,
                'years': years,
                'semesters': semesters,
                'course_statistics': course_statistics
            })
        except Exception as e:
            current_app.logger.error(f"Error executing statistics queries: {str(e)}")
            import traceback
            current_app.logger.error(traceback.format_exc())
            return jsonify({'success': False, 'message': f'Error processing statistics: {str(e)}'}), 500
        
    except Exception as e:
        current_app.logger.error(f"Error in get_statistics: {str(e)}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return jsonify({'success': False, 'message': f'An error occurred: {str(e)}'}), 500
    
    finally:
        if cursor:
            cursor.close()


def get_student_levels_data():
    """Get student distribution by academic level"""
    try:
        cursor = get_db_cursor()
        
        # Query for student levels distribution
        query = """
        SELECT 
            level, 
            COUNT(*) as count
        FROM 
            student
        WHERE 
            enrollment_status = 'enrolled'
        GROUP BY 
            level
        ORDER BY 
            CASE 
                WHEN level = 'Freshman' THEN 1
                WHEN level = 'Sophomore' THEN 2
                WHEN level = 'Junior' THEN 3
                WHEN level = 'Senior' THEN 4
                ELSE 5
            END
        """
        
        cursor.execute(query)
        
        levels_data = []
        for row in cursor.fetchall():
            levels_data.append({
                'level': row[0],
                'count': row[1]
            })
        
        return jsonify({
            'success': True,
            'levels_data': levels_data
        })
        
    except Exception as e:
        return handle_db_error(e, "Failed to retrieve student levels data")


def get_major_distribution_data():
    """Get student distribution by major (including second majors)"""
    try:
        cursor = get_db_cursor()
        
        # Query for major distribution
        query = """
        SELECT 
            major_type, 
            COUNT(*) as count
        FROM (
            SELECT major as major_type FROM student WHERE major IS NOT NULL AND major != ''
            UNION ALL
            SELECT second_major as major_type FROM student WHERE second_major IS NOT NULL AND second_major != ''
        ) as all_majors
        GROUP BY 
            major_type
        ORDER BY 
            count DESC
        """
        
        cursor.execute(query)
        
        major_data = []
        total_majors = 0
        
        for row in cursor.fetchall():
            count = row[1]
            major_data.append({
                'major_type': row[0],
                'count': count
            })
            total_majors += count
        
        return jsonify({
            'success': True,
            'major_data': major_data,
            'total_majors': total_majors
        })
        
    except Exception as e:
        return handle_db_error(e, "Failed to retrieve major distribution data")


def get_enrolled_students_count():
    """Get count of currently enrolled students"""
    try:
        cursor = get_db_cursor()
        
        # Query for enrolled students count
        query = """
        SELECT 
            COUNT(*) as enrolled_count
        FROM 
            student
        WHERE 
            enrollment_status = 'enrolled'
        """
        
        cursor.execute(query)
        result = cursor.fetchone()
        
        enrolled_count = result[0] if result else 0
        
        return jsonify({
            'success': True,
            'enrolled_count': enrolled_count
        })
        
    except Exception as e:
        return handle_db_error(e, "Failed to retrieve enrolled students count")


def get_curriculum_courses_count():
    """Get count of courses in curriculum"""
    try:
        cursor = get_db_cursor()
        
        # Query for curriculum courses count
        query = """
        SELECT 
            COUNT(*) as courses_count
        FROM 
            courses
        WHERE 
            in_curriculum = 1
        """
        
        cursor.execute(query)
        result = cursor.fetchone()
        
        courses_count = result[0] if result else 0
        
        return jsonify({
            'success': True,
            'courses_count': courses_count
        })
        
    except Exception as e:
        return handle_db_error(e, "Failed to retrieve curriculum courses count")


def get_direct_student_count(status='enrolled'):
    """Get direct count of students with specified status"""
    try:
        cursor = get_db_cursor()
        
        # Query for student count
        query = """
        SELECT 
            COUNT(*) as count
        FROM 
            student
        WHERE 
            enrollment_status = %s
        """
        
        cursor.execute(query, (status,))
        result = cursor.fetchone()
        
        count = result[0] if result else 0
        
        return jsonify({
            'success': True,
            'count': count
        })
        
    except Exception as e:
        return handle_db_error(e, "Failed to retrieve student count")


def get_direct_courses_count(in_curriculum='1'):
    """Get direct count of courses with specified curriculum status"""
    try:
        cursor = get_db_cursor()
        
        # Query for courses count
        query = """
        SELECT 
            COUNT(*) as count
        FROM 
            courses
        WHERE 
            in_curriculum = %s
        """
        
        cursor.execute(query, (in_curriculum,))
        result = cursor.fetchone()
        
        count = result[0] if result else 0
        
        return jsonify({
            'success': True,
            'count': count
        })
        
    except Exception as e:
        return handle_db_error(e, "Failed to retrieve courses count")


def get_graduation_time_data():
    """Get statistics on how many years it takes students to graduate"""
    try:
        cursor = get_db_cursor()
        
        # Query for graduation time distribution - count graduates grouped by year_of_study
        query = """
        SELECT 
            year_of_study as years_to_graduate, 
            COUNT(*) as count
        FROM 
            student
        WHERE 
            enrollment_status = 'graduated'
            AND year_of_study IS NOT NULL
        GROUP BY 
            year_of_study
        ORDER BY 
            year_of_study
        """
        
        cursor.execute(query)
        
        graduation_data = []
        for row in cursor.fetchall():
            graduation_data.append({
                'years': row[0],
                'count': row[1]
            })
        
        return jsonify({
            'success': True,
            'graduation_data': graduation_data
        })
        
    except Exception as e:
        return handle_db_error(e, "Failed to retrieve graduation time data")

@admin_bp.route('/course_registration/drop_requests', methods=['GET'])
def get_drop_course_requests():
    try:
        # Check admin authentication
        admin_id = check_admin_auth()
        if not admin_id:
            return jsonify({'success': False, 'message': 'Not authorized'}), 401
        
        cursor = get_db_cursor()
        
        # Get all pending drop course requests with student information
        # Removed the join with course table that doesn't exist
        cursor.execute("""
            SELECT dcr.id, dcr.student_id, dcr.course_code, dcr.status, dcr.request_date, dcr.type,
                   s.first_name, s.last_name, s.national_id
            FROM drop_course_requests dcr
            JOIN student s ON dcr.student_id = s.student_id
            ORDER BY dcr.request_date DESC
        """)
        
        requests = []
        for row in cursor.fetchall():
            request_date = row[4].strftime('%Y-%m-%d %H:%M:%S') if row[4] else None
            requests.append({
                'id': row[0],
                'student_id': row[1],
                'course_code': row[2],
                'status': row[3],
                'request_date': request_date,
                'type': row[5],
                'student_name': f"{row[6]} {row[7]}",
                'national_id': row[8],
                'course_name': row[2],  # Use course code as course name since we don't have course table
                'credits': "N/A"  # Set credits to N/A since we don't have course table
            })
        
        cursor.close()
        return jsonify({'success': True, 'requests': requests})
    
    except Exception as e:
        current_app.logger.error(f"Error getting drop course requests: {str(e)}")
        return handle_db_error(e, "Failed to load drop course requests")

@admin_bp.route('/course_registration/drop_requests/<int:request_id>', methods=['PUT'])
def handle_drop_request(request_id):
    try:
        # Debug the incoming request
        current_app.logger.info(f"Received request to handle drop request {request_id}")
        current_app.logger.info(f"Request JSON: {request.json}")
        
        # Check admin authentication
        admin_id = check_admin_auth()
        if not admin_id:
            current_app.logger.warning(f"Unauthorized attempt to handle drop request {request_id}")
            return jsonify({'success': False, 'message': 'Not authorized'}), 401
        
        current_app.logger.info(f"Admin {admin_id} handling drop request {request_id}")
        
        data = request.json
        current_app.logger.info(f"Request data: {data}")
        
        if not data or 'action' not in data:
            current_app.logger.warning(f"Missing action in request data: {data}")
            return jsonify({'success': False, 'message': 'Missing required data'}), 400
        
        action = data['action']
        if action not in ['approve', 'reject']:
            current_app.logger.warning(f"Invalid action '{action}' for request {request_id}")
            return jsonify({'success': False, 'message': 'Invalid action'}), 400
        
        cursor = get_db_cursor()
        
        # Check the structure of the drop_course_requests table
        try:
            cursor.execute("DESCRIBE drop_course_requests")
            columns = {row[0]: row[1] for row in cursor.fetchall()}
            current_app.logger.info(f"drop_course_requests table columns: {columns}")
        except Exception as e:
            current_app.logger.error(f"Error checking drop_course_requests table: {str(e)}")
        
        # Get request details
        cursor.execute("""
            SELECT student_id, course_code, type
            FROM drop_course_requests
            WHERE id = %s AND status = 'pending'
        """, (request_id,))
        
        request_data = cursor.fetchone()
        current_app.logger.info(f"Request data from DB: {request_data}")
        
        if not request_data:
            cursor.close()
            current_app.logger.warning(f"Drop request {request_id} not found or already processed")
            return jsonify({'success': False, 'message': 'Drop request not found or already processed'}), 404
        
        student_id, course_code, request_type = request_data
        current_app.logger.info(f"Processing request: student_id={student_id}, course_code={course_code}, type={request_type}")
        
        if action == 'approve':
            # Handle based on request type
            if request_type in ['Retake', 'Extra']:
                # Delete the course enrollment
                current_app.logger.info(f"Deleting course enrollment for {student_id}, {course_code} (type: {request_type})")
                sql = """
                    DELETE FROM add_course
                    WHERE student_id = %s AND course_code = %s AND status = 'enrolled'
                """
                params = (student_id, course_code)
                current_app.logger.info(f"Executing SQL: {sql} with params: {params}")
                cursor.execute(sql, params)
                
                # Check if any rows were affected
                if cursor.rowcount == 0:
                    current_app.logger.warning(f"No enrolled course found for {student_id}, {course_code}")
                    cursor.close()
                    return jsonify({
                        'success': False, 
                        'message': 'Course enrollment not found'
                    }), 400
                
                current_app.logger.info(f"Deleted {cursor.rowcount} course enrollment(s)")
                
            elif request_type in ['Current', 'Skipped']:
                # Update status to notenrolled
                current_app.logger.info(f"Updating course status to notenrolled for {student_id}, {course_code} (type: {request_type})")
                
                try:
                    sql = """
                        UPDATE add_course
                        SET status = 'notenrolled', handled_by_admin = %s
                        WHERE student_id = %s AND course_code = %s AND status = 'enrolled'
                    """
                    # Ensure admin_id is an integer
                    admin_id_int = int(admin_id) if admin_id is not None else None
                    params = (admin_id_int, student_id, course_code)
                    current_app.logger.info(f"Executing SQL: {sql} with params: {params}")
                    cursor.execute(sql, params)
                except Exception as e:
                    # If that fails, try without the handled_by_admin field
                    current_app.logger.warning(f"Error updating add_course: {str(e)}. Trying without handled_by_admin.")
                    sql = """
                        UPDATE add_course
                        SET status = 'notenrolled'
                        WHERE student_id = %s AND course_code = %s AND status = 'enrolled'
                    """
                    params = (student_id, course_code)
                    current_app.logger.info(f"Executing SQL: {sql} with params: {params}")
                    cursor.execute(sql, params)
                
                # Check if any rows were affected
                if cursor.rowcount == 0:
                    current_app.logger.warning(f"No enrolled course found for {student_id}, {course_code}")
                    cursor.close()
                    return jsonify({
                        'success': False, 
                        'message': 'Course enrollment not found'
                    }), 400
                
                current_app.logger.info(f"Updated {cursor.rowcount} course enrollment(s)")
            
            # Update request status to approved
            try:
                current_app.logger.info(f"Updating request {request_id} status to approved")
                sql = """
                    UPDATE drop_course_requests
                    SET status = 'approved', handled_by_admin = %s
                    WHERE id = %s
                """
                # Ensure admin_id is an integer
                admin_id_int = int(admin_id) if admin_id is not None else None
                params = (admin_id_int, request_id)
                current_app.logger.info(f"Executing SQL: {sql} with params: {params}")
                cursor.execute(sql, params)
            except Exception as e:
                # If that fails, try without the handled_by_admin field
                current_app.logger.warning(f"Error updating drop_course_requests: {str(e)}. Trying without handled_by_admin.")
                sql = """
                    UPDATE drop_course_requests
                    SET status = 'approved'
                    WHERE id = %s
                """
                params = (request_id,)
                current_app.logger.info(f"Executing SQL: {sql} with params: {params}")
                cursor.execute(sql, params)
            
        elif action == 'reject':
            # Update request status to rejected
            try:
                current_app.logger.info(f"Updating request {request_id} status to rejected")
                sql = """
                    UPDATE drop_course_requests
                    SET status = 'rejected', handled_by_admin = %s
                    WHERE id = %s
                """
                # Ensure admin_id is an integer
                admin_id_int = int(admin_id) if admin_id is not None else None
                params = (admin_id_int, request_id)
                current_app.logger.info(f"Executing SQL: {sql} with params: {params}")
                cursor.execute(sql, params)
            except Exception as e:
                # If that fails, try without the handled_by_admin field
                current_app.logger.warning(f"Error updating drop_course_requests: {str(e)}. Trying without handled_by_admin.")
                sql = """
                    UPDATE drop_course_requests
                    SET status = 'rejected'
                    WHERE id = %s
                """
                params = (request_id,)
                current_app.logger.info(f"Executing SQL: {sql} with params: {params}")
                cursor.execute(sql, params)
        
        current_app.mysql.connection.commit()
        cursor.close()
        
        current_app.logger.info(f"Successfully {action}d request {request_id}")
        return jsonify({
            'success': True, 
            'message': f'Request {action}d successfully',
            'action': action,
            'request_id': request_id
        })
    
    except Exception as e:
        current_app.logger.error(f"Error handling drop course request {request_id}: {str(e)}")
        return handle_db_error(e, f"Failed to {action} drop course request")

@admin_bp.route('/course_registration/forgiveness', methods=['GET'])
def get_forgiveness_requests():
    """Get forgiveness policy requests with optional status filter"""
    try:
        # Verify admin authentication
        admin_data = check_admin_auth()
        if not admin_data:
            return jsonify({'success': False, 'message': 'Admin authentication required'}), 401
        
        # Get status filter from query parameters - default to 'pending' if not specified
        status_filter = request.args.get('status', 'pending')
        
        # Log the status filter for debugging
        current_app.logger.info(f"Getting forgiveness requests with status filter: {status_filter}")
        
        cursor = get_db_cursor()
        
        # Build the WHERE clause based on the status filter
        where_clause = ""
        if status_filter == 'pending':
            where_clause = "WHERE fr.status = 'pending'"
        elif status_filter == 'processed':
            where_clause = "WHERE fr.status IN ('approved', 'rejected')"
        elif status_filter == 'all':
            where_clause = ""  # No filter
        else:
            where_clause = f"WHERE fr.status = '{status_filter}'"  # Specific status
            
        # Query to get forgiveness requests with student info
        query = f"""
            SELECT 
                fr.id,
                fr.student_id,
                s.first_name,
                s.last_name,
                s.national_id,
                fr.course_code,
                fr.status,
                fr.handled_by_admin,
                fr.request_date,
                fr.handling_date,
                fr.forgiven_grade,
                fr.new_grade,
                fr.academic_year,
                a.first_name as admin_first_name,
                a.last_name as admin_last_name,
                fr.add_id
            FROM 
                forgiveness_requests fr
            JOIN 
                student s ON fr.student_id = s.student_id
            LEFT JOIN
                admin a ON fr.handled_by_admin = a.admin_id
            {where_clause}
            ORDER BY
                CASE WHEN fr.status = 'pending' THEN 0 
                     WHEN fr.status = 'approved' THEN 1
                     ELSE 2 END,
                fr.request_date DESC
        """
        
        cursor.execute(query)
        
        requests = []
        columns = [desc[0] for desc in cursor.description]
        
        for row in cursor.fetchall():
            request_data = dict(zip(columns, row))
            # Format dates for JSON response
            if request_data['request_date']:
                request_data['request_date'] = request_data['request_date'].strftime('%Y-%m-%d %H:%M:%S')
            if request_data['handling_date']:
                request_data['handling_date'] = request_data['handling_date'].strftime('%Y-%m-%d %H:%M:%S')
            requests.append(request_data)
        
        return jsonify({
            'success': True,
            'requests': requests
        })
        
    except Exception as e:
        return handle_db_error(e, "Failed to retrieve forgiveness requests")

@admin_bp.route('/course_registration/forgiveness/<int:request_id>', methods=['PUT'])
def handle_forgiveness_request(request_id):
    """Handle a forgiveness policy request (approve or reject)"""
    try:
        # Debug the incoming request
        current_app.logger.info(f"Received request to handle forgiveness request {request_id}")
        current_app.logger.info(f"Request JSON: {request.json}")
        
        # Verify admin authentication
        admin_data, error = check_admin_auth()
        if error:
            current_app.logger.warning(f"Unauthorized attempt to handle forgiveness request {request_id}")
            return error
        
        admin_id = admin_data.get('admin_id')
        current_app.logger.info(f"Admin {admin_id} handling forgiveness request {request_id}")
        
        # Get request data from body
        data = request.json
        current_app.logger.info(f"Request data: {data}")
        
        if not data or 'action' not in data:
            current_app.logger.warning(f"Missing action in request data: {data}")
            return jsonify({'success': False, 'message': 'Missing required parameters'}), 400
        
        action = data.get('action')
        
        if action not in ['approve', 'reject']:
            current_app.logger.warning(f"Invalid action '{action}' for request {request_id}")
            return jsonify({'success': False, 'message': 'Invalid action'}), 400
        
        cursor = get_db_cursor()
        
        # Check the structure of the forgiveness_requests table
        try:
            cursor.execute("DESCRIBE forgiveness_requests")
            columns = {row[0]: row[1] for row in cursor.fetchall()}
            current_app.logger.info(f"forgiveness_requests table columns: {columns}")
        except Exception as e:
            current_app.logger.error(f"Error checking forgiveness_requests table: {str(e)}")
        
        # Check if request exists and is pending
        cursor.execute("""
            SELECT id, status, student_id, course_code, forgiven_grade, new_grade, add_id
            FROM forgiveness_requests
            WHERE id = %s
        """, (request_id,))
        
        request_data = cursor.fetchone()
        current_app.logger.info(f"Request data from DB: {request_data}")
        
        if not request_data:
            cursor.close()
            current_app.logger.warning(f"Forgiveness request {request_id} not found")
            return jsonify({'success': False, 'message': 'Request not found'}), 404
        
        if request_data[1] != 'pending':
            cursor.close()
            current_app.logger.warning(f"Forgiveness request {request_id} has already been {request_data[1]}")
            return jsonify({'success': False, 'message': f'Request has already been {request_data[1]}'}), 400
        
        # Update request status - SIMPLIFIED
        status = 'approved' if action == 'approve' else 'rejected'
        
        try:
            # Ensure admin_id is an integer
            admin_id_int = int(admin_id) if admin_id is not None else None
            current_app.logger.info(f"Updating request {request_id} status to {status}")
            
            sql = """
                UPDATE forgiveness_requests
                SET status = %s,
                    handled_by_admin = %s,
                    handling_date = NOW()
                WHERE id = %s
            """
            params = (status, admin_id_int, request_id)
            current_app.logger.info(f"Executing SQL: {sql} with params: {params}")
            cursor.execute(sql, params)
            
            # If approved, update the forgiveness flag in add_course table
            if status == 'approved' and request_data[6]:  # Check if add_id exists
                add_id = request_data[6]
                current_app.logger.info(f"Setting forgiveness flag for add_course record with id={add_id}")
                
                update_sql = """
                    UPDATE add_course
                    SET forgiveness = 1
                    WHERE id = %s
                """
                cursor.execute(update_sql, (add_id,))
                
                affected_rows = cursor.rowcount
                if affected_rows == 0:
                    current_app.logger.warning(f"No add_course record updated for id={add_id}")
                else:
                    current_app.logger.info(f"Successfully updated forgiveness flag for add_course record with id={add_id}")
            
        except Exception as e:
            # If that fails, try without the handled_by_admin field
            current_app.logger.warning(f"Error updating forgiveness_requests: {str(e)}. Trying without handled_by_admin.")
            sql = """
                UPDATE forgiveness_requests
                SET status = %s,
                    handling_date = NOW()
                WHERE id = %s
            """
            params = (status, request_id)
            current_app.logger.info(f"Executing SQL: {sql} with params: {params}")
            cursor.execute(sql, params)
        
        # Commit the changes
        current_app.mysql.connection.commit()
        cursor.close()
        
        current_app.logger.info(f"Successfully {action}d forgiveness request {request_id}")
        return jsonify({
            'success': True,
            'message': f'Forgiveness request has been {status}',
            'request_id': request_id
        })
        
    except Exception as e:
        # More detailed error logging and helpful message
        current_app.logger.error(f"Exception in forgiveness request handling: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}. Please try again or contact the administrator.'
        }), 500

def validate_makeup_dates(start_date, end_date):
    """Validate makeup session start and end dates"""
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
        end_date = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')

        now = datetime.now()
        if end_date < now:
            return None, jsonify({'success': False, 'message': 'End date must be in the future'}), 400

        if start_date >= end_date:
            return None, jsonify({'success': False, 'message': 'Start date must be before end date'}), 400

        return (start_date, end_date), None

    except ValueError as e:
        current_app.logger.error(f"Invalid date format: {str(e)}")
        return None, jsonify({'success': False, 'message': 'Invalid date format. Use YYYY-MM-DD HH:MM:SS'}), 400

def get_makeup_session_status(cursor):
    """Get current makeup session status"""
    # Check for scheduled sessions that should be activated
    cursor.execute("""
        UPDATE makeup_session
        SET status = 'open'
        WHERE status = 'scheduled' 
        AND open_date <= NOW()
    """)
    current_app.mysql.connection.commit()
    
    # Check for open sessions that should be auto-closed
    cursor.execute("""
        UPDATE makeup_session
        SET status = 'closed'
        WHERE status = 'open' 
        AND close_date <= NOW()
    """)
    current_app.mysql.connection.commit()
    
    # Get current active session
    cursor.execute("""
        SELECT id, status, open_date, close_date 
        FROM makeup_session 
        WHERE status IN ('open', 'scheduled')
        ORDER BY close_date DESC
        LIMIT 1
    """)
    
    result = cursor.fetchone()
    
    if result:
        session_id, status, open_date, close_date = result
        return {
            'success': True,
            'is_open': status == 'open',
            'is_scheduled': status == 'scheduled',
            'open_date': open_date.strftime('%Y-%m-%d %H:%M:%S') if open_date else None,
            'close_date': close_date.strftime('%Y-%m-%d %H:%M:%S') if close_date else None
        }
    else:
        return {
            'success': True,
            'is_open': False,
            'is_scheduled': False
        }

def start_makeup_session(cursor, admin_id, open_date, close_date):
    """Start a new makeup session period"""
    # Check if there is an active semester
    cursor.execute("""
        SELECT calendar_id, semester, academic_year
        FROM academic_calendar 
        WHERE is_current = 1
    """)
    current_semester = cursor.fetchone()
    
    if current_semester:
        calendar_id, semester_num, academic_year = current_semester
        semester_name = get_semester_name(semester_num)
        return None, jsonify({
            'success': False, 
            'message': f'Cannot start a makeup session while {semester_name} {academic_year} semester is active. Please close the current semester first.'
        }), 400
    
    # Check if this is after semester 2
    cursor.execute("""
        SELECT calendar_id, semester 
        FROM academic_calendar 
        ORDER BY academic_year DESC, semester DESC 
        LIMIT 1
    """)
    last_semester = cursor.fetchone()
    
    if not last_semester or last_semester[1] != 2:
        return None, jsonify({
            'success': False, 
            'message': 'Makeup sessions can only be scheduled after semester 2'
        }), 400
    
    # Close any existing open or scheduled sessions
    cursor.execute("UPDATE makeup_session SET status = 'closed' WHERE status IN ('open', 'scheduled')")
    
    # Determine status based on open date
    status = 'scheduled' if open_date > datetime.now() else 'open'
    
    # Insert new session
    cursor.execute("""
        INSERT INTO makeup_session (status, open_date, opened_by_admin, close_date)
        VALUES (%s, %s, %s, %s)
    """, (status, open_date, admin_id, close_date))
    
    current_app.mysql.connection.commit()
    
    return {
        'success': True,
        'message': f'Makeup session {"scheduled" if status == "scheduled" else "opened"} successfully',
        'open_date': open_date.strftime('%Y-%m-%d %H:%M:%S'),
        'close_date': close_date.strftime('%Y-%m-%d %H:%M:%S'),
        'is_scheduled': status == 'scheduled'
    }, None

def close_makeup_session(cursor, admin_id):
    """Close an active makeup session"""
    cursor.execute("""
        UPDATE makeup_session
        SET status = 'closed',
            closed_by_admin = %s
        WHERE status = 'open'
    """, (admin_id,))
    
    affected = cursor.rowcount
    current_app.mysql.connection.commit()
    
    if affected == 0:
        return None, jsonify({'success': False, 'message': 'No active makeup session to close'}), 400
    
    return {'success': True, 'message': 'Makeup session closed successfully'}, None

def cancel_makeup_session(cursor, admin_id):
    """Cancel a scheduled makeup session"""
    cursor.execute("""
        UPDATE makeup_session
        SET status = 'closed',
            closed_by_admin = %s
        WHERE status = 'scheduled'
    """, (admin_id,))
    
    affected = cursor.rowcount
    current_app.mysql.connection.commit()
    
    if affected == 0:
        return None, jsonify({'success': False, 'message': 'No scheduled makeup session to cancel'}), 400
    
    return {'success': True, 'message': 'Scheduled makeup session cancelled successfully'}, None

@admin_bp.route('/course_registration/makeup_session', methods=['GET', 'POST'])
def makeup_session():
    """Endpoint for managing makeup session period"""
    admin = session.get('admin')
    if not admin:
        return jsonify({'success': False, 'message': 'Admin not logged in'}), 401
    
    cursor = None
    try:
        cursor = current_app.mysql.connection.cursor()
        
        if request.method == 'GET':
            return jsonify(get_makeup_session_status(cursor))
        
        # POST method for actions
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
        
        action = data.get('action')
        admin_id = admin.get('admin_id')
        
        if action == 'start_session':
            open_date = data.get('open_date')
            close_date = data.get('close_date')
            
            if not open_date or not close_date:
                return jsonify({'success': False, 'message': 'Open date and close date are required'}), 400
            
            # Validate dates
            dates, error = validate_makeup_dates(open_date, close_date)
            if error:
                return error
                
            open_date, close_date = dates
            result, error = start_makeup_session(cursor, admin_id, open_date, close_date)
            if error:
                return error
            return jsonify(result)
            
        elif action == 'close_session':
            result, error = close_makeup_session(cursor, admin_id)
            if error:
                return error
            return jsonify(result)
            
        elif action == 'cancel_session':
            result, error = cancel_makeup_session(cursor, admin_id)
            if error:
                return error
            return jsonify(result)
            
        else:
            return jsonify({'success': False, 'message': 'Invalid action'}), 400
            
    except Exception as e:
        current_app.logger.error(f"Error in makeup session management: {str(e)}")
        if cursor:
            current_app.mysql.connection.rollback()
            
        # Check if there's an active semester to provide a more specific error message
        try:
            if cursor:
                cursor.execute("""
                    SELECT calendar_id, semester, academic_year
                    FROM academic_calendar 
                    WHERE is_current = 1
                """)
                current_semester = cursor.fetchone()
                
                if current_semester:
                    calendar_id, semester_num, academic_year = current_semester
                    semester_name = get_semester_name(semester_num)
                    return jsonify({
                        'success': False,
                        'message': f'Cannot manage makeup sessions while {semester_name} {academic_year} semester is active',
                        'details': 'Please close the current semester before scheduling makeup sessions'
                    }), 400
        except:
            pass  # If this check fails, fall back to generic error
            
        return jsonify({
            'success': False,
            'message': 'Error processing makeup session request',
            'details': str(e)
        }), 500
    finally:
        if cursor:
            cursor.close()

@admin_bp.route('/statistics/gpa_by_major', methods=['GET'])
@admin_required
def get_gpa_by_major():
    """Get GPA by major for enrolled, graduated, or all students"""
    admin = session.get('admin')

    try:
        cursor = get_db_cursor()
        
        # Get student type from request
        student_type = request.args.get('student_type', 'enrolled')
        
        # Build the WHERE clause based on student type
        if student_type == 'enrolled':
            status_filter = "s.enrollment_status = 'enrolled'"
        elif student_type == 'graduated':
            status_filter = "s.enrollment_status = 'graduated'"
        else:  # 'all'
            status_filter = "s.enrollment_status IN ('enrolled', 'graduated')"
        
        # Execute the query with the proper status filter and INNER JOIN
        query = f"""
        SELECT major_field AS major, ROUND(AVG(ss.cumulative_gpa), 2) AS avg_cumulative_gpa
        FROM (
            SELECT 
                s.student_id,
                s.major AS major_field
            FROM student s
            WHERE {status_filter}
              AND s.major IS NOT NULL
            UNION ALL
            SELECT 
                s.student_id,
                s.second_major AS major_field
            FROM student s
            WHERE {status_filter}
              AND s.second_major IS NOT NULL
        ) AS majors
        INNER JOIN (
            SELECT s1.student_id, s1.cumulative_gpa
            FROM student_semester_summary s1
            JOIN (
                SELECT student_id, MAX(year * 10 + semester) as max_sem
                FROM student_semester_summary
                GROUP BY student_id
            ) s2 ON s1.student_id = s2.student_id AND (s1.year * 10 + s1.semester) = s2.max_sem
            WHERE s1.cumulative_gpa IS NOT NULL AND s1.cumulative_gpa > 0
        ) AS ss ON majors.student_id = ss.student_id
        GROUP BY major_field
        """
        
        cursor.execute(query)
        
        majors_data = []
        for row in cursor.fetchall():
            major_type, avg_gpa = row
            # Handle NULL values by converting them to 0.0
            majors_data.append({
                'major': major_type,
                'gpa': float(avg_gpa) if avg_gpa is not None else 0.0
            })
        
        return jsonify({
            'success': True,
            'data': majors_data,
            'student_type': student_type
        })
    
    
    except Exception as e:
        current_app.logger.error(f"Error getting GPA by major: {str(e)}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500
    
    finally:
        if cursor:
            cursor.close()

@admin_bp.route('/statistics/course_enrollment_count', methods=['GET'])
@admin_required
def get_course_enrollment_count():
    """Get count of how many students have enrolled in specific numbers of courses"""
    admin = session.get('admin')

    try:
        cursor = get_db_cursor()
        
        # Count how many courses each student is enrolled in and group by count
        query = """
        SELECT 
            course_count,
            COUNT(*) as student_count
        FROM (
            SELECT 
                student_id,
                COUNT(*) as course_count
            FROM add_course
            WHERE status = 'enrolled'
            GROUP BY student_id
        ) as student_courses
        GROUP BY course_count
        ORDER BY course_count
        """
        
        cursor.execute(query)
        
        enrollment_data = []
        for row in cursor.fetchall():
            course_count, student_count = row
            enrollment_data.append({
                'courseCount': int(course_count),
                'studentCount': int(student_count)
            })
        
        return jsonify({
            'success': True,
            'data': enrollment_data
        })
    
    except Exception as e:
        current_app.logger.error(f"Error getting course enrollment count: {str(e)}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500    
    finally:
        if cursor:
            cursor.close()

@admin_bp.route('/probation_extension_requests', methods=['GET'])
def get_probation_extension_requests():
    """Get all pending probation extension requests for board review"""
    try:
        # Verify admin authentication
        admin_id = check_admin_auth()
        if not admin_id:
            return jsonify({'success': False, 'message': 'Admin authentication required'}), 401
        
        cursor = get_db_cursor()
        
        # Get all pending requests
        cursor.execute("""
            SELECT 
                bpe.id,
                bpe.student_id,
                s.first_name,
                s.last_name,
                bpe.status,
                bpe.handled_by_admin,
                bpe.decision_date,
                bpe.board_comments,
                sss.probation_counter,
                sss.cumulative_gpa,
                COALESCE(spo.max_probation_board, sp.max_probation_board) AS max_probation_limit
            FROM 
                board_probation_extension bpe
            JOIN 
                student s ON bpe.student_id = s.student_id
            JOIN 
                                 student_semester_summary sss ON bpe.student_id = sss.student_id
            JOIN (
                SELECT * FROM system_parameters ORDER BY last_updated DESC LIMIT 1
            ) sp
            LEFT JOIN 
                student_parameters_overrides spo ON bpe.student_id = spo.student_id
            WHERE 
                (sss.year * 10 + sss.semester) = (
                    SELECT MAX(year * 10 + semester) 
                    FROM student_semester_summary 
                    WHERE student_id = bpe.student_id
                )
            ORDER BY
                CASE WHEN bpe.status = 'pending' THEN 0 
                     WHEN bpe.status = 'approved' THEN 1
                     ELSE 2 END,
                bpe.decision_date DESC
        """)
        
        requests = []
        columns = [desc[0] for desc in cursor.description]
        
        for row in cursor.fetchall():
            request_data = dict(zip(columns, row))
            requests.append(request_data)
        
        return jsonify({
            'success': True,
            'requests': requests
        })
        
    except Exception as e:
        return handle_db_error(e, "Failed to retrieve probation extension requests")

@admin_bp.route('/probation_extension_requests/<int:request_id>', methods=['PUT'])
def handle_probation_extension_request(request_id):
    """Handle a probation extension request (approve or reject)"""
    try:
        # Verify admin authentication
        admin_id = check_admin_auth()
        if not admin_id:
            return jsonify({'success': False, 'message': 'Admin authentication required'}), 401
        
        # Get request data from body
        data = request.get_json()
        
        if not data or 'action' not in data:
            return jsonify({'success': False, 'message': 'Missing required parameters'}), 400
        
        action = data.get('action')
        comments = data.get('comments', '')
        
        if action not in ['approve', 'reject']:
            return jsonify({'success': False, 'message': 'Invalid action'}), 400
        
        cursor = get_db_cursor()
        
        # Check if request exists and is pending
        cursor.execute("""
            SELECT id, student_id, status FROM board_probation_extension
            WHERE id = %s
        """, (request_id,))
        
        request_data = cursor.fetchone()
        
        if not request_data:
            return jsonify({'success': False, 'message': 'Request not found'}), 404
        
        if request_data[2] != 'pending':
            return jsonify({'success': False, 'message': f'Request has already been {request_data[2]}'}), 400
        
        # Get student_id from request
        student_id = request_data[1]
        
        # Update request status
        status = 'approved' if action == 'approve' else 'rejected'
        
        cursor.execute("""
            UPDATE board_probation_extension
            SET status = %s,
                handled_by_admin = %s,
                decision_date = NOW(),
                board_comments = %s
            WHERE id = %s
        """, (status, admin_id, comments, request_id))
        
        # If rejected, update student enrollment status to dismissed
        if status == 'rejected':
            cursor.execute("""
                UPDATE student
                SET enrollment_status = 'dismissed'
                WHERE student_id = %s
            """, (student_id,))
            current_app.logger.info(f"Student {student_id} has been dismissed due to rejected probation extension")
            
            # Delete any pending requests for this student
            cursor.execute("""
                DELETE FROM board_probation_extension
                WHERE student_id = %s AND status = 'pending' AND id != %s
            """, (student_id, request_id))
        # If approved, delete any other pending requests
        elif status == 'approved':
            cursor.execute("""
                DELETE FROM board_probation_extension
                WHERE student_id = %s AND status = 'pending' AND id != %s
            """, (student_id, request_id))
        
        current_app.mysql.connection.commit()
        
        return jsonify({
            'success': True,
            'message': f'Probation extension request has been {status}',
            'request_id': request_id
        })
        
    except Exception as e:
        # More detailed error logging and helpful message
        current_app.logger.error(f"Exception in probation extension handling: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}. Please try again or contact the administrator.'
        }), 500

@admin_bp.route('/course_registration/probation_extension', methods=['GET'])
def get_probation_extension_requests_ui():
    """Get probation extension requests for the admin UI with optional status filter"""
    try:
        # Verify admin authentication
        admin_data = check_admin_auth()
        if not admin_data:
            return jsonify({'success': False, 'message': 'Admin authentication required'}), 401
        
        # Get status filter from query parameters - default to 'pending' if not specified
        status_filter = request.args.get('status', 'pending')
        
        # Log the status filter for debugging
        current_app.logger.info(f"Getting probation extension requests with status filter: {status_filter}")
        
        cursor = get_db_cursor()
        
        # Build the WHERE clause based on the status filter
        where_clause = ""
        if status_filter == 'pending':
            where_clause = "WHERE bpe.status = 'pending'"
        elif status_filter == 'processed':
            where_clause = "WHERE bpe.status IN ('approved', 'rejected')"
        elif status_filter == 'all':
            where_clause = ""  # No filter
        else:
            where_clause = f"WHERE bpe.status = '{status_filter}'"  # Specific status
            
        # Updated query to include cumulative GPA, national_id, and apply status filter
        query = f"""
            SELECT 
                bpe.id,
                bpe.student_id,
                s.first_name,
                s.last_name,
                bpe.status,
                bpe.handled_by_admin,
                bpe.decision_date,
                sss.cumulative_gpa,
                s.national_id
            FROM 
                board_probation_extension bpe
            JOIN 
                student s ON bpe.student_id = s.student_id
            LEFT JOIN 
                (SELECT 
                    ss1.student_id, 
                    ss1.cumulative_gpa
                FROM 
                    student_semester_summary ss1
                JOIN 
                    (SELECT 
                        student_id, 
                        MAX(year * 10 + semester) as max_sem
                    FROM 
                        student_semester_summary
                    GROUP BY 
                        student_id
                    ) ss2 ON ss1.student_id = ss2.student_id 
                      AND (ss1.year * 10 + ss1.semester) = ss2.max_sem
                ) sss ON bpe.student_id = sss.student_id
            {where_clause}
            ORDER BY
                CASE WHEN bpe.status = 'pending' THEN 0 
                     WHEN bpe.status = 'approved' THEN 1
                     ELSE 2 END,
                bpe.id DESC
        """
        
        # Log the query for debugging
        current_app.logger.info(f"Executing query: {query}")
        
        cursor.execute(query)
        
        requests = []
        columns = [desc[0] for desc in cursor.description]
        
        for row in cursor.fetchall():
            request_data = dict(zip(columns, row))
            
            # Format GPA to 2 decimal places if it exists
            if request_data.get('cumulative_gpa') is not None:
                request_data['cumulative_gpa'] = float(round(request_data['cumulative_gpa'], 2))
                
            requests.append(request_data)
        
        return jsonify({
            'success': True,
            'requests': requests
        })
        
    except Exception as e:
        # Better error handling
        current_app.logger.error(f"Error retrieving probation extension requests: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Failed to retrieve probation extension requests: {str(e)}'
        }), 500

@admin_bp.route('/course_registration/probation_extension/<int:request_id>', methods=['PUT'])
def handle_probation_extension_request_ui(request_id):
    """Handle a probation extension request (approve or reject) from the UI"""
    try:
        # Verify admin authentication
        admin_data = check_admin_auth()
        if not admin_data:
            return jsonify({'success': False, 'message': 'Admin authentication required'}), 401
        
        # Extract just the admin ID integer value
        if isinstance(admin_data, tuple) and admin_data[0] and 'admin_id' in admin_data[0]:
            admin_id = admin_data[0]['admin_id']
        elif isinstance(admin_data, dict) and 'admin_id' in admin_data:
            admin_id = admin_data['admin_id']
        else:
            admin_id = int(admin_data) if isinstance(admin_data, (int, str)) else None
            
        if not admin_id:
            return jsonify({'success': False, 'message': 'Admin ID not available'}), 401
        
        # Get request data from body
        data = request.get_json()
        
        if not data or 'action' not in data:
            return jsonify({'success': False, 'message': 'Missing required parameters'}), 400
        
        action = data.get('action')
        comments = data.get('comments', '')
        
        # Log the received data for debugging
        current_app.logger.info(f"Handling probation extension: request_id={request_id}, action={action}, comments={comments}")
        
        if action not in ['approve', 'reject']:
            return jsonify({'success': False, 'message': 'Invalid action'}), 400
        
        cursor = get_db_cursor()
        
        # Check if request exists and is pending
        cursor.execute("""
            SELECT id, student_id, status FROM board_probation_extension
            WHERE id = %s
        """, (request_id,))
        
        request_data = cursor.fetchone()
        
        if not request_data:
            return jsonify({'success': False, 'message': 'Request not found'}), 404
        
        if request_data[2] != 'pending':
            return jsonify({'success': False, 'message': f'Request has already been {request_data[2]}'}), 400
        
        # Update request status
        status = 'approved' if action == 'approve' else 'rejected'
        
        try:
            # Get the student_id from the request
            student_id = request_data[1]
            
            # Create a simple direct query with individually passed parameters
            query = """
                UPDATE board_probation_extension
                SET status = %s,
                    handled_by_admin = %s,
                    decision_date = NOW(),
                    board_comments = %s
                WHERE id = %s
            """
            
            # Log the exact query and parameters we're using - now with just the admin ID integer
            current_app.logger.info(f"Update query: {query}")
            current_app.logger.info(f"Parameters: status={status}, admin_id={admin_id} (type: {type(admin_id)}), comments={comments}, request_id={request_id}")
            
            cursor.execute(query, (status, admin_id, comments, request_id))
            
            # If rejected, update student enrollment status to dismissed
            if status == 'rejected':
                cursor.execute("""
                    UPDATE student
                    SET enrollment_status = 'dismissed'
                    WHERE student_id = %s
                """, (student_id,))
                current_app.logger.info(f"Student {student_id} has been dismissed due to rejected probation extension")
                
                # Delete any pending requests for this student
                cursor.execute("""
                    DELETE FROM board_probation_extension
                    WHERE student_id = %s AND status = 'pending' AND id != %s
                """, (student_id, request_id))
                
            # If approved, check if the student's probation counter has reached max_probation_total
            elif status == 'approved':
                # Get the student's probation counter and max_probation_total
                cursor.execute("""
                    SELECT 
                        sss.probation_counter,
                        COALESCE(spo.max_probation_total, sp.max_probation_total) AS max_probation_total
                    FROM 
                        student_semester_summary sss
                    JOIN 
                        (SELECT max_probation_total FROM system_parameters ORDER BY last_updated DESC LIMIT 1) sp
                    LEFT JOIN 
                        student_parameters_overrides spo ON sss.student_id = spo.student_id
                    WHERE 
                        sss.student_id = %s
                    ORDER BY 
                        sss.year DESC, sss.semester DESC
                    LIMIT 1
                """, (student_id,))
                
                probation_data = cursor.fetchone()
                if probation_data:
                    probation_counter = probation_data[0]
                    max_probation_total = probation_data[1]
                    
                    # If probation counter has reached or exceeded max_probation_total, dismiss the student
                    if probation_counter >= max_probation_total:
                        cursor.execute("""
                            UPDATE student
                            SET enrollment_status = 'dismissed'
                            WHERE student_id = %s
                        """, (student_id,))
                        current_app.logger.info(f"Student {student_id} has been dismissed due to reaching max probation total")
                
                # Delete any other pending requests for this student
                cursor.execute("""
                    DELETE FROM board_probation_extension
                    WHERE student_id = %s AND status = 'pending' AND id != %s
                """, (student_id, request_id))
            
            current_app.mysql.connection.commit()
            
            # Log success
            current_app.logger.info(f"Successfully updated probation extension request {request_id} to {status}")
            
            return jsonify({
                'success': True,
                'message': f'Probation extension request has been {status}',
                'request_id': request_id
            })
        except Exception as e:
            # Detailed error for troubleshooting the SQL issue
            current_app.logger.error(f"SQL Error in probation extension update: {str(e)}")
            current_app.logger.error(f"Parameters were: status={status}, admin_id={admin_id} (type: {type(admin_id)}), comments_length={len(comments)}, request_id={request_id}")
            
            # Return a more helpful error message to the client
            return jsonify({
                'success': False,
                'message': f'Database error: {str(e)}. Please try again or contact the administrator.'
            }), 500
        
    except Exception as e:
        return handle_db_error(e, "Failed to handle probation extension request")

@admin_bp.route('/course_registration/probation_extension/<int:request_id>/history', methods=['GET'])
def get_probation_extension_request_history(request_id):
    """Get the history of a specific probation extension request"""
    try:
        # Verify admin authentication
        admin_data = check_admin_auth()
        if not admin_data:
            return jsonify({'success': False, 'message': 'Admin authentication required'}), 401
        
        cursor = get_db_cursor()
        
        # Check if request exists
        cursor.execute("""
            SELECT id FROM board_probation_extension
            WHERE id = %s
        """, (request_id,))
        
        if not cursor.fetchone():
            return jsonify({'success': False, 'message': 'Request not found'}), 404
        
        # Get request history with cumulative GPA
        cursor.execute("""
            SELECT 
                bpe.id,
                bpe.student_id,
                CONCAT(s.first_name, ' ', s.last_name) as student_name,
                bpe.status,
                bpe.handled_by_admin,
                CONCAT(a.first_name, ' ', a.last_name) as admin_name,
                bpe.decision_date,
                bpe.board_comments,
                sss.cumulative_gpa
            FROM 
                board_probation_extension bpe
            JOIN 
                student s ON bpe.student_id = s.student_id
            LEFT JOIN 
                admin a ON bpe.handled_by_admin = a.admin_id
            LEFT JOIN 
                (SELECT 
                    ss1.student_id, 
                    ss1.cumulative_gpa
                FROM 
                    student_semester_summary ss1
                JOIN 
                    (SELECT 
                        student_id, 
                        MAX(year + semester) as max_sem
                    FROM 
                        student_semester_summary
                    GROUP BY 
                        student_id
                    ) ss2 ON ss1.student_id = ss2.student_id 
                      AND (ss1.year + ss1.semester) = ss2.max_sem
                ) sss ON bpe.student_id = sss.student_id
            WHERE 
                bpe.id = %s
        """, (request_id,))
        
        history = []
        columns = [desc[0] for desc in cursor.description]
        
        for row in cursor.fetchall():
            item = dict(zip(columns, row))
            
            # Format dates for display
            if item['decision_date']:
                item['decision_date'] = item['decision_date'].strftime('%Y-%m-%d %H:%M:%S')
            
            # Format GPA to 2 decimal places if it exists
            if item.get('cumulative_gpa') is not None:
                item['cumulative_gpa'] = float(round(item['cumulative_gpa'], 2))
                
            history.append(item)
        
        return jsonify({
            'success': True,
            'history': history
        })
        
    except Exception as e:
        # Better error handling
        current_app.logger.error(f"Error retrieving probation extension history: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Failed to retrieve probation extension request history: {str(e)}'
        }), 500

@admin_bp.route('/profile-info', methods=['GET', 'POST'])
@admin_required
def admin_profile_info():
    """Get or update admin profile information"""
    try:
        admin = session.get('admin')
            
        admin_id = admin['admin_id']
        cursor = current_app.mysql.connection.cursor()
        
        # GET request: Return current profile information
        if request.method == 'GET':
            try:
                cursor.execute("""
                    SELECT 
                        admin_id, first_name, last_name, email_address, 
                        profile_image, phone, national_id
                    FROM admin 
                    WHERE admin_id = %s
                """, (admin_id,))
                
                result = cursor.fetchone()
                if not result:
                    return jsonify({
                        'success': False,
                        'message': 'Admin not found',
                        'code': 'NOT_FOUND'
                    }), 404
                
                # Convert profile picture to base64 if exists
                profile_data = None
                if result[4]:  # index 4 is profile_image
                    profile_data = base64.b64encode(result[4]).decode('utf-8')
                
                profile_info = {
                    'admin_id': result[0],
                    'first_name': result[1],
                    'last_name': result[2],
                    'email_address': result[3],
                    'profile_image': profile_data,
                    'phone': result[5] or '',
                    'national_id': result[6]
                }
                
                return jsonify({
                    'success': True,
                    'data': profile_info
                })
                
            except Exception as e:
                current_app.logger.error(f"Error fetching admin profile info: {str(e)}")
                return jsonify({
                    'success': False,
                    'message': f'Error fetching profile information: {str(e)}',
                    'code': 'DB_ERROR'
                }), 500
                
        # POST request: Update profile information
        elif request.method == 'POST':
            try:
                # Check if we're getting form data or JSON
                if request.content_type and 'multipart/form-data' in request.content_type:
                    # Handle form data with file uploads
                    first_name = request.form.get('first_name')
                    last_name = request.form.get('last_name')
                    phone = request.form.get('phone')
                    
                    # Handle profile image if uploaded
                    profile_image = None
                    if 'profile_image' in request.files and request.files['profile_image'].filename:
                        file = request.files['profile_image']
                        profile_image = file.read()  # Read binary data from file
                else:
                    # Handle JSON data
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
                    profile_image = data.get('profile_image')
                
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
                
                # Handle profile picture update if provided
                if profile_image:
                    # Remove data URL prefix if present
                    if isinstance(profile_image, str) and profile_image.startswith('data:image'):
                        image_data = profile_image.split(',')[1]
                    else:
                        image_data = profile_image
                    
                    try:
                        if isinstance(image_data, str):
                            binary_data = base64.b64decode(image_data)
                        else:
                            binary_data = profile_image  # Already binary from file upload
                            
                        query_parts.append("profile_image = %s")
                        params.append(binary_data)
                    except Exception as e:
                        current_app.logger.error(f"Error decoding profile image: {str(e)}")
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
                query = f"UPDATE admin SET {', '.join(query_parts)} WHERE admin_id = %s"
                params.append(admin_id)
                
                cursor.execute(query, params)
                current_app.mysql.connection.commit()
                
                # Update session info
                if first_name:
                    session['admin']['first_name'] = first_name
                if last_name:
                    session['admin']['last_name'] = last_name
                if profile_image:
                    # For profile_image, we just note that it's been updated
                    # The actual image will be refreshed on page reload
                    session['admin']['profile_image_updated'] = True
                
                return jsonify({
                    'success': True,
                    'message': 'Profile updated successfully'
                })
                
            except Exception as e:
                current_app.logger.error(f"Error updating admin profile: {str(e)}")
                return jsonify({
                    'success': False,
                    'message': f'Error updating profile: {str(e)}',
                    'code': 'UPDATE_ERROR'
                }), 500
                
    except Exception as e:
        current_app.logger.error(f"Unexpected error in admin_profile_info: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'An unexpected error occurred: {str(e)}',
            'code': 'UNEXPECTED_ERROR'
        }), 500
    finally:
        if 'cursor' in locals():
            cursor.close()

@admin_bp.route('/change-password', methods=['POST'])
@admin_required
def admin_change_password():
    """Change admin password"""
    try:
        admin = session.get('admin')
            
        admin_id = admin['admin_id']
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided',
                'code': 'NO_DATA'
            }), 400
            
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({
                'success': False,
                'message': 'Current password and new password are required',
                'code': 'MISSING_REQUIRED'
            }), 400
            
        # Check if new password meets requirements
        if len(new_password) < 8:
            return jsonify({
                'success': False,
                'message': 'New password must be at least 8 characters long',
                'code': 'INVALID_PASSWORD'
            }), 400
            
        cursor = current_app.mysql.connection.cursor()
        
        # Verify current password
        cursor.execute("SELECT password FROM admin WHERE admin_id = %s", (admin_id,))
        result = cursor.fetchone()
        
        if not result:
            return jsonify({
                'success': False,
                'message': 'Admin not found',
                'code': 'NOT_FOUND'
            }), 404
            
        # Check if current password matches
        stored_password = result[0]
        if not check_password_hash(stored_password, current_password):
            return jsonify({
                'success': False,
                'message': 'Current password is incorrect',
                'code': 'INVALID_PASSWORD'
            }), 401
            
        # Hash the new password
        hashed_password = generate_password_hash(new_password)
        
        # Update password in database
        cursor.execute(
            "UPDATE admin SET password = %s WHERE admin_id = %s",
            (hashed_password, admin_id)
        )
        current_app.mysql.connection.commit()
        
        return jsonify({
            'success': True,
            'message': 'Password changed successfully'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error changing admin password: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error changing password: {str(e)}',
            'code': 'CHANGE_PASSWORD_ERROR'
        }), 500
    finally:
        if 'cursor' in locals():
            cursor.close()

@admin_bp.route('/system_adjustments/special_cases/gaps', methods=['GET', 'POST'])
def system_adjustments_gaps():
    """Handle gaps special case functionality"""
    admin = session.get('admin')
    if not admin:
        return jsonify({'success': False, 'message': 'Admin not logged in'}), 401
    
    # GET request to load the UI
    if request.method == 'GET':
        return jsonify({
            'success': True,
            'title': 'Gaps Special Case'
        })
    
    # POST request to add gaps for a student
    elif request.method == 'POST':
        data = request.get_json()
        student_id = data.get('student_id')
        
        if not student_id:
            return jsonify({'success': False, 'message': 'Student ID is required'}), 400
        
        try:
            # Get database connection
            cursor = get_db_cursor()
            
            # Get current semester and year for the student
            try:
                # Get current semester courses for the student
                from course_select import get_current_courses, get_current_semester, get_current_year
                
                current_semester = get_current_semester()
                current_year = get_current_year(student_id)
                
                current_app.logger.info(f"Getting courses for student {student_id}, semester {current_semester}, year {current_year}")
                
                # Get courses that should be enrolled in the current semester
                current_courses = get_current_courses(current_semester, current_year, student_id)
                
                if not current_courses:
                    return jsonify({'success': False, 'message': 'No current semester courses found for this student'}), 404
                
                # Insert/update each course as "notenrolled" status in add_course table
                inserted_courses = []
                updated_courses = []
                
                for course in current_courses:
                    current_app.logger.info(f"Processing course {course['course_code']} for student {student_id}")
                    # Check if course already exists for this student
                    cursor.execute("""
                        SELECT id FROM add_course 
                        WHERE student_id = %s AND course_code = %s AND year = %s AND semester = %s
                    """, (student_id, course['course_code'], current_year, current_semester))
                    
                    existing_course = cursor.fetchone()
                    
                    if existing_course:
                        # Update the existing course with "notenrolled" status
                        cursor.execute("""
                            UPDATE add_course 
                            SET status = 'notenrolled', letter_grade = NULL, grade_point = NULL, date = CURDATE()
                            WHERE id = %s
                        """, (existing_course[0],))
                        
                        updated_courses.append(course['course_code'])
                    else:
                        # Insert the course with "notenrolled" status
                        cursor.execute("""
                            INSERT INTO add_course 
                            (student_id, course_code, year, semester, status, date) 
                            VALUES (%s, %s, %s, %s, 'notenrolled', CURDATE())
                        """, (student_id, course['course_code'], current_year, current_semester))
                        
                        inserted_courses.append(course['course_code'])
                
                total_processed = len(inserted_courses) + len(updated_courses)
                
                if total_processed == 0:
                    return jsonify({'success': True, 'message': 'No courses to process', 'added_courses': []}), 200
                
                cursor.connection.commit()
                
                current_app.logger.info(f"Added {len(inserted_courses)} and updated {len(updated_courses)} courses as gaps for student {student_id}")
                return jsonify({
                    'success': True, 
                    'message': f'{len(inserted_courses) + len(updated_courses)} courses processed as gaps for student {student_id}',
                    'added_courses': inserted_courses + updated_courses
                })
                
            except Exception as e:
                current_app.logger.error(f"Error in special cases gaps: {str(e)}")
                cursor.connection.rollback()
                return handle_db_error(e, 'Error processing gaps special case')
                
        except Exception as e:
            current_app.logger.error(f"Database error in special cases gaps: {str(e)}")
            return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
            
    return jsonify({'success': False, 'message': 'Invalid request method'}), 405

@admin_bp.route('/system_adjustments/special_cases/gaps/<student_id>', methods=['GET'])
def get_student_info(student_id):
    """Get student information by ID for admin interface"""
    admin = session.get('admin')
    if not admin:
        current_app.logger.error(f"Admin not logged in when searching for student: {student_id}")
        return jsonify({'success': False, 'message': 'Admin not logged in'}), 401
    
    try:
        current_app.logger.info(f"Searching for student with ID: {student_id}")
        cursor = get_db_cursor()
        
        # First try to search by student_id
        cursor.execute("""
            SELECT student_id, first_name, last_name, email_address, national_id 
            FROM student 
            WHERE student_id = %s
        """, (student_id,))
        
        student = cursor.fetchone()
        
        # If not found, try searching by national_id
        if not student:
            current_app.logger.info(f"Student not found by student_id, trying national_id: {student_id}")
            cursor.execute("""
                SELECT student_id, first_name, last_name, email_address, national_id 
                FROM student 
                WHERE national_id = %s
            """, (student_id,))
            
            student = cursor.fetchone()
        
        if not student:
            current_app.logger.warning(f"Student not found with ID or national_id: {student_id}")
            return jsonify({'success': False, 'message': 'Student not found'}), 404
        
        # Format student data
        student_data = {
            'id': student[0],
            'first_name': student[1],
            'last_name': student[2],
            'email': student[3],
            'national_id': student[4]
        }
        
        current_app.logger.info(f"Found student: {student_data['first_name']} {student_data['last_name']}")
        return jsonify({
            'success': True,
            'student': student_data
        })
        
    except Exception as e:
        current_app.logger.error(f"Error searching for student {student_id}: {str(e)}")
        return handle_db_error(e, 'Error fetching student information')
    finally:
        if 'cursor' in locals():
            cursor.close()

@admin_bp.route('/system_adjustments/special_cases/gaps/<student_id>/current_courses', methods=['GET'])
def get_student_current_courses(student_id):
    """Get current semester courses for a student"""
    admin = session.get('admin')
    if not admin:
        current_app.logger.error(f"Admin not logged in when fetching courses for student: {student_id}")
        return jsonify({'success': False, 'message': 'Admin not logged in'}), 401
    
    try:
        current_app.logger.info(f"Fetching current courses for student: {student_id}")
        
        # Import the required functions
        from course_select import get_current_courses, get_current_semester, get_current_year
        
        # Get current semester and year
        current_semester = get_current_semester()
        current_year = get_current_year(student_id)
        
        current_app.logger.info(f"Current semester: {current_semester}, current year: {current_year}")
        
        if not current_semester or not current_year:
            current_app.logger.error(f"Missing semester ({current_semester}) or year ({current_year}) for student: {student_id}")
            return jsonify({
                'success': False,
                'message': 'Could not determine current semester or year for student'
            }), 500
        
        # Get current courses
        current_app.logger.info(f"Calling get_current_courses for student: {student_id}")
        current_courses = get_current_courses(current_semester, current_year, student_id)
        
        if not current_courses:
            current_app.logger.info(f"No current courses found for student: {student_id}")
            return jsonify({
                'success': True, 
                'courses': [],
                'message': 'No current semester courses found for this student'
            })
        
        # Format course data
        formatted_courses = []
        for course in current_courses:
            formatted_courses.append({
                'course_code': course['course_code'],
                'course_name': course['course_name']
            })
        
        current_app.logger.info(f"Found {len(formatted_courses)} courses for student {student_id}")
        return jsonify({
            'success': True,
            'courses': formatted_courses,
            'semester': current_semester,
            'year': current_year
        })
        
    except Exception as e:
        current_app.logger.error(f"Error fetching current courses for student {student_id}: {str(e)}")
        # Log the traceback for more debugging information
        import traceback
        current_app.logger.error(traceback.format_exc())
        return jsonify({
            'success': False, 
            'message': f'Error fetching current courses: {str(e)}'
        }), 500
    


# Transfers section endpoints
@admin_bp.route('/system_adjustments/special_cases/transfers', methods=['GET', 'POST'])
def system_adjustments_transfers():
    """Handle transfers special case functionality"""
    admin = session.get('admin')
    if not admin:
        return jsonify({'success': False, 'message': 'Admin not logged in'}), 401
    
    # GET request to load the UI
    if request.method == 'GET':
        return jsonify({
            'success': True,
            'title': 'Transfers Special Case'
        })
    
    # POST request to add transfers for a student
    elif request.method == 'POST':
        data = request.get_json()
        student_id = data.get('student_id')
        selected_courses = data.get('selected_courses', [])
        unselected_courses = data.get('unselected_courses', [])
        
        if not student_id:
            return jsonify({'success': False, 'message': 'Student ID is required'}), 400
        
        if not selected_courses and not unselected_courses:
            return jsonify({'success': False, 'message': 'No courses provided'}), 400
        
        try:
            # Get database connection
            cursor = get_db_cursor()
            
            # Get current semester and year for the student
            try:
                # Import the required functions
                from course_select import get_current_semester, get_current_year
                
                current_semester = get_current_semester()
                current_year = get_current_year(student_id)
                
                current_app.logger.info(f"Processing transfers for student {student_id}, semester {current_semester}, year {current_year}")
                
                # Process selected courses (add as passed with TC grade)
                inserted_selected_courses = []
                updated_selected_courses = []
                for course_code in selected_courses:
                    current_app.logger.info(f"Processing selected course {course_code} for student {student_id}")
                    
                    # Check if course already exists for this student
                    cursor.execute("""
                        SELECT id FROM add_course 
                        WHERE student_id = %s AND course_code = %s AND year = %s AND semester = %s
                    """, (student_id, course_code, current_year, current_semester))
                    
                    existing_course = cursor.fetchone()
                    
                    if existing_course:
                        # Update the existing course with "passed" status and "TC" letter grade
                        cursor.execute("""
                            UPDATE add_course 
                            SET status = 'passed', letter_grade = 'TC', grade_point = 0.0, date = CURDATE()
                            WHERE id = %s
                        """, (existing_course[0],))
                        
                        updated_selected_courses.append(course_code)
                    else:
                        # Insert the course with "passed" status and "TC" letter grade
                        cursor.execute("""
                            INSERT INTO add_course 
                            (student_id, course_code, year, semester, status, date, letter_grade, grade_point) 
                            VALUES (%s, %s, %s, %s, 'passed', CURDATE(), 'TC', 0.0)
                        """, (student_id, course_code, current_year, current_semester))
                        
                        inserted_selected_courses.append(course_code)
                
                # Process unselected courses (add as notenrolled)
                inserted_unselected_courses = []
                updated_unselected_courses = []
                for course_code in unselected_courses:
                    current_app.logger.info(f"Processing unselected course {course_code} for student {student_id}")
                    
                    # Check if course already exists for this student
                    cursor.execute("""
                        SELECT id FROM add_course 
                        WHERE student_id = %s AND course_code = %s AND year = %s AND semester = %s
                    """, (student_id, course_code, current_year, current_semester))
                    
                    existing_course = cursor.fetchone()
                    
                    if existing_course:
                        # Update the existing course with "notenrolled" status
                        cursor.execute("""
                            UPDATE add_course 
                            SET status = 'notenrolled', letter_grade = NULL, grade_point = NULL, date = CURDATE()
                            WHERE id = %s
                        """, (existing_course[0],))
                        
                        updated_unselected_courses.append(course_code)
                    else:
                        # Insert the course with "notenrolled" status
                        cursor.execute("""
                            INSERT INTO add_course 
                            (student_id, course_code, year, semester, status, date) 
                            VALUES (%s, %s, %s, %s, 'notenrolled', CURDATE())
                        """, (student_id, course_code, current_year, current_semester))
                        
                        inserted_unselected_courses.append(course_code)
                
                if not inserted_selected_courses and not inserted_unselected_courses and not updated_selected_courses and not updated_unselected_courses:
                    return jsonify({'success': False, 'message': 'No courses were added or updated'}), 200
                
                cursor.connection.commit()
                
                current_app.logger.info(f"Added {len(inserted_selected_courses)} and updated {len(updated_selected_courses)} courses as transfers; Added {len(inserted_unselected_courses)} and updated {len(updated_unselected_courses)} as not enrolled")
                return jsonify({
                    'success': True, 
                    'message': f'Successfully processed {len(inserted_selected_courses) + len(updated_selected_courses)} transfer courses and {len(inserted_unselected_courses) + len(updated_unselected_courses)} not enrolled courses',
                    'inserted_transferred_courses': inserted_selected_courses,
                    'updated_transferred_courses': updated_selected_courses,
                    'inserted_notenrolled_courses': inserted_unselected_courses,
                    'updated_notenrolled_courses': updated_unselected_courses
                })
                
            except Exception as e:
                current_app.logger.error(f"Error in transfers special case: {str(e)}")
                cursor.connection.rollback()
                return handle_db_error(e, 'Error processing transfers special case')
                
        except Exception as e:
            current_app.logger.error(f"Database error in transfers special case: {str(e)}")
            return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
            
    return jsonify({'success': False, 'message': 'Invalid request method'}), 405

@admin_bp.route('/system_adjustments/special_cases/transfers/<student_id>', methods=['GET'])
def get_student_info_for_transfers(student_id):
    """Get student information by ID for transfers interface"""
    admin = session.get('admin')
    if not admin:
        current_app.logger.error(f"Admin not logged in when searching for student: {student_id}")
        return jsonify({'success': False, 'message': 'Admin not logged in'}), 401
    
    try:
        current_app.logger.info(f"Searching for student with ID: {student_id}")
        cursor = get_db_cursor()
        
        # First try to search by student_id
        cursor.execute("""
            SELECT student_id, first_name, last_name, email_address, national_id 
            FROM student 
            WHERE student_id = %s
        """, (student_id,))
        
        student = cursor.fetchone()
        
        # If not found, try searching by national_id
        if not student:
            current_app.logger.info(f"Student not found by student_id, trying national_id: {student_id}")
            cursor.execute("""
                SELECT student_id, first_name, last_name, email_address, national_id 
                FROM student 
                WHERE national_id = %s
            """, (student_id,))
            
            student = cursor.fetchone()
        
        if not student:
            current_app.logger.warning(f"Student not found with ID or national_id: {student_id}")
            return jsonify({'success': False, 'message': 'Student not found'}), 404
        
        # Format student data
        student_data = {
            'id': student[0],
            'first_name': student[1],
            'last_name': student[2],
            'email': student[3],
            'national_id': student[4]
        }
        
        current_app.logger.info(f"Found student: {student_data['first_name']} {student_data['last_name']}")
        return jsonify({
            'success': True,
            'student': student_data
        })
        
    except Exception as e:
        current_app.logger.error(f"Error searching for student {student_id}: {str(e)}")
        return handle_db_error(e, 'Error fetching student information')
    finally:
        if 'cursor' in locals():
            cursor.close()

@admin_bp.route('/system_adjustments/special_cases/transfers/<student_id>/current_courses', methods=['GET'])
def get_student_current_courses_for_transfers(student_id):
    """Get current semester courses for a student for transfers"""
    admin = session.get('admin')
    if not admin:
        current_app.logger.error(f"Admin not logged in when fetching courses for student: {student_id}")
        return jsonify({'success': False, 'message': 'Admin not logged in'}), 401
    
    try:
        current_app.logger.info(f"Fetching current courses for student transfers: {student_id}")
        
        # Import the required functions
        from course_select import get_current_courses, get_current_semester, get_current_year
        
        # Get current semester and year
        current_semester = get_current_semester()
        current_year = get_current_year(student_id)
        
        current_app.logger.info(f"Current semester: {current_semester}, current year: {current_year}")
        
        if not current_semester or not current_year:
            current_app.logger.error(f"Missing semester ({current_semester}) or year ({current_year}) for student: {student_id}")
            return jsonify({
                'success': False,
                'message': 'Could not determine current semester or year for student'
            }), 500
        
        # Get current courses
        current_app.logger.info(f"Calling get_current_courses for student: {student_id}")
        current_courses = get_current_courses(current_semester, current_year, student_id)
        
        if not current_courses:
            current_app.logger.info(f"No current courses found for student: {student_id}")
            return jsonify({
                'success': True, 
                'courses': [],
                'message': 'No current semester courses found for this student'
            })
        
        # Format course data
        formatted_courses = []
        for course in current_courses:
            formatted_courses.append({
                'course_code': course['course_code'],
                'course_name': course['course_name']
            })
        
        current_app.logger.info(f"Found {len(formatted_courses)} courses for student {student_id}")
        return jsonify({
            'success': True,
            'courses': formatted_courses,
            'semester': current_semester,
            'year': current_year
        })
        
    except Exception as e:
        current_app.logger.error(f"Error fetching current courses for transfers: {str(e)}")
        return handle_db_error(e, 'Error fetching current courses')

@admin_bp.route('/academic-calendar/current', methods=['GET'])
def get_current_academic_calendar():
    try:
        cursor = current_app.mysql.connection.cursor()
        cursor.execute("""
            SELECT calendar_id, academic_year, semester, start_date, end_date
            FROM academic_calendar
            WHERE is_current = 1
            LIMIT 1
        """)
        
        result = cursor.fetchone()
        cursor.close()
        
        if not result:
            return jsonify({
                'success': False,
                'message': 'No current semester found'
            }), 404
        
        # Convert to dictionary
        calendar = {
            'calendar_id': result[0],
            'year': result[1],
            'semester': result[2],
            'start_date': result[3].strftime('%Y-%m-%d') if result[3] else None,
            'end_date': result[4].strftime('%Y-%m-%d') if result[4] else None
        }
        
        return jsonify(calendar)
        
    except Exception as e:
        current_app.logger.error(f"Error getting current academic calendar: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to retrieve current semester information'
        }), 500

@admin_bp.route('/registration-config/current', methods=['GET'])
def get_current_registration_config():
    try:
        cursor = current_app.mysql.connection.cursor()
        cursor.execute("""
            SELECT id, status, start_date, end_date
            FROM registration_config
            ORDER BY id DESC
            LIMIT 1
        """)
        
        result = cursor.fetchone()
        cursor.close()
        
        if not result:
            return jsonify({
                'success': False,
                'message': 'No registration configuration found'
            }), 404
        
        # Convert to dictionary
        config = {
            'id': result[0],
            'status': result[1],
            'start_date': result[2].strftime('%Y-%m-%d %H:%M:%S') if result[2] else None,
            'end_date': result[3].strftime('%Y-%m-%d %H:%M:%S') if result[3] else None
        }
        
        return jsonify(config)
        
    except Exception as e:
        current_app.logger.error(f"Error getting current registration config: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to retrieve registration configuration'
        }), 500

@admin_bp.route('/create-admin', methods=['POST'])
@admin_required
def create_admin():
    """Create a new admin account"""
    try:
        # Only existing admins can create new admin accounts
        if 'admin' not in session:
            return jsonify({
                'success': False,
                'message': 'Unauthorized access',
                'code': 'UNAUTHORIZED'
            }), 401
        
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided',
                'code': 'NO_DATA'
            }), 400
        
        # Extract required fields
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email_address = data.get('email_address')
        password = data.get('password')
        national_id = data.get('national_id')
        phone = data.get('phone', '')  # Optional
        
        # Validate required fields
        if not all([first_name, last_name, email_address, password, national_id]):
            return jsonify({
                'success': False,
                'message': 'Missing required fields',
                'code': 'MISSING_REQUIRED'
            }), 400
        
        # Validate email format
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email_address):
            return jsonify({
                'success': False,
                'message': 'Invalid email format',
                'code': 'INVALID_EMAIL'
            }), 400
        
        # Validate password length
        if len(password) < 8:
            return jsonify({
                'success': False,
                'message': 'Password must be at least 8 characters long',
                'code': 'INVALID_PASSWORD'
            }), 400
        
        cursor = current_app.mysql.connection.cursor()
        
        # Check if email already exists
        cursor.execute("SELECT admin_id FROM admin WHERE email_address = %s", (email_address,))
        if cursor.fetchone():
            return jsonify({
                'success': False,
                'message': 'Email address already in use',
                'code': 'EMAIL_EXISTS'
            }), 400
        
        # Check if national ID already exists
        cursor.execute("SELECT admin_id FROM admin WHERE national_id = %s", (national_id,))
        if cursor.fetchone():
            return jsonify({
                'success': False,
                'message': 'National ID already in use',
                'code': 'NATIONAL_ID_EXISTS'
            }), 400
        
        # Hash the password
        hashed_password = generate_password_hash(password)
        
        # Insert new admin into database
        cursor.execute("""
            INSERT INTO admin (first_name, last_name, email_address, password, national_id, phone)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (first_name, last_name, email_address, hashed_password, national_id, phone))
        
        current_app.mysql.connection.commit()
        new_admin_id = cursor.lastrowid
        
        # Send email with login credentials
        from email_service import mail
        from flask_mail import Message
        
        subject = "Your TBS Admin Account Has Been Created"
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e5ec; border-radius: 5px; background-color: #f8f9fa;">
            <div style="text-align: center; margin-bottom: 20px;">
                <h2 style="color: #4a5568;">Tunis Business School</h2>
            </div>
            <h2 style="color: #4a5568;">Admin Account Created</h2>
            <p>Hello {first_name} {last_name},</p>
            <p>An administrator account has been created for you. Here are your login details:</p>
            <p><strong>Email:</strong> {email_address}</p>
            <p><strong>Password:</strong> {password}</p>
            <p>Please log in and change your password immediately for security reasons.</p>
            <p>Best regards,<br>TBS Administration</p>
        </div>
        """
        
        try:
            msg = Message(
                subject=subject,
                recipients=[email_address],
                html=html,
                sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'TBS Registration <majdhamdi777@gmail.com>')
            )
            mail.send(msg)
            current_app.logger.info(f"Admin account creation email sent to {email_address}")
        except Exception as e:
            current_app.logger.error(f"Failed to send admin account creation email: {str(e)}")
            return jsonify({
                'success': True,
                'message': 'Admin account created successfully but failed to send email notification',
                'admin_id': new_admin_id,
                'code': 'EMAIL_FAILED'
            })
        
        return jsonify({
            'success': True,
            'message': 'Admin account created successfully and email sent',
            'admin_id': new_admin_id
        })
        
    except Exception as e:
        current_app.logger.error(f"Error creating admin account: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'An error occurred: {str(e)}',
            'code': 'ERROR'
        }), 500
    finally:
        if 'cursor' in locals():
            cursor.close()

@admin_bp.route('/reset-student-password', methods=['POST'])
@admin_required
def reset_student_password():
    """Reset a student's password and send them an email with the new password"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided',
                'code': 'NO_DATA'
            }), 400
        
        national_id = data.get('national_id')
        
        if not national_id:
            return jsonify({
                'success': False,
                'message': 'Student National ID is required',
                'code': 'MISSING_REQUIRED'
            }), 400
        
        # Get database cursor
        cursor = get_db_cursor()
        
        # Check if student exists
        cursor.execute("""
            SELECT student_id, first_name, last_name, email_address
            FROM student
            WHERE national_id = %s
        """, (national_id,))
        
        student = cursor.fetchone()
        
        if not student:
            return jsonify({
                'success': False,
                'message': 'Student not found with the provided National ID',
                'code': 'NOT_FOUND'
            }), 404
        
        student_id, first_name, last_name, email_address = student
        
        # Generate a random password
        import string
        import random
        
        # Generate a random password with 10 characters
        characters = string.ascii_letters + string.digits + string.punctuation
        new_password = ''.join(random.choice(characters) for i in range(10))
        
        # Hash the password
        hashed_password = generate_password_hash(new_password)
        
        # Update the student's password
        cursor.execute("""
            UPDATE student
            SET password = %s
            WHERE student_id = %s
        """, (hashed_password, student_id))
        
        current_app.mysql.connection.commit()
        
        # Send email with new password
        from email_service import mail
        from flask_mail import Message
        
        subject = "Your TBS Account Password Has Been Reset"
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e5ec; border-radius: 5px; background-color: #f8f9fa;">
            <div style="text-align: center; margin-bottom: 20px;">
                <h2 style="color: #4a5568;">Tunis Business School</h2>
            </div>
            <h2 style="color: #4a5568;">Password Reset</h2>
            <p>Hello {first_name} {last_name},</p>
            <p>Your TBS account password has been reset by an administrator. Your new password is:</p>
            <p style="margin: 25px 0; text-align: center; background-color: #edf2f7; padding: 10px; font-family: monospace; font-size: 18px; border-radius: 5px;">
                {new_password}
            </p>
            <p>Please log in with this password and change it immediately for security reasons.</p>
            <p>If you did not request this password reset, please contact the TBS administration immediately.</p>
            <p>Best regards,<br>TBS Administration</p>
        </div>
        """
        
        try:
            msg = Message(
                subject=subject,
                recipients=[email_address],
                html=html,
                sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'TBS Registration <majdhamdi777@gmail.com>')
            )
            mail.send(msg)
            current_app.logger.info(f"Password reset email sent to {email_address}")
        except Exception as e:
            current_app.logger.error(f"Failed to send password reset email: {str(e)}")
            # Return success even if email fails, but include the new password in the response
            # so admin can manually communicate it to the student
            return jsonify({
                'success': True,
                'message': 'Password reset successful but failed to send email notification',
                'code': 'EMAIL_FAILED',
                'new_password': new_password
            })
        
        return jsonify({
            'success': True,
            'message': 'Student password reset successfully and email sent',
            'code': 'SUCCESS'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error resetting student password: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred while resetting the student password',
            'details': str(e),
            'code': 'SERVER_ERROR'
        }), 500

