from flask import Flask, render_template, request, redirect, url_for, Response, jsonify
import sqlite3
import os
import cv2
import face_recognition
from datetime import datetime
import numpy as np
import base64

app = Flask(__name__)
DATABASE = 'database.db'
UPLOAD_FOLDER = './static/studentimages/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Utility functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def get_encoded_faces():
    conn = get_db_connection()
    students = conn.execute('SELECT * FROM students').fetchall()
    known_face_encodings = []
    known_face_names = []

    for student in students:
        face_encoding_blob = conn.execute('SELECT face_encoding FROM face_encodings WHERE student_id = ?', (student['id'],)).fetchone()
        if face_encoding_blob:
            face_encoding = np.frombuffer(face_encoding_blob['face_encoding'], dtype=np.float64)  # Convert BLOB to numpy array
            known_face_encodings.append(face_encoding)
            known_face_names.append(student['name'])
    
    conn.close()
    return known_face_encodings, known_face_names

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/view_attendance')
def view_attendance():
    conn = get_db_connection()
    # Fetch all attendance records with student names and dates
    attendance_records = conn.execute('''
        SELECT students.name, attendance.attendance_date
        FROM attendance
        JOIN students ON attendance.student_id = students.id
        ORDER BY attendance.attendance_date DESC
    ''').fetchall()
    conn.close()

    return render_template('attendance.html', attendance_records=attendance_records)


@app.route('/add_student', methods=['POST'])
def add_student():
    name = request.form['name']
    file = request.files['image']

    # Ensure the upload folder exists
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    if file and allowed_file(file.filename):
        filename = file.filename
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        # Save the uploaded image to the specified path
        file.save(filepath)

        # Process image to extract face encoding
        image = face_recognition.load_image_file(filepath)
        face_encodings = face_recognition.face_encodings(image)

        if len(face_encodings) > 0:
            face_encoding = face_encodings[0]

            conn = get_db_connection()
            
            # Insert the student into the students table
            conn.execute('INSERT INTO students (name, image_path) VALUES (?, ?)', (name, filepath))
            student_id = conn.execute('SELECT id FROM students WHERE name = ?', (name,)).fetchone()['id']

            # Store face encoding as a BLOB in the face_encodings table
            conn.execute('INSERT INTO face_encodings (student_id, face_encoding) VALUES (?, ?)', 
                         (student_id, face_encoding.tobytes()))  # Convert numpy array to BLOB

            conn.commit()
            conn.close()

            return redirect(url_for('index'))
        else:
            return "No face found in the image"
    return "Failed to add student"

@app.route('/video_feed')
def video_feed():
    def generate():
        video_capture = cv2.VideoCapture(0)
        while True:
            ret, frame = video_capture.read()
            if not ret:
                break

            # Convert frame to JPEG format
            ret, jpeg = cv2.imencode('.jpg', frame)
            if not ret:
                break

            # Yield the frame in the format required for streaming
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')

        video_capture.release()

    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/process_frame', methods=['POST'])
def process_frame():
    data = request.get_json()
    image_data = data['image']

    # Decode the base64 image data
    image_data = image_data.split(',')[1]
    image_data = base64.b64decode(image_data)
    
    # Convert image data to numpy array
    np_image = np.frombuffer(image_data, np.uint8)
    
    # Handle empty image data
    if np_image.size == 0:
        return jsonify({'message': 'No image data received'})

    image = cv2.imdecode(np_image, cv2.IMREAD_COLOR)
    known_face_encodings, known_face_names = get_encoded_faces()
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_image)
    face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
    
    attendance_list = []
    messages = []
    
    conn = get_db_connection()
    for i, face_encoding in enumerate(face_encodings):
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)

        if matches[best_match_index]:
            name = known_face_names[best_match_index]
            bounding_box = face_locations[i]

            if name not in attendance_list:
                attendance_list.append(name)
                print(name)
                student = conn.execute('SELECT id FROM students WHERE name = ?', (name,)).fetchone()
                if student:
                    student_id = student['id']
                    current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    existing_attendance = conn.execute(
                        'SELECT * FROM attendance WHERE student_id = ? AND DATE(attendance_date) = DATE(?)',
                        (student_id, current_date)
                    ).fetchone()
                    if existing_attendance:
                        messages.append(f"Attendance for {name} already marked for today.")
                    else:
                        conn.execute('INSERT INTO attendance (student_id, attendance_date) VALUES (?, ?)', 
                                     (student_id, current_date))
                        conn.commit()
                        messages.append(f"Attendance marked for {name}.")
                
            # Return name and bounding box
            return jsonify({
                'message': 'success',
                'attendance': attendance_list,
                'bounding_boxes': {name: bounding_box for name, bounding_box in zip(attendance_list, face_locations)},
                'messages': messages
            })

    conn.close()
    return jsonify({
        'message': 'No faces recognized',
        'attendance': attendance_list,
        'bounding_boxes': {},
        'messages': messages
    })

if __name__ == '__main__':
    app.run(debug=True)
