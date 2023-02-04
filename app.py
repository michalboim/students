from flask import Flask, redirect, url_for, render_template, request
app = Flask(__name__)
from setup_db import query
import classes
import crud

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

@app.route('/students')
def students():
    return render_template('students.html')

@app.route('/courses')
def courses():  
    return render_template('courses.html')

@app.route('/add_course', methods=['GET','POST'])
def add_course():
    teachers=crud.read_all('teachers')
    teachers_object=[classes.Teacher(teacher[0], teacher[1], teacher[2]) for teacher in teachers]   
    if request.method=='POST':  
        num_courses=len(crud.read_all('courses'))
        crud.create('courses', 'name, description, teacher_id', f" '{request.form['new_name'].title()}', '{request.form['new_description']}', '{request.form['teacher_tid']}' ")
        new_num=len(crud.read_all('courses'))
        if num_courses<new_num:
            return render_template ('add_course.html', teachers_object=teachers_object ,note=f"{request.form['new_name'].title()} course added successfully")
        else:
            return render_template ('add_course.html',teachers_object=teachers_object ,note="A mistake occurred please try again")
    else:
        return render_template('add_course.html', teachers_object=teachers_object)

