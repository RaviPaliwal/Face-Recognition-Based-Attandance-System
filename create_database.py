import sqlite3

conn = sqlite3.connect('database.db')
c = conn.cursor()

# Drop existing tables if they exist
c.execute('DROP TABLE IF EXISTS students')
c.execute('DROP TABLE IF EXISTS attendance')
c.execute('DROP TABLE IF EXISTS face_encodings')

# Create students table (without face encodings)
c.execute('''
    CREATE TABLE students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        image_path TEXT NOT NULL
    )
''')

# Create attendance table
c.execute('''
    CREATE TABLE attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        attendance_date TEXT NOT NULL,
        FOREIGN KEY(student_id) REFERENCES students(id)
    )
''')

# Create face_encodings table (linked to students)
c.execute('''
    CREATE TABLE face_encodings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        face_encoding BLOB NOT NULL,
        FOREIGN KEY(student_id) REFERENCES students(id)
    )
''')

conn.commit()
conn.close()