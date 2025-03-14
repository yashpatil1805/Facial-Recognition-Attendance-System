import os
from functools import wraps

import dlib
import face_recognition
import numpy as np
from flask import render_template, redirect, url_for, flash, request, jsonify, Response
from flask_login import login_user, logout_user, current_user, login_required
from app import app, mysql, bcrypt, login_manager
from forms import LoginForm, RegistrationForm
from forms2 import LoginForm, RegistrationForm2
from models import User, load_user
import cv2
import base64
from io import BytesIO
from flask import send_file
login_manager.user_loader(load_user)
captured_frame = None
camera = cv2.VideoCapture(0)

#def role_required(required_role):
#    def decorator(f):
 #       @wraps(f)
  #      def wrapped_function(*args, **kwargs):
   #         if current_user.role != required_role:
    #            flash('Access Denied. You do not have permission to access this page.', 'danger')
     #           return redirect(url_for('dashboard'))
      #      return f(*args, **kwargs)
       # return wrapped_function
    #return decorator


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/howitworks')
def howitworks():
    return render_template('howitworks.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/features')
def features():
    return render_template('features.html')


@app.route('/take_attendance')
def take_attendance():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM subjects WHERE faculty_id = 5")
    subjects = cursor.fetchall()
    cursor.close()

    return render_template('faculty/take_attendance.html', subjects=subjects)


import base64
from flask import render_template
from flask_login import login_required, current_user

@app.route('/student/attendancedisplay')
@login_required
def attendancedisplay():
    cursor = mysql.connection.cursor()

    try:
        # Fetch attendance records for the logged-in student
        cursor.execute("""
            SELECT s.student_id, s.name, s.enrollment_number, s.img, 
                   a.attendance_date, a.attendance_time, a.subject_id 
            FROM students s 
            JOIN attendance a ON s.student_id = a.student_id
            WHERE s.student_id = %s
        """, (current_user.id,))
        students = cursor.fetchall()

        # If no attendance records are found, return an empty list
        if not students:
            return render_template('student/attendancedisplay.html', attendancedisplay=[])

        students_data = []

        for student in students:
            subject_id = student['subject_id']

            # Fetch subject details
            cursor.execute("SELECT subject_name, class_id FROM subjects WHERE subject_id = %s", (subject_id,))
            subject = cursor.fetchone()
            subject_name = subject['subject_name'] if subject else "Unknown"
            class_id = subject['class_id'] if subject else None

            # Fetch class details
            class_name = "Unknown"
            if class_id:
                cursor.execute("SELECT class_name FROM classes WHERE class_id = %s", (class_id,))
                class_result = cursor.fetchone()
                class_name = class_result['class_name'] if class_result else "Unknown"

            # Convert image data to base64 for rendering in the HTML
            img_data = base64.b64encode(student['img']).decode('utf-8') if student['img'] else None

            students_data.append({
                'student_id': student['student_id'],
                'name': student['name'],
                'enrollment_number': student['enrollment_number'],
                'img_data': img_data,
                'attendance_date': student['attendance_date'],
                'attendance_time': student['attendance_time'],
                'subject_id': student['subject_id'],
                'subject_name': subject_name,
                'class_name': class_name,
            })

        return render_template('student/attendancedisplay.html', attendancedisplay=students_data)

    except Exception as e:
        print(f"Error fetching student attendance display: {e}")
        return render_template('student/attendancedisplay.html', attendancedisplay=[])

    finally:
        cursor.close()


import base64
from flask import render_template

