import classes
import crud

def create_courses_objects():
    courses_list=crud.read_all('courses')
    courses_objects=[classes.Course(course[0], course[1], course[2], course[3]) for course in courses_list]
    return courses_objects

def create_teachers_objects():
    teachers_list=crud.read_all('teachers')
    teachers_objects=[classes.Teacher(teacher[0], teacher[1], teacher[2]) for teacher in teachers_list]
    return teachers_objects

def create_students_objects():
    students_list=crud.read_all('students')
    students_objects=[classes.Student(student[0], student[1], student[2]) for student in students_list]
    return students_objects