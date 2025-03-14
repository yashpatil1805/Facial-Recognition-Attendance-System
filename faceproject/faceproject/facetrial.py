import cv2
import mysql.connector
import os
import shutil
import numpy as np
import face_recognition
from PIL import Image
from io import BytesIO


# Function to fetch images from the database
def fetch_images_from_database(connection):
    cursor = connection.cursor(dictionary=True)
    query = "SELECT name, img FROM students"
    cursor.execute(query)
    students = cursor.fetchall()
    cursor.close()
    return students


# Function to create temporary images folder
def create_images_folder(folder_path="images"):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Temporary folder '{folder_path}' created.")
    return folder_path


# Function to delete the images folder
def delete_images_folder(folder_path="images"):
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
        print(f"Temporary folder '{folder_path}' and all contents have been deleted.")


# Function to process the database images and extract face encodings
def process_database_images(folder_path="images"):
    students = []
    known_face_encodings = []
    known_face_names = []

    for filename in os.listdir(folder_path):
        if filename.endswith(".jpg"):
            try:
                # Load the image from the file
                image_path = os.path.join(folder_path, filename)
                image = cv2.imread(image_path)
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                # Detect faces in the image and get encodings
                face_locations = face_recognition.face_locations(rgb_image)
                face_encodings = face_recognition.face_encodings(rgb_image, face_locations)

                # If faces are detected, add them to known faces
                for face_encoding in face_encodings:
                    name = filename.split('_')[0]  # Use the student name from the filename
                    known_face_encodings.append(face_encoding)
                    known_face_names.append(name)

                students.append({
                    'name': filename.split('_')[0],
                    'image': image,
                })
            except Exception as e:
                print(f"Error processing image {filename}: {e}")

    return known_face_encodings, known_face_names


# Function to display live feed and recognize faces using Haar Cascade and deep learning model
def display_and_recognize_faces():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="facial_recognition_attendance"
    )

    # Create temporary 'images' folder
    folder_path = create_images_folder()

    print("Fetching images from the database...")
    students = fetch_images_from_database(connection)
    print(f"Total images fetched: {len(students)}")

    # Process images from the database to extract face encodings
    known_face_encodings, known_face_names = process_database_images(folder_path)

    # Initialize the Haar Cascade Classifier for face detection
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    # Initialize the video capture from webcam
    video_capture = cv2.VideoCapture(0)

    while True:
        ret, frame = video_capture.read()
        if not ret:
            print("Failed to capture video frame. Exiting...")
            break

        # Convert frame to grayscale for Haar Cascade detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces using Haar Cascade
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        # Process each detected face
        for (x, y, w, h) in faces:
            # Extract the face region
            face_roi = frame[y:y + h, x:x + w]

            # Convert face region to RGB (needed for face recognition)
            rgb_face = cv2.cvtColor(face_roi, cv2.COLOR_BGR2RGB)

            # Get face encodings for the current face
            face_encodings = face_recognition.face_encodings(rgb_face)

            if face_encodings:  # Ensure that face encodings are found
                face_encoding = face_encodings[0]
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

                # If matches are found, get the best match
                if True in matches:
                    face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)
                    name = known_face_names[best_match_index]
                else:
                    name = "Unknown"

                # Draw a rectangle around the face and label with the name
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        # Display the resulting frame
        cv2.imshow("Video", frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()

    # Delete the temporary folder and its contents after the script finishes
    delete_images_folder(folder_path)
    connection.close()


if __name__ == "__main__":
    display_and_recognize_faces()
