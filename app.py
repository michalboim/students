from flask import Flask, redirect, url_for, render_template, request, session
app = Flask(__name__)
from setup_db import query
import classes
import crud
from functions import create_courses_objects, create_students_objects, create_teachers_objects, courses_teachers, authenticate
from collections import namedtuple
import datetime

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

def check_log():
    log_result={}
    if "name" in session:
        link='/logout'
        log='Logout'
        log_result['link']=link
        log_result['log']=log        
        return log_result
    else:
        link='/login'
        log='Login'
        log_result['link']=link
        log_result['log']=log
        return log_result

def chek_admin():
    if "role" in session:
        if session['role']=='admin':
            admin_dict={}
            admin_dict['id']=session['id']
            admin_dict['link']=f"/administrator/{session['id']}"
            admin_dict['word']='Administrator'
            return admin_dict
        else:
            admin_dict=''
            return admin_dict

@app.route('/')
def home():
    log=check_log()
    admin_dict=chek_admin()
    return render_template('home.html', log=log, admin_dict=admin_dict)

@app.route('/home')
def go_home():
    return redirect(url_for('home'))

@app.route('/search')
def search():
    log=check_log()
    admin_dict=chek_admin()
    title=['Courses Resulte:', 'Students Resulte:', 'Teachers Resulte:']
    courses_list=crud.read_like('*', 'courses', 'name', request.args['search'].title())
    course_object=[]
    if len(courses_list)==0:
        course_object=['No results found']
    else:
        course_object.append(create_courses_objects(courses_list))
    students_list=crud.read_like('*', 'students', 'name', request.args['search'].title())
    student_object=[]
    if len (students_list)==0:
        student_object=['No results found']
    else:
        student_object.append(create_students_objects(students_list))
    teachers_list=crud.read_like('*', 'teachers', 'name', request.args['search'].title())
    teacher_object=[]
    if len(teachers_list)==0:
        teacher_object=['No results found']
    if len(teachers_list)>=1:
        teacher_object.append(create_students_objects(teachers_list)) 
    return render_template('search.html', log=log, admin_dict=admin_dict, title=title ,course_object=course_object, student_object=student_object, teacher_object=teacher_object)

@app.route('/login', methods=['get','post'])
def login():
    log=check_log()
    admin_dict=chek_admin()
    if request.method=='POST':
        auth=authenticate(request.form['email'], request.form['password'])
        if auth=='student':
            session['role']='student'
            session['id']=crud.student_id(request.form['email'])
            session['name']=crud.student_name(session['id'])
            return redirect(url_for('student_profile', student_id=session['id']))
        if auth=='teacher':
            session['role']='teacher'
            session['id']=crud.teacher_id(request.form['email'])
            session['name']=crud.teacher_name(session['id'])
            return redirect(url_for('teacher_profile', teacher_id=session['id']))
        if auth=='admin':
            session['role']='admin'
            session['id']=crud.admin_id(request.form['email'])
            session['name']=crud.admin_name(session['id'])
            return redirect(url_for('administrator', admin_id=session['id']))
        else:
            return render_template('login.html', log=log, admin_dict=admin_dict, note='Incorrect username or password' )
    return render_template('login.html', log=log, admin_dict=admin_dict)

@app.route('/logout')
def logout():
   session.pop('name','none') 
   session.pop('id','none') 
   session.pop('role','none') 
   return redirect(url_for('home'))

@app.route('/administrator/<admin_id>' )
def administrator(admin_id):
    log=check_log()
    admin_dict=chek_admin()
    name=crud.admin_name(admin_id)
    return render_template ('administrator.html',log=log, admin_dict=admin_dict, name=f"Hello {name} what do you whant to do?")

@app.route('/admin_courses',methods=['GET', 'POST'])
def admin_courses():
    log=check_log()
    admin_dict=chek_admin()
    form=['create']
    if request.method=='POST':
        courses_list=crud.read_like('*', 'courses', 'name', request.form['search'].title())
        if len(courses_list)==0:
            return render_template('admin_courses.html',log=log, admin_dict=admin_dict, course_dict='', form=form, result='No such course was found')
        else:
            courses_object=create_courses_objects(courses_list)
            for course in courses_object:
                course.teacher_id=crud.teacher_name(course.teacher_id)  
            return render_template('admin_courses.html',log=log, admin_dict=admin_dict, course_dict='', form=form, courses_objects=courses_object)
    return render_template('admin_courses.html', log=log, admin_dict=admin_dict, course_dict='', form=form, courses_teachers=courses_teachers())