@app.route('/admin/admin_attendancedisplay')
def admin_attendancedisplay():
    cursor = mysql.connection.cursor()

    try:
        # Fetch attendance records with student details
        cursor.execute("""
            SELECT s.student_id, s.name, s.enrollment_number, s.img, 
                   a.attendance_date, a.attendance_time, a.subject_id 
            FROM students s 
            JOIN attendance a ON s.student_id = a.student_id
        """)
        students = cursor.fetchall()

        # If no students are found, return an empty list
        if not students:
            return render_template('admin/admin_attendancedisplay.html', attendancedisplay=[])

        students_data = []

        for student in students:
            subject_id = student['subject_id']

            # Fetch subject details
            cursor.execute("SELECT subject_name, class_id FROM subjects WHERE subject_id = %s", (subject_id,))
            subject = cursor.fetchone()
            subject_name = subject['subject_name'] if subject else "Unknown"
            class_id = subject['class_id'] if subject else None

            # Fetch class details
            class_name = "Unknown"
            if class_id:
                cursor.execute("SELECT class_name FROM classes WHERE class_id = %s", (class_id,))
                class_result = cursor.fetchone()
                class_name = class_result['class_name'] if class_result else "Unknown"

            # Convert image data to base64 for rendering in the HTML
            img_data = base64.b64encode(student['img']).decode('utf-8') if student['img'] else None

            students_data.append({
                'student_id': student['student_id'],
                'name': student['name'],
                'enrollment_number': student['enrollment_number'],
                'img_data': img_data,
                'attendance_date': student['attendance_date'],
                'attendance_time': student['attendance_time'],
                'subject_id': student['subject_id'],
                'subject_name': subject_name,
                'class_name': class_name,
            })

        return render_template('admin/admin_attendancedisplay.html', attendancedisplay=students_data)

    except Exception as e:
        print(f"Error fetching admin attendance display: {e}")
        return render_template('admin/admin_attendancedisplay.html', attendancedisplay=[])

    finally:
        cursor.close()


import base64
from flask import render_template

@app.route('/facultyattendancedisplay')
def facultyattendancedisplay():
    cursor = mysql.connection.cursor()

    try:

        today_date = date.today().strftime('%Y-%m-%d')  # Get today's date in 'YYYY-MM-DD' format
        # Fetch attendance records with student details
        cursor.execute("""
            SELECT s.student_id, s.name, s.enrollment_number, s.img, 
                   a.attendance_date, a.attendance_time, a.subject_id 
            FROM students s 
            JOIN attendance a ON s.student_id = a.student_id
            WHERE a.attendance_date = %s
        """, (today_date,))
        students = cursor.fetchall()

        # If no students are found, return an empty list
        if not students:
            return render_template('faculty/facultyattendancedisplay.html', attendancedisplay=[])

        students_data = []

        for student in students:
            subject_id = student['subject_id']

            # Fetch subject details
            cursor.execute("SELECT subject_name, class_id FROM subjects WHERE subject_id = %s", (subject_id,))
            subject = cursor.fetchone()
            subject_name = subject['subject_name'] if subject else "Unknown"
            class_id = subject['class_id'] if subject else None

            # Fetch class details
            class_name = "Unknown"
            if class_id:
                cursor.execute("SELECT class_name FROM classes WHERE class_id = %s", (class_id,))
                class_result = cursor.fetchone()
                class_name = class_result['class_name'] if class_result else "Unknown"

            # Convert image data to base64 for rendering in the HTML
            img_data = base64.b64encode(student['img']).decode('utf-8') if student['img'] else None

            students_data.append({
                'student_id': student['student_id'],
                'name': student['name'],
                'enrollment_number': student['enrollment_number'],
                'img_data': img_data,
                'attendance_date': student['attendance_date'],
                'attendance_time': student['attendance_time'],
                'subject_id': student['subject_id'],
                'subject_name': subject_name,
                'class_name': class_name,
            })

        return render_template('faculty/facultyattendancedisplay.html', attendancedisplay=students_data)

    except Exception as e:
        print(f"Error fetching faculty attendance display: {e}")
        return render_template('faculty/facultyattendancedisplay.html', attendancedisplay=[])

    finally:
        cursor.close()


from flask import send_file, request, render_template
import base64
from fpdf import FPDF
from flask import send_file, request
from MySQLdb.cursors import DictCursor
import pandas as pd
from datetime import datetime, timedelta


class AttendancePDF(FPDF):
    def header(self):
        # Add Logo
        self.image("static/admin/logo.jpg", 10, 8, 25)  # Adjust path to your college logo

        # College Name
        self.set_font("Arial", "B", 14)
        self.cell(200, 10, "Shree Chanakya Education Society", ln=True, align="C")

        # Institute Name
        self.set_font("Arial", "B", 12)
        self.cell(200, 10, "INDIRA COLLEGE OF COMMERCE & SCIENCE", ln=True, align="C")

        # Address
        self.set_font("Arial", "", 10)
        self.cell(200, 5, "DHRUV, 89/2A, NEW PUNE-MUMBAI HIGHWAY, TATHAWADE", ln=True, align="C")
        self.ln(5)

    def footer(self):
        # Page Number
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


from flask import request, send_file
import pandas as pd
from datetime import datetime, timedelta
from fpdf import FPDF

