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
        description TEXT DEFAULT "Still not updated",
        teacher_id TEXT NOT NULL DEFAULT "Still not updated",
        start TEXT DEFAULT "Still not updated",
        day TEXT DEFAULT "Still not updated",
        time TEXT DEFAULT "Still not updated", 
        FOREIGN KEY (teacher_id) REFERENCES teachers (id)
        )
    """)
    query("""
    CREATE TABLE IF NOT EXISTS teachers (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE ,
        phone TEXT UNIQUE ,
        user_id INTEGER,
        FOREIGN KEY(user_id) REFERENCES new_users (id)
        ) 
    """) 
    query("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE,
        phone TEXT UNIQUE,
        user_id INTEGER,
        FOREIGN KEY(user_id) REFERENCES new_users (id)
        )
    """)
    query("""
    CREATE TABLE IF NOT EXISTS administrators (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE,
        phone TEXT UNIQUE,
        user_id INTEGER,
        FOREIGN KEY(user_id) REFERENCES new_users (id)
        ) 
    """) 
    query("""
    CREATE TABLE IF NOT EXISTS new_users (
        id INTEGER,
	    username TEXT UNIQUE,
	    password TEXT DEFAULT "123456",
	    role_id INTEGER,
	    PRIMARY KEY(id),
        FOREIGN KEY (role_id) REFERENCES roles (id)
        )
    """)
    query("""
    CREATE TABLE IF NOT EXISTS roles (
        id INTEGER,
	    type TEXT,
	    PRIMARY KEY(id)
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
        id INTEGER PRIMARY KEY,
	    message TEXT,
	    location TEXT,
        time TEXT,
        UNIQUE (message, time)
    )
    """)
    query("""
    CREATE TABLE IF NOT EXISTS messages_courses (
        id INTEGER PRIMARY KEY,
        message_id INTEGER,
        course_id INTEGER,
        status TEXT DEFAULT "publish",
        UNIQUE (message_id, course_id),
        FOREIGN KEY (message_id) REFERENCES messages (id),
        FOREIGN KEY (course_id) REFERENCES courses (id)
    )
    """)
    query("""
    CREATE TABLE IF NOT EXISTS publish_courses (
        id INTEGER PRIMARY KEY,
        course_name TEXT,
        description TEXT DEFAULT "Still not updated",
        picture TEXT,
        status TEXT DEFAULT "publish"
    )
    """)

def create_fake_data(students_num=10, teachers_num=4):
    roels={1:'student', 2:'teacher', 3:'admin'}
    for role in roels.values():
        query(f"INSERT INTO roles (type) VALUES ('{role}')")
    fake=faker.Faker()
    for student in range(students_num):
        email=fake.email()
        query(f"INSERT INTO new_users (username, role_id) VALUES ('{email}', '1')")
        user_id=query(f"SELECT id FROM new_users WHERE username='{email}'")
        query(f"INSERT INTO students (name, email, user_id) VALUES ('{fake.name()}','{email}', '{user_id[0][0]}')")
    for teachers in range(teachers_num):
        email=fake.email()
        query(f"INSERT INTO new_users (username, role_id) VALUES ('{email}', '2')")
        user_id=query(f"SELECT id FROM new_users WHERE username='{email}'")
        query(f"INSERT INTO teachers (name, email, user_id) VALUES ('{fake.name()}','{email}', '{user_id[0][0]}')")
    for admin in range(teachers_num):
        email=fake.email()
        query(f"INSERT INTO new_users (username, role_id, password) VALUES ('{email}', '3', 'admin')")
        user_id=query(f"SELECT id FROM new_users WHERE username='{email}'")
        query(f"INSERT INTO administrators (name, email, user_id) VALUES ('{fake.name()}','{email}', '{user_id[0][0]}')")
    courses=['python', 'java', 'html', 'css', 'js']
    for course in courses:
        trachers_ids=[tup[0] for tup in query("SELECT id FROM teachers")]
        query(f"INSERT INTO courses (name, teacher_id, start) VALUES ('{course.title()}', '{random.choice(trachers_ids)}','2000-01-01' )")
    for course in range(courses):
        query(f"INSERT INTO publish_courses (course_name) VALUES ('{random.choice(courses)}')")

    query(f"INSERT INTO new_users (username, role_id) VALUES ('d@d', '1')")
    user_id=query(f"SELECT id FROM new_users WHERE username='d@d'")
    query(f"INSERT INTO students (name, email, user_id) VALUES ('dan','d@d', '{user_id[0][0]}')")
    
    query(f"INSERT INTO new_users (username, role_id) VALUES ('t@t', '2')")
    user_id=query(f"SELECT id FROM new_users WHERE username='t@t'")
    query(f"INSERT INTO teachers (name, email, user_id) VALUES ('tal','t@t', '{user_id[0][0]}')")
    
    query(f"INSERT INTO new_users (username, role_id, password) VALUES ('m@m', '3', 'admin')")
    user_id=query(f"SELECT id FROM new_users WHERE username='m@m'")
    query(f"INSERT INTO administrators (name, email, user_id) VALUES ('michal','m@m', '{user_id[0][0]}')")

if __name__=="__main__":
    create_tables()
    #create_fake_data()