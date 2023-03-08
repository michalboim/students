from flask import Flask, redirect, url_for, render_template, request
app = Flask(__name__)
from setup_db import query
import classes
import crud
from functions import create_courses_objects, create_students_objects, create_teachers_objects, courses_teachers
from collections import namedtuple
import datetime

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/home')
def go_home():
    return render_template('home.html')

@app.route('/administrator' )
def administrator():
    return render_template ('administrator.html')

@app.route('/admin_courses',methods=['GET', 'POST'])
def admin_courses():
    if request.method=='POST':
        courses_list=crud.read_like('*', 'courses', 'name', request.form['search'].title())
        if len(courses_list)<1:
            return render_template('admin_courses.html', result='No such course was found')
        if len(courses_list)>=1:
            course_object=create_courses_objects(courses_list)
            for course in course_object:
                course.teacher_id=crud.teacher_name(course.teacher_id)  
            return render_template('admin_courses.html',courses_objects=course_object)
    return render_template('admin_courses.html', courses_teachers=courses_teachers())

@app.route('/course_info/<course_id>')
def course_info(course_id):
    course=crud.read_if('*',"courses","id", course_id)
    course_object=create_courses_objects(course)
    teacher_info=[]
    for course in course_object:
        for teacher in create_teachers_objects(crud.read_all('teachers')):
            if course.teacher_id==str(teacher.tid):
                teacher_info.append(teacher.tid)
                teacher_info.append(teacher.name)
    return render_template ('course_info.html', course_object=course_object, teacher_info=teacher_info )

@app.route('/add_course', methods=['GET','POST'])
def add_course():
    if request.method=='POST':  
        num_courses=len(crud.read_all('courses'))
        crud.create('courses', 'name, description, teacher_id, start, day, time', f" '{request.form['new_name'].title()}', '{request.form['new_description']}', '{request.form['teacher_tid']}', '{request.form['new_start']}', '{request.form['new_day']}', '{request.form['new_time']}' ")
        new_num=len(crud.read_all('courses'))
        if num_courses<new_num:
            return render_template ('add_course.html', teachers_object=create_teachers_objects(crud.read_all('teachers')) ,note=f"{request.form['new_name'].title()} course added successfully")
        else:
            return render_template ('add_course.html',teachers_object=create_teachers_objects(crud.read_all('teachers')) ,note="A mistake occurred please try again")
    else:
        return render_template('add_course.html', teachers_object=create_teachers_objects(crud.read_all('teachers')))

@app.route('/update_courses', methods=['GET', 'POST'])
def update_courses():
    if request.method=='POST':
        courses_list=crud.read_like('*', 'courses', 'name', request.form['search'].title())
        if len(courses_list)<1:
            return render_template('update_courses.html', result='No such course was found')
        if len(courses_list)>=1:
            course_object=create_courses_objects(courses_list)  
            return render_template('update_courses.html',courses_objects=course_object)
    else:    
        return render_template('update_courses.html', courses=courses_teachers())

@app.route('/chosen_course/<course_id>', methods=['GET', 'POST'])
def chosen_course_update(course_id):
    course_info=crud.read_if('*',"courses","id", course_id)
    course_object=create_courses_objects(course_info)
    teacher_info=[]
    for course in course_object:
        for teacher in create_teachers_objects(crud.read_all('teachers')):
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
        crud.update_if('courses', 'name, description, teacher_id, start, day, time', f"'{name}', '{description}', '{teacher_id}', '{start}', '{day}', '{time}'",'id', course_id)
        return redirect(url_for('admin_courses'))
    else:
        return render_template('chosen_course.html',course_object=course_object, teachers_objects=create_teachers_objects(crud.read_all('teachers')), teacher_info=teacher_info ) 

@app.route('/admin_students')
def admin_students():
    return render_template('admin_students.html', students_objects=create_students_objects(crud.read_all('students')))

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
            student_object=create_students_objects(students_list) 
            return render_template('update_students.html',student_objects=student_object)
    else:    
        return render_template('update_students.html', students=create_students_objects(crud.read_all('students')))

@app.route('/chosen_student/<student_id>', methods=['GET', 'POST'])
def chosen_student_update(student_id):
    student_info=crud.read_if('*',"students","id", student_id)
    student_object=create_students_objects(student_info)
    if request.method=='POST':
        name=request.form['name'].title()
        email=request.form['email']
        phone=request.form['phone']
        crud.update_if('students', 'name, email, phone', f"'{name}', '{email}', '{phone}'",'id', student_id)
        return redirect(url_for('admin_students'))
    else:
        return render_template('chosen_student.html',student_object=student_object) 

@app.route('/admin_teachers')
def admin_teachers():
    return render_template('admin_teachers.html', teachers_objects=create_teachers_objects(crud.read_all('teachers')))

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
            teacher_object=create_teachers_objects(teachers_list)   
            return render_template('update_teachers.html',teacher_objects=teacher_object)
    else:    
        return render_template('update_teachers.html', teachers=create_teachers_objects(crud.read_all('teachers')))

