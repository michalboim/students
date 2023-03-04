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
    CREATE TABLE IF NOT EXISTS teachers (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        phone TEXT
        ) 
    """)  
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
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        phone TEXT
        )
    """)
    query("""
    CREATE TABLE IF NOT EXISTS students_courses (
        id INTEGER PRIMARY KEY,
        student_id INTEGER,
        course_id INTEGER,
        grade INTEGER,
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
        attendance TEXT,
        UNIQUE (student_id, course_id, date),
        FOREIGN KEY (student_id) REFERENCES students (id),
        FOREIGN KEY (course_id) REFERENCES courses (id)
    )
    """)

def create_fake_data(students_num=10, teachers_num=4):

    fake=faker.Faker()
    for student in range(students_num):
        query(f"INSERT INTO students (name, email) VALUES ('{fake.name()}','{fake.email()}')")
    for teachers in range(teachers_num):
        query(f"INSERT INTO teachers (name, email) VALUES ('{fake.name()}','{fake.email()}')")
    courses=['python', 'java', 'html', 'css', 'js']
    for course in courses:
        trachers_ids=[tup[0] for tup in query("SELECT id FROM teachers")] #[(1,),(2,)]
        query(f"INSERT INTO courses (name, teacher_id, start) VALUES ('{course.title()}', '{random.choice(trachers_ids)}','2000-01-01' )")


if __name__=="__main__":
    create_tables()
    create_fake_data()