@app.route('/download_attendance/<file_type>', methods=['POST'])
def download_attendance(file_type):
    cursor = mysql.connection.cursor(DictCursor)

    start_date = session.get('start_date')
    end_date = session.get('end_date')



    if not start_date or not end_date:
        return "Please select a valid date range.", 400

    try:
        # Query to fetch filtered student attendance details
        query = """
            SELECT s.student_id, s.name, c.class_name, sub.subject_name, 
                   a.attendance_date, a.attendance_time 
            FROM attendance a
            JOIN students s ON a.student_id = s.student_id
            JOIN subjects sub ON a.subject_id = sub.subject_id
            JOIN classes c ON sub.class_id = c.class_id
            WHERE a.attendance_date BETWEEN %s AND %s
        """
        cursor.execute(query, (start_date, end_date))
        data = cursor.fetchall()
    finally:
        cursor.close()

    if not data:
        return "No attendance data available for the selected date range.", 400

    # Convert `attendance_date` and `attendance_time` to string format
    for record in data:
        record['attendance_date'] = record['attendance_date'].strftime('%Y-%m-%d') if isinstance(
            record['attendance_date'], datetime) else record['attendance_date']
        if isinstance(record['attendance_time'], timedelta):
            record['attendance_time'] = str(record['attendance_time'])  # Convert to HH:MM:SS format
        elif isinstance(record['attendance_time'], datetime):
            record['attendance_time'] = record['attendance_time'].strftime('%H:%M:%S')

    # Convert fetched data into Pandas DataFrame
    df = pd.DataFrame(data)

    if file_type == 'excel':
        file_path = "/tmp/attendance_report.xlsx"
        df.to_excel(file_path, index=False)
        return send_file(file_path, as_attachment=True, download_name="Attendance_Report.xlsx")

    elif file_type == 'pdf':
        pdf = AttendancePDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 10)

        # Table headers
        pdf.cell(30, 10, "Student ID", border=1, align='C')
        pdf.cell(30, 10, "Student Name", border=1, align='C')
        pdf.cell(30, 10, "Class Name", border=1, align='C')
        pdf.cell(30, 10, "Subject Name", border=1, align='C')
        pdf.cell(30, 10, "Attendance Date", border=1, align='C')
        pdf.cell(30, 10, "Attendance Time", border=1, ln=True, align='C')

        pdf.set_font("Arial", "", 8)

        # Table data
        for index, row in df.iterrows():
            pdf.cell(30, 10, str(row['student_id']), border=1, align='C')
            pdf.cell(30, 10, row['name'], border=1, align='C')
            pdf.cell(30, 10, row['class_name'], border=1, align='C')
            pdf.cell(30, 10, row['subject_name'], border=1, align='C')
            pdf.cell(30, 10, str(row['attendance_date']), border=1, align='C')
            pdf.cell(30, 10, str(row['attendance_time']), border=1, align='C', ln=True)

        file_path = "/tmp/attendance_report.pdf"
        pdf.output(file_path)
        return send_file(file_path, as_attachment=True, download_name="Attendance_Report.pdf")

    return "Invalid file type selected.", 400


import base64
from flask import render_template, request
from flask_login import login_required
from datetime import date
from MySQLdb.cursors import DictCursor

