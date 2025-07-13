import pulp
import mysql.connector
from datetime import datetime, time, timedelta
from flask import current_app
from collections import defaultdict

class ScheduleOptimizer:

    def __init__(self, db_connection, student_id):

        self.db = db_connection
        self.student_id = student_id
        self.cursor = self.db.cursor()
        
        self.enrolled_courses = []
        self.schedule_options = []
        self.course_sessions = {}
        self.groups = {}
        
        # Initialize student group and level information
        self.student_group = None
        self.student_level = None
        self.has_failed_courses = False
        self.has_skipped_courses = False
        
        # Initialize FixSlot as an instance variable
        self.FixSlot = []
        
        # Initialize FixProf for fixed professor assignments (i,k,p)
        # Each item will be a tuple: (course_index, session_number, professor_index)
        self.FixProf = []
        
        # Initialize preferences and weights
        self.preferences = None
        self.timeslot_weights = {}
        
    def load_data(self):
        self._load_student_info()
        self._load_enrolled_courses()
        self._load_course_sessions()
        self._load_schedule_options()
        self._load_professor_preferences()
        self._load_timeslot_preferences()
        self._check_failed_skipped_courses()
        
    def _load_student_info(self):
        """Load student group information from the database"""
        # Try to fetch both main group and academic level (if the column exists)
        query = "SELECT `group`, level FROM student WHERE student_id = %s"
        try:
            self.cursor.execute(query, (self.student_id,))
            result = self.cursor.fetchone()
            if result:
                self.student_group = result[0]
                self.student_level = result[1] if len(result) > 1 else None
                current_app.logger.debug(
                    f"Loaded student group: {self.student_group}, level: {self.student_level}")
        except mysql.connector.Error as e:
            # Fallback: older schema without a level column
            current_app.logger.warning("Student table does not include 'level' column or query failed; proceeding without level info")
            query_fallback = "SELECT `group` FROM student WHERE student_id = %s"
            self.cursor.execute(query_fallback, (self.student_id,))
            result = self.cursor.fetchone()
            if result:
                self.student_group = result[0]
                current_app.logger.debug(f"Loaded student main group: {self.student_group}")
        
        # Initialize course-specific groups
        self.lecture_groups = {}
        self.tutorial_groups = {}
        
        # Load course-specific groups from add_course table
        query = """
            SELECT course_code, lecture_study_group, tutorial_study_group
            FROM add_course
            WHERE student_id = %s
            AND status = 'enrolled'
        """
        self.cursor.execute(query, (self.student_id,))
        for course_code, lecture_group, tutorial_group in self.cursor.fetchall():
            if lecture_group and lecture_group.strip():
                self.lecture_groups[course_code] = lecture_group
            if tutorial_group and tutorial_group.strip():
                self.tutorial_groups[course_code] = tutorial_group
                
        if self.lecture_groups or self.tutorial_groups:
            current_app.logger.debug(f"Loaded course-specific groups: {len(self.lecture_groups)} lecture groups, {len(self.tutorial_groups)} tutorial groups")
            
    def _check_failed_skipped_courses(self):
        """Check if student has failed or skipped courses by looking at add_course table"""
        # First get all course history for the student, ordered by course and date
        query = """
            SELECT course_code, status, date
                    FROM add_course
                    WHERE student_id = %s
            ORDER BY course_code, date DESC
        """
        self.cursor.execute(query, (self.student_id,))
        
        # Build a mapping of course -> list of statuses (descending by date)
        status_map = defaultdict(list)
        for course_code, status, _ in self.cursor.fetchall():
            status_map[course_code].append(status)

        self.current_failed_courses = []
        skipped_any = False

        for course_code, statuses in status_map.items():
            # Find the first status that is not 'enrolled'
            first_non_enrolled = None
            for st in statuses:
                if st != 'enrolled':
                    first_non_enrolled = st
                    break

            if first_non_enrolled == 'failed':
                self.current_failed_courses.append(course_code)
            if first_non_enrolled == 'notenrolled':
                skipped_any = True

        # Determine overall flags
        self.has_failed_courses = len(self.current_failed_courses) > 0
        self.has_skipped_courses = skipped_any

        current_app.logger.debug(
            f"Student {self.student_id} failed courses: {self.current_failed_courses}, skipped_any: {self.has_skipped_courses}")
        
    def _load_enrolled_courses(self):
        query = """
            SELECT ac.course_code
            FROM add_course ac
            WHERE ac.student_id = %s 
            AND ac.status = 'enrolled'
        """
        self.cursor.execute(query, (self.student_id,))
        self.enrolled_courses = [row[0] for row in self.cursor.fetchall()]
        current_app.logger.debug(f"Loaded {len(self.enrolled_courses)} enrolled courses for student {self.student_id}")
        
        # Load course indices for enrolled courses
        self.course_indices = {}
        if self.enrolled_courses:
            placeholders = ', '.join(['%s'] * len(self.enrolled_courses))
            query = f"""
                SELECT DISTINCT course_code, course_index 
                FROM schedule 
                WHERE course_code IN ({placeholders})
            """
            self.cursor.execute(query, self.enrolled_courses)
            for row in self.cursor.fetchall():
                self.course_indices[row[0]] = row[1]
            current_app.logger.debug(f"Loaded course indices: {self.course_indices}")
            
    def _load_course_sessions(self):
        """Determine required number of sessions for each course"""
        if not self.enrolled_courses:
            current_app.logger.warning("No enrolled courses found, skipping course sessions loading")
            return
            
        placeholders = ', '.join(['%s'] * len(self.enrolled_courses))
        query = f"""
            SELECT course_code, lecture_sessions, tutorial_sessions, total_sessions
            FROM course_sessions
            WHERE course_code IN ({placeholders})
        """
        self.cursor.execute(query, self.enrolled_courses)
        
        for row in self.cursor.fetchall():
            self.course_sessions[row[0]] = {
                'lecture_sessions': row[1],
                'tutorial_sessions': row[2],
                'total_sessions': row[3]
            }
        current_app.logger.debug(f"Loaded session info for {len(self.course_sessions)} courses")
    
    def _load_schedule_options(self):
        if not self.enrolled_courses:
            current_app.logger.warning("No enrolled courses found")
            return
            
        # Log the enrolled courses
        current_app.logger.debug(f"Loading schedule options for courses: {self.enrolled_courses}")
            
        placeholders = ', '.join(['%s'] * len(self.enrolled_courses))
        query = f"""
            SELECT id, course_code, week_day, start_time, end_time, 
                   professor, classroom, `group`,
                   course_index, session_number_index,
                   time_slot_index, professor_index,
                   Tutprof_index, lect_prof_index
            FROM schedule
            WHERE course_code IN ({placeholders})
        """
        self.cursor.execute(query, self.enrolled_courses)
        
        # Convert to list of dictionaries
        columns = [col[0] for col in self.cursor.description]
        self.schedule_options = []
        
        for row in self.cursor.fetchall():
            option = dict(zip(columns, row))
            # Make sure time_slot_index is an integer
            if 'time_slot_index' in option and option['time_slot_index'] is not None:
                try:
                    option['time_slot_index'] = int(option['time_slot_index'])
                except (ValueError, TypeError):
                    current_app.logger.warning(f"Invalid time_slot_index value: {option['time_slot_index']} for course {option.get('course_code')}")
            self.schedule_options.append(option)
            
        # Log results
        if not self.schedule_options:
            current_app.logger.warning(f"No schedule options found in database for courses: {self.enrolled_courses}")
        else:
            # Log counts by course
            courses_count = {}
            session_numbers = {}
            time_slots = {}
            
            for option in self.schedule_options:
                course = option.get('course_code')
                session = option.get('session_number_index')
                slot = option.get('time_slot_index')
                
                # Count by course
                if course not in courses_count:
                    courses_count[course] = 0
                courses_count[course] += 1
                
                # Count by session number
                if session not in session_numbers:
                    session_numbers[session] = 0
                session_numbers[session] += 1
                
                # Count by time slot
                if slot not in time_slots:
                    time_slots[slot] = 0
                time_slots[slot] += 1
            
            current_app.logger.debug(f"Loaded {len(self.schedule_options)} schedule options")
            current_app.logger.debug(f"Options by course: {courses_count}")
            current_app.logger.debug(f"Options by session number: {session_numbers}")
            current_app.logger.debug(f"Options by time slot: {time_slots}")
            
            # Sample some options
            if self.schedule_options:
                current_app.logger.debug(f"Sample schedule option: {self.schedule_options[0]}")
    
    def _load_professor_preferences(self):
        """Load professor preferences for the student"""
        self.professor_preferences = {}
        
        query = """
            SELECT course_code, professor_index, ranked
            FROM professor_preferences
            WHERE student_id = %s
        """
        self.cursor.execute(query, (self.student_id,))
        
        for row in self.cursor.fetchall():
            course_code, professor_index, rank = row
            
            if course_code not in self.professor_preferences:
                self.professor_preferences[course_code] = {}
                
            self.professor_preferences[course_code][professor_index] = rank
            
        current_app.logger.debug(f"Loaded professor preferences for student {self.student_id}")
        
    def _load_timeslot_preferences(self):
        """Load time slot preferences for the student"""
        self.timeslot_preferences = {}
        
        query = """
            SELECT time_slot_number, is_preferred
            FROM time_slot_preferences
            WHERE student_id = %s
        """
        self.cursor.execute(query, (self.student_id,))
        
        for row in self.cursor.fetchall():
            time_slot_number, is_preferred = row
            self.timeslot_preferences[time_slot_number] = is_preferred
            
        # Initialize timeslot_weights dictionary
        self.timeslot_weights = {}
        
        # We'll load the specific weight when build_model is called
        # based on the priority_mode in preferences
        current_app.logger.debug(f"Loaded time slot preferences for student {self.student_id}")
        
    def load_weight_from_db(self, priority_mode=None):
        
        # Fetch all schedule-wide parameters (weights, max solutions, time limit)
        weight_query = (
            "SELECT weight_mode_a, weight_mode_b, maximum_solutions, time_limit "
            "FROM schedule_parameters LIMIT 1"
        )
        self.cursor.execute(weight_query)
        weight_row = self.cursor.fetchone()

        if not weight_row:
            error_msg = (
                "No schedule parameters found in database. "
                "Please add a row to the schedule_parameters table."
            )
            current_app.logger.error(error_msg)
            raise ValueError(error_msg)

        weight_mode_a = float(weight_row[0])
        weight_mode_b = float(weight_row[1])

        # Read additional global parameters -----------------------------------------
        try:
            self.maximum_solutions = int(weight_row[2])
            self.model_time_limit = int(weight_row[3])
        except (TypeError, ValueError):
            error_msg = "Invalid maximum_solutions or time_limit value in schedule_parameters table."
            current_app.logger.error(error_msg)
            raise ValueError(error_msg)

        # ------------------------------------------------------------------
        # Determine which priority mode (a or b) should be active
        # ------------------------------------------------------------------
        priority_letter = None  # will be set to 'a' or 'b'

        # 1. Explicit override provided by the caller ----------------------------------


        # 2. Otherwise, fetch the student's stored preference --------------------------
        if priority_letter is None:
            pref_query = "SELECT priority FROM priority_preferences WHERE student_id = %s"
            self.cursor.execute(pref_query, (self.student_id,))
            pref_row = self.cursor.fetchone()
            if pref_row and pref_row[0] in ('a', 'b'):
                priority_letter = pref_row[0]
                current_app.logger.debug(
                    f"Loaded stored priority '{priority_letter}' for student {self.student_id}"
                )
            else:
                priority_letter = 'a'  # default if nothing stored

        # 3. Choose the correct weight --------------------------------------------------
        if priority_letter == 'b':
            self.timeslot_weights['active_weight'] = weight_mode_b
            current_app.logger.debug(
                f"Using priority 'b' (professors). Weight: {weight_mode_b}"
            )
        else:
            self.timeslot_weights['active_weight'] = weight_mode_a
            current_app.logger.debug(
                f"Using priority 'a' (timeslots). Weight: {weight_mode_a}"
            )

        return self.timeslot_weights['active_weight']
        
    def _load_weight_from_db(self, priority_mode=None):
        """Load the appropriate weight from the database based on priority mode"""
        # This is now just a wrapper around the public method for backward compatibility
        return self.load_weight_from_db(priority_mode)
        
    def build_model(self):
        """Build the integer linear programming model based on the mathematical formulation"""
        # Create the model - maximize objective function
        model = pulp.LpProblem(name="Student_Schedule_Optimization", sense=pulp.LpMaximize)
        
        # If no enrolled courses or schedule options, return empty model
        if not self.enrolled_courses or not self.schedule_options:
            current_app.logger.warning(f"Cannot build model: enrolled_courses={len(self.enrolled_courses)}, schedule_options={len(self.schedule_options)}")
            return model, {}, {}
            
        # Always load the weight from the database
        # This will use the stored mode if no explicit priority_mode is provided
        self.load_weight_from_db(
            priority_mode=self.preferences.get('priority_mode') if self.preferences else None
        )
        
        # Define sets as in the mathematical formulation
        # Set I: indexes for the courses the student is enrolled in
        I = {}
        for course_code in self.enrolled_courses:
            if course_code in self.course_indices:
                I[course_code] = self.course_indices[course_code]
            else:
                # If no index found, use the course code as a fallback
                current_app.logger.warning(f"No course index found for {course_code}, using course code as index")
                I[course_code] = course_code
        current_app.logger.debug(f"Set I (enrolled courses with indices): {I}")
        
        # Set I_1: subset of I containing indexes of courses that have tutorials
        # Set I_2: subset of I containing indexes of courses that do not have tutorials
        I_1 = {}
        I_2 = {}
        
        for course_code, i in I.items():
            if self.course_sessions.get(course_code, {}).get('tutorial_sessions', 0) > 0:
                I_1[course_code] = i
            else:
                I_2[course_code] = i
        
        current_app.logger.debug(f"Set I_1 (courses with tutorials): {I_1}")
        current_app.logger.debug(f"Set I_2 (courses without tutorials): {I_2}")
        
        # Parameter K_i: total number of sessions of course i
        K = {}
        for course_code, i in I.items():
            K[i] = self.course_sessions.get(course_code, {}).get('total_sessions', 0)
        
        current_app.logger.debug(f"Parameter K (total sessions per course): {K}")
        
        # Set L_i_k: time slots for session number k for course i
        L = {}
        for course_code, i in I.items():
            L[i] = {}
            for k in range(1, K[i] + 1):
                L[i][k] = set()
                for option in self.schedule_options:
                    if (option['course_code'] == course_code and 
                        option['session_number_index'] == k and
                        'time_slot_index' in option and 
                        option['time_slot_index'] is not None):
                        L[i][k].add(option['time_slot_index'])
                
                L[i][k] = sorted(list(L[i][k]))
                
                # If no time slots found, log a warning
                if not L[i][k]:
                    current_app.logger.warning(f"No time slots found for course {course_code} (idx: {i}), session {k}")
        
        current_app.logger.debug(f"Set L (time slots per course and session): {L}")
        
        # Set Prof_i: professors who teach course i
        Prof = {}
        for course_code, i in I.items():
            Prof[i] = set()
            for option in self.schedule_options:
                if (option['course_code'] == course_code and 
                    'professor_index' in option and 
                    option['professor_index'] is not None):
                    Prof[i].add(option['professor_index'])
            
            Prof[i] = sorted(list(Prof[i]))
        
        current_app.logger.debug(f"Set Prof (professors per course): {Prof}")
        
        LectProf = {}
        for course_code, i in I.items():
            LectProf[i] = set()
            lecture_sessions = self.course_sessions.get(course_code, {}).get('lecture_sessions', 0)
            for option in self.schedule_options:
                if (option['course_code'] == course_code and 
                    option['session_number_index'] <= lecture_sessions and  # lecture session
                    option.get('professor_index') is not None):
                    LectProf[i].add(option['professor_index'])
            LectProf[i] = sorted(list(LectProf[i]))

        current_app.logger.debug(f"Set LectProf (lecture professors per course): {LectProf}")
        # Set T_i_p: time slots where professor p is available to teach course i
        T = {}
        for course_code, i in I.items():
            T[i] = {}
            for p in Prof[i]:
                T[i][p] = set()
                for option in self.schedule_options:
                    if (option['course_code'] == course_code and
                        option['professor_index'] == p and
                        'time_slot_index' in option and 
                        option['time_slot_index'] is not None):
                        T[i][p].add(option['time_slot_index'])
                
                T[i][p] = sorted(list(T[i][p]))
        
        current_app.logger.debug(f"Set T (time slots per course and professor): {T}")
        
        # Set L_i_k_p: time slots where professor p teaches session k of course i
        L_p = {}
        for course_code, i in I.items():
            L_p[i] = {}
            for k in range(1, K.get(i, 0) + 1):
                L_p[i][k] = {}
                for p in Prof[i]:
                    L_p[i][k][p] = set()
                    for option in self.schedule_options:
                        if (option['course_code'] == course_code and 
                            option['session_number_index'] == k and
                            option['professor_index'] == p and
                            'time_slot_index' in option and 
                            option['time_slot_index'] is not None):
                            L_p[i][k][p].add(option['time_slot_index'])
                    
                    L_p[i][k][p] = sorted(list(L_p[i][k][p]))
        
        current_app.logger.debug(f"Set L_p (time slots per course, session, and professor) created")
        
        # Set TutProf_i_q: tutorial professors who can be assigned when professor q teaches lecture
        TutProf = {}
        for course_code, i in I_1.items():  # Only for courses with tutorials
            TutProf[i] = {}
            lecture_sessions = self.course_sessions.get(course_code, {}).get('lecture_sessions', 0)
            
            for q in Prof[i]:  # For each professor
                TutProf[i][q] = set()
                for option in self.schedule_options:
                    if (option['course_code'] == course_code and 
                        option['session_number_index'] > lecture_sessions and
                        'lect_prof_index' in option and 
                        option['lect_prof_index'] == q and
                        'professor_index' in option and 
                        option['professor_index'] is not None):
                        TutProf[i][q].add(option['professor_index'])
                
                TutProf[i][q] = sorted(list(TutProf[i][q]))
                
                # If no specific tutorial professors found, use all tutorial professors
                if not TutProf[i][q]:
                    # Find all professors who teach tutorials for this course
                    tut_profs = set()
                    for opt in self.schedule_options:
                        if (opt['course_code'] == course_code and
                            opt['session_number_index'] > lecture_sessions and
                            'professor_index' in opt and 
                            opt['professor_index'] is not None):
                            tut_profs.add(opt['professor_index'])
                    
                    TutProf[i][q] = sorted(list(tut_profs))
        
        current_app.logger.debug(f"Set TutProf (tutorial professors per lecture professor): {TutProf}")
        
        # Create a reverse mapping from i to course_code for later use
        idx_to_code = {idx: code for code, idx in I.items()}
        
        # Define self.FixSlot: set of fixed (i,k,l) combinations for the student's group
        self.FixSlot = []
        
        # ------------------------------------------------------------------
        # Case 1 – Good-standing student (no failed/skipped) -> fix ALL courses
        # ------------------------------------------------------------------
        if not self.has_failed_courses and not self.has_skipped_courses:
            current_app.logger.info(f"Student {self.student_id} has no failed or skipped courses. Fixing schedule to group sessions.")
            
            # Track courses that have been fixed with course-specific groups
            fixed_courses = set()
            
            # First try to use course-specific groups from add_course table
            for course_code, i in I.items():
                lecture_sessions = self.course_sessions.get(course_code, {}).get('lecture_sessions', 0)
                tutorial_sessions = self.course_sessions.get(course_code, {}).get('tutorial_sessions', 0)
                
                # Handle lecture sessions
                if course_code in self.lecture_groups:
                    group = self.lecture_groups[course_code]
                    for k in range(1, lecture_sessions + 1):
                        for option in self.schedule_options:
                            if (option['course_code'] == course_code and 
                                option['session_number_index'] == k and
                                option['group'] == group and
                                'time_slot_index' in option and 
                                option['time_slot_index'] is not None):
                                
                                # Add this (i,k,l) to self.FixSlot
                                self.FixSlot.append((i, k, option['time_slot_index']))
                                fixed_courses.add(course_code)
                                current_app.logger.debug(f"Added fixed lecture session: Course {course_code}, Session {k}, Group {group}, Time slot {option['time_slot_index']}")
                
                # Handle tutorial sessions
                if course_code in self.tutorial_groups:
                    group = self.tutorial_groups[course_code]
                    for k in range(lecture_sessions + 1, lecture_sessions + tutorial_sessions + 1):
                        for option in self.schedule_options:
                            if (option['course_code'] == course_code and 
                                option['session_number_index'] == k and
                                option['group'] == group and
                                'time_slot_index' in option and 
                                option['time_slot_index'] is not None):
                                
                                # Add this (i,k,l) to self.FixSlot
                                self.FixSlot.append((i, k, option['time_slot_index']))
                                fixed_courses.add(course_code)
                                current_app.logger.debug(f"Added fixed tutorial session: Course {course_code}, Session {k}, Group {group}, Time slot {option['time_slot_index']}")
            
            # For any courses not fixed with course-specific groups, try using the main group
            if self.student_group:
                for course_code, i in I.items():
                    if course_code not in fixed_courses:
                        for k in range(1, K[i] + 1):
                            for option in self.schedule_options:
                                if (option['course_code'] == course_code and 
                                    option['session_number_index'] == k and
                                    option['group'] == self.student_group and
                                    'time_slot_index' in option and 
                                    option['time_slot_index'] is not None):
                                    
                                    # Add this (i,k,l) to self.FixSlot
                                    self.FixSlot.append((i, k, option['time_slot_index']))
                                    current_app.logger.debug(f"Added fixed session using main group: Course {course_code}, Session {k}, Group {self.student_group}, Time slot {option['time_slot_index']}")
            
            current_app.logger.info(f"Defined {len(self.FixSlot)} fixed sessions for student's groups")
        # ------------------------------------------------------------------
        # Case 2 – Junior/Senior with CURRENT failed course(s) -> fix ONLY those courses
        # ------------------------------------------------------------------
        elif (self.student_level in ("Junior", "Senior") and self.student_group and self.current_failed_courses):
            current_app.logger.info(
                f"Junior/Senior student with failed courses {self.current_failed_courses}. Fixing sessions for these courses.")

            for course_code in self.current_failed_courses:
                if course_code not in I:
                    continue  # failed course may not be part of current I set
                i = I[course_code]
                total_sessions = self.course_sessions.get(course_code, {}).get('total_sessions', 0)

                for k in range(1, total_sessions + 1):
                    for option in self.schedule_options:
                        if (
                            option['course_code'] == course_code and
                            option['session_number_index'] == k and
                            option.get('group') == self.student_group and
                            option.get('time_slot_index') is not None
                        ):
                            self.FixSlot.append((i, k, option['time_slot_index']))

            current_app.logger.info(
                f"Defined {len(self.FixSlot)} fixed sessions for failed courses (group {self.student_group}).")
        else:
            current_app.logger.debug(
                "Conditions for FixSlot not met (student not good-standing and not in Junior/Senior failed-case).")
        
        # ------------------------------------------------------------------
        # Build FixProf: fixed professor assignments for the student's main group
        # Populate if:
        #   • Case 1: good-standing student (as before) OR
        #   • Case 2: Junior/Senior with failed courses (only for those courses)
        # ------------------------------------------------------------------
        self.FixProf = []  # reset in case build_model is called twice

        need_prof_fix_all = (not self.has_failed_courses and not self.has_skipped_courses and self.student_group)
        need_prof_fix_failed = (self.student_level in ("Junior", "Senior") and self.student_group and self.current_failed_courses)

        if need_prof_fix_all or need_prof_fix_failed:
            fixed_prof_set = set()
            for option in self.schedule_options:
                if (
                    option.get('group') == self.student_group and
                    option.get('professor_index') is not None and
                    option.get('course_code') in I
                ):
                    course_code = option['course_code']
                    # If we're in failed-courses case, skip other courses
                    if need_prof_fix_failed and not need_prof_fix_all and course_code not in self.current_failed_courses:
                        continue
                    i = I[course_code]
                    k = option['session_number_index']
                    p = option['professor_index']
                    fixed_prof_set.add((i, k, p))

            self.FixProf = sorted(list(fixed_prof_set))

            current_app.logger.info(
                f"Defined {len(self.FixProf)} fixed professor assignments for group '{self.student_group}'"
            )
        else:
            current_app.logger.debug(
                "Conditions for FixProf not met for current scenario."
            )
        
        # Decision variables
        # x_i_k_l: 1 if session k for course i is scheduled in time slot l
        x = {}
        for i in I.values():
            for k in range(1, K[i] + 1):
                if k in L[i]:
                    for l in L[i][k]:
                        x[(i, k, l)] = pulp.LpVariable(
                            f"x_{i}_{k}_{l}", 
                            cat=pulp.LpBinary
                        )
        
        # y_i_k_p: 1 if professor p is assigned to session k for course i
        y = {}
        for i in I.values():
            for k in range(1, K[i] + 1):
                if k in L[i]:
                    for p in Prof[i]:
                        y[(i, k, p)] = pulp.LpVariable(
                            f"y_{i}_{k}_{p}", 
                            cat=pulp.LpBinary
                        )
        
        # Preference weights calculation
        # Alpha: professor preference weights based on student rankings
        alpha = {}
        for i in I.values():
            course_code = idx_to_code[i]
            alpha[i] = {}
            for p in Prof[i]:
                # Default weight is 1 (no preference)
                alpha[i][p] = 1
                
                # Check if we have preference data for this course and professor
                if course_code in self.professor_preferences:
                    # Get all professor preferences for this course
                    profs_ranked = 0
                    rank_of_p = None
                    
                    # Count ranked professors and find rank of p
                    for prof_idx, rank in self.professor_preferences[course_code].items():
                        if rank > 0:
                            profs_ranked += 1
                        if prof_idx == p:
                            rank_of_p = rank
                    
                    # Calculate weight if professor p was ranked
                    if rank_of_p is not None and rank_of_p > 0 and profs_ranked > 0:
                        alpha[i][p] = profs_ranked - rank_of_p + 1
        
        # Beta: time slot preference weights
        beta = {}
        
        # Determine the weight to use for preferred time slots
        # Check if timeslot weights are available
        if 'active_weight' not in self.timeslot_weights:
            error_msg = "Timeslot weights not loaded from database. Please check the schedule_parameters table."
            current_app.logger.error(error_msg)
            raise ValueError(error_msg)
            
        timeslot_weight = self.timeslot_weights['active_weight']
        
        # Check if there's a weight override in the preferences
        if self.preferences and 'timeslot_weight_override' in self.preferences:
            timeslot_weight = float(self.preferences['timeslot_weight_override'])
            current_app.logger.debug(f"Using override timeslot weight: {timeslot_weight}")
        
        current_app.logger.debug(f"Using timeslot weight: {timeslot_weight}")
        
        for l in range(1, 31):  # Assuming 30 time slots
            beta[l] = 0
            if l in self.timeslot_preferences and self.timeslot_preferences[l]:
                beta[l] = timeslot_weight
        
        current_app.logger.debug(f"Beta weights for preferred timeslots: {timeslot_weight}")
        
        # Lambda: gap penalty weight
        lambda_weight = 100  # Large number for gap penalty
        
        # Create variables to track used time slots
        used_slot = {}
        for l in range(1, 31):  # Assuming 30 time slots
            used_slot[l] = pulp.LpVariable(f"used_slot_{l}", cat=pulp.LpBinary)
        
        # Link used_slot variables to x variables
        for l in range(1, 31):
            # Collect all x variables for time slot l
            x_vars_for_slot = []
            for i in I.values():
                for k in range(1, K[i] + 1):
                    if k in L[i] and l in L[i][k]:
                        if (i, k, l) in x:
                            x_vars_for_slot.append(x[(i, k, l)])
            
            if x_vars_for_slot:
                # If any session is scheduled in this slot, the slot is used
                model += used_slot[l] <= pulp.lpSum(x_vars_for_slot), f"used_slot_upper_{l}"
                model += used_slot[l] * len(x_vars_for_slot) >= pulp.lpSum(x_vars_for_slot), f"used_slot_lower_{l}"
        
        # Gap penalty calculation
        gap_vars = []
        total_gaps = 0
        
        # For each day (6 days, 5 slots per day)
        for day in range(6):
            day_slots = [day*5 + slot + 1 for slot in range(5)]  # slots for this day
            
            # For each possible gap pattern
            for start_idx in range(4):  # First 4 slots
                for end_idx in range(start_idx + 2, 5):  # At least 2 slots later
                    # The slots at the ends that must be used
                    first_slot = day_slots[start_idx]
                    last_slot = day_slots[end_idx]
                    
                    # The slots in between (the gap)
                    middle_slots = [day_slots[i] for i in range(start_idx + 1, end_idx)]
                    
                    # Create a binary variable for this gap pattern
                    gap_var = pulp.LpVariable(f"gap_{day}_{start_idx}_{end_idx}", cat=pulp.LpBinary)
                    gap_vars.append(gap_var)
                    
                    # This variable will be 1 if and only if:
                    # 1. The first slot is used
                    # 2. The last slot is used
                    # 3. All middle slots are unused
                    
                    # Constraint: gap_var <= first_slot_used
                    model += gap_var <= used_slot[first_slot], f"gap_first_{day}_{start_idx}_{end_idx}"
                    
                    # Constraint: gap_var <= last_slot_used
                    model += gap_var <= used_slot[last_slot], f"gap_last_{day}_{start_idx}_{end_idx}"
                    
                    # Constraints: gap_var <= 1 - middle_slot_used (for each middle slot)
                    for idx, mid_slot in enumerate(middle_slots):
                        model += gap_var <= 1 - used_slot[mid_slot], f"gap_mid_{day}_{start_idx}_{end_idx}_{idx}"
                    
                    # Constraint: gap_var >= first_used + last_used - sum(middle_used) - 1
                    middle_sum = pulp.lpSum([used_slot[mid] for mid in middle_slots])
                    model += gap_var >= used_slot[first_slot] + used_slot[last_slot] - middle_sum - 1, f"gap_def_{day}_{start_idx}_{end_idx}"
                    
                    # Add to total gaps: gap_size * gap_var
                    gap_size = len(middle_slots)
                    total_gaps += gap_size * gap_var
        
        # Objective function
        obj_terms = []
        
        # Professor preference terms
        for i in I.values():
            for k in range(1, K[i] + 1):
                if k in L[i]:
                    for p in Prof[i]:
                        if (i, k, p) in y:
                            obj_terms.append(alpha[i][p] * y[(i, k, p)])
        
        # Time slot preference terms
        for i in I.values():
            for k in range(1, K[i] + 1):
                if k in L[i]:
                    for l in L[i][k]:
                        if (i, k, l) in x:
                            obj_terms.append(beta[l] * x[(i, k, l)])
        
        # Gap penalty term
        obj_terms.append(-lambda_weight * total_gaps)
        
        # Set objective function
        model += pulp.lpSum(obj_terms), "Maximize_Preferences"
        
        # CONSTRAINTS
        
        # Constraint 1: Each Required Session Scheduled Exactly Once
        for i in I.values():
            for k in range(1, K[i] + 1):
                if k in L[i]:
                    session_vars = [x[(i, k, l)] for l in L[i][k] if (i, k, l) in x]
                    if session_vars:
                        model += pulp.lpSum(session_vars) == 1, f"C1_one_session_{i}_{k}"
        
        # Constraint 2: No Overlapping Sessions
        for l in range(1, 31):  # Assuming 30 time slots
            slot_vars = []
            for i in I.values():
                for k in range(1, K[i] + 1):
                    if k in L[i] and l in L[i][k] and (i, k, l) in x:
                        slot_vars.append(x[(i, k, l)])
            
            if slot_vars:
                model += pulp.lpSum(slot_vars) <= 1, f"C2_no_overlap_{l}"
        
        # Constraint 3: Chronological Ordering of Lecture Sessions
        # For courses with tutorials (I_1)
        for course_code, i in I_1.items():
            lecture_sessions = self.course_sessions.get(course_code, {}).get('lecture_sessions', 0)
            if lecture_sessions > 1:
                for k in range(1, lecture_sessions - 1):
                    # Left side: time slot for session k
                    left_side = []
                    for l in L[i][k]:
                        if (i, k, l) in x:
                            left_side.append(l * x[(i, k, l)])
                    
                    # Right side: time slot for session k+1
                    right_side = []
                    for l in L[i][k+1]:
                        if (i, k+1, l) in x:
                            right_side.append(l * x[(i, k+1, l)])
                    
                    if left_side and right_side:
                        model += 1 + pulp.lpSum(left_side) <= pulp.lpSum(right_side), f"C3_chrono_I1_{i}_{k}"
        
        # For courses without tutorials (I_2)
        for course_code, i in I_2.items():
            lecture_sessions = self.course_sessions.get(course_code, {}).get('lecture_sessions', 0)
            if lecture_sessions > 1:
                for k in range(1, lecture_sessions):
                    # Left side: time slot for session k
                    left_side = []
                    for l in L[i][k]:
                        if (i, k, l) in x:
                            left_side.append(l * x[(i, k, l)])
                    
                    # Right side: time slot for session k+1
                    right_side = []
                    for l in L[i][k+1]:
                        if (i, k+1, l) in x:
                            right_side.append(l * x[(i, k+1, l)])
                    
                    if left_side and right_side:
                        model += 1 + pulp.lpSum(left_side) <= pulp.lpSum(right_side), f"C3_chrono_I2_{i}_{k}"
        
        # Constraint 4/a: Each course session must be assigned exactly one professor
        
        # For courses with tutorials (I_1), each lecture session must have exactly one professor
        # \sum_{p \in \text{Prof}_{i}} y_{i,k,p} = 1 \quad \forall i \in I_1, k = 1 .. K_{i}-1
        for course_code, i in I_1.items():
            lecture_sessions = self.course_sessions.get(course_code, {}).get('lecture_sessions', 0)
            for k in range(1, lecture_sessions + 1):  # Only for lecture sessions
                if k in L[i]:
                    prof_vars = [y[(i, k, p)] for p in LectProf[i] if (i, k, p) in y]
                    if prof_vars:
                        model += pulp.lpSum(prof_vars) == 1, f"C4a_one_prof_I1_{i}_{k}"
        
        # For courses without tutorials (I_2), each session must have exactly one professor
        for course_code, i in I_2.items():
            for k in range(1, K[i] + 1):
                if k in L[i]:
                    prof_vars = [y[(i, k, p)] for p in Prof[i] if (i, k, p) in y]
                    if prof_vars:
                        model += pulp.lpSum(prof_vars) == 1, f"C4a_one_prof_I2_{i}_{k}"
        
        # Constraint 4/b: Same Professor for All Lecture Sessions
        # For courses with tutorials (I_1)
        for course_code, i in I_1.items():
            lecture_sessions = self.course_sessions.get(course_code, {}).get('lecture_sessions', 0)
            if lecture_sessions > 1:
                for p in LectProf[i]:
                    for k in range(1, lecture_sessions):
                        for k_prime in range(k+1, lecture_sessions + 1):
                            if (i, k, p) in y and (i, k_prime, p) in y:
                                model += y[(i, k, p)] == y[(i, k_prime, p)], f"C4b_same_prof_I1_{i}_{k}_{k_prime}_{p}"
        
        # For courses without tutorials (I_2)
        for course_code, i in I_2.items():
            lecture_sessions = self.course_sessions.get(course_code, {}).get('lecture_sessions', 0)
            if lecture_sessions > 1:
                for p in Prof[i]:
                    for k in range(1, lecture_sessions):
                        for k_prime in range(k+1, lecture_sessions + 1):
                            if (i, k, p) in y and (i, k_prime, p) in y:
                                model += y[(i, k, p)] == y[(i, k_prime, p)], f"C4b_same_prof_I2_{i}_{k}_{k_prime}_{p}"
        
        # Constraint 5: Respect Existing Professor Pairs
        for course_code, i in I_1.items():
            lecture_sessions = self.course_sessions.get(course_code, {}).get('lecture_sessions', 0)
            tutorial_sessions = self.course_sessions.get(course_code, {}).get('tutorial_sessions', 0)
            
            for q in LectProf[i]:  # For each lecture professor
                # For each tutorial session
                for k in range(lecture_sessions + 1, lecture_sessions + tutorial_sessions + 1):
                    if k in L[i]:
                        # Sum of y variables for valid tutorial professors
                        tut_prof_vars = []
                        for p in TutProf[i][q]:
                            if (i, k, p) in y:
                                tut_prof_vars.append(y[(i, k, p)])
                        
                        if tut_prof_vars:
                            # Link to lecture professor selection
                            lect_prof_vars = []
                            for k_lect in range(1, lecture_sessions + 1):
                                if (i, k_lect, q) in y:
                                    lect_prof_vars.append(y[(i, k_lect, q)])
                            
                            if lect_prof_vars:
                            # If lecture professor q is selected, sum of valid tutorial profs must be 1
                                # Exactly matching the mathematical model: sum_{p ∈ TutProf_i,q} y_i,k,p = 1
                                model += pulp.lpSum(tut_prof_vars) == 1, f"C5_tut_prof_{i}_{k}_{q}"
        
        # Constraint 6: Link Professor to his time slot (exactly as requested)
        #   I₁  → p ∈ Prof_i
        #   I₂  → p ∈ LectProf_i
        
        # Courses WITH tutorials  (i ∈ I_1)
        for course_code, i in I_1.items():
            for k in range(1, K[i] + 1):
                if k in L[i]:
                    for p in Prof[i]:
                        if (i, k, p) in y:
                            rhs_vars = [x[(i, k, l)] for l in L_p[i][k][p] if (i, k, l) in x]
                            model += y[(i, k, p)] <= (pulp.lpSum(rhs_vars) if rhs_vars else 0), f"C6_I1_{i}_{k}_{p}"
        
        # Courses WITHOUT tutorials (i ∈ I_2)
        for course_code, i in I_2.items():
            for k in range(1, K[i] + 1):
                if k in L[i]:
                    for p in Prof[i]:
                        if (i, k, p) in y:
                            rhs_vars = [x[(i, k, l)] for l in L_p[i][k][p] if (i, k, l) in x]
                            model += y[(i, k, p)] <= (pulp.lpSum(rhs_vars) if rhs_vars else 0), f"C6_I2_{i}_{k}_{p}"
        
        # Constraint 7: Fixed Group Sessions
        # x_i,k,l = 1 for (i,k,l) in self.FixSlot
        # Only apply this constraint if the student has no failed or skipped courses
        if self.FixSlot:
            current_app.logger.info(f"Adding Constraint 7: Fixed Group Sessions for student {self.student_id}")
            for i, k, l in self.FixSlot:
                if (i, k, l) in x:
                    model += x[(i, k, l)] == 1, f"C7_FixSlot_session_{i}_{k}_{l}"
                    current_app.logger.debug(f"Added constraint for fixed session: Course {idx_to_code.get(i, i)}, Session {k}, Time slot {l}")
        
        # ------------------------------------------------------------------
        # Constraint 7 (extended): Fixed professor assignments
        # y_{i,k,p} = 1  for all (i,k,p) in FixProf
        # ------------------------------------------------------------------
        if getattr(self, 'FixProf', None):
            current_app.logger.info(
                f"Adding Constraint 7b: Fixed professor assignments for student {self.student_id}"
            )
            for i, k, p in self.FixProf:
                if (i, k, p) in y:
                    model += y[(i, k, p)] == 1, f"C7b_fixed_professor_{i}_{k}_{p}"
                    current_app.logger.debug(
                        f"Added fixed professor: Course {idx_to_code.get(i, i)}, Session {k}, Prof {p}"
                    )

        
        return model, x, y, I
            
    def solve(self, preferences=None):
        """Build and solve the optimization model"""
        # Set preferences if provided
        self.preferences = preferences
        
        if self.preferences:
            current_app.logger.debug(f"Solving with preferences: {self.preferences}")
        
        model, x, y, I = self.build_model()
        
        if not x:  # No variables created
            return {
                'success': False,
                'message': 'No schedule options available for the enrolled courses'
            }
        
        # Create reverse mapping from course index to course code
        idx_to_code = {idx: code for code, idx in I.items()}
        
        # Solve the model using the time limit specified in schedule_parameters
        solver_time = getattr(self, 'model_time_limit', None)
        if solver_time is None:
            error_msg = "Model time limit not loaded from schedule_parameters table."
            current_app.logger.error(error_msg)
            raise ValueError(error_msg)

        solver = pulp.PULP_CBC_CMD(msg=True, timeLimit=solver_time)
        
        # Log that we're starting to solve
        current_app.logger.info("Starting to solve the optimization model...")
        
        # Check if the model has variables and constraints
        num_vars = len(model.variables())
        num_constraints = len(model.constraints)
        current_app.logger.debug(f"Model has {num_vars} variables and {num_constraints} constraints")
        
        # Log some of the constraints for debugging
        if num_constraints > 0:
            constraints_sample = list(model.constraints.items())[:6] 
            for name, constraint in constraints_sample:
                current_app.logger.debug(f"Constraint {name}: {constraint}")
        else:
            current_app.logger.warning("Model has no constraints - this might indicate a problem")
        
        if num_vars == 0:
            current_app.logger.warning("Model has no variables - no feasible schedule possible")
            return {
                'success': True,  # Still return success but with empty schedule
                'message': 'No schedule options could be found - check your course registrations',
                'schedule': [],
                'objective_components': {
                    'professor_preference_value': 0,
                    'timeslot_preference_value': 0,
                    'gap_penalty': 0
                },
                'total_objective_value': 0,
                'model_objective_value': 0,
                'has_issues': False
            }
        
        result = model.solve(solver)
        
        # Log the result status
        current_app.logger.info(f"Optimization result status: {pulp.LpStatus[result]}")
        current_app.logger.info(f"Objective value: {pulp.value(model.objective)}")
        
        # Print all active decision variables (x and y with value 1)
        print("\n=== ACTIVE DECISION VARIABLES (VALUE=1) ===")
        active_x_vars = []
        active_y_vars = []
        
        for var in model.variables():
            var_value = pulp.value(var)
            if var_value is not None and var_value > 0.5:
                if var.name.startswith('x_'):
                    # Parse x_i_k_l
                    parts = var.name.split('_')
                    if len(parts) >= 4:
                        i = parts[1]
                        k = parts[2]
                        l = parts[3]
                        course_code = idx_to_code.get(int(i), i)
                        active_x_vars.append(f"x({course_code},{k},{l})=1")
                
                elif var.name.startswith('y_'):
                    # Parse y_i_k_p
                    parts = var.name.split('_')
                    if len(parts) >= 4:
                        i = parts[1]
                        k = parts[2]
                        p = parts[3]
                        course_code = idx_to_code.get(int(i), i)
                        active_y_vars.append(f"y({course_code},{k},{p})=1")
        
        print("ACTIVE X VARIABLES (SCHEDULE ASSIGNMENTS):")
        if active_x_vars:
            for var in active_x_vars:
                print(f"  {var}")
        else:
            print("  None")
            
        print("\nACTIVE Y VARIABLES (PROFESSOR ASSIGNMENTS):")
        if active_y_vars:
            for var in active_y_vars:
                print(f"  {var}")
        else:
            print("  None")
        print("="*50)
        
        # Log gap variables that are active in the solution
        active_gap_vars = []
        for var in model.variables():
            var_value = pulp.value(var)
            if var.name.startswith('gap_') and var_value is not None and var_value > 0.5:
                active_gap_vars.append(f"{var.name}={var_value}")
        
        current_app.logger.info(f"Active gap variables: {', '.join(active_gap_vars) if active_gap_vars else 'None'}")
        
        if result != pulp.LpStatusOptimal:
            return {
                'success': False,
                'message': f'No feasible schedule found. Status: {pulp.LpStatus[result]}'
            }
        
        # Extract the solution using the helper method
        solution_data = self._extract_solution(model, x, y, I, idx_to_code)
        
        # Get the schedule from the solution data
        schedule = solution_data.get('schedule', [])
        
        # Log how many decision variables were created
        x_vars = [v for v in model.variables() if v.name.startswith('x_')]
        y_vars = [v for v in model.variables() if v.name.startswith('y_')]
        current_app.logger.debug(f"Decision variables: {len(x_vars)} x-variables, {len(y_vars)} y-variables")
        
        # Log the selected decision variables
        print("\n=== DECISION VARIABLES WITH VALUE 1 ===")
        selected_vars = []
        x_selected = []
        y_selected = []
        for var in model.variables():
            var_value = pulp.value(var)
            if var_value is not None and var_value > 0.5:
                selected_vars.append(var.name)
                if var.name.startswith('x_'):
                    x_selected.append(var.name)
                elif var.name.startswith('y_'):
                    y_selected.append(var.name)
        
        # Print x variables in a concise format
        print("X VARIABLES (SCHEDULE ASSIGNMENTS):")
        print(", ".join(x_selected))
        
        # Print y variables in a concise format
        print("\nY VARIABLES (PROFESSOR ASSIGNMENTS):")
        print(", ".join(y_selected))
        
        # Log gap variables for debugging
        print("\n=== GAP VARIABLES ===")
        gap_vars = []
        for var in model.variables():
            var_value = pulp.value(var)
            if var.name.startswith('gap_') and var_value is not None and var_value > 0.5:
                gap_vars.append(f"{var.name}={var_value}")
        print(", ".join(gap_vars) if gap_vars else "No active gap variables")
        
        # Log used slots for debugging
        print("\n=== USED SLOT VARIABLES ===")
        used_slots = []
        for var in model.variables():
            var_value = pulp.value(var)
            if var.name.startswith('used_slot_') and var_value is not None and var_value > 0.5:
                used_slots.append(f"{var.name}={var_value}")
        print(", ".join(used_slots) if used_slots else "No active used_slot variables")
        
        print("=======================================\n")
        current_app.logger.debug(f"Selected variables: {selected_vars}")
        
        # Calculate objective components using helper methods
        professor_preference_value = self._calculate_professor_preference(model, x, y, I, idx_to_code)
        
        # Use the pre-calculated values from _extract_solution if available
        if 'objective_components' in solution_data:
            timeslot_preference_value = solution_data['objective_components'].get('timeslot_preference_value', 0)
            gap_penalty = solution_data['objective_components'].get('gap_penalty', 0)
        else:
            # Otherwise, calculate them
            timeslot_preference_value = 0
            gap_penalty = 0
            
            # Only calculate if we have a valid schedule
            if schedule and isinstance(schedule, list):
                try:
                    timeslot_preference_value = self._calculate_timeslot_preference(schedule)
                    gap_penalty = self._calculate_gap_penalty(schedule)
                except Exception as e:
                    current_app.logger.error(f"Error calculating preferences: {str(e)}")
                    # Use default values if calculation fails
        
        # Total objective value
        total_objective = professor_preference_value + timeslot_preference_value - gap_penalty
        
        # Verify chronological ordering of lectures
        lectures_by_course = {}
        has_issues = False
        
        for session in schedule:
            lecture_sessions = self.course_sessions.get(session['course_code'], {}).get('lecture_sessions', 0)
            if session['session_number'] <= lecture_sessions:
                course_code = session['course_code']
                if course_code not in lectures_by_course:
                    lectures_by_course[course_code] = []
                lectures_by_course[course_code].append(session)
        
        for course_code, lectures in lectures_by_course.items():
            if len(lectures) > 1:
                # Sort by session number
                lectures.sort(key=lambda l: l['session_number'])
                # Check if time slots are in order
                for i in range(len(lectures) - 1):
                    # Convert time slots to integers for comparison
                    current_slot = int(lectures[i]['time_slot'])
                    next_slot = int(lectures[i+1]['time_slot'])
                    
                    if current_slot >= next_slot:
                        current_app.logger.warning(
                            f"Ordering issue for course {course_code}: lecture {lectures[i]['session_number']} " +
                            f"(slot {current_slot}) should be before lecture {lectures[i+1]['session_number']} " +
                            f"(slot {next_slot})"
                        )
                        has_issues = True
        
        # Check if we ended up with an empty schedule even though we found a solution
        if len(schedule) == 0:
            current_app.logger.warning("Empty schedule despite successful optimization")
            
            # Check why the schedule is empty
            selected_x_vars = [v.name for v in model.variables() if v.name.startswith('x_') and pulp.value(v) > 0.5]
            if selected_x_vars:
                current_app.logger.warning(f"Selected x-variables exist but schedule is empty - possible data issue")
                current_app.logger.debug(f"Selected x-variables: {selected_x_vars}")
            else:
                current_app.logger.warning("No x-variables were selected by the optimizer")
        else:
            current_app.logger.info(f"Successfully generated schedule with {len(schedule)} sessions")
        
        # Return the optimized schedule with detailed information
        return {
            'success': True,
            'schedule': schedule,
            'objective_components': {
                'professor_preference_value': professor_preference_value,
                'timeslot_preference_value': timeslot_preference_value,
                'gap_penalty': gap_penalty
            },
            'total_objective_value': total_objective,
            'model_objective_value': pulp.value(model.objective),
            'has_issues': solution_data.get('has_issues', has_issues),
            'message': "Schedule generated successfully" if len(schedule) > 0 else "No valid schedule could be generated - try adjusting preferences",
            'FixSlotroup_sessions': len(self.FixSlot) > 0,
            'student_group': self.student_group if len(self.FixSlot) > 0 else None,
            'lecture_groups': self.lecture_groups if len(self.FixSlot) > 0 else {},
            'tutorial_groups': self.tutorial_groups if len(self.FixSlot) > 0 else {}
        }

    def _extract_solution(self, model, x, y, I, idx_to_code):
        """Extract a solution from the solved model"""
        schedule = []
        
        # First, collect all the selected time slots from x variables
        selected_slots = []
        # Build lookup sets so we can quickly test if a session or professor triple was forced by FixSlot/FixProf.
        fixslot_set = set(self.FixSlot)
        fixprof_set = set(self.FixProf)
        
        for var in model.variables():
            var_name = var.name
            var_value = pulp.value(var)
            # Check if var_value is not None before comparing
            if var_name.startswith('x_') and var_value is not None and var_value > 0.5:
                # Parse the variable name to extract i, k, l
                parts = var_name.split('_')
                if len(parts) >= 4:
                    i = int(parts[1])
                    k = int(parts[2])
                    l = int(parts[3])
                    
                    # Get the course code from the index
                    course_code = idx_to_code.get(i)
                    if not course_code:
                        current_app.logger.warning(f"No course code found for index {i}")
                        continue
                    
                    selected_slots.append((course_code, k, l, i))
        
        if not selected_slots:
            current_app.logger.warning("No schedule slots selected in the solution")
            # Log all variables with non-zero values to help debug
            non_zero_vars = []
            for var in model.variables():
                var_value = pulp.value(var)
                if var_value is not None and abs(var_value) > 1e-6:
                    non_zero_vars.append(f"{var.name}={var_value}")
            
            if non_zero_vars:
                current_app.logger.debug(f"Non-zero variables in solution: {', '.join(non_zero_vars)}")
            else:
                current_app.logger.warning("No non-zero variables found in solution")
            
            return {
                'schedule': [],
                'objective_components': {
                    'professor_preference_value': 0,
                    'timeslot_preference_value': 0,
                    'gap_penalty': 0
                },
                'total_objective_value': 0,
                'has_issues': False
            }
        
        # Build a query to fetch all schedule data in a single database call
        query_parts = []
        query_params = []
        
        for course_code, session_number, time_slot, _ in selected_slots:
            query_parts.append("(course_code = %s AND session_number_index = %s AND time_slot_index = %s)")
            query_params.extend([course_code, session_number, time_slot])
        
        # Execute a single query to get all schedule options
        cursor = self.db.cursor()
        try:
            # Ensure we get ALL relevant details for accurate matching
            query = f"""
                SELECT id, course_code, week_day, start_time, end_time, 
                       professor, classroom, `group`, session_type,
                       course_index, session_number_index, time_slot_index, 
                       professor_index, Tutprof_index, lect_prof_index
                FROM schedule 
                WHERE {" OR ".join(query_parts)}
            """
            cursor.execute(query, query_params)
            columns = [col[0] for col in cursor.description]
            schedule_options = {}
            
            # Create a lookup dictionary keyed by (course_code, session_number, time_slot)
            for row in cursor.fetchall():
                option = dict(zip(columns, row))
                key = (option['course_code'], option['session_number_index'], option['time_slot_index'])
                if key not in schedule_options:
                    schedule_options[key] = []
                schedule_options[key].append(option)
            
            current_app.logger.debug(f"Fetched {len(schedule_options)} unique schedule options from database")
        except Exception as e:
            current_app.logger.error(f"Error querying schedule table: {e}")
            return {
                'schedule': [],
                'objective_components': {
                    'professor_preference_value': 0,
                    'timeslot_preference_value': 0,
                    'gap_penalty': 0
                },
                'total_objective_value': 0,
                'has_issues': True
            }
        finally:
            cursor.close()
        
        # Find professor assignments from y variables
        professor_assignments = {}
        
        for var in model.variables():
            var_name = var.name
            var_value = pulp.value(var)
            # Check if var_value is not None before comparing
            if var_name.startswith('y_') and var_value is not None and var_value > 0.5:
                parts = var_name.split('_')
                if len(parts) >= 4:
                    i = int(parts[1])  # course index
                    k = int(parts[2])  # session number
                    p = int(parts[3])  # professor index
                    
                    course_code = idx_to_code.get(i)
                    if not course_code:
                        continue
                    
                    # Use (course_code, session_number) as key without time slot
                    key = (course_code, k)
                    professor_assignments[key] = p
        
        # Now create the schedule items using the fetched data
        for course_code, session_number, time_slot, i in selected_slots:
            key = (course_code, session_number, time_slot)
            
            if key not in schedule_options:
                current_app.logger.warning(f"No matching schedule option found for {key}")
                continue
            
            # Choose a template option.
            # Prioritise the student's group **only** if this session is one of the
            # fixed (i,k,l) triples from FixSlot.
            if len(schedule_options[key]) > 1 and self.student_group and (i, session_number, time_slot) in fixslot_set:
                grp_match = next((opt for opt in schedule_options[key] if opt.get('group') == self.student_group), None)
                option = grp_match if grp_match else schedule_options[key][0]
            else:
                option = schedule_options[key][0]
            
            # Get the professor index for this session
            prof_idx = professor_assignments.get((course_code, session_number))
            
            # Find the option that matches both time slot and professor
            matching_option = None
            if prof_idx is not None:
                # Build list of candidates matching professor and slot
                candidates = [opt for opt in schedule_options[key]
                              if opt.get('professor_index') == prof_idx and
                                 opt.get('time_slot_index') == time_slot]
                if candidates:
                    # Prioritise student's group only if either the session or the professor triple is fixed
                    prioritise = ((i, session_number, time_slot) in fixslot_set) or ((i, session_number, prof_idx) in fixprof_set)
                    if prioritise and self.student_group:
                        matching_option = next((opt for opt in candidates if opt.get('group') == self.student_group), candidates[0])
                    else:
                        matching_option = candidates[0]
            # Fallback handled later if matching_option stays None
            
            # Determine the correct group based on session type and student's group assignments
            lecture_sessions = self.course_sessions.get(course_code, {}).get('lecture_sessions', 0)
            session_type = 'lecture' if session_number <= lecture_sessions else 'tutorial'
            
                        # Only use student's group if they have no failed or skipped courses
            if not self.has_failed_courses and not self.has_skipped_courses:
                # First try to get the student's specific group for this course and session type
                if session_type == 'lecture' and course_code in self.lecture_groups:
                    group = self.lecture_groups[course_code]
                    current_app.logger.debug(f"Using student's lecture group '{group}' for {course_code}")
                elif session_type == 'tutorial' and course_code in self.tutorial_groups:
                    group = self.tutorial_groups[course_code]
                    current_app.logger.debug(f"Using student's tutorial group '{group}' for {course_code}")
                # If no course-specific group, try to use the main student group
                elif self.student_group:
                    # Default to main group disabled to allow model-assigned groups for non-fixed sessions
                    group = matching_option.get('group', option.get('group', 'Default Group'))
                    current_app.logger.debug(f"Using option's group '{group}' for {course_code} (main group fallback disabled)")
                else:
                    # Fall back to the matching option's group
                    if matching_option:
                        group = matching_option.get('group', 'Default Group')
                        current_app.logger.debug(f"Using option's group '{group}' for {course_code}")
                    else:
                        group = option.get('group', 'Default Group')
                        current_app.logger.debug(f"Using fallback group '{group}' for {course_code}")
            else:
                # Student has failed or skipped courses, so don't restrict to their group
                if matching_option:
                    group = matching_option.get('group', 'Default Group')
                    current_app.logger.debug(f"Student has failed courses - using option's group '{group}' for {course_code}")
                else:
                    group = option.get('group', 'Default Group')
                    current_app.logger.debug(f"Student has failed courses - using fallback group '{group}' for {course_code}")
            
            # Get classroom from the matching option if found, otherwise use the first option
            if matching_option:
                classroom = matching_option.get('classroom', 'TBD')
            else:
                classroom = option.get('classroom', 'TBD')
                current_app.logger.warning(f"No exact match found for course {course_code}, session {session_number}, time slot {time_slot}, prof {prof_idx}")
            
            # Get professor from the assignments - we already have prof_idx from above
            professor = "TBD"
            
            # If we have a matching option with both correct time slot and professor index, use that
            if matching_option:
                professor = matching_option.get('professor', 'TBD')
            # Otherwise, fall back to any option with the right professor index
            elif prof_idx is not None:
                # First try to find an exact match
                for opt in schedule_options[key]:
                    if opt.get('professor_index') == prof_idx:
                        professor = opt.get('professor', 'TBD')
                        break
                
                # If still TBD and this is a tutorial session, try to find a match based on lecture professor
                if professor == "TBD" and session_type == 'tutorial':
                    # Find the lecture professor first
                    lecture_prof_idx = None
                    for lecture_key in professor_assignments:
                        lecture_course, lecture_session = lecture_key
                        if lecture_course == course_code and lecture_session <= lecture_sessions:
                            lecture_prof_idx = professor_assignments[lecture_key]
                            break
                    
                    if lecture_prof_idx is not None:
                        # Try to find a tutorial option with this lecture professor
                        for opt in schedule_options[key]:
                            if (opt.get('lect_prof_index') == lecture_prof_idx and
                                opt.get('professor_index') == prof_idx):
                                professor = opt.get('professor', 'TBD')
                                break
                        
                        # If still not found, try any tutorial professor for this time slot
                        if professor == "TBD":
                            current_app.logger.debug(f"Looking for fallback tutorial professor for {course_code}, session {session_number}, time slot {time_slot}")
                            
                            # First try to find a tutorial option with this time slot and any professor
                            for opt in schedule_options[key]:
                                if opt.get('time_slot_index') == time_slot and opt.get('professor') and opt.get('professor') != "TBD":
                                    professor = opt.get('professor')
                                    current_app.logger.debug(f"Found fallback tutorial professor {professor} for {course_code}, session {session_number}")
                                    break
                            
                            # If still not found, check if there's only one professor for this session
                            if professor == "TBD":
                                professors_for_session = set()
                                for opt in schedule_options[key]:
                                    if opt.get('professor') and opt.get('professor') != "TBD":
                                        professors_for_session.add(opt.get('professor'))
                                
                                if len(professors_for_session) == 1:
                                    professor = list(professors_for_session)[0]
                                    current_app.logger.debug(f"Using only available tutorial professor {professor} for {course_code}, session {session_number}")
                                elif professors_for_session:
                                    professor = list(professors_for_session)[0]
                                    current_app.logger.debug(f"Using first available tutorial professor {professor} from {len(professors_for_session)} options for {course_code}, session {session_number}")
                                else:
                                    current_app.logger.warning(f"No professor found for tutorial session {course_code}, session {session_number}, time slot {time_slot}")
            
            # Format the times
            start_time = option['start_time']
            end_time = option['end_time']
            
            # Use the _format_time helper function
            start_time = self._format_time(start_time)
            end_time = self._format_time(end_time)
            
            # We already determined session type above, no need to recalculate it
            
            # Use the matching option for all details if available, otherwise fallback to option
            source_option = matching_option if matching_option else option
            
            # Add to the schedule
            schedule_item = {
                'course_code': course_code,
                'session_number': session_number,
                'day': source_option['week_day'],
                'start_time': start_time,
                'end_time': end_time,
                'professor': professor,
                'classroom': classroom,
                'group': group,
                'time_slot': time_slot,
                'professor_index': prof_idx,
                'course_index': i,
                'session_type': session_type,  # Add session type for frontend display
                'option_id': source_option.get('id')  # Store the original schedule option ID for reference
            }
            
            # If this (i,k,l) triple was fixed by Constraint 7, we rely on the schedule table's group value
            # (no override needed because the fixed time slot already belongs to the desired group)
            
            schedule.append(schedule_item)
        
        # Sort schedule by day and time
        day_order = {day: idx for idx, day in enumerate(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'])}
        schedule.sort(key=lambda s: (day_order.get(s['day'], 999), s['start_time']))
        
        # Log the schedule for debugging
        if schedule:
            current_app.logger.debug(f"Schedule has {len(schedule)} items")
            current_app.logger.debug(f"Sample schedule item: {schedule[0]}")
        else:
            current_app.logger.warning("Empty schedule after extraction")
        
        # Calculate objective components
        professor_preference_value = self._calculate_professor_preference(model, x, y, I, idx_to_code)
        timeslot_preference_value = self._calculate_timeslot_preference(schedule)
        gap_penalty = self._calculate_gap_penalty(schedule)
        
        return {
            'schedule': schedule,
            'objective_components': {
                'professor_preference_value': professor_preference_value,
                'timeslot_preference_value': timeslot_preference_value,
                'gap_penalty': gap_penalty
            },
            'total_objective_value': professor_preference_value + timeslot_preference_value - gap_penalty,
            'has_issues': False
        }

    def find_all_optimal_solutions(self, random_seed=None, preferences=None):
        """Find all optimal solutions using an iterative approach"""
        # Import time module for generating unique constraint IDs
        import time
        
        # Set preferences if provided
        self.preferences = preferences
        
        if self.preferences:
            current_app.logger.debug(f"Finding all optimal solutions with preferences: {self.preferences}")
            
        # Load weights directly from database using the new function
        # This will use the stored mode if no explicit priority_mode is provided
        self.load_weight_from_db(
            priority_mode=self.preferences.get('priority_mode') if self.preferences else None
        )
        
        # Build initial model
        model, x, y, I = self.build_model()
        
        if not x:  # No variables created
            return {
                'success': False,
                'message': 'No schedule options available for the enrolled courses',
                'solutions': []
            }
        
        # Create reverse mapping from course index to course code
        idx_to_code = {idx: code for code, idx in I.items()}
        
        # Check if the model has variables and constraints
        num_vars = len(model.variables())
        num_constraints = len(model.constraints)
        current_app.logger.debug(f"Model has {num_vars} variables and {num_constraints} constraints")
        
        # Log some of the constraints for debugging
        if num_constraints > 0:
            constraints_sample = list(model.constraints.items())[:5]  # Get first 5 constraints
            for name, constraint in constraints_sample:
                current_app.logger.debug(f"Constraint {name}: {constraint}")
        else:
            current_app.logger.warning("Model has no constraints - this might indicate a problem")
        
        if num_vars == 0:
            current_app.logger.warning("Model has no variables - no feasible schedule possible")
            return {
                'success': False,
                'message': 'No schedule options could be found - check your course registrations',
                'solutions': []
            }
        
        # Solver using configured time limit
        solver_time = getattr(self, 'model_time_limit', None)
        if solver_time is None:
            error_msg = "Model time limit not loaded from schedule_parameters table."
            current_app.logger.error(error_msg)
            raise ValueError(error_msg)

        solver = pulp.PULP_CBC_CMD(msg=True, timeLimit=solver_time)
        
        # Store all solutions
        all_solutions = []
        
        # Solve the initial model
        current_app.logger.info("Starting to find all optimal solutions...")
        result = model.solve(solver)
        
        if result != pulp.LpStatusOptimal:
            return {
                'success': False,
                'message': f'No feasible schedule found. Status: {pulp.LpStatus[result]}',
                'solutions': []
            }
        
        # Store the optimal objective value
        optimal_objective_value = pulp.value(model.objective)
        if optimal_objective_value is None:
            current_app.logger.warning("Objective value is None")
            
        current_app.logger.info(f"Found initial optimal solution with objective value: {optimal_objective_value}")
        
        # Print detailed breakdown of objective value components
        print("\n" + "="*80)
        print("OBJECTIVE VALUE COMPONENT BREAKDOWN")
        print("="*80)
        
        # Keep track of how many solutions we've found
        solution_count = 0
        if not hasattr(self, 'maximum_solutions'):
            error_msg = "maximum_solutions not loaded from schedule_parameters table."
            current_app.logger.error(error_msg)
            raise ValueError(error_msg)

        max_solutions = self.maximum_solutions  # Strictly use DB value
        
        # Print header for solution scores in terminal
        print("\n" + "="*80)
        print("OPTIMAL SCHEDULE SOLUTIONS WEIGHTED SCORES")
        print("="*80)
        print(f"{'#':<3} {'Total Score':<12} {'Prof Pref':<12} {'Time Pref':<12} {'Gap Penalty':<12} {'Sessions':<8}")
        print("-"*80)
        
        while solution_count < max_solutions:
            # Extract the current solution
            current_solution = self._extract_solution(model, x, y, I, idx_to_code)
            
            if not current_solution['schedule']:
                current_app.logger.warning("Empty schedule in solution, stopping iteration")
                break
                
            # Print all active decision variables for this solution
            print(f"\n=== SOLUTION {solution_count + 1} ACTIVE DECISION VARIABLES (VALUE=1) ===")
            active_x_vars = []
            active_y_vars = []
            
            for var in model.variables():
                var_value = pulp.value(var)
                if var_value is not None and var_value > 0.5:
                    if var.name.startswith('x_'):
                        # Parse x_i_k_l
                        parts = var.name.split('_')
                        if len(parts) >= 4:
                            i = parts[1]
                            k = parts[2]
                            l = parts[3]
                            course_code = idx_to_code.get(int(i), i)
                            active_x_vars.append(f"x({course_code},{k},{l})=1")
                    
                    elif var.name.startswith('y_'):
                        # Parse y_i_k_p
                        parts = var.name.split('_')
                        if len(parts) >= 4:
                            i = parts[1]
                            k = parts[2]
                            p = parts[3]
                            course_code = idx_to_code.get(int(i), i)
                            active_y_vars.append(f"y({course_code},{k},{p})=1")
            
            print(f"SOLUTION {solution_count + 1} - ACTIVE X VARIABLES (SCHEDULE ASSIGNMENTS):")
            if active_x_vars:
                for var in sorted(active_x_vars):
                    print(f"  {var}")
            else:
                print("  None")
                
            print(f"\nSOLUTION {solution_count + 1} - ACTIVE Y VARIABLES (PROFESSOR ASSIGNMENTS):")
            if active_y_vars:
                for var in sorted(active_y_vars):
                    print(f"  {var}")
            else:
                print("  None")
            print("="*50)
            
            # Add debug logging to check the solution format
            current_app.logger.debug(f"Solution {solution_count + 1} details: {len(current_solution['schedule'])} sessions")
            # Log first session for debugging
            if current_solution['schedule']:
                first_session = current_solution['schedule'][0]
                # Log the session details in a more readable format
                current_app.logger.debug(f"First session: {first_session['course_code']} on {first_session['day']} at {first_session['start_time']}")
                current_app.logger.debug(f"Time values: start={type(first_session['start_time'])}, end={type(first_session['end_time'])}")
                
                # Double-check all sessions have proper time formatting
                for i, session in enumerate(current_solution['schedule']):
                    if not isinstance(session['start_time'], str):
                        current_app.logger.warning(f"Session {i} start_time is not a string: {type(session['start_time'])}")
                        session['start_time'] = self._format_time(session['start_time'])
                    if not isinstance(session['end_time'], str):
                        current_app.logger.warning(f"Session {i} end_time is not a string: {type(session['end_time'])}")
                        session['end_time'] = self._format_time(session['end_time'])
            
            # Check if this solution has gaps (for logging purposes only)
            gap_penalty = current_solution['objective_components']['gap_penalty']
            if gap_penalty > 0:
                current_app.logger.warning(f"Solution {solution_count + 1} has gaps with penalty {gap_penalty}")
                # Log the schedule to help debug
                for session in current_solution['schedule']:
                    current_app.logger.debug(f"Session: {session['course_code']} on {session['day']} at {session['start_time']}, slot {session['time_slot']}")
            
            # Add the solution to our list
            all_solutions.append(current_solution)
            solution_count += 1
            
            # Print solution scores in terminal
            total_score = current_solution['total_objective_value']
            prof_pref = current_solution['objective_components']['professor_preference_value']
            time_pref = current_solution['objective_components']['timeslot_preference_value']
            gap_pen = current_solution['objective_components']['gap_penalty']
            sessions_count = len(current_solution['schedule'])
            
            print(f"{solution_count:<3} {total_score:<12.2f} {prof_pref:<12.2f} {time_pref:<12.2f} {gap_pen:<12.2f} {sessions_count:<8}")
            
            current_app.logger.info(f"Found solution {solution_count} with {len(current_solution['schedule'])} sessions, objective value: {total_score}")
            current_app.logger.info(f"  Prof pref: {prof_pref}, Time pref: {time_pref}, Gap penalty: {gap_pen}")
            
            # Add a constraint to exclude this solution
            # We need to identify all active x variables in the current solution
            active_x_vars = []
            for var in model.variables():
                var_value = pulp.value(var)
                if var.name.startswith('x_') and var_value is not None and var_value > 0.5:
                    active_x_vars.append(var)
            
            if not active_x_vars:
                current_app.logger.warning("No active x decision variables in solution, stopping iteration")
                break
                
            # Create a constraint that ensures we don't get the same solution again
            # Sum of all active decision variables must be less than the number of active variables
            unique_id = int(time.time() * 1000) % 10000  # Get milliseconds as unique ID
            constraint_name = f"exclude_solution_{solution_count}_{unique_id}"
            model += pulp.lpSum(active_x_vars) <= len(active_x_vars) - 1, constraint_name
            
            # Add a constraint to maintain optimality
            model += model.objective >= optimal_objective_value, f"maintain_optimality_{solution_count}_{unique_id}"
            
            current_app.logger.info(f"Added constraints to exclude solution {solution_count} and searching for next solution...")
            
            # Solve again
            result = model.solve(solver)
            
            # Check if we found another optimal solution
            if result != pulp.LpStatusOptimal:
                current_app.logger.info(f"No more optimal solutions found. Status: {pulp.LpStatus[result]}")
                break
            
            # Check if the objective value is still optimal
            new_obj_value = pulp.value(model.objective)
            if new_obj_value is None or new_obj_value < optimal_objective_value - 0.001:  # Allow for small numerical differences
                current_app.logger.info(f"Next solution has lower objective value ({new_obj_value}), stopping search")
                break
        
        # Print footer
        print("-"*80)
        print(f"Total optimal solutions found: {len(all_solutions)}")
        print("="*80 + "\n")
        
        current_app.logger.info(f"Found {len(all_solutions)} optimal solutions")
        
        # If only one solution was found, make sure to mention that in the message
        message = f"Found {len(all_solutions)} optimal schedule"
        if len(all_solutions) == 1:
            message += ". There is only one optimal solution for this configuration."
        else:
            message += "s"
        
        return {
            'success': True,
            'message': message,
            'solutions': all_solutions,
            'objective_value': optimal_objective_value
        }
    
    def _calculate_professor_preference(self, model, x, y, I, idx_to_code):
        """Calculate professor preference value from the model solution"""
        professor_preference_value = 0
        
        # Process each active y variable to calculate professor preference
        for var in model.variables():
            var_name = var.name
            var_value = pulp.value(var)
            # Check if var_value is not None before comparing
            if var_name.startswith('y_') and var_value is not None and var_value > 0.5:
                parts = var_name.split('_')
                if len(parts) >= 4:
                    i = int(parts[1])  # course index
                    k = int(parts[2])  # session number
                    p = int(parts[3])  # professor index
                    
                    # Get course code from index
                    course_code = idx_to_code.get(i)
                    if not course_code:
                        continue
                    
                    # Default weight is 1 (no preference)
                    weight = 1
                    
                    # Check if we have preference data for this course and professor
                    if course_code in self.professor_preferences and p in self.professor_preferences[course_code]:
                        # Get all professor preferences for this course
                        profs_ranked = 0
                        rank_of_p = self.professor_preferences[course_code][p]
                        
                        # Count ranked professors
                        for prof_idx, rank in self.professor_preferences[course_code].items():
                            if rank > 0:
                                profs_ranked += 1
                        
                        # Calculate weight if professor p was ranked
                        if rank_of_p is not None and rank_of_p > 0 and profs_ranked > 0:
                            weight = profs_ranked - rank_of_p + 1
                    
                    professor_preference_value += weight
        
        return professor_preference_value
    
    def _calculate_timeslot_preference(self, schedule):
        """Calculate timeslot preference value for a given schedule"""
        timeslot_preference_value = 0
        
        for session in schedule:
            time_slot = session['time_slot']
            if time_slot in self.timeslot_preferences and self.timeslot_preferences[time_slot]:
                timeslot_preference_value += 1
        
        return timeslot_preference_value
    
    def _calculate_gap_penalty(self, schedule, lambda_weight=100):
        """Calculate gap penalty for a given schedule"""
        # Create a dictionary to track used time slots by day
        used_slots_by_day = {}
        for session in schedule:
            day = session['day']
            time_slot = int(session['time_slot'])
            
            if day not in used_slots_by_day:
                used_slots_by_day[day] = set()
            used_slots_by_day[day].add(time_slot)
        
        # Count gaps in each day
        gap_penalty = 0
        gaps_found = []
        
        for day, time_slots in used_slots_by_day.items():
            # Skip days with 0 or 1 session
            if len(time_slots) <= 1:
                continue
            
            # Get day index (0-5)
            day_idx = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'].index(day)
            
            # Get the day's slots (1-5)
            day_slots = [day_idx*5 + slot + 1 for slot in range(5)]
            
            # For each possible gap pattern
            for start_idx in range(4):  # First 4 slots
                for end_idx in range(start_idx + 2, 5):  # At least 2 slots later
                    first_slot = day_slots[start_idx]
                    last_slot = day_slots[end_idx]
                    
                    # The slots in between (the potential gap)
                    middle_slots = [day_slots[i] for i in range(start_idx + 1, end_idx)]
                    
                    # Check if this is a gap: first and last slots used, all middle slots empty
                    if (first_slot in time_slots and 
                        last_slot in time_slots and 
                        all(mid not in time_slots for mid in middle_slots)):
                        
                        # Gap size is the number of empty slots
                        gap_size = len(middle_slots)
                        gap_penalty += gap_size
                        gaps_found.append(f"{gap_size}-slot gap on {day}: slots {first_slot}-{last_slot}")
        
        # Log any gaps found
        if gaps_found:
            current_app.logger.warning(f"Found {len(gaps_found)} gaps in schedule: {', '.join(gaps_found)}")
        
        # Apply the weight to the gap penalty
        return gap_penalty * lambda_weight

    def _format_time(self, time_obj):
        """Format time object to HH:MM string format"""
        if isinstance(time_obj, time):
            return time_obj.strftime('%H:%M')
        elif isinstance(time_obj, timedelta):
            # Convert timedelta to hours and minutes
            total_minutes = int(time_obj.total_seconds() / 60)
            hours = total_minutes // 60
            minutes = total_minutes % 60
            return f"{hours:02d}:{minutes:02d}"
        elif isinstance(time_obj, str):
            # If it's already a string, try to ensure it's in HH:MM format
            try:
                if ':' in time_obj:
                    parts = time_obj.split(':')
                    if len(parts) >= 2:
                        hours = int(parts[0])
                        minutes = int(parts[1])
                        return f"{hours:02d}:{minutes:02d}"
            except ValueError:
                pass
            return time_obj
        else:
            # For any other type, convert to string
            return str(time_obj)

def optimize_student_schedule(student_id, db_connection=None, random_seed=None, preferences=None, find_all=False):
  
    close_connection = False
    
    try:
        # Create database connection if not provided
        if db_connection is None:
            db_connection = mysql.connector.connect(
                host=current_app.config['MYSQL_HOST'],
                user=current_app.config['MYSQL_USER'],
                password=current_app.config['MYSQL_PASSWORD'],
                database=current_app.config['MYSQL_DB']
            )
            close_connection = True
        
        # Create and run optimizer
        optimizer = ScheduleOptimizer(db_connection, student_id)
        optimizer.load_data()
        
        # Check if student has enrolled courses
        if not optimizer.enrolled_courses:
            return {
                'success': False,
                'message': 'No enrolled courses found'
            }
        
        # Check if we have schedule options for the enrolled courses
        if not optimizer.schedule_options:
            return {
                'success': False,
                'message': 'No schedule options available for the enrolled courses'
            }
        
        # Check if we have session information for the enrolled courses
        missing_sessions = [c for c in optimizer.enrolled_courses if c not in optimizer.course_sessions]
        if missing_sessions:
            return {
                'success': False,
                'message': f'Missing session information for courses: {", ".join(missing_sessions)}'
            }
        
        # Build and solve the model
        if find_all:
            result = optimizer.find_all_optimal_solutions(random_seed, preferences)
            # If we found solutions, add semester and year info to the solutions
            if result['success'] and 'solutions' in result and result['solutions'] and len(result['solutions']) > 0 and 'schedule' in result['solutions'][0]:
                cursor = db_connection.cursor()
                cursor.execute("""
                    SELECT DISTINCT ac.semester, ac.year 
                    FROM add_course ac
                    WHERE ac.student_id = %s AND ac.status = 'enrolled'
                    ORDER BY ac.year DESC, ac.semester DESC
                    LIMIT 1
                """, (student_id,))
                semester_info = cursor.fetchone()
                if semester_info:
                    for solution in result['solutions']:
                        solution['semester'] = semester_info[0]
                        solution['year'] = semester_info[1]
                cursor.close()
        else:
            result = optimizer.solve(preferences)
            
            # Get semester and year info for display
            if result['success'] and 'schedule' in result and result['schedule']:
                cursor = db_connection.cursor()
                cursor.execute("""
                    SELECT DISTINCT ac.semester, ac.year 
                    FROM add_course ac
                    WHERE ac.student_id = %s AND ac.status = 'enrolled'
                    ORDER BY ac.year DESC, ac.semester DESC
                    LIMIT 1
                """, (student_id,))
                semester_info = cursor.fetchone()
                if semester_info:
                    result['semester'] = semester_info[0]
                    result['year'] = semester_info[1]
                cursor.close()
            
        return result
        
    except Exception as e:
        current_app.logger.error(f"Error in schedule optimization: {str(e)}", exc_info=True)
        return {
            'success': False,
            'message': f'Error optimizing schedule: {str(e)}'
        }
    finally:
        # Close connection if we created it
        if close_connection and db_connection:
            db_connection.close() 