@app.route('/course_info/<course_id>')
def course_info(course_id):
    log=check_log()
    admin_dict=chek_admin()
    course_dict={}
    course_dict['students_title']='Students: '
    students=crud.read_if('student_id','students_courses', 'course_id', course_id)
    if len(students)==0:
        course_dict['students']=''
        course_dict['no_students']='There are no students enrolled to the course'
    else:
        students_name=[[student[0],crud.student_name(student[0])] for student in students]
        course_dict['students']=students_name
        course_dict['no_students']=''
    course=crud.read_if('*',"courses","id", course_id)
    course_object=create_courses_objects(course)
    for course in course_object:
        course.teacher_id=[course.teacher_id, crud.teacher_name(course.teacher_id)]
    return render_template ('admin_courses.html', log=log, admin_dict=admin_dict, course_object=course_object, course_dict=course_dict )

@app.route('/add_course', methods=['GET','POST'])
def add_course():
    log=check_log()
    admin_dict=chek_admin()
    if request.method=='POST':          
        crud.create('courses', 'name, description, teacher_id, start, day, time', f" '{request.form['new_name'].title()}', '{request.form['new_description']}', '{request.form['teacher_tid']}', '{request.form['new_start']}', '{request.form['new_day']}', '{request.form['new_time']}' ")
        return redirect(url_for('admin_course'))
    else:
        return render_template('add_course.html', log=log, admin_dict=admin_dict, teachers_object=create_teachers_objects(crud.read_all('teachers')))

@app.route('/update_courses', methods=['GET', 'POST'])
def update_courses():
    log=check_log()
    admin_dict=chek_admin()
    form=['create']
    if request.method=='POST':
        courses_list=crud.read_like('*', 'courses', 'name', request.form['search'].title())
        if len(courses_list)==0:
            return render_template('update_courses.html', log=log, admin_dict=admin_dict, form=form, chosen_course='', result='No such course was found')
        else:
            course_object=create_courses_objects(courses_list)  
            return render_template('update_courses.html', log=log, admin_dict=admin_dict, form=form, chosen_course='',teacher_info='', courses_objects=course_object)
    else:    
        return render_template('update_courses.html', log=log, admin_dict=admin_dict, form=form, chosen_course='',teacher_info='', courses=courses_teachers())

@app.route('/chosen_course/<course_id>', methods=['GET', 'POST'])
def chosen_course_update(course_id):
    log=check_log()
    admin_dict=chek_admin()
    form2=['create']
    chosen_course={}
    chosen_course['title_chosen']='Edit the Changes:'
    course=crud.read_if('*',"courses","id", course_id)
    course_info=create_courses_objects(course)
    for c in course_info:
        c.start=crud.read_if('start',"courses","id", course_id)[0]
    chosen_course['course_info']=course_info
    chosen_course['teachers']=create_teachers_objects(crud.read_all('teachers'))
    teacher_info=[]
    for course in course_info:
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
        return render_template('update_courses.html', log=log, admin_dict=admin_dict, form='', form2=form2 ,chosen_course=chosen_course, teacher_info=teacher_info) 

@app.route('/course_registration', methods=['GET', 'POST'])
def course_registrationt():
    log=check_log()
    admin_dict=chek_admin()
    form=['create']
    if request.method=='POST':
        courses_list=crud.read_like('*', 'courses', 'name', request.form['search'].title())
        if len(courses_list)==0:
            return render_template('course_registration.html', log=log, admin_dict=admin_dict, form=form, course_dict='', result1='No such course was found')
        else:
            course_object=create_students_objects(courses_list) 
            return render_template('course_registration.html', log=log, admin_dict=admin_dict, form=form, course_dict='', course_objects=course_object)
    else:    
        return render_template('course_registration.html', log=log, admin_dict=admin_dict, form=form, course_dict='', courses=create_courses_objects(crud.read_all('courses')))

