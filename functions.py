import classes
import crud
from setup_db import query
def create_courses_objects(courses: list):
    courses_objects=[classes.Course(course[0], course[1], course[2], course[3], course[4], course[5], course[6] ) for course in courses]
    for c in courses_objects:
        c.start=f'{c.start[8:]}-{c.start[5:7]}-{c.start[0:4]}'
    return courses_objects

def create_teachers_objects(teachers: list):
    teachers_objects=[classes.Teacher(teacher[0], teacher[1], teacher[2], teacher[3]) for teacher in teachers]
    return teachers_objects

def create_students_objects(students: list):
    students_objects=[classes.Student(student[0], student[1], student[2], student[3]) for student in students]
    return students_objects

def courses_teachers():
    courses_teachers=[]
    for course in create_courses_objects(crud.read_all('courses')):
        for teacher in create_teachers_objects(crud.read_all('teachers')):
            if course.teacher_id==str(teacher.tid):
                course_teacher=classes.Course(course.tid, course.name, course.description, teacher.name, course.start, course.day, course.time)
                courses_teachers.append(course_teacher)
    return courses_teachers

def authenticate(email,password):
    result=query(f"SELECT new_users.id, roles.type from new_users, roles WHERE new_users.username='{email}' AND new_users.password='{password}' AND roles.id=new_users.role_id")
    if len(result)!=0:
        return result
    return []