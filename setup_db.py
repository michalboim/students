import sqlite3
import faker
import random

def query(sql):
    with sqlite3.connect('students.db') as conn:
        cur=conn.cursor()
        cur.execute(sql)
        return cur.fetchall()

def create_tables():
    query("""
    CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        teacher_id TEXT NOT NULL,
        start TEXT,
        day TEXT,
        time TEXT, 
        FOREIGN KEY (teacher_id) REFERENCES teachers (id)
        )
    """)
    query("""
    CREATE TABLE IF NOT EXISTS teachers (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        phone TEXT UNIQUE
        ) 
    """) 
    query("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        phone TEXT UNIQUE
        )
    """)
    query("""
    CREATE TABLE IF NOT EXISTS administrators (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE
        ) 
    """) 
    query("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER,
	    student_user TEXT  UNIQUE,
	    teacher_user TEXT  UNIQUE,
	    admin_user TEXT UNIQUE,
	    password TEXT DEFAULT "123456",
	    role TEXT,
	    PRIMARY KEY(id),
	    FOREIGN KEY(student_user) REFERENCES students (email),
	    FOREIGN KEY (teacher_user) REFERENCES teachers (email),
        FOREIGN KEY (admin_user) REFERENCES administrators (email)
        )
    """)
    query("""
    CREATE TABLE IF NOT EXISTS students_courses (
        id INTEGER PRIMARY KEY,
        student_id INTEGER,
        course_id INTEGER,
        grade INTEGER DEFAULT "unknown",
        UNIQUE (student_id, course_id),
        FOREIGN KEY (student_id) REFERENCES students (id),
        FOREIGN KEY (course_id) REFERENCES courses (id)
    )
    """)
    query("""
    CREATE TABLE IF NOT EXISTS students_attendance (
        id INTEGER PRIMARY KEY,
        student_id INTEGER,
        course_id INTEGER,
        date TEXT,
        attendance TEXT DEFAULT "unknown",
        UNIQUE (student_id, course_id, date),
        FOREIGN KEY (student_id) REFERENCES students (id),
        FOREIGN KEY (course_id) REFERENCES courses (id)
    )
    """)
    query("""
    CREATE TABLE IF NOT EXISTS messages (
        message TEXT
    )
    """)
def create_fake_data(students_num=10, teachers_num=4):

    fake=faker.Faker()
    for student in range(students_num):
        email=fake.email()
        query(f"INSERT INTO students (name, email) VALUES ('{fake.name()}','{email}')")
        query(f"INSERT INTO users (student_user, role) VALUES ('{email}', 'student')")
    for teachers in range(teachers_num):
        email=fake.email()
        query(f"INSERT INTO teachers (name, email) VALUES ('{fake.name()}','{email}')")
        query(f"INSERT INTO users (teacher_user, role) VALUES ('{email}', 'teacher')")
    for admin in range(teachers_num):
        email=fake.email()
        query(f"INSERT INTO administrators (name, email) VALUES ('{fake.name()}','{email}')")
        query(f"INSERT INTO users (admin_user,password, role) VALUES ('{email}', 'admin','admin')")
    courses=['python', 'java', 'html', 'css', 'js']
    for course in courses:
        trachers_ids=[tup[0] for tup in query("SELECT id FROM teachers")] #[(1,),(2,)]
        query(f"INSERT INTO courses (name, teacher_id, start) VALUES ('{course.title()}', '{random.choice(trachers_ids)}','2000-01-01' )")
    messages=['message 1', 'message 2', 'message 3']
    for message in messages:
        query(f"INSERT INTO messages (message) VALUES ('{message}')")

if __name__=="__main__":
    create_tables()
    create_fake_data()