@app.route('/reports', methods=['GET'])
@login_required
def reports():
    cursor = mysql.connection.cursor(DictCursor)

    try:
        # Default: Show attendance for today
        default_date = date.today().strftime('%Y-%m-%d')
        start_date = request.args.get('start_date', default_date)
        end_date = request.args.get('end_date', default_date)
        if start_date and end_date:
            session['start_date'] = start_date
            session['end_date'] = end_date
        # Query to get filtered attendance
        query = """
            SELECT s.student_id, s.name, s.enrollment_number, s.img, 
                   a.attendance_date, a.attendance_time, a.subject_id, 
                   sub.subject_name, c.class_name
            FROM students s
            JOIN attendance a ON s.student_id = a.student_id
            JOIN subjects sub ON a.subject_id = sub.subject_id
            JOIN classes c ON sub.class_id = c.class_id
            WHERE a.attendance_date BETWEEN %s AND %s
        """
        cursor.execute(query, (start_date, end_date))
        students = cursor.fetchall()

        students_data = []
        for student in students:
            img_data = base64.b64encode(student['img']).decode('utf-8') if student['img'] else None
            students_data.append({
                'student_id': student['student_id'],
                'name': student['name'],
                'enrollment_number': student['enrollment_number'],
                'img_data': img_data,
                'attendance_date': student['attendance_date'],
                'attendance_time': student['attendance_time'],
                'subject_id': student['subject_id'],
                'subject_name': student['subject_name'],
                'class_name': student['class_name'],
            })

        # Fetch total present students
        cursor.execute(
            "SELECT COUNT(DISTINCT student_id) AS total_present FROM attendance WHERE attendance_date BETWEEN %s AND %s",
            (start_date, end_date)
        )
        total_present = cursor.fetchone()
        total_present = total_present['total_present'] if total_present else 0

        # Fetch total classes conducted
        cursor.execute(
            "SELECT COUNT(DISTINCT attendance_date) AS total_classes FROM attendance WHERE attendance_date BETWEEN %s AND %s",
            (start_date, end_date)
        )
        total_classes = cursor.fetchone()
        total_classes = total_classes['total_classes'] if total_classes else 0

        # Prepare data for graphs
        cursor.execute(
            "SELECT attendance_date, COUNT(*) AS count FROM attendance WHERE attendance_date BETWEEN %s AND %s GROUP BY attendance_date",
            (start_date, end_date)
        )
        graph_data = cursor.fetchall()
        attendance_dates = [row['attendance_date'].strftime('%Y-%m-%d') for row in graph_data] if graph_data else []
        attendance_counts = [row['count'] for row in graph_data] if graph_data else []

        return render_template(
            'faculty/reports.html',
            attendancedisplay=students_data,
            default_date=default_date,
            total_present=total_present,
            total_classes=total_classes,
            attendance_dates=attendance_dates,
            attendance_counts=attendance_counts

        )

    except Exception as e:
        print(f"Error fetching reports: {e}")
        return render_template(
            'faculty/reports.html',
            attendancedisplay=[],
            default_date=default_date,
            total_present=0,
            total_classes=0,
            attendance_dates=[],
            attendance_counts=[]
        )

    finally:
        cursor.close()


import cv2

# Load the Haar Cascade for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')


def generate_frames():
    """Generate frames from the camera for live feed with face detection."""
    # Open a connection to the camera
    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("Error: Could not open camera.")
        return

    try:
        while True:
            # Capture frame-by-frame
            success, frame = camera.read()
            if not success:
                break

            # Convert to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detect faces in the frame
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=10, minSize=(30, 30))

            # Draw green rectangles around the faces
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Encode the frame for streaming
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            # Yield the frame to the video stream
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    finally:
        # Release the camera when done
        camera.release()


@app.route('/video_feed')
def video_feed():
    """Route to stream video feed."""
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')



@app.route('/capture_image', methods=['POST'])
def capture_image():
    global captured_frame
    # Capture image from the live feed
    success, captured_frame = camera.read()
    if not success:
        return jsonify({'message': 'Failed to capture image'}), 500
    return jsonify({'message': 'Image captured successfully'})



@app.route('/employee')
def employee():
    cursor = mysql.connection.cursor()
    cursor.execute(
        "SELECT s.student_id, s.name, s.enrollment_number, s.img, u.username FROM students s JOIN users u ON s.user_id = u.user_id")
    students = cursor.fetchall()
    cursor.close()

    # Convert image data to base64 for rendering in the HTML
    students_data = []
    for student in students:
        img_data = base64.b64encode(student['img']).decode('utf-8')
        students_data.append({
            'student_id': student['student_id'],
            'name': student['name'],
            'enrollment_number': student['enrollment_number'],
            'img_data': img_data,
            'username': student['username']
        })

    return render_template('employee.html', students=students_data)


import base64
from flask import render_template


import base64
from flask import render_template

@app.route('/faculty/students')
def faculty_students():
    cursor = mysql.connection.cursor()

    try:
        # Fetch students based on user_id
        cursor.execute("SELECT student_id, name, enrollment_number, img FROM STUDENTS WHERE user_id=%s", (current_user.id,))
        students = cursor.fetchall()

        # If no students are found, return an empty list
        if not students:
            return render_template('faculty/students.html', students=[])

        # Convert image data to base64 for rendering in the HTML
        students_data = []
        for student in students:
            img_data = base64.b64encode(student['img']).decode('utf-8') if student['img'] else None
            students_data.append({
                'student_id': student['student_id'],
                'name': student['name'],
                'enrollment_number': student['enrollment_number'],
                'img_data': img_data,
            })

        return render_template('faculty/students.html', students=students_data)

    except Exception as e:
        print(f"Error fetching students: {e}")  # Log the error
        return render_template('faculty/students.html', students=[])

    finally:
        cursor.close()


