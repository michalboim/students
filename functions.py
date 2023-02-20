import classes
import crud

def create_courses_objects(courses: list):
    courses_objects=[classes.Course(course[0], course[1], course[2], course[3], course[4], course[5], course[6] ) for course in courses]
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