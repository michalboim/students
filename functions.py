import classes
import crud

def create_courses_objects():
    courses_list=crud.read_all('courses')
    courses_objects=[classes.Course(course[0], course[1], course[2], course[3], course[4], course[5], course[6] ) for course in courses_list]
    return courses_objects

def create_teachers_objects():
    teachers_list=crud.read_all('teachers')
    teachers_objects=[classes.Teacher(teacher[0], teacher[1], teacher[2], teacher[3]) for teacher in teachers_list]
    return teachers_objects

def create_students_objects():
    students_list=crud.read_all('students')
    students_objects=[classes.Student(student[0], student[1], student[2], student[3]) for student in students_list]
    return students_objects

def courses_teachers():
    courses_teachers=[]
    for course in create_courses_objects():
        for teacher in create_teachers_objects():
            if course.teacher_id==str(teacher.tid):
                course_teacher=classes.Course(course.tid, course.name, course.description, teacher.name, course.start, course.day, course.time)
                courses_teachers.append(course_teacher)
    return courses_teachers