@app.route('/chosen_teacher/<teacher_id>', methods=['GET', 'POST'])
def chosen_teacher_update(teacher_id):
    teacher_info=crud.read_if('*',"teachers","id", teacher_id)
    teacher_object=create_teachers_objects(teacher_info) 
    if request.method=='POST':
        name=request.form['name'].title()
        email=request.form['email']
        phone=request.form['phone']
        crud.update_if('teachers', 'name, email, phone', f"'{name}', '{email}', '{phone}'",'id', teacher_id)
        return redirect(url_for('admin_teachers'))
    else:
        return render_template('chosen_teacher.html',teacher_object=teacher_object) 

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method=='POST':
        title=['Courses Resulte:', 'Students Resulte:', 'Teachers Resulte:']
        courses_list=crud.read_like('*', 'courses', 'name', request.form['search'].title())
        course_object=[]
        if len(courses_list)==0:
            course_object=['No results found']
        else:
            course_object.append(create_courses_objects(courses_list))
        students_list=crud.read_like('*', 'students', 'name', request.form['search'].title())
        student_object=[]
        if len (students_list)==0:
            student_object=['No results found']
        else:
            student_object.append(create_students_objects(students_list))
        teachers_list=crud.read_like('*', 'teachers', 'name', request.form['search'].title())
        teacher_object=[]
        if len(teachers_list)==0:
            teacher_object=['No results found']
        if len(teachers_list)>=1:
            teacher_object.append(create_students_objects(teachers_list)) 
        return render_template('search.html', title=title ,course_object=course_object, student_object=student_object, teacher_object=teacher_object)
    else:
        return render_template('search.html', title='', course_object='')

@app.route('/course_student')
def course_student():
    students=crud.read_all('students')
    return render_template('course_student.html', students=create_students_objects(students))

@app.route('/registration/<student_id>',  methods=['GET', 'POST'])
def registration(student_id):
    if request.method=='POST':
        course_id=request.form['course_id']
        crud.create('students_courses', 'student_id, course_id', f"'{student_id}', '{course_id}'")
        return render_template('course_student.html')
    student=crud.read_if('*',"students","id", student_id)
    student_object=create_students_objects(student)
    courses=crud.read_all('courses')
    return render_template('registration.html', student=student_object, courses=create_courses_objects(courses))

@app.route('/teachers')
def show_teachers():
    teachers=crud.read_all('teachers')
    return render_template('teachers.html', teachers=create_teachers_objects(teachers))

@app.route('/teacher/<teacher_id>',  methods=['GET', 'POST'])
def teacher_info(teacher_id):
    if request.method=='POST':        
        new_grade=request.form['new_grade']
        student_id=request.form['student_id']
        course_id=request.form['course_id']
        crud.change_grade(new_grade, student_id, course_id)
    teacher=crud.read_if('*',"teachers","id", teacher_id)
    teacher_object=create_students_objects(teacher)
    teacher_courses=crud.read_if('*', 'courses', 'teacher_id', teacher_id)
    teacher_course_object=create_courses_objects(teacher_courses)
    students_courses=[]
    for course in teacher_course_object:    
        students=[]
        students_info=crud.read_if('student_id, grade', 'students_courses', 'course_id', course.tid )
        students.append(course.name)
        for s in students_info:
             student=namedtuple('C_S', [ 'student_id','student_name','course_id','grade'])
             student.student_id=s[0]
             student.student_name=crud.student_name(s[0])
             student.course_id=course.tid
             student.grade=s[1]
             students.append(student)
        students_courses.append(students)
    return render_template('teachers.html', teacher=teacher_object, teacher_courses=teacher_course_object, students_courses=students_courses)

@app.route('/attendance', methods=['GET','POST'])
def attendance():
    form=['create form']
    courses=crud.read_all('courses')
    courses=create_courses_objects(courses)
    students_search=crud.read_all('students')
    students_search=create_students_objects(students_search)
    if request.method=='POST':
        if 'form1' in request.form:
            courses_list=crud.read_like('*', 'courses', 'name', request.form['search1'].title())
            if len(courses_list)<1:
                return render_template('attendance.html', jinja='', dates_dict='' ,form=form ,result1='No such course was found')
            if len(courses_list)>=1:
                course_object=create_courses_objects(courses_list)
                return render_template('attendance.html',jinja='', dates_dict='', form=form ,courses_objects=course_object, students_search=students_search)
        elif 'form2' in request.form:
            students_search_list=crud.read_like('*', 'students', 'name', request.form['search2'].title())
            if len(students_search_list)<1:
                return render_template('attendance.html', jinja='', dates_dict='' ,form=form ,result1='No such studentd was found')
            if len(students_search_list)>=1:
                student_object=create_students_objects(students_search_list)
                return render_template('attendance.html',jinja='', dates_dict='', form=form ,students_objects=student_object, courses=courses)
    return render_template('attendance.html',jinja='', dates_dict='', form=form ,courses=courses, students_search=students_search)

