from flask import Flask, redirect, url_for, render_template, request
app = Flask(__name__)
from setup_db import query
import classes
import crud
from functions import create_courses_objects, create_students_objects, create_teachers_objects

@app.route('/register/<student_id>/<course_id>')
def register(student_id, course_id):
    query (F"INSERT INTO students_courses (student_id, course_id) VALUES ('{student_id}', '{course_id}')")
    return redirect(url_for('registations', student_id=student_id))# שליחת המשתנה על הנתיב

@app.route('/registations/<student_id>')
def registations(student_id):
    course_ids=query(f"SELECT course_id FROM students_courses WHERE student_id={student_id}")
    return render_template("registations.html", course_ids=course_ids)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/home')
def go_home():
    return render_template('home.html')

@app.route('/courses')
def courses():
    courses_teachers=[]
    for course in create_courses_objects():
        for teacher in create_teachers_objects():
            if course.teacher_id==str(teacher.tid):
                course_teacher=classes.Course(course.tid, course.name, course.description, teacher.name)
                courses_teachers.append(course_teacher)
    return render_template('courses.html', courses_teachers=courses_teachers)

@app.route('/add_course', methods=['GET','POST'])
def add_course():
    if request.method=='POST':  
        num_courses=len(crud.read_all('courses'))
        crud.create('courses', 'name, description, teacher_id', f" '{request.form['new_name'].title()}', '{request.form['new_description']}', '{request.form['teacher_tid']}' ")
        new_num=len(crud.read_all('courses'))
        if num_courses<new_num:
            return render_template ('add_course.html', teachers_object=create_teachers_objects() ,note=f"{request.form['new_name'].title()} course added successfully")
        else:
            return render_template ('add_course.html',teachers_object=create_teachers_objects() ,note="A mistake occurred please try again")
    else:
        return render_template('add_course.html', teachers_object=create_teachers_objects())

@app.route('/students')
def students():
    return render_template('students.html', students_objects=create_students_objects())

@app.route('/add_student', methods=['POST','GET'])
def add_student():
    if request.method=='POST':
        num_students=len(crud.read_all('students'))
        crud.create('students', 'name,email', f"'{request.form['new_name'].title()}','{request.form['new_email']}'")
        new_num=len(crud.read_all('students'))
        if new_num>num_students:
            return render_template('add_student.html', note=f"{request.form['new_name'].title()} added successfully")
        else:
            return render_template('add_student.html', note="A mistake occurred please try again")
    else:
        return render_template('add_student.html')

