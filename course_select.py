from flask import current_app, jsonify

def get_course_registration_data(student_id):
    """Get all course registration data for a student"""
    cursor = current_app.mysql.connection.cursor()
    
    try:
        # Get current semester/year information
        current_semester = get_current_semester()
        current_year = get_current_year(student_id)
        
        # Get student's academic year and specializations
        cursor.execute("""
            SELECT year_of_study, non_french, major, second_major, minor, second_minor 
            FROM student 
            WHERE student_id = %s
        """, (student_id,))
        student_result = cursor.fetchone()
        
        student_year = student_result[0] if student_result else None
        is_non_french = bool(student_result[1]) if student_result else False
        
        # Count specializations (major, second_major, minor, second_minor)
        specialization_count = 0
        if student_result:
            for i in range(2, 6):  # indices 2-5 contain the specializations
                if student_result[i]:
                    specialization_count += 1
        
        # If no active semester, return early with None values
        if not current_semester or not current_year:
            return {
                'current_semester': None,
                'current_year': None,
                'student_year': student_year,
                'has_failed': False,
                'has_notenrolled': False,
                'failed_courses': [],
                'eligible_current_courses': [],
                'eligible_notenrolled_courses': [],
                'retake_courses': [],
                'not_met_requirements': [],
                'enrolled_courses': [],
                'extra_courses': [],
                'elective_courses': {},
                'specialization_count': specialization_count,
                'has_specializations': specialization_count > 0,
                'filtered_majors': []
            }
        
        # Check credit requirements for year 3+ students
        credit_requirement_met = True
        credit_status = None
        
        if student_year >= 3:
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
            
            # Calculate earned credits for year 1 and 2 courses - use DISTINCT to count each course only once
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
            
            # Calculate required credits based on min_percentage
            required_credits = None
            if min_percentage and total_weights:
                required_credits = total_weights * (min_percentage / 100)
                # For major eligibility, we check if ALL credits are earned (earned_credits >= total_weights)
                # For course registration, we check against the percentage (earned_credits >= required_credits)
                # Here we use the same criteria as in api/student.py for consistency
                credit_requirement_met = earned_credits >= total_weights
            
            credit_status = {
                'earned_credits': earned_credits,
                'required_credits': required_credits,
                'meets_requirement': credit_requirement_met,
                'min_percentage': min_percentage,
                'total_weights': total_weights
            }
        
        # Get student's course history flags
        has_failed = has_failed_courses(student_id)
        has_notenrolled = has_notenrolled_courses(student_id)
        
        # Get course lists
        failed_courses = get_failed_courses(student_id, current_semester, current_year)
        notenrolled_courses = get_notenrolled_courses(student_id, current_semester, current_year)
        retake_courses = get_retake_courses(student_id, current_semester, current_year)
        
        # Get eligible current courses
        current_courses_data = get_current_courses(current_semester, current_year, student_id)
        eligible_current, not_met_current = get_eligible_courses(student_id, current_courses_data['courses'])
        filtered_majors = current_courses_data['filtered_majors']
        
        # Get other course lists
        eligible_notenrolled, not_met_notenrolled = get_eligible_courses(student_id, notenrolled_courses)
        
        # Combine not met requirements from all sources
        not_met_requirements = not_met_current + not_met_notenrolled
        
        # Get currently enrolled courses
        enrolled_courses = get_enrolled_courses(student_id, current_semester, current_year)
        
        # Get extra courses (for 3rd year and above)
        extra_courses = []
        if student_year >= 3:
            extra_courses = get_extra_courses(current_semester, student_id)
            
        # Get elective courses
        elective_courses = get_elective_courses(current_semester, current_year, student_id)
        
        # Check if student is eligible to choose a major
        cursor.execute("""
            SELECT COUNT(*)
            FROM major_minor_requests mmr
            WHERE mmr.student_id = %s AND (mmr.status = 'accepted' OR mmr.status = 'pending')
            ORDER BY submission_date DESC
            LIMIT 1
        """, (student_id,))
        has_major_selection = cursor.fetchone()[0] > 0
        
        # Check if student has selected "NONE" as major
        cursor.execute("""
            SELECT major
            FROM major_minor_requests mmr
            WHERE mmr.student_id = %s AND (mmr.status = 'accepted' OR mmr.status = 'pending')
            ORDER BY submission_date DESC
            LIMIT 1
        """, (student_id,))
        major_selection = cursor.fetchone()
        selected_none = major_selection and major_selection[0] == 'NONE'
        
        # Get eligible majors count for this student
        cursor.execute("""
            SELECT acct_gpa, ba_gpa, fin_gpa, it_gpa, mrk_gpa
            FROM student_semester_summary
            WHERE student_id = %s
            ORDER BY year DESC, semester DESC
            LIMIT 1
        """, (student_id,))
        specialized_gpas = cursor.fetchone()
        
        cursor.execute("""
            SELECT min_gpa_acct, min_gpa_ba, min_gpa_fin, min_gpa_it, min_gpa_mrk
            FROM system_parameters
            ORDER BY last_updated DESC
            LIMIT 1
        """)
        min_gpas = cursor.fetchone()
        
        eligible_major_count = 0
        eligible_majors = []
        if specialized_gpas and min_gpas:
            major_codes = ['ACCT', 'BA', 'FIN', 'IT', 'MRK']
            for i in range(5):  # Check all 5 majors
                if specialized_gpas[i] is not None and min_gpas[i] is not None and specialized_gpas[i] >= min_gpas[i]:
                    eligible_major_count += 1
                    eligible_majors.append(major_codes[i])
        
        # Check if student has an accepted major (not pending)
        cursor.execute("""
            SELECT major
            FROM student
            WHERE student_id = %s AND major IS NOT NULL
        """, (student_id,))
        has_accepted_major = cursor.fetchone() is not None
        
        # Default guidance message - only show if student is not eligible or hasn't made a selection yet
        # Check if student meets all requirements to choose a major
        # 1. Must have at least one eligible major based on specialized GPA
        # 2. Must meet credit requirements for year 3+ (earned ALL year 1-2 credits)
        # 3. Must not already have an accepted major
        
        # Check if student is eligible for major based on the same criteria used in major_minor section
        is_eligible_for_major = eligible_major_count > 0 and (student_year < 3 or credit_requirement_met)
        
        if not is_eligible_for_major:
            if eligible_major_count == 0:
                guidance_message = "Dear Student, Since you are not eligible to choose a Major/Minor yet, we highly recommend picking courses related to the Major & Minor you are aiming for in the future. Please note that you can only select courses from majors where you meet the minimum specialized GPA requirements."
            else:
                guidance_message = "Dear Student, You need to earn ALL credits of Freshman and Sophomore levels before you can select a Major/Minor.<br>However, you are free to enroll in Junior courses related to a major where the minimum specialized GPA is met.<br>It is RECOMMANDED to enroll in courses that belongs to the Major/Minor combination you are aiming for."
        elif not has_accepted_major:
            guidance_message = "You are eligible to choose a Major/Minor. Please visit the Major/Minor section to make your selection."
        else:
            guidance_message = None  # No guidance message needed if student has already made a selection
        
        # For year 3+ students who don't meet credit requirements, filter out year 3-4 courses
        # For course registration, we use the percentage requirement (earned_credits >= required_credits)
        use_max_year_filter = student_year >= 3 and credit_status and not credit_status['meets_requirement']
        
        # If student doesn't meet credit requirements, get filtered courses limited to year 1-2
        if use_max_year_filter:
            max_year = 2  # Limit to Freshman and Sophomore courses
            current_courses_data = get_current_courses(current_semester, current_year, student_id, max_year=max_year)
            eligible_current, not_met_current = get_eligible_courses(student_id, current_courses_data['courses'])
            filtered_majors = current_courses_data['filtered_majors']
        
        return {
            'current_semester': current_semester,
            'current_year': current_year,
            'student_year': student_year,
            'has_failed': has_failed,
            'has_notenrolled': has_notenrolled,
            'failed_courses': failed_courses,
            'eligible_current_courses': eligible_current,
            'eligible_notenrolled_courses': eligible_notenrolled,
            'retake_courses': retake_courses,
            'not_met_requirements': not_met_requirements,
            'enrolled_courses': enrolled_courses,
            'extra_courses': extra_courses,
            'elective_courses': elective_courses,
            'guidance_message': guidance_message,
            'credit_status': credit_status,
            'specialization_count': specialization_count,
            'has_specializations': specialization_count > 0,
            'is_eligible_for_major': is_eligible_for_major,
            'filtered_majors': filtered_majors
        }
    except Exception as e:
        current_app.logger.error(f"Error in get_course_registration_data: {str(e)}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return None
    finally:
        cursor.close()

def get_current_semester():
    """Get current semester from academic_calendar"""
    cursor = current_app.mysql.connection.cursor()
    try:
        cursor.execute(
            "SELECT semester FROM academic_calendar WHERE is_current = 1 LIMIT 1"
        )
        result = cursor.fetchone()
        return result[0] if result else None
    except Exception as e:
        current_app.logger.error(f"Error in get_current_semester: {str(e)}")
        return None
    finally:
        cursor.close()

def get_current_year(student_id):
    """Get current year from student record"""
    cursor = current_app.mysql.connection.cursor()
    try:
        cursor.execute(
            "SELECT year_of_study FROM student WHERE student_id = %s",
            (student_id,)
        )
        result = cursor.fetchone()
        return result[0] if result else None
    except Exception as e:
        current_app.logger.error(f"Error in get_current_year: {str(e)}")
        return None
    finally:
        cursor.close()

def has_failed_courses(student_id):
    """Check if student has any currently failed courses"""
    cursor = current_app.mysql.connection.cursor()
    try:
        cursor.execute("""
            SELECT COUNT(*) FROM (
                SELECT ac1.course_code, ac1.status
                FROM add_course ac1
                INNER JOIN (
                    SELECT course_code, MAX(id) as latest_id
                    FROM add_course
                    WHERE student_id = %s
                    GROUP BY course_code
                ) latest ON ac1.id = latest.latest_id
                WHERE ac1.student_id = %s AND ac1.status = 'failed'
            ) as current_failed_courses
        """, (student_id, student_id))
        count = cursor.fetchone()[0]
        return count > 0
    except Exception as e:
        current_app.logger.error(f"Error in has_failed_courses: {str(e)}")
        return False
    finally:
        cursor.close()

def has_notenrolled_courses(student_id):
    """Check if student has any currently notenrolled courses"""
    cursor = current_app.mysql.connection.cursor()
    try:
        cursor.execute("""
            SELECT COUNT(*) FROM (
                SELECT ac1.course_code, ac1.status
                FROM add_course ac1
                INNER JOIN (
                    SELECT course_code, MAX(id) as latest_id
                    FROM add_course
                    WHERE student_id = %s
                    GROUP BY course_code
                ) latest ON ac1.id = latest.latest_id
                WHERE ac1.student_id = %s AND ac1.status = 'notenrolled'
            ) as current_notenrolled_courses
        """, (student_id, student_id))
        count = cursor.fetchone()[0]
        return count > 0
    except Exception as e:
        current_app.logger.error(f"Error in has_notenrolled_courses: {str(e)}")
        return False
    finally:
        cursor.close()

def get_enrolled_courses(student_id, semester, year):
    """Get currently enrolled courses for the current semester"""
    cursor = current_app.mysql.connection.cursor()
    try:
        cursor.execute("""
            SELECT ac.course_code, c.course_name, c.coefficient, ac.forgiveness
            FROM add_course ac
            JOIN courses c ON ac.course_code = c.course_code
            WHERE ac.student_id = %s 
            AND ac.semester = %s
            AND ac.year = %s
            AND ac.status = 'enrolled'
            ORDER BY ac.id DESC
        """, (student_id, semester, year))
        
        return [dict(zip([col[0] for col in cursor.description], row)) 
                for row in cursor.fetchall()]
    except Exception as e:
        current_app.logger.error(f"Error in get_enrolled_courses: {str(e)}")
        return []
    finally:
        cursor.close()

def get_failed_courses(student_id, current_semester, current_year):
    """Get the last failed attempt for each course from previous years"""
    cursor = current_app.mysql.connection.cursor()
    try:
        cursor.execute("""
        SELECT c.course_code, c.course_name, c.coefficient, 
               ac.year AS failed_year, ac.grade_point
        FROM (
            SELECT course_code, MAX(id) AS latest_id
            FROM add_course
            WHERE student_id = %s
            AND status = 'failed'
            AND year < %s
            GROUP BY course_code
        ) AS latest_failed
        JOIN add_course ac ON ac.id = latest_failed.latest_id
        JOIN courses c ON ac.course_code = c.course_code
        WHERE c.semester = %s
        AND NOT EXISTS (
            SELECT 1 FROM add_course ac2
            WHERE ac2.student_id = %s
            AND ac2.course_code = ac.course_code
            AND ac2.status = 'passed'
            AND ac2.year >= ac.year  # Passed in same or later year
        )
        """, (student_id, current_year, current_semester, student_id))

        return [dict(zip([col[0] for col in cursor.description], row))
                for row in cursor.fetchall()]
    except Exception as e:
        current_app.logger.error(f"Error in get_failed_courses: {str(e)}")
        return []
    finally:
        cursor.close()

def get_notenrolled_courses(student_id, current_semester, current_year):
    """Get notenrolled courses from previous years (same semester)"""
    cursor = current_app.mysql.connection.cursor()
    try:
        cursor.execute("""
            SELECT c.course_code, c.course_name, c.coefficient,
                   ac.year AS notenrolled_year
            FROM (
                SELECT course_code, MAX(year) AS max_year
                FROM add_course
                WHERE student_id = %s
                AND semester = %s
                AND status = 'notenrolled'
                AND year < %s
                GROUP BY course_code
            ) AS latest_notenrolled
            JOIN add_course ac ON ac.course_code = latest_notenrolled.course_code 
                              AND ac.year = latest_notenrolled.max_year
                              AND ac.status = 'notenrolled'
                              AND ac.student_id = %s
            JOIN courses c ON ac.course_code = c.course_code
            WHERE c.semester = %s
            AND NOT EXISTS (
                SELECT 1 FROM add_course ac2
                WHERE ac2.student_id = %s
                AND ac2.course_code = ac.course_code
                AND ac2.status = 'passed'
                AND ac2.year >= ac.year
            )
            AND NOT EXISTS (
                -- Exclude courses that have been registered for makeup (semester 3)
                SELECT 1 FROM add_course ac3
                WHERE ac3.student_id = %s
                AND ac3.course_code = ac.course_code
                AND ac3.semester = 3
            )
            ORDER BY c.course_code
        """, (student_id, current_semester, current_year, 
              student_id, current_semester, student_id, student_id))
        
        return [dict(zip([col[0] for col in cursor.description], row)) 
                for row in cursor.fetchall()]
    except Exception as e:
        current_app.logger.error(f"Error in get_notenrolled_courses: {str(e)}")
        return []
    finally:
        cursor.close()

def get_retake_courses(student_id, current_semester, current_year):
    """Get the last passed attempt (with grade_point <= maximum_forgive_grade) for each course from previous years"""
    cursor = current_app.mysql.connection.cursor()
    try:
        # Get maximum_forgive_grade from system_parameters
        cursor.execute("SELECT maximum_forgive_grade FROM system_parameters ORDER BY last_updated DESC LIMIT 1")
        min_grade_row = cursor.fetchone()
        maximum_forgive_grade = float(min_grade_row[0]) if min_grade_row and min_grade_row[0] is not None else 2.0

        cursor.execute("""
        SELECT c.course_code, c.course_name, c.coefficient, 
               ac.year AS passed_year, ac.grade_point, ac.letter_grade
        FROM (
            SELECT course_code, MAX(id) AS latest_id
            FROM add_course
            WHERE student_id = %s
            AND status = 'passed'
            AND grade_point <= %s
            AND year < %s
            GROUP BY course_code
        ) AS latest_passed
        JOIN add_course ac ON ac.id = latest_passed.latest_id
        JOIN courses c ON ac.course_code = c.course_code
        WHERE c.semester = %s
        AND NOT EXISTS (
            SELECT 1 FROM add_course ac2
            WHERE ac2.student_id = %s
            AND ac2.course_code = ac.course_code
            AND (
                (ac2.status = 'passed' AND ac2.grade_point > %s) OR  # Better passing grade
                (ac2.status = 'passed' AND ac2.year > ac.year)        # Or later passing attempt
            )
        )
        """, (student_id, maximum_forgive_grade, current_year, current_semester, student_id, maximum_forgive_grade))

        return [dict(zip([col[0] for col in cursor.description], row))
                for row in cursor.fetchall()]
    except Exception as e:
        current_app.logger.error(f"Error in get_retake_courses: {str(e)}")
        return []
    finally:
        cursor.close()

def get_current_courses(current_semester, current_year, student_id, max_year=None):
    """Get courses offered in current semester/year, considering French requirements and major/minor selections"""
    cursor = current_app.mysql.connection.cursor()
    try:
        # Get student's French status and academic info - ONLY from student table
        cursor.execute("""
            SELECT s.non_french, s.year_of_study, s.major, s.second_major, s.minor, s.second_minor
            FROM student s
            WHERE s.student_id = %s
        """, (student_id,))
        result = cursor.fetchone()
        
        if not result:
            return []
            
        non_french, year_of_study = result[0], result[1]
        major, second_major, minor, second_minor = result[2:6]

        # ONLY use selections from the student table (accepted majors/minors)
        # Ignore pending requests from major_minor_requests table
        selected_majors = []
        selected_majors.extend([m for m in [major, second_major] if m])

        selected_minors = []
        selected_minors.extend([m for m in [minor, second_minor] if m])

        # Get specialized GPAs and minimum required GPAs for each major
        eligible_majors = []
        all_majors = ['ACCT', 'BA', 'FIN', 'IT', 'MRK']
        filtered_majors = []  # Track majors that don't meet GPA requirements
        
        if year_of_study >= 3:
            # First check for student-specific parameter overrides
            cursor.execute("""
                SELECT min_gpa_acct, min_gpa_ba, min_gpa_fin, min_gpa_it, min_gpa_mrk
                FROM student_parameters_overrides
                WHERE student_id = %s
            """, (student_id,))
            
            min_gpas_override = cursor.fetchone()
            
            # If no overrides, get system parameters
            if not min_gpas_override:
                cursor.execute("""
                    SELECT min_gpa_acct, min_gpa_ba, min_gpa_fin, min_gpa_it, min_gpa_mrk
                    FROM system_parameters
                    ORDER BY last_updated DESC
                    LIMIT 1
                """)
                min_gpas = cursor.fetchone()
            else:
                min_gpas = min_gpas_override
                current_app.logger.info(f"Using parameter overrides for student {student_id}: {min_gpas}")
            
            if min_gpas:
                min_gpa_map = {
                    'ACCT': float(min_gpas[0]) if min_gpas[0] is not None else 0,
                    'BA': float(min_gpas[1]) if min_gpas[1] is not None else 0,
                    'FIN': float(min_gpas[2]) if min_gpas[2] is not None else 0,
                    'IT': float(min_gpas[3]) if min_gpas[3] is not None else 0,
                    'MRK': float(min_gpas[4]) if min_gpas[4] is not None else 0
                }
                
                # Get student's specialized GPAs
                cursor.execute("""
                    SELECT acct_gpa, ba_gpa, fin_gpa, it_gpa, mrk_gpa
                    FROM student_semester_summary
                    WHERE student_id = %s
                    ORDER BY year DESC, semester DESC
                    LIMIT 1
                """, (student_id,))
                
                specialized_gpas = cursor.fetchone()
                
                if specialized_gpas:
                    specialized_gpa_map = {
                        'ACCT': float(specialized_gpas[0]) if specialized_gpas[0] is not None else 0,
                        'BA': float(specialized_gpas[1]) if specialized_gpas[1] is not None else 0,
                        'FIN': float(specialized_gpas[2]) if specialized_gpas[2] is not None else 0,
                        'IT': float(specialized_gpas[3]) if specialized_gpas[3] is not None else 0,
                        'MRK': float(specialized_gpas[4]) if specialized_gpas[4] is not None else 0
                    }
                    
                    # Determine which majors meet the specialized GPA requirements
                    for major_code in all_majors:
                        if specialized_gpa_map[major_code] >= min_gpa_map[major_code]:
                            eligible_majors.append(major_code)
                        else:
                            filtered_majors.append(major_code)
                            
                    current_app.logger.info(f"Student {student_id} eligible majors based on specialized GPA: {eligible_majors}")
                    current_app.logger.info(f"Student {student_id} filtered majors due to insufficient GPA: {filtered_majors}")
                else:
                    # If no specialized GPAs found, assume no majors are eligible
                    current_app.logger.warning(f"No specialized GPAs found for student {student_id}")
                    filtered_majors = all_majors
            else:
                # If no minimum GPA requirements found, assume all majors are eligible
                current_app.logger.warning("No minimum GPA requirements found in system_parameters")
                eligible_majors = all_majors.copy()

        # Base query - note we don't filter by year here as it will be handled in the conditions
        query = """
            SELECT course_code, course_name, coefficient, requires_french, for_major
            FROM courses
            WHERE semester = %s
            AND in_curriculum = 1
            AND NOT EXISTS (
                SELECT 1 FROM course_elective_groups ceg
                WHERE ceg.course_id = courses.id
            )
        """
        params = [current_semester]

        # If student is non-French, exclude courses that require French
        if non_french:
            query += " AND (requires_french = 0 OR requires_french IS NULL)"

        # If student is in 3rd year and has at least 2 selections
        if year_of_study >= 3 and len(selected_majors) + len(selected_minors) >= 2:
            major_minor_conditions = []
            
            # Add conditions for majors - these use the default year
            if selected_majors:
                major_conditions = []
                for major in selected_majors:
                    major_conditions.append(f"(FIND_IN_SET(%s, for_major) > 0 AND year = %s)")
                    params.append(major)
                    params.append(current_year)
                major_minor_conditions.append("(" + " OR ".join(major_conditions) + ")")
            
            # Add conditions for minors with major restriction and proper year handling
            if selected_minors:
                minor_conditions = []
                for minor in selected_minors:
                    # For each minor, create a condition that checks:
                    # 1. If the course is for this minor AND
                    # 2. Either:
                    #    a. for_minor_if_major_is is NULL (no major restriction) OR
                    #    b. Student's major is in for_minor_if_major_is AND
                    # 3. The year matches either:
                    #    a. minor_study_year if it's set OR
                    #    b. the default year if minor_study_year is NULL
                    minor_condition = f"""(
                        FIND_IN_SET(%s, for_minor) > 0 AND 
                        (
                            for_minor_if_major_is IS NULL OR 
                            {' OR '.join(['FIND_IN_SET(%s, for_minor_if_major_is) > 0' for _ in selected_majors])}
                        ) AND
                        (
                            (minor_study_year IS NOT NULL AND minor_study_year = %s) OR
                            (minor_study_year IS NULL AND year = %s)
                        )
                    )"""
                    minor_conditions.append(minor_condition)
                    params.append(minor)
                    # Add each major to params for the FIND_IN_SET checks
                    params.extend(selected_majors)
                    # Add current year twice - once for minor_study_year check, once for default year check
                    params.append(current_year)
                    params.append(current_year)
                
                major_minor_conditions.append("(" + " OR ".join(minor_conditions) + ")")
            
            # Combine all conditions
            if major_minor_conditions:
                query += " AND (" + " OR ".join(major_minor_conditions) + ")"
        else:
            # For non-major/minor specific courses, use the default year
            query += " AND year = %s"
            params.append(current_year)

        if max_year:
            query += " AND year <= %s"
            params.append(max_year)

        cursor.execute(query, tuple(params))
        
        courses = [dict(zip([col[0] for col in cursor.description], row)) 
                for row in cursor.fetchall()]
        
        # Filter courses based on specialized GPA requirements for year 3+ students
        # who don't have enough selections but meet the credit percentage requirement
        if year_of_study >= 3 and (len(selected_majors) + len(selected_minors) < 2) and eligible_majors:
            filtered_courses = []
            for course in courses:
                course_major = course.get('for_major')
                
                # If course is not assigned to any major or is assigned to an eligible major, include it
                if not course_major or course_major == '' or any(major in eligible_majors for major in course_major.split(',')):
                    filtered_courses.append(course)
                else:
                    current_app.logger.info(f"Filtering out course {course['course_code']} for major {course_major} due to insufficient specialized GPA")
            
            # Return courses along with filtered majors information
            return {
                'courses': filtered_courses,
                'filtered_majors': filtered_majors
            }
        
        # Return courses along with empty filtered majors list (no filtering occurred)
        return {
            'courses': courses,
            'filtered_majors': []
        }
    except Exception as e:
        current_app.logger.error(f"Error in get_current_courses: {str(e)}")
        return {'courses': [], 'filtered_majors': []}
    finally:
        cursor.close()

def get_extra_courses(current_semester, student_id):
    """Get extra courses available for 3rd year and above students"""
    cursor = current_app.mysql.connection.cursor()
    try:
        # Get student's academic year and French status
        cursor.execute("""
            SELECT year_of_study, non_french
            FROM student
            WHERE student_id = %s
        """, (student_id,))
        student_info = cursor.fetchone()
        
        if not student_info or student_info[0] < 3:  # year_of_study < 3
            return []
            
        year_of_study, non_french = student_info
        
        # Get specialized GPAs and minimum required GPAs for each major
        eligible_majors = []
        
        # First check for student-specific parameter overrides
        cursor.execute("""
            SELECT min_gpa_acct, min_gpa_ba, min_gpa_fin, min_gpa_it, min_gpa_mrk
            FROM student_parameters_overrides
            WHERE student_id = %s
        """, (student_id,))
        
        min_gpas_override = cursor.fetchone()
        
        # If no overrides, get system parameters
        if not min_gpas_override:
            cursor.execute("""
                SELECT min_gpa_acct, min_gpa_ba, min_gpa_fin, min_gpa_it, min_gpa_mrk
                FROM system_parameters
                ORDER BY last_updated DESC
                LIMIT 1
            """)
            min_gpas = cursor.fetchone()
        else:
            min_gpas = min_gpas_override
            current_app.logger.info(f"Using parameter overrides for student {student_id} in extra courses: {min_gpas}")
        
        if min_gpas:
            min_gpa_map = {
                'ACCT': float(min_gpas[0]) if min_gpas[0] is not None else 0,
                'BA': float(min_gpas[1]) if min_gpas[1] is not None else 0,
                'FIN': float(min_gpas[2]) if min_gpas[2] is not None else 0,
                'IT': float(min_gpas[3]) if min_gpas[3] is not None else 0,
                'MRK': float(min_gpas[4]) if min_gpas[4] is not None else 0
            }
            
            # Get student's specialized GPAs
            cursor.execute("""
                SELECT acct_gpa, ba_gpa, fin_gpa, it_gpa, mrk_gpa
                FROM student_semester_summary
                WHERE student_id = %s
                ORDER BY year DESC, semester DESC
                LIMIT 1
            """, (student_id,))
            
            specialized_gpas = cursor.fetchone()
            
            if specialized_gpas:
                specialized_gpa_map = {
                    'ACCT': float(specialized_gpas[0]) if specialized_gpas[0] is not None else 0,
                    'BA': float(specialized_gpas[1]) if specialized_gpas[1] is not None else 0,
                    'FIN': float(specialized_gpas[2]) if specialized_gpas[2] is not None else 0,
                    'IT': float(specialized_gpas[3]) if specialized_gpas[3] is not None else 0,
                    'MRK': float(specialized_gpas[4]) if specialized_gpas[4] is not None else 0
                }
                
                # Determine which majors meet the specialized GPA requirements
                for major_code in ['ACCT', 'BA', 'FIN', 'IT', 'MRK']:
                    if specialized_gpa_map[major_code] >= min_gpa_map[major_code]:
                        eligible_majors.append(major_code)
                        
                current_app.logger.info(f"Student {student_id} eligible majors for extra courses based on specialized GPA: {eligible_majors}")
            else:
                # If no specialized GPAs found, assume no majors are eligible
                current_app.logger.warning(f"No specialized GPAs found for student {student_id}")
        else:
            # If no minimum GPA requirements found, assume all majors are eligible
            current_app.logger.warning("No minimum GPA requirements found in system_parameters")
            eligible_majors = ['ACCT', 'BA', 'FIN', 'IT', 'MRK']
        
        # First, get current courses to exclude from extra courses
        current_year = year_of_study  # Use student's year of study as current year
        current_courses = get_current_courses(current_semester, current_year, student_id)
        current_course_codes = {course['course_code'] for course in current_courses['courses']} if current_courses['courses'] else set()
        
        # Build query to get all eligible courses
        query = """
            SELECT DISTINCT c.course_code, c.course_name, c.coefficient, 
                   c.year, c.for_major, c.for_minor, c.description
            FROM courses c
            WHERE c.semester = %s
            AND c.in_curriculum = 1
            AND (c.as_extra = 1 OR c.as_extra IS NULL)
            AND (
                (c.year <= %s) -- Allow courses up to current academic year
                OR (%s >= 4)   -- If student is in year 4 or above, show all courses
            )
            AND NOT EXISTS (
                -- Exclude ALL courses from add_course regardless of status
                SELECT 1 FROM add_course ac
                WHERE ac.student_id = %s
                AND ac.course_code = c.course_code
            )
        """
        params = [current_semester, year_of_study, year_of_study, student_id]

        # Add French requirement filter if needed
        if non_french:
            query += " AND (c.requires_french = 0 OR c.requires_french IS NULL)"

        cursor.execute(query, tuple(params))
        
        # Fetch all potential courses
        courses = [dict(zip([col[0] for col in cursor.description], row)) 
                  for row in cursor.fetchall()]
        
        # Filter courses based on prerequisites, exclude current courses, and filter by eligible majors
        eligible_courses = []
        for course in courses:
            # Skip courses that are already in current_courses
            if course['course_code'] in current_course_codes:
                continue
            
            # Check if course is for a major that meets specialized GPA requirements
            course_major = course.get('for_major')
            if course_major and course_major != '':
                # Check if any of the course's majors are in the eligible majors list
                major_match = False
                for major in course_major.split(','):
                    if major in eligible_majors:
                        major_match = True
                        break
                
                if not major_match:
                    current_app.logger.info(f"Filtering out extra course {course['course_code']} for major {course_major} due to insufficient specialized GPA")
                    continue
            
            # Only add courses that meet prerequisites
            if check_prerequisites(student_id, course['course_code']):
                eligible_courses.append(course)
        
        return eligible_courses

    except Exception as e:
        current_app.logger.error(f"Error in get_extra_courses: {str(e)}")
        return []
    finally:
        cursor.close()

def get_elective_courses(current_semester, current_year, student_id):
    """Get elective courses grouped by elective_group_number with their requirements"""
    cursor = current_app.mysql.connection.cursor()
    try:
        # Get student's French status, majors, and year of study
        cursor.execute("""
            SELECT non_french, major, second_major, year_of_study
            FROM student
            WHERE student_id = %s
        """, (student_id,))
        student_result = cursor.fetchone()
        is_non_french = bool(student_result[0]) if student_result else False
        student_major = student_result[1] if student_result else None
        student_second_major = student_result[2] if student_result else None
        year_of_study = student_result[3] if student_result else 1
        
        # Get specialized GPAs and minimum required GPAs for each major if student is year 3+
        eligible_majors = []
        if year_of_study >= 3:
            # First check for student-specific parameter overrides
            cursor.execute("""
                SELECT min_gpa_acct, min_gpa_ba, min_gpa_fin, min_gpa_it, min_gpa_mrk
                FROM student_parameters_overrides
                WHERE student_id = %s
            """, (student_id,))
            
            min_gpas_override = cursor.fetchone()
            
            # If no overrides, get system parameters
            if not min_gpas_override:
                cursor.execute("""
                    SELECT min_gpa_acct, min_gpa_ba, min_gpa_fin, min_gpa_it, min_gpa_mrk
                    FROM system_parameters
                    ORDER BY last_updated DESC
                    LIMIT 1
                """)
                min_gpas = cursor.fetchone()
            else:
                min_gpas = min_gpas_override
                current_app.logger.info(f"Using parameter overrides for student {student_id} in elective courses: {min_gpas}")
            
            if min_gpas:
                min_gpa_map = {
                    'ACCT': float(min_gpas[0]) if min_gpas[0] is not None else 0,
                    'BA': float(min_gpas[1]) if min_gpas[1] is not None else 0,
                    'FIN': float(min_gpas[2]) if min_gpas[2] is not None else 0,
                    'IT': float(min_gpas[3]) if min_gpas[3] is not None else 0,
                    'MRK': float(min_gpas[4]) if min_gpas[4] is not None else 0
                }
                
                # Get student's specialized GPAs
                cursor.execute("""
                    SELECT acct_gpa, ba_gpa, fin_gpa, it_gpa, mrk_gpa
                    FROM student_semester_summary
                    WHERE student_id = %s
                    ORDER BY year DESC, semester DESC
                    LIMIT 1
                """, (student_id,))
                
                specialized_gpas = cursor.fetchone()
                
                if specialized_gpas:
                    specialized_gpa_map = {
                        'ACCT': float(specialized_gpas[0]) if specialized_gpas[0] is not None else 0,
                        'BA': float(specialized_gpas[1]) if specialized_gpas[1] is not None else 0,
                        'FIN': float(specialized_gpas[2]) if specialized_gpas[2] is not None else 0,
                        'IT': float(specialized_gpas[3]) if specialized_gpas[3] is not None else 0,
                        'MRK': float(specialized_gpas[4]) if specialized_gpas[4] is not None else 0
                    }
                    
                    # Determine which majors meet the specialized GPA requirements
                    for major_code in ['ACCT', 'BA', 'FIN', 'IT', 'MRK']:
                        if specialized_gpa_map[major_code] >= min_gpa_map[major_code]:
                            eligible_majors.append(major_code)
                            
                    current_app.logger.info(f"Student {student_id} eligible majors for elective courses based on specialized GPA: {eligible_majors}")
                else:
                    # If no specialized GPAs found, assume no majors are eligible
                    current_app.logger.warning(f"No specialized GPAs found for student {student_id}")
            else:
                # If no minimum GPA requirements found, assume all majors are eligible
                current_app.logger.warning("No minimum GPA requirements found in system_parameters")
                eligible_majors = ['ACCT', 'BA', 'FIN', 'IT', 'MRK']
        else:
            # For students in years 1-2, all majors are eligible
            eligible_majors = ['ACCT', 'BA', 'FIN', 'IT', 'MRK']
        
        # Get elective courses for the current semester
        query = """
            SELECT c.course_code, c.course_name, c.coefficient,
                   ceg.elective_group_number, c.for_major, egr.follows_major_pick,
                   egr.related_to_course, egr.maximum_picks
            FROM courses c
            JOIN course_elective_groups ceg ON c.id = ceg.course_id
            JOIN elective_group_requirements egr ON ceg.elective_group_number = egr.elective_group_number
            WHERE c.semester = %s
            AND c.year = %s
            AND c.in_curriculum = 1
        """
        params = [current_semester, current_year]
        
        # Add French requirement filter if needed
        if is_non_french:
            query += " AND (c.requires_french = 0 OR c.requires_french IS NULL)"
            
        # Order by elective group and course code
        query += " ORDER BY ceg.elective_group_number, c.course_code"
        
        cursor.execute(query, tuple(params))
        
        # Fetch all elective courses
        all_courses = [dict(zip([col[0] for col in cursor.description], row)) 
                      for row in cursor.fetchall()]
        
        # Filter courses based on follows_major_pick, student's majors, and specialized GPA requirements
        filtered_courses = []
        for course in all_courses:
            follows_major_pick = bool(course['follows_major_pick'])
            course_for_major = course['for_major']
            
            # For year 3+ students, check if the course is for a major that meets specialized GPA requirements
            if year_of_study >= 3 and course_for_major and course_for_major not in ('', None):
                # Check if any of the course's majors are in the eligible majors list
                major_match = False
                for major in course_for_major.split(','):
                    if major in eligible_majors:
                        major_match = True
                        break
                
                if not major_match:
                    current_app.logger.info(f"Filtering out elective course {course['course_code']} for major {course_for_major} due to insufficient specialized GPA")
                    continue
            
            # If follows_major_pick is True and course has a specific major requirement
            if follows_major_pick and course_for_major and course_for_major not in ('', None):
                # Only include if it matches student's major or second major
                if course_for_major == student_major or course_for_major == student_second_major:
                    filtered_courses.append(course)
            else:
                # No major restriction or doesn't follow major pick
                filtered_courses.append(course)
        
        # Get requirements for each elective group
        cursor.execute("""
            SELECT elective_group_number, required_picks, maximum_picks, related_to_course
            FROM elective_group_requirements
        """)
        
        # Create a dictionary of requirements by group number
        requirements = {}
        for row in cursor.fetchall():
            group_num, req_picks, max_picks, related_ids = row
            # Parse related_ids (comma-separated list of course IDs) -> list[int]
            related_id_list = []
            if related_ids:
                try:
                    related_id_list = [int(i.strip()) for i in related_ids.split(',') if i.strip().isdigit()]
                except ValueError:
                    current_app.logger.warning(f"Invalid related_to_course format for elective group {group_num}: {related_ids}")
            # Translate IDs to course codes offered this semester/year
            related_course_codes = []
            if related_id_list:
                format_strings = ','.join(['%s'] * len(related_id_list))
                cursor.execute(f"""
                    SELECT course_code FROM courses
                    WHERE id IN ({format_strings}) AND semester = %s AND year = %s
                """, tuple(related_id_list + [current_semester, current_year]))
                related_course_codes = [row[0] for row in cursor.fetchall()]
            requirements[group_num] = {
                'required_picks': req_picks,
                'maximum_picks': max_picks,
                'related_to_course': related_ids,
                'related_course_codes': related_course_codes
            }
        
        # Group courses by elective_group_number
        grouped_courses = {}
        for course in filtered_courses:
            group_number = course['elective_group_number']

            # Skip group if it is tied to other course(s) that are *not* offered this semester/year
            group_req = requirements.get(group_number, {})
            related_codes_offered = group_req.get('related_course_codes', [])
            if group_req.get('related_to_course') and not related_codes_offered:
                # No related courses offered → do not include this group at all
                continue

            if group_number not in grouped_courses:
                grouped_courses[group_number] = {
                    'courses': [],
                    'required_picks': group_req.get('required_picks', 0),
                    'maximum_picks': group_req.get('maximum_picks'),
                    'related_to_course': group_req.get('related_to_course'),
                    'related_course_codes': related_codes_offered
                }
            grouped_courses[group_number]['courses'].append(course)
        
        # Check if student has already enrolled in any of these courses
        for group_number, group_data in grouped_courses.items():
            for course in group_data['courses']:
                cursor.execute("""
                    SELECT status
                    FROM add_course
                    WHERE student_id = %s
                    AND course_code = %s
                    AND status IN ('enrolled', 'passed')
                    ORDER BY id DESC
                    LIMIT 1
                """, (student_id, course['course_code']))
                
                result = cursor.fetchone()
                course['enrolled'] = result is not None and result[0] in ('enrolled', 'passed')
                
                # Check prerequisites
                course['eligible'] = check_prerequisites(student_id, course['course_code'])
        
        return grouped_courses
        
    except Exception as e:
        current_app.logger.error(f"Error in get_elective_courses: {str(e)}")
        return {}
    finally:
        cursor.close()

def get_eligible_courses(student_id, courses):
    """Filter courses to only those where prerequisites are met"""
    eligible = []
    not_met = []
    
    for course in courses:
        if check_prerequisites(student_id, course['course_code']):
            eligible.append(course)
        else:
            not_met.append(course)
    
    return eligible, not_met

def check_prerequisites(student_id, course_code):
    """Check if student has passed all prerequisites for a course"""
    cursor = current_app.mysql.connection.cursor()
    try:
        # Get all prerequisites for the course
        cursor.execute("""
            SELECT cp.prerequisite_id 
            FROM course_prerequisites cp
            JOIN courses c ON cp.course_id = c.id
            WHERE c.course_code = %s
        """, (course_code,))
        prerequisites = [row[0] for row in cursor.fetchall()]
        
        if not prerequisites:
            return True  # No prerequisites
        
        # Check if student has passed all prerequisites
        cursor.execute("""
            SELECT COUNT(DISTINCT c.id) 
            FROM courses c
            JOIN add_course ac ON c.course_code = ac.course_code
            WHERE ac.student_id = %s 
            AND c.id IN %s
            AND ac.status = 'passed'
            AND ac.id = (
                SELECT MAX(id) FROM add_course 
                WHERE student_id = ac.student_id 
                AND course_code = ac.course_code
            )
        """, (student_id, tuple(prerequisites)))
        
        passed_count = cursor.fetchone()[0]
        return passed_count == len(prerequisites)
        
    except Exception as e:
        current_app.logger.error(f"Error in check_prerequisites: {str(e)}")
        return False
    finally:
        cursor.close()