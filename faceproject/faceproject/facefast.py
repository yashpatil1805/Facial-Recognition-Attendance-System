import cv2
import face_recognition
import numpy as np

# Load known faces and encodings
def load_known_faces():
    # Example: Replace with your actual image paths and names
    known_face_encodings = []
    known_face_names = []

    # Add faces
    known_faces = [
        {"name": "yash", "image_path": "yash.jpg"},
        {"name": "prajakta", "image_path": "prajakta.jpg"},
        {"name": "ranjana", "image_path": "ranjana.jpg"},
    ]

    for face in known_faces:
        image = face_recognition.load_image_file(face["image_path"])
        encoding = face_recognition.face_encodings(image)
        known_face_encodings.append(encoding)
        known_face_names.append(face["name"])

    return known_face_encodings, known_face_names

# Initialize known faces
known_face_encodings, known_face_names = load_known_faces()

def process_frame(frame):
    """Resize frame for faster processing and detect faces."""
    # Resize frame to 1/4 size for faster face processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = small_frame[:, :, ::-1]  # Convert BGR to RGB

    # Find face locations and encodings
    face_locations = face_recognition.face_locations(rgb_small_frame, model="hog")
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    face_names = []
    for face_encoding in face_encodings:
        # Compare face with known encodings
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.6)
        name = "Unknown"

        # Use the first match
        if True in matches:
            first_match_index = matches.index(True)
            name = known_face_names[first_match_index]

        face_names.append(name)

    return face_locations, face_names

# Start webcam feed
def main():
    video_capture = cv2.VideoCapture(0)

    while True:
        # Capture a single frame of video
        ret, frame = video_capture.read()
        if not ret:
            print("Failed to grab frame.")
            break

        # Process the frame for face detection and recognition
        face_locations, face_names = process_frame(frame)

        # Draw results on the original frame
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Scale back up face locations since the frame was scaled to 1/4
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw a rectangle around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            # Draw a label with the name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
            cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)

        # Display the resulting image
        cv2.imshow("Video", frame)

        # Break the loop with 'q'
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # Release the capture
    video_capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
