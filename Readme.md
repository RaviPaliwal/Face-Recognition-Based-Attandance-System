# Face Recognition Attendance System

A web-based attendance system using Face Recognition built with Flask, OpenCV, and face_recognition. The system allows automatic attendance marking via real-time video feeds.

## Features

- **Add Students**: Upload an image and store student details in the database.
- **Mark Attendance**: Recognizes students via webcam feed and logs their attendance.
- **View Attendance**: Displays attendance records with timestamps.
- **Web Interface**: Simple and intuitive interface for user interaction.

## Technologies Used

- **Flask** for backend
- **SQLite** for database
- **OpenCV** and **face_recognition** for face detection
- **HTML/CSS** for frontend

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Ravipaliwal/FaceRecognitionAttendance.git
   cd FaceRecognitionAttendance

## Install dependencies:
pip install Flask opencv-python face-recognition
Set up the database:

python create_database.py
Run the Flask app:

python app.py
Access the app: Open your browser and go to http://127.0.0.1:5000/.

## Usage
**Add Students**: Input name and upload a clear image.
**Mark Attendance**: Start the webcam feed and mark attendance by recognizing faces.
**View Attendance**: Navigate to the attendance page to view records.
# Face Recognition Based Attandance System
 This is a Flask + CV project for a realtime face recognition based attandance system very simple and effective.