@app.route('/course_id_registration/<course_id>',  methods=['GET', 'POST'])
def course_id_registration(course_id):
    log=check_log()
    admin_dict=chek_admin()
    form=['create']
    course_dict={}
    course_dict['form']=['create']
    students=create_students_objects(crud.read_all('students'))
    course_dict['students']=students
    course_dict['course_title']=f'Choose student for {crud.course_name(course_id)}:'
    if request.method=='POST':
        if 'form1' in request.form:
            return redirect(url_for('course_registrationt'))
        if 'form2' in request.form:
            students_list=crud.read_like('*', 'students', 'name', request.form['search'].title())
            if len(students_list)==0:
                return render_template('course_registration.html', log=log, admin_dict=admin_dict, form=form, course_dict=course_dict, result2='No such student was found')
            else:
                students_object=create_students_objects(students_list)
                course_dict['students']=students_object
                return render_template('course_registration.html', log=log, admin_dict=admin_dict, form=form, course_dict=course_dict)
        if 'form3' in request.form:
            students_ids=request.form.getlist('student_id')
            for student in students_ids:
                try:
                    crud.create('students_courses', 'student_id, course_id', f'{student}, {course_id}')
                except:
                    pass
            return redirect(url_for('course_registrationt'))
    return render_template('course_registration.html', log=log, admin_dict=admin_dict, form=form, course_dict=course_dict)

@app.route('/admin_students', methods=['GET', 'POST'])
def admin_students():
    log=check_log()
    admin_dict=chek_admin()
    if request.method=='POST':
        students=crud.read_like('*', 'students', 'name', request.form['search'].title())
        if len(students)==0:
            return render_template('admin_students.html', log=log, admin_dict=admin_dict, result='No such studentd was found')
        else:
            student_object=create_students_objects(students)
            return render_template('admin_students.html', log=log, admin_dict=admin_dict, students_objects=student_object)
    return render_template('admin_students.html', log=log, admin_dict=admin_dict, students=create_students_objects(crud.read_all('students')))

@app.route('/add_student', methods=['POST','GET'])
def add_student():
    log=check_log()
    admin_dict=chek_admin()
    if request.method=='POST':
        num_students=len(crud.read_all('students'))
        try:
            crud.create('students', 'name, email, phone', f"'{request.form['new_name'].title()}','{request.form['new_email']}','{request.form['new_phone']}'")
            crud.create('users', 'student_user, role', f"'{request.form['new_email']}', 'student'" )
        except:
            return render_template('add_student.html', log=log, admin_dict=admin_dict, note="Email or Mobile number already exists")
        new_num=len(crud.read_all('students'))
        if new_num>num_students:
            return redirect(url_for("admin_students"))
        else:
            return render_template('add_student.html', log=log, admin_dict=admin_dict, note="A mistake occurred please try again")
    else:
        return render_template('add_student.html', log=log, admin_dict=admin_dict)

@app.route('/update_students', methods=['GET', 'POST'])
def update_students():
    log=check_log()
    admin_dict=chek_admin()
    form=['create']
    if request.method=='POST':
        students_list=crud.read_like('*', 'students', 'name', request.form['search'].title())
        if len(students_list)==0:
            return render_template('update_students.html', log=log, admin_dict=admin_dict, form=form, result='No such student was found')
        else:
            student_object=create_students_objects(students_list) 
            return render_template('update_students.html', log=log, admin_dict=admin_dict, form=form, student_objects=student_object)
    else:    
        return render_template('update_students.html', log=log, admin_dict=admin_dict, form=form, students=create_students_objects(crud.read_all('students')))

@app.route('/chosen_student/<student_id>', methods=['GET', 'POST'])
def chosen_student_update(student_id):
    log=check_log()
    admin_dict=chek_admin()
    student_info=crud.read_if('*',"students","id", student_id)
    student_object=create_students_objects(student_info)
    if request.method=='POST':
        name=request.form['name'].title()
        email=request.form['email']
        phone=request.form['phone']
        try:
            crud.update_if('students', 'name, email, phone', f"'{name}', '{email}', '{phone}'",'id', student_id)
        except:
          return render_template('update_students.html', log=log, admin_dict=admin_dict, title='Edit the Changes:', student_object=student_object, note="Email or Mobile number already exists")  
        return redirect(url_for('admin_students'))
    else:
        return render_template('update_students.html', log=log, admin_dict=admin_dict, title='Edit the Changes:', student_object=student_object) 