@app.route('/attendance/<course_id>', methods=['get', 'post'])
def course_attendance(course_id):
    jinja={}
    jinja['course_id']=course_id
    jinja['chose_date']=['Choose different date:']
    current_date=datetime.date.today()
    current_date=current_date.strftime("%d/%m/%Y")
    current_date=current_date.replace('/','-')
    jinja['current_date']=f"Date: {current_date}"
    course_name=crud.course_name(course_id)
    jinja['course_name']=f"Attendance for {course_name}"
    if request.method=='GET':
        students_ids=crud.read_if('student_id', 'students_courses', 'course_id', course_id)
        if len(students_ids)==0:
            return render_template ('attendance.html' ,jinja='', dates_dict='', note=f"There are no students enrolled to {course_name}" )
        else:
            answer_attend=crud.read_two_if('date', 'students_attendance', 'course_id', course_id, 'date', current_date)
            if len(answer_attend)==0:    
                for s_id in students_ids:
                    crud.create('students_attendance', 'student_id, course_id, date', f"'{s_id[0]}', '{course_id}', '{current_date}'")
            else:
                students_ids_atten=crud.read_two_if('student_id','students_attendance','course_id', course_id, 'date', current_date)
                if len(students_ids)==len(students_ids_atten):
                    pass
                else:
                    for s_i in students_ids:    
                            if s_i in students_ids_atten:
                                pass
                            else:
                                crud.create('students_attendance', 'student_id, course_id, date', f"'{s_i[0]}', '{course_id}', '{current_date}'")                
            dates=crud.read_if('DISTINCT date', 'students_attendance', 'course_id', course_id)
            jinja['dates']=dates
            course_atten=crud.read_two_if('student_id, attendance','students_attendance','course_id', course_id, 'date', current_date)
            students_attend=[]
            for s_a in course_atten:
                student_a=namedtuple('S_Attend',['id','name','attend'])
                student_a.id=s_a[0]
                student_a.name=f"{crud.student_name(s_a[0])}:"
                student_a.attend={}
                if s_a[1]=='yes':
                    student_a.attend['yes']='checked'
                    student_a.attend['no']=''
                else:
                    student_a.attend['yes']=''
                    student_a.attend['no']='checked'
                students_attend.append(student_a)
            return render_template ('attendance.html', students_attend=students_attend, jinja=jinja, dates_dict='')
    else:   
        if request.method=='POST':
            answer=request.form['attendance']
            student_id=request.form['student_id']
            crud.update_three_if('students_attendance', 'attendance',f"'{answer}'", 'student_id', student_id, 'course_id', course_id, 'date', current_date)    
            return redirect(url_for('course_attendance',course_id=course_id))

@app.route('/attendance_chosen_date/<course_id>', methods=['get', 'post'])
def attendance_chosen_date(course_id):
    if request.method=='GET':
        jinja={}
        jinja['course_id']=course_id
        jinja['chose_date']=['Choose different date:']
        current_date=datetime.date.today()
        current_date=current_date.strftime("%d/%m/%Y")
        current_date=current_date.replace('/','-')
        jinja['current_date']=f"Date: {current_date}"
        course_name=crud.course_name(course_id)
        jinja['course_name']=f"Attendance for {course_name}"
        dates=crud.read_if('DISTINCT date', 'students_attendance', 'course_id', course_id)
        jinja['dates']=dates
        course_atten=crud.read_two_if('student_id, attendance','students_attendance','course_id', course_id, 'date', current_date)
        students_attend=[]
        for s_a in course_atten:
            student_a=namedtuple('S_Attend',['id','name','attend'])
            student_a.id=s_a[0]
            student_a.name=f"{crud.student_name(s_a[0])}:"
            student_a.attend={}
            if s_a[1]=='yes':
                student_a.attend['yes']='checked'
                student_a.attend['no']=''
            else:
                student_a.attend['yes']=''
                student_a.attend['no']='checked'
            students_attend.append(student_a)
        dates_dict={}
        dates_dict['chosen_date']=f"{request.args['chosen_date']} attendance list:"
        dates_dict['yes_title']='Students who ATTENDED the class:'
        dates_dict['no_title']='Students who DID NOT attend the class:'
        ids_attend=crud.read_three_if('student_id', 'students_attendance', 'course_id', course_id, 'date', request.args['chosen_date'], 'attendance', 'yes' )
        if len(ids_attend)==0:
             dates_dict['attend_date']=['No students found',]
        else:
            names_attend=[]
            for ids in ids_attend:
                name=crud.student_name(ids[0])
                names_attend.append(name)    
            dates_dict['attend_date']=names_attend
        ids_not_attend=crud.read_three_if('student_id', 'students_attendance', 'course_id', course_id, 'date', request.args['chosen_date'], 'attendance', 'no' )
        if len(ids_not_attend)==0:
             dates_dict['not_attend']=['No students found']
        else:
            names_not_attend=[]
            for ids in ids_not_attend:
                name=crud.student_name(ids[0])
                names_not_attend.append(name)            
            dates_dict['not_attend']=names_not_attend
        return  render_template ('attendance.html', students_attend=students_attend, jinja=jinja, dates_dict=dates_dict)
    else:
        return redirect(url_for('course_attendance',course_id=course_id))

        