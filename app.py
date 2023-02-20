from flask import Flask, redirect, url_for, render_template, request
app = Flask(__name__)
from setup_db import query
import classes
import crud
from functions import create_courses_objects, create_students_objects, create_teachers_objects, courses_teachers

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/home')
def go_home():
    return render_template('home.html')

@app.route('/administrator')
def administrator():
    return render_template ('administrator.html')

@app.route('/admin_courses')
def admin_courses():
    return render_template('admin_courses.html', courses_teachers=courses_teachers())

@app.route('/add_course', methods=['GET','POST'])
def add_course():
    if request.method=='POST':  
        num_courses=len(crud.read_all('courses'))
        crud.create('courses', 'name, description, teacher_id, start, day, time', f" '{request.form['new_name'].title()}', '{request.form['new_description']}', '{request.form['teacher_tid']}', '{request.form['new_start']}', '{request.form['new_day']}', '{request.form['new_time']}' ")
        new_num=len(crud.read_all('courses'))
        if num_courses<new_num:
            return render_template ('add_course.html', teachers_object=create_teachers_objects() ,note=f"{request.form['new_name'].title()} course added successfully")
        else:
            return render_template ('add_course.html',teachers_object=create_teachers_objects() ,note="A mistake occurred please try again")
    else:
        return render_template('add_course.html', teachers_object=create_teachers_objects())

@app.route('/update_courses', methods=['GET', 'POST'])
def update_courses():
    if request.method=='POST':
        courses_list=crud.read_like('*', 'courses', 'name', request.form['search'].title())
        if len(courses_list)<1:
            return render_template('update_courses.html', result='No such course was found')
        if len(courses_list)>=1:
            course_object=[classes.Course(course[0], course[1], course[2], course[3], course[4], course[5], course[6]) for course in courses_list]  
            return render_template('update_courses.html',courses_objects=course_object)
    else:    
        return render_template('update_courses.html', courses=courses_teachers())

@app.route('/chosen_course/<course_id>', methods=['GET', 'POST'])
def chosen_course_update(course_id):
    course_info=crud.read_if('*',"courses","id", course_id)
    course_object=[classes.Course(course[0], course[1], course[2], course[3], course[4], course[5], course[6]) for course in course_info]
    teacher_info=[]
    for course in course_object:
        for teacher in create_teachers_objects():
            if course.teacher_id==str(teacher.tid):
                teacher_info.append(teacher.tid)
                teacher_info.append(teacher.name)
    if request.method=='POST':
        name=request.form['name'].title()
        description=request.form['description']
        teacher_id=request.form['teacher_id']
        start=request.form['start']
        day=request.form['day']
        time=request.form['time']
        crud.update('courses', 'name, description, teacher_id, start, day, time', f"'{name}', '{description}', '{teacher_id}', '{start}', '{day}', '{time}'", course_id)
        return redirect(url_for('admin_courses'))
    else:
        return render_template('chosen_course.html',course_object=course_object, teachers_objects=create_teachers_objects(), teacher_info=teacher_info ) 

@app.route('/admin_students')
def admin_students():
    return render_template('admin_students.html', students_objects=create_students_objects())

@app.route('/add_student', methods=['POST','GET'])
def add_student():
    if request.method=='POST':
        num_students=len(crud.read_all('students'))
        crud.create('students', 'name, email, phone', f"'{request.form['new_name'].title()}','{request.form['new_email']}','{request.form['new_phone']}'")
        new_num=len(crud.read_all('students'))
        if new_num>num_students:
            return render_template('add_student.html', note=f"{request.form['new_name'].title()} added successfully")
        else:
            return render_template('add_student.html', note="A mistake occurred please try again")
    else:
        return render_template('add_student.html')

@app.route('/update_students', methods=['GET', 'POST'])
def update_students():
    if request.method=='POST':
        students_list=crud.read_like('*', 'students', 'name', request.form['search'].title())
        if len(students_list)<1:
            return render_template('update_students.html', result='No such student was found')
        if len(students_list)>=1:
            student_object=[classes.Student(student[0], student[1], student[2], student[3]) for student in students_list]  
            return render_template('update_students.html',student_objects=student_object)
    else:    
        return render_template('update_students.html', students=create_students_objects())

@app.route('/chosen_student/<student_id>', methods=['GET', 'POST'])
def chosen_student_update(student_id):
    student_info=crud.read_if('*',"students","id", student_id)
    student_object=[classes.Student(student[0], student[1], student[2], student[3]) for student in student_info]
    if request.method=='POST':
        name=request.form['name'].title()
        email=request.form['email']
        phone=request.form['phone']
        crud.update('students', 'name, email, phone', f"'{name}', '{email}', '{phone}'", student_id)
        return redirect(url_for('admin_students'))
    else:
        return render_template('chosen_student.html',student_object=student_object) 


@app.route('/admin_teachers')
def admin_teachers():
    return render_template('admin_teachers.html', teachers_objects=create_teachers_objects())

@app.route('/add_teacher', methods=['POST','GET'])
def add_teacher():
    if request.method=='POST':
        num_teachers=len(crud.read_all('teachers'))
        crud.create('teachers', 'name, email, phone', f"'{request.form['new_name'].title()}','{request.form['new_email']}','{request.form['new_phone']}'")
        new_num=len(crud.read_all('teachers'))
        if new_num>num_teachers:
            return render_template('add_teacher.html', note=f"{request.form['new_name'].title()} added successfully")
        else:
            return render_template('add_teacher.html', note="A mistake occurred please try again")
    else:
        return render_template('add_teacher.html')

@app.route('/update_teachers', methods=['GET', 'POST'])
def update_teachers():
    if request.method=='POST':
        teachers_list=crud.read_like('*', 'teachers', 'name', request.form['search'].title())
        if len(teachers_list)<1:
            return render_template('update_teachers.html', result='No such teacher was found')
        if len(teachers_list)>=1:
            teacher_object=[classes.Teacher(teacher[0], teacher[1], teacher[2], teacher[3]) for teacher in teachers_list]  
            return render_template('update_teachers.html',teacher_objects=teacher_object)
    else:    
        return render_template('update_teachers.html', teachers=create_teachers_objects())

@app.route('/chosen_teacher/<teacher_id>', methods=['GET', 'POST'])
def chosen_teacher_update(teacher_id):
    teacher_info=crud.read_if('*',"teachers","id", teacher_id)
    teacher_object=[classes.Teacher(teacher[0], teacher[1], teacher[2], teacher[3]) for teacher in teacher_info]
    if request.method=='POST':
        name=request.form['name'].title()
        email=request.form['email']
        phone=request.form['phone']
        crud.update('teachers', 'name, email, phone', f"'{name}', '{email}', '{phone}'", teacher_id)
        return redirect(url_for('admin_teachers'))
    else:
        return render_template('chosen_teacher.html',teacher_object=teacher_object) 