@app.route('/student_registration', methods=['GET', 'POST'])
def student_registrationt():
    log=check_log()
    admin_dict=chek_admin()
    form=['create']
    if request.method=='POST':
        students_list=crud.read_like('*', 'students', 'name', request.form['search'].title())
        if len(students_list)==0:
            return render_template('student_registration.html', log=log, admin_dict=admin_dict, form=form, student_dict='', result1='No such student was found')
        else:
            student_object=create_students_objects(students_list) 
            return render_template('student_registration.html', log=log, admin_dict=admin_dict, form=form, student_dict='', student_objects=student_object)
    else:    
        return render_template('student_registration.html', log=log, admin_dict=admin_dict, form=form, student_dict='', students=create_students_objects(crud.read_all('students')))

@app.route('/student_id_registration/<student_id>',  methods=['GET', 'POST'])
def student_id_registration(student_id):
    log=check_log()
    admin_dict=chek_admin()
    form=['create']
    student_dict={}
    student_dict['form']=['create']
    courses=create_courses_objects(crud.read_all('courses'))
    student_dict['courses']=courses
    student_dict['student_title']=f'Choose course for {crud.student_name(student_id)}:'
    if request.method=='POST':
        if 'form1' in request.form:
            return redirect(url_for('student_registrationt'))
        if 'form2' in request.form:
            courses_list=crud.read_like('*', 'courses', 'name', request.form['search'].title())
            if len(courses_list)==0:
                return render_template('student_registration.html', log=log, admin_dict=admin_dict, form=form, student_dict=student_dict, result2='No such course was found')
            else:
                courses_object=create_courses_objects(courses_list)
                student_dict['courses']=courses_object
                return render_template('student_registration.html', log=log, admin_dict=admin_dict, form=form, student_dict=student_dict)
        if 'form3' in request.form:
            courses_ids=request.form.getlist('course_id')
            for course in courses_ids:
                try:
                    crud.create('students_courses', 'student_id, course_id', f'{student_id}, {course}')
                except:
                    pass
    return render_template('student_registration.html', log=log, admin_dict=admin_dict, form=form, student_dict=student_dict)

@app.route('/admin_teachers',methods=['GET', 'POST'])
def admin_teachers():
    log=check_log()
    admin_dict=chek_admin()
    if request.method=='POST':
        teachers=crud.read_like('*', 'teachers', 'name', request.form['search'].title())
        if len(teachers)==0:
            return render_template('admin_teachers.html', log=log, admin_dict=admin_dict, result='No such teacher was found')
        else:
            teachers_object=create_students_objects(teachers)
            return render_template('admin_teachers.html', log=log, admin_dict=admin_dict, teachers_objects=teachers_object)
    return render_template('admin_teachers.html', log=log, admin_dict=admin_dict, teachers_objects=create_teachers_objects(crud.read_all('teachers')))

@app.route('/add_teacher', methods=['POST','GET'])
def add_teacher():
    log=check_log()
    admin_dict=chek_admin()
    if request.method=='POST':
        num_teachers=len(crud.read_all('teachers'))
        try:
            crud.create('teachers', 'name, email, phone', f"'{request.form['new_name'].title()}','{request.form['new_email']}','{request.form['new_phone']}'")
            crud.create('users', 'teacher_user, role', f"'{request.form['new_email']}', 'teacher'" )
        except:
            return render_template('add_teacher.html', log=log, admin_dict=admin_dict, note="Email or Mobile number already exists")
        new_num=len(crud.read_all('teachers'))
        if new_num>num_teachers:
            return redirect(url_for("admin_teachers"))
        else:
            return render_template('add_teacher.html', log=log, admin_dict=admin_dict, note="A mistake occurred please try again")
    else:
        return render_template('add_teacher.html', log=log, admin_dict=admin_dict)

@app.route('/update_teachers', methods=['GET', 'POST'])
def update_teachers():
    log=check_log()
    admin_dict=chek_admin()
    form1=['create']
    if request.method=='POST':
        teachers_list=crud.read_like('*', 'teachers', 'name', request.form['search'].title())
        if len(teachers_list)==0:
            return render_template('update_teachers.html', log=log, admin_dict=admin_dict, form1=form1, result='No such teacher was found')
        else:
            teacher_object=create_teachers_objects(teachers_list)   
            return render_template('update_teachers.html', log=log, admin_dict=admin_dict, form1=form1, teacher_objects=teacher_object)
    else:    
        return render_template('update_teachers.html', log=log, admin_dict=admin_dict, form1=form1, teachers=create_teachers_objects(crud.read_all('teachers')))