@app.route('/faculty/viewstudent/<int:student_id>')
def viewstudent(student_id):
    cursor = mysql.connection.cursor()
    cursor.execute(
        "SELECT * FROM STUDENTS WHERE student_id=%s", (student_id,))
    students = cursor.fetchall()
    cursor.close()

    # Convert image data to base64 for rendering in the HTML
    students_data = []
    for student in students:
        img_data = base64.b64encode(student['img']).decode('utf-8')
        students_data.append({
            'student_id': student['student_id'],
            'name': student['name'],
            'enrollment_number': student['enrollment_number'],
            'img_data': img_data,

        })

    return render_template('faculty/viewstudent.html', students=students_data)


@app.route('/student/profile')
def profile():
        cursor = mysql.connection.cursor()
        cursor.execute(
            "SELECT s.student_id, s.name, s.enrollment_number, s.img, u.username FROM students s JOIN users u ON s.user_id = u.user_id WHERE s.student_id = %s", (current_user.id,))
        students = cursor.fetchall()
        cursor.close()
        # Convert image data to base64 for rendering in the HTML
        students_data = []
        for student in students:

                img_data = base64.b64encode(student['img']).decode('utf-8')
                students_data.append({
                    'student_id': student['student_id'],
                    'name': student['name'],
                    'enrollment_number': student['enrollment_number'],
                    'img_data': img_data,
                    'username': student['username']
                })


        return render_template('student/profile.html', students=students_data)


@app.route('/admin/employee')
def admin_employee():
    cursor = mysql.connection.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE role='faculty'")
    users = cursor.fetchall()
    cursor.close()

    # Convert image data to base64 for rendering in the HTML
    users_data = []
    for user in users:
         users_data.append({
            'user_id': user['user_id'],
            'username': user['username'],
            'created_at': user['created_at'],
        })

    return render_template('admin/employee.html', users=users_data)


@app.route('/admin/addclass')
def addclass():
    cursor = mysql.connection.cursor()
    cursor.execute(
        "SELECT * FROM classes")
    classes = cursor.fetchall()
    cursor.close()

    # Convert image data to base64 for rendering in the HTML
    class_data = []
    for c in classes:
         class_data.append({
            'class_id': c['class_id'],
            'class_name': c['class_name'],

        })

    return render_template('admin/addclass.html', c=class_data)


