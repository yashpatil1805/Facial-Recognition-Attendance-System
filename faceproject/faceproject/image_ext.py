from flask import Flask, render_template, Response, jsonify
import cv2
import face_recognition
import mysql.connector
import numpy as np
import os
import shutil

image_ext = Flask(__name__)


# Function to process database images and extract face encodings
def process_database_images():
    known_face_encodings = []
    known_face_names = []

    # Process images from the database to extract face encodings
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="facial_recognition_attendance"
    )

    cursor = connection.cursor(dictionary=True)
    query = "SELECT name, img FROM students"
    cursor.execute(query)
    students = cursor.fetchall()

    for student in students:
        try:
            # Decode the image from the database
            image_data = np.frombuffer(student['img'], np.uint8)
            image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # Detect faces and extract encodings
            face_locations = face_recognition.face_locations(rgb_image)
            face_encodings = face_recognition.face_encodings(rgb_image, face_locations)

            for face_encoding in face_encodings:
                name = student['name']
                known_face_encodings.append(face_encoding)
                known_face_names.append(name)

        except Exception as e:
            print(f"Error processing image for student {student['name']}: {e}")

    return known_face_encodings, known_face_names


# Video streaming generator function for Flask
def generate_video_stream():
    # Initialize the webcam
    video_capture = cv2.VideoCapture(0)

    # Load the known face encodings from the database
    known_face_encodings, known_face_names = process_database_images()

    while True:
        ret, frame = video_capture.read()
        if not ret:
            break

        # Convert frame to RGB for face_recognition
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Detect faces in the frame
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

            if True in matches:
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]
            else:
                name = "Unknown"

            # Draw bounding box and name on the frame
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        # Encode the frame as JPEG and yield it for the stream
        ret, jpeg = cv2.imencode('.jpg', frame)
        if ret:
            frame_data = jpeg.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n\r\n')

    video_capture.release()


# Route to display the attendance page
@image_ext.route('/')
def index():
    return render_template('index.html')


# Route for the live video stream (MJPEG)
@image_ext.route('/video_feed')
def video_feed():
    return Response(generate_video_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    image_ext.run(debug=True)