@app.route('/chosen_teacher/<teacher_id>', methods=['GET', 'POST'])
def chosen_teacher_update(teacher_id):
    log=check_log()
    admin_dict=chek_admin()
    teacher_info=crud.read_if('*',"teachers","id", teacher_id)
    teacher_object=create_teachers_objects(teacher_info) 
    if request.method=='POST':
        name=request.form['name'].title()
        email=request.form['email']
        phone=request.form['phone']
        try:
            crud.update_if('teachers', 'name, email, phone', f"'{name}', '{email}', '{phone}'",'id', teacher_id)
        except:
            return render_template('update_teachers.html', log=log, admin_dict=admin_dict, title='Edit the Changes:' ,teacher_object=teacher_object, note="Email or Mobile number already exists")
        return redirect(url_for('admin_teachers'))
    else:
        return render_template('update_teachers.html', log=log, admin_dict=admin_dict, title='Edit the Changes:' ,teacher_object=teacher_object) 

@app.route('/teachers')
def show_teachers():
    log=check_log()
    admin_dict=chek_admin()
    teachers=crud.read_all('teachers')
    return render_template('teachers.html', log=log, admin_dict=admin_dict, teachers=create_teachers_objects(teachers))

@app.route('/teacher/<teacher_id>',  methods=['GET', 'POST'])
def teacher_info(teacher_id):
    log=check_log()
    admin_dict=chek_admin()
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
    return render_template('teachers.html', log=log, admin_dict=admin_dict, teacher=teacher_object, teacher_courses=teacher_course_object, students_courses=students_courses)

@app.route('/attendance', methods=['GET','POST'])
def attendance():
    log=check_log()
    admin_dict=chek_admin()
    form=['create form']
    courses=crud.read_all('courses')
    courses=create_courses_objects(courses)
    students_search=crud.read_all('students')
    students_search=create_students_objects(students_search)
    if request.method=='POST':
        if 'form1' in request.form:
            courses_list=crud.read_like('*', 'courses', 'name', request.form['search1'].title())
            if len(courses_list)==0:
                return render_template('attendance.html', log=log, admin_dict=admin_dict, jinja='', dates_dict='',course_dict='', form=form, course_dates_dict='' ,result1='No such course was found', students_search=students_search)
            else:
                course_object=create_courses_objects(courses_list)
                return render_template('attendance.html', log=log, admin_dict=admin_dict, jinja='', dates_dict='',course_dict='', course_dates_dict='', form=form ,courses_objects=course_object, students_search=students_search)
        elif 'form2' in request.form:
            students_search_list=crud.read_like('*', 'students', 'name', request.form['search2'].title())
            if len(students_search_list)==0:
                return render_template('attendance.html', log=log, admin_dict=admin_dict, jinja='', dates_dict='', course_dict='', course_dates_dict='', form=form ,result2='No such studentd was found', courses=courses)
            else:
                student_object=create_students_objects(students_search_list)
                return render_template('attendance.html', log=log, admin_dict=admin_dict, jinja='', dates_dict='', course_dict='', course_dates_dict='', form=form ,students_objects=student_object, courses=courses)
    return render_template('attendance.html', log=log, admin_dict=admin_dict, jinja='', dates_dict='', course_dict='', course_dates_dict='', form=form ,courses=courses, students_search=students_search)

@app.route('/attendance/<course_id>', methods=['get', 'post'])
def course_attendance(course_id):
    log=check_log()
    admin_dict=chek_admin()
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
            return render_template ('attendance.html', log=log, admin_dict=admin_dict, jinja='', dates_dict='', course_dict='',course_dates_dict='' , note1=f"There are no students enrolled to {course_name}" )
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
            return render_template ('attendance.html', log=log, admin_dict=admin_dict, students_attend=students_attend, jinja=jinja, dates_dict='', course_dict='', course_dates_dict='')
    else:   
        if request.method=='POST':
            answer=request.form['attendance']
            student_id=request.form['student_id']
            crud.update_three_if('students_attendance', 'attendance',f"'{answer}'", 'student_id', student_id, 'course_id', course_id, 'date', current_date)    
            return redirect(url_for('course_attendance',course_id=course_id))