@app.route('/admin/students')
def admin_students():
    cursor = mysql.connection.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE role='faculty'")
    users = cursor.fetchall()
    cursor.close()

    # Convert image data to base64 for rendering in the HTML
    users_data = []
    for user in users:
         users_data.append({
            'user_id': user['user_id'],
            'username': user['username'],
            'created_at': user['created_at'],
        })

    return render_template('admin/employee.html', users=users_data)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM Users WHERE username = %s", (form.username.data,))
        user = cursor.fetchone()
        if user and bcrypt.check_password_hash(user['password_hash'], form.password.data):
            user_obj=User(user['user_id'], user['username'], user['role'])
            login_user(user_obj)
            flash('Login successful', 'success')
            if user_obj.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user_obj.role == 'faculty':
                return redirect(url_for('faculty_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))
        else:
            flash('Login unsuccessful. Check username and password', 'danger')
    return render_template('login.html', form=form)
import random
import string
from flask import render_template, url_for, flash, redirect, request
from app import app, mysql, bcrypt
from forms import RegistrationForm

def generate_employee_number():
    """Generate a unique employee number, e.g., 'FAC12345'"""
    return "FAC" + ''.join(random.choices(string.digits, k=5))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        cursor = mysql.connection.cursor()

        # Insert into Users table
        cursor.execute("INSERT INTO Users (username, password_hash, role) VALUES (%s, %s, %s)",
                       (form.username.data, hashed_password, form.role.data))
        mysql.connection.commit()

        # Fetch the last inserted user_id correctly
        user_id = cursor.lastrowid  # ✅ More reliable way to get last inserted ID

        if not user_id:
            flash("User registration failed. Please try again.", "danger")
            return redirect(url_for('register'))

        # Insert into respective table based on role
        if form.role.data == 'faculty':
            employee_number = generate_employee_number()
            cursor.execute("INSERT INTO faculty (faculty_id, user_id, name, employee_number) VALUES (%s, %s, %s, %s)",
                           (user_id, user_id, form.username.data, employee_number))


        mysql.connection.commit()
        cursor.close()

        flash('Account created successfully', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)



@app.route('/adminregister', methods=['GET', 'POST'])
def adminregister():
    form = RegistrationForm2()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        cursor = mysql.connection.cursor()

        # Insert into Users table
        cursor.execute("INSERT INTO Users (username, password_hash, role) VALUES (%s, %s, %s)",
                       (form.username.data, hashed_password, form.role.data))
        mysql.connection.commit()

        # Fetch the last inserted user_id correctly
        user_id = cursor.lastrowid  # ✅ More reliable way to get last inserted ID

        if not user_id:
            flash("User registration failed. Please try again.", "danger")
            return redirect(url_for('adminregister'))

        mysql.connection.commit()
        cursor.close()

        flash('Account created successfully', 'success')
        return redirect(url_for('login'))

    return render_template('adminregister.html', form=form)

@app.route('/admin/dashboard')
def admin_dashboard():

    return render_template('admin/employee.html')
@app.route('/faculty/dashboard')
@login_required
def faculty_dashboard():
    cursor = mysql.connection.cursor(DictCursor)
    cursor2 = mysql.connection.cursor()
    # Fetch total students
    cursor.execute("SELECT COUNT(*) AS total_students FROM students WHERE user_id = %s", (current_user.id,))
    total_students = cursor.fetchone()
    cursor2.execute("SELECT * FROM users WHERE user_id = %s", (current_user.id,))
    users = cursor2.fetchall()
    user = []
    for u in users:
        user.append({
            'username': u['username'],

        })
    total_students = total_students['total_students'] if total_students else 0
    print(f"Total Students: {total_students}")  # Debugging
    # Fetch today's attendance stats
    today_date = date.today().strftime('%Y-%m-%d')

    cursor.execute("SELECT COUNT(*) AS total_present FROM attendance WHERE attendance_date = %s", (today_date,))
    total_present = cursor.fetchone()['total_present']

    cursor.execute("""
        SELECT COUNT(*) AS total_late_arrivals 
        FROM attendance 
        WHERE attendance_date = %s AND attendance_time > '18:00:00'
    """, (today_date,))
    total_late_arrivals = cursor.fetchone()['total_late_arrivals']

    total_absent = total_students - total_present
    attendance_rate = (total_present / total_students * 100) if total_students else 0
    absentee_rate = 100 - attendance_rate

    # Fetch attendance data for the last 7 days (for the chart)
    cursor.execute("""
        SELECT attendance_date, COUNT(*) AS count 
        FROM attendance 
        WHERE attendance_date >= DATE_SUB(%s, INTERVAL 30 DAY) 
        GROUP BY attendance_date
    """, (today_date,))

    graph_data = cursor.fetchall()
    attendance_dates = [row['attendance_date'].strftime('%Y-%m-%d') for row in graph_data]
    attendance_counts = [row['count'] for row in graph_data]

    cursor.close()

    return render_template(
        'faculty/dashboard.html',
        total_students=total_students,
        total_present=total_present,
        total_late_arrivals=total_late_arrivals,
        total_absent=total_absent,
        attendance_rate=round(attendance_rate, 2),
        absentee_rate=round(absentee_rate, 2),
        attendance_dates=attendance_dates,
        attendance_counts=attendance_counts,
        u=user,
    )
@app.route('/student/dashboard')
#@login_required
#@role_required('student')
def student_dashboard():

    return render_template(
        'student/attendancedisplay.html',

    )

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

from werkzeug.utils import secure_filename

# Define Upload Folder
UPLOAD_FOLDER = 'uploads/'
# Ensure upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)  # Create 'uploads/' if it does not exist
def allowed_file(filename):
    """Check if the uploaded file has a valid extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def compress_image(image_data, quality=1):
    """Compresses the image to reduce size before storing in MySQL."""
    img_array = np.frombuffer(image_data, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]  # Adjust quality (10-100)
    success, compressed_img = cv2.imencode('.jpg', img, encode_param)

    if success:
        return compressed_img.tobytes()
    return image_data  # Return original if compression fails
@app.route('/student/register', methods=['GET', 'POST'])
def register_student():
    if request.method == 'POST':
        student_id = request.form['student_id']
        user_id = current_user.id
        name = request.form['name']
        enrollment_number = request.form['enrollment_number']
        img_blob = None  # Placeholder for image data
        image_source = None  # To track whether image is from capture or upload

        # Check if the user uploaded an image
        if 'file' in request.files and request.files['file'].filename != '':
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)

                # Read image as binary data
                with open(file_path, 'rb') as img_file:
                    img_blob = img_file.read()
                os.remove(file_path)  # Remove the saved file after reading
                image_source = "Uploaded File"

        # If no uploaded image, check if a captured frame exists
        elif captured_frame is not None:
            img_path = 'captured_image.jpg'
            cv2.imwrite(img_path, captured_frame)
            with open(img_path, 'rb') as img_file:
                img_blob = img_file.read()
                img_blob = compress_image(img_blob)  # Compress before storing

            os.remove(img_path)
            image_source = "Live Capture"

        # If neither an uploaded file nor a live capture is provided, return an error
        if img_blob is None:
            flash('Please provide an image (either upload or capture).', 'danger')
            return redirect(url_for('register_student'))

        # Insert into MySQL
        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO students (student_id, user_id, name, enrollment_number, img) VALUES (%s, %s, %s, %s, %s)",
            (student_id, user_id, name, enrollment_number, img_blob))
        mysql.connection.commit()

        cursor.execute(
            "INSERT INTO users (user_id, username, password_hash, role) VALUES (%s, %s, %s, %s)",
            (student_id, name, bcrypt.generate_password_hash(name).decode('utf-8'), 'student'))
        mysql.connection.commit()

        cursor.close()
        flash(f'Student registered successfully! (Image Source: {image_source})', 'success')

    return render_template('faculty/register_student.html')

@app.route('/adminclass', methods=['GET', 'POST'])
def adminclass():
    if request.method == 'POST':
        name = request.form['name']
        # Insert into MySQL
        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO classes (class_name) VALUES (%s)",
            (name,))
        mysql.connection.commit()
        cursor.close()

        flash('Class registered successfully!', 'success')



    return render_template('admin/adminclass.html')


from flask import session


@app.route('/admin/addsubject/', methods=['GET', 'POST'])
def addsubject():
    if request.method == 'GET':
        class_id = request.args.get('class_id')
        if class_id:
            session['class_id'] = class_id

    class_id = session.get('class_id')

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM subjects WHERE class_id = %s", (class_id,))
    subjects = cursor.fetchall()
    cursor.close()

    # Prepare subject data for rendering
    subject_data = [{'subject_id': c['subject_id'], 'subject_name': c['subject_name'], 'class_id': c['class_id'],
                     'faculty_id': c['faculty_id']} for c in subjects]
    if request.method == 'POST':
        name = request.form['name']
        faculty_id = request.form['faculty_id']
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO subjects (subject_name, class_id, faculty_id) VALUES (%s, %s, %s)", (name, class_id, faculty_id))
        mysql.connection.commit()
        cursor.close()

        flash('Subject registered successfully!', 'success')
        return redirect(url_for('addsubject'))

    return render_template('/admin/addsubject.html', class_id=class_id, subject=subject_data)



# Initialize the camera
video_capture = cv2.VideoCapture(0)

# Load dlib models
detector = dlib.get_frontal_face_detector()
shape_predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")  # Download this file if needed


# ** Route for Face Detection (Attendance Feed) **
@app.route('/attendance_feed')
def attendance_feed():
    return Response(attendance_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


# ** Function to Stream Frames with Face Detection **
def attendance_frames():
    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("Error: Could not open camera.")
        return

    try:
        while True:
            success, frame = camera.read()
            if not success:
                break

            # Preprocess frame
            processed_frame = preprocess_frame(frame)

            # Convert to grayscale for face detection
            gray = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2GRAY)

            # Detect faces
            faces = detector(gray)

            # Draw rectangles around detected faces
            for face in faces:
                x, y, w, h = (face.left(), face.top(), face.width(), face.height())
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Encode the frame for streaming
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    finally:
        camera.release()


# ** Face Alignment Using dlib **
def align_face(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)

    if len(faces) == 0:
        return image  # Return original if no faces found

    for face in faces:
        shape = shape_predictor(gray, face)
        aligned_face = dlib.get_face_chip(image, shape)
        return aligned_face

    return image


# ** Preprocessing Function (Contrast & Blur) **
def preprocess_frame(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    contrast_img = cv2.equalizeHist(gray)  # Improve contrast
    blur_img = cv2.GaussianBlur(contrast_img, (3, 3), 0)  # Reduce noise
    return cv2.cvtColor(blur_img, cv2.COLOR_GRAY2RGB)


# ** Load Student Images & Train Model **
def process_database_images():

    known_face_encodings = []
    known_face_names = []
    with app.app_context():
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT name, img FROM students")
        students = cursor.fetchall()

        for student in students:
            try:
                # Decode image
                image_data = np.frombuffer(student['img'], np.uint8)
                image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)

                # Align the face
                aligned_face = align_face(image)

                # Convert to RGB
                rgb_image = cv2.cvtColor(aligned_face, cv2.COLOR_BGR2RGB)

                # Extract face encodings
                face_locations = face_recognition.face_locations(rgb_image)
                face_encodings = face_recognition.face_encodings(rgb_image, face_locations)

                for face_encoding in face_encodings:
                    known_face_encodings.append(face_encoding)
                    known_face_names.append(student['name'])

            except Exception as e:
                print(f"Error processing image for {student['name']}: {e}")

    return known_face_encodings, known_face_names


# ** Recognize Face Using Face Distance **
def recognize_face(face_encoding, known_face_encodings, known_face_names, tolerance=0.45):
    if len(known_face_encodings) == 0:
        return "Unknown"

    distances = face_recognition.face_distance(known_face_encodings, face_encoding)
    best_match_index = np.argmin(distances)

    if distances[best_match_index] < tolerance:
        return known_face_names[best_match_index]
    else:
        return "Unknown"


# ** Record Attendance in the Database **
def record_attendance(student_name):
    with app.app_context():
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT student_id, user_id FROM students WHERE name = %s", (student_name,))
            student = cursor.fetchone()

            if not student:
                print(f"No student found with name {student_name}")
                return

            student_id = student['student_id']
            user_id = student['user_id']

            cursor.execute("SELECT subject_id, subject_name, class_id FROM subjects WHERE faculty_id = %s", (user_id,))
            subject = cursor.fetchone()

            if not subject:
                print(f"No subject found for faculty_id: {user_id}")
                return

            subject_id = subject['subject_id']
            subject_name = subject['subject_name']
            class_id = subject['class_id']

            cursor.execute("SELECT class_name FROM classes WHERE class_id = %s", (class_id,))
            class_data = cursor.fetchone()

            if not class_data:
                print(f"Class ID {class_id} not found.")
                return

            class_name = class_data['class_name']
            attendance_date = date.today()
            attendance_time = datetime.now().time()

            # Check if attendance already exists
            cursor.execute("""
                SELECT * FROM attendance WHERE student_id = %s AND attendance_date = %s AND subject_id = %s
            """, (student_id, attendance_date, subject_id))
            existing_record = cursor.fetchone()

            if not existing_record:
                cursor.execute("""
                    INSERT INTO attendance (subject_id, student_id, attendance_date, status, attendance_time, class_name, subject_name)
                    VALUES (%s, %s, %s, 'present', %s, %s, %s)
                """, (subject_id, student_id, attendance_date, attendance_time, class_name, subject_name))
                mysql.connection.commit()
                print(f"Attendance recorded for {student_name}")
            else:
                print(f"Attendance already recorded for {student_name}")

        except Exception as e:
            print(f"Error recording attendance: {e}")


# ** Generate Live Video Stream with Face Recognition (Facefeed) **
@app.route('/facefeed')
def facefeed():
    return Response(generate_video_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')


def generate_video_stream():
    streaming = True
    with app.app_context():
     known_face_encodings, known_face_names = process_database_images()

    while streaming:
        ret, frame = video_capture.read()
        if not ret:
            break

        processed_frame = preprocess_frame(frame)
        rgb_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            name = recognize_face(face_encoding, known_face_encodings, known_face_names, tolerance=0.45)

            # Default label and color
            label = name
            color = (0, 255, 0)  # Green for newly marked
            if name != "Unknown":
                attendance_status = record_attendance(name)
                # If attendance was already recorded, change color to yellow
                if attendance_status == "already_marked":
                    label = f"{name} Already Marked"
                    color = (0, 255, 255)  # Yellow for already marked
                else:
                    label = f"{name} Marked"
                    color = (0, 255, 0)  # Green for newly marked

            else:
                color = (0, 0, 255)  # Red for unknown faces

                # Draw bounding box and text
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, label, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

        ret, jpeg = cv2.imencode('.jpg', frame)
        if ret:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

    video_capture.release()


@app.route('/stop_stream', methods=['POST'])
def stop_stream():
    global streaming
    streaming = False
    return jsonify({"message": "Stream stopped"})