@app.route('/attendance_chosen_date/<course_id>', methods=['get', 'post'])
def attendance_chosen_date(course_id):
    log=check_log()
    admin_dict=chek_admin()
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
        return  render_template ('attendance.html', log=log, admin_dict=admin_dict, students_attend=students_attend, jinja=jinja, dates_dict=dates_dict, course_dict='', course_dates_dict='')
    else:
        return redirect(url_for('course_attendance',course_id=course_id))

@app.route('/students_attendance/<student_id>', methods=['get', 'post'])
def students_attendance(student_id):
    log=check_log()
    admin_dict=chek_admin()
    form=['create form']
    courses=crud.read_all('courses')
    courses=create_courses_objects(courses)
    student_courses=crud.read_if('course_id', 'students_courses', 'student_id', student_id)
    course_dict={}
    course_dict['student_name']=f"{crud.student_name(student_id)} courses:"
    course_dict['form']=['create form']
    course_dates_dict={}
    course_dates_dict['form']=['create form']
    courses_ids=[]
    for c in student_courses:
        name=crud.course_name(c[0])
        course_name=[c[0],name]
        courses_ids.append(course_name)
    if len(courses_ids)==0:
        return render_template('attendance.html', log=log, admin_dict=admin_dict, jinja='', form='', dates_dict='' , course_dict='', course_dates_dict='', note2=f"{crud.student_name(student_id)} student is not enrolled to any of the courses" )
    else:
        course_dict['course_list']=courses_ids
    if request.method=='POST':
        if 'form2' in request.form or 'form1' in request.form:
            return redirect(url_for('attendance'))
        if 'form3' in request.form:            
            chosen_course_id=request.form['course_select']
            course_dates=crud.read_if('DISTINCT date', 'students_attendance', 'course_id', chosen_course_id)
            course_dates_dict['course_id']=chosen_course_id
            course_dates_dict['course_name']=f'{crud.course_name(chosen_course_id)} dates:'
            course_dates_dict['course_dates']=course_dates
            if len(course_dates)==0:
                return render_template('attendance.html', log=log, admin_dict=admin_dict, jinja='', form='', dates_dict='', course_dates_dict='' , course_dict='', note3=f"{crud.course_name(chosen_course_id)} course did not have lesson found in the system" )
            else:       
                return  render_template('attendance.html', log=log, admin_dict=admin_dict, jinja='', form=form, courses=courses, dates_dict='', course_dates_dict=course_dates_dict , course_dict=course_dict)
        elif 'form4' in request.form:
            course_id=request.form['chosen_course_id']
            course_dates_dict['course_id']=course_id
            course_dates_dict['course_name']=f'{crud.course_name(course_id)} dates:'
            course_dates_dict['course_dates']=crud.read_if('DISTINCT date', 'students_attendance', 'course_id', course_id)
            date=request.form['date_select']
            student_attend=crud.read_three_if('attendance','students_attendance', 'student_id', student_id, 'course_id', course_id, 'date', date)
            if student_attend[0][0]=='yes':
                answer=f'The student attended in {date} lesson'
            elif student_attend[0][0]=='no':
                answer=f'The student did not attend in {date} lesson'
            else:
                answer=f"There is no reference to the student's participation in {date} lesson in the system"
            return  render_template('attendance.html', log=log, admin_dict=admin_dict, jinja='', form=form, dates_dict='' ,courses=courses, course_dict=course_dict, course_dates_dict=course_dates_dict, answer=answer) 
    else:
        return render_template('attendance.html',log=log, admin_dict=admin_dict, jinja='', form=form, dates_dict='' ,courses=courses, course_dict=course_dict, course_dates_dict='' )  
    
@app.route('/messages')
def messages():
    all_messages=crud.read_all('messages')
    messages_list=[message[0] for message in all_messages]
    return messages_list

@app.route('/student_profile/<student_id>')
def student_profile(student_id):
    log=check_log()
    admin_dict=chek_admin()
    return render_template('home.html', log=log, admin_dict=admin_dict, hello= f"hello {crud.student_name(student_id)}") 

@app.route('/teacher_profile/<teacher_id>')
def teacher_profile(teacher_id):
    log=check_log()
    admin_dict=chek_admin()
    return render_template('home.html', log=log, admin_dict=admin_dict, hello= f"hello {crud.student_name(teacher_id)}") 