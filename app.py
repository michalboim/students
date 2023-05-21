from flask import Flask, redirect, url_for, render_template, request, session, flash
import crud
from functions import create_courses_objects, create_students_objects, create_teachers_objects, create_admins_objects, authenticate, allowed_file
from collections import namedtuple
import datetime, statistics
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = './static/images'

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# session functions:
def check_log(): #check if user is loged in or not
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

def info_user(): # get user info
    if "role" in session:
        info={}
        if session['role']=='admin':
            info['id']=session['id']
            info['link']=f"/administrator/{session['id']}"
            info['word']='Administrator'
            info['hello']=f"Hello {crud.admin_name(session['id'])}- what do you want to do?"
        if session['role']=='teacher':
            info['id']=session['id']
            info['link']=f"/teacher_profile/{session['id']}"
            info['word']=f"Welcome {crud.teacher_name(session['id'])}"
            info['class']='user_hello'
        if session['role']=='student':
            info['id']=session['id']
            info['link']=f"/student_profile/{session['id']}"
            info['word']=f"Welcome {crud.student_name(session['id'])}"
            info['class']='user_hello'
        return info

# react routes:
@app.route('/users_details')
def users_details():# get user datails for react
    details={}
    if "role" in session:
        details['role']=session['role']
        details['id']=session['id']
        details['name']=session['name']
        if details['role']=='student' or details['role']=='teacher':
            e_p=crud.read_if('email, phone', f"{session['role']}s", 'id', session['id'])
            details['email']=e_p[0][0]
            if type(e_p[0][1])!=str or e_p[0][1]=='':
                details['phone']='Phone still not updated'
            else:
                details['phone']=e_p[0][1]
        if details['role']=='teacher':
            courses=crud.read_if('id, name', 'courses', 'teacher_id', session['id'])
            if len(courses)==0:
                details['no_courses']='You were not assigned to teach in any of the courses'
                details['courses']=[]
            else:
                details['courses']=courses
        if details['role']=='student':
            courses=crud.read_if('course_id, grade', 'students_courses', 'student_id', session['id'])
            if len(courses)==0:
                details['no_courses']='You are not enrolled to eny fo the courses'
                details['courses']=[]
            else:
                details['courses']=[]
                for course in courses:
                    info={}
                    info['course_id']=course[0]
                    info['course_name']=crud.course_name(course[0])
                    info['course_grade']=f'Your grade is: {course[1]}'
                    course_attend=crud.read_two_if('attendance','students_attendance', 'student_id', session['id'], 'course_id', course[0])
                    if len(course_attend)==0:
                        info['course_attend']='There is no record in the system for your attendance in this course'
                    else:
                        average_attend=[]
                        average_not_attend=[]
                        average_unknown=[]
                        for a in course_attend:
                            if a[0]=='yes':
                                average_attend.append(a)
                            if a[0]=='no':
                                average_not_attend.append(a)
                            if a[0]=='unknown':
                                average_unknown.append(a)
                        try:
                            info['course_attend']=f"Your Average attendance: {round(len(average_attend)*100/(len(average_attend)+len(average_not_attend)))}%"
                        except:
                            info['course_attend']='No record was found in the system for your attendance or non-attendance'
                    details['courses'].append(info)
    return details

@app.route('/courses_details')
def courses(): # get all courses datails for react
    courses_ids=create_courses_objects(crud.read_all('courses'))
    courses_list=[]
    for course in courses_ids:
        course_dict={}
        course_dict['id']=course.tid
        course_dict['course_name']=f'{course.name} Information:'
        course_dict['desc']=f"Description: {course.description}"
        if course.teacher_id[0]=='':
            course_dict['teacher_title']='Teacher not yet assigned'
        else:
            info_teacher=crud.read_if('*', 'teachers', 'id', course.teacher_id[0])
            for t in create_teachers_objects(info_teacher):
                course_dict['teacher_title']='Teacher information:'
                course_dict['teacher_id']=t.tid
                course_dict['teacher_name']=f'{t.name},'
                course_dict['teacher_email']=f'{t.email},'
                if t.phone=='Still not updated':
                    course_dict['teacher_phone']='Phone still not updated'
                else:
                    course_dict['teacher_phone']=t.phone
        course_dict['start']=f'Start: {course.start}'
        course_dict['day']=f'Day: {course.day}'
        course_dict['time']=f'Time: {course.time}'
        course_dict['line']='|'        
        course_dict['class']=['students_grid_title','students_grid_email','students_grid_phone','students_grid_grade']
        course_messages=crud.read_two_if('message_id', 'messages_courses', 'course_id', course.tid, 'status', 'Publish')
        if len(course_messages)==0:
            course_dict['no_messages']=f'There are no messages to {crud.course_name(course.tid)} course'
            course_dict['messages']=[]
        else:
            course_dict['messages_title']=f'{crud.course_name(course.tid)} messages:'
            course_dict['messages']=[]
            for message in course_messages:
                message_info={}
                mes=crud.read_if('message, time', 'messages', 'id', message[0])
                message_info['text']=mes[0][0]
                message_info['time']=mes[0][1]
                course_dict['messages'].append(message_info)
        students_ids=crud.read_if('student_id, grade', 'students_courses', 'course_id', course.tid)
        if len(students_ids)==0:
            course_dict['no_students']=f'There are no students enrolled to {crud.course_name(course.tid)}'
            course_dict['students']=[]
            course_dict['class']=[]
            course_dict['average_attend_title']=''
            course_dict['mean_grades_title']=''
        else:
            course_dict['title_name']='Name'
            course_dict['title_email']='Email'
            course_dict['title_phone']='Phone'
            course_dict['title_grade']='Grade'
            course_dict['title_grade']='Grade'
            course_dict['average_attend_title']=f'{crud.course_name(course.tid)} Attendance:'
            course_dict['mean_grades_title']=f'{crud.course_name(course.tid)} Grades:'
            course_dict['students_title']=f'Students who are enrolled to {crud.course_name(course.tid)}:'
            course_dict['students']=[]
            grades=[]
            for student in students_ids:
                info=create_students_objects(crud.read_if('*','students', 'id', student[0])) 
                for s in info:
                    info_student={}
                    info_student['id']=s.tid
                    info_student['name']=s.name
                    info_student['email']=s.email
                    info_student['phone']=s.phone
                    info_student['grade']=student[1]
                    if type(info_student['grade'])==int:
                        grades.append(info_student['grade'])
                    else:
                        pass
                    course_dict['students'].append(info_student)
            if len(grades)==0:
                course_dict['mean_grades']='*No records was found in the system'
            else:
                course_dict['mean_grades']=f'*The average grades is: {round(statistics.mean(grades),2)}'
                course_dict['max_grade']=f'The hiest grade is: {max(grades)}'
                course_dict['min_grade']=f'The lowest grade is: {min(grades)}'
            average_attend=[]
            average_not_attend=[]
            average_unknown=[]
            attend=crud.read_if('student_id, date, attendance', 'students_attendance', 'course_id', course.tid)
            if len(attend)==0:
                course_dict['average_attend']='There is no record in the system for lessons in this course'
            else:    
                for a in attend:
                    if a[2]=='yes':
                        average_attend.append(a)
                    if a[2]=='no':
                        average_not_attend.append(a)
                    if a[2]=='unknown':
                        average_unknown.append(a)
                try:
                    course_dict['average_attend']=f"*Average attendance: {round(len(average_attend)*100/(len(average_attend)+len(average_not_attend)))}%"
                except:
                    course_dict['average_attend']='No record was found in the system for student attendance or non-attendance'
            course_dict['average_note']='*Excludes students with unknown status'
        courses_list.append(course_dict)
    return courses_list

@app.route('/published_courses')
def published_courses():  # get course fo publish datails for react
    info_course=crud.read_if('*', 'publish_courses', 'status', 'Publish')
    course_list=[]
    for c in info_course:
        course_dict={}
        course_dict['id']=c[0]
        course_dict['name']=c[1]
        course_dict['description']=c[2]
        course_dict['picture']=c[3]
        course_dict['link_picture']=f"'url('/static/images/{c[3]}'"
        'url("/static/images/Python.png")'
        course_dict['status']=c[4]
        course_list.append(course_dict)
    return course_list


# start routes:
@app.route('/')
def home():
    log=check_log()
    info=info_user()
    search_form=['create']
    return render_template('home.html', log=log, info=info, search_form=search_form)

@app.route('/home')
def go_home():
    return redirect(url_for('home'))

@app.route('/search')
def search():
    log=check_log()
    info=info_user()
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
    return render_template('search.html', log=log, info=info, title=title ,course_object=course_object, student_object=student_object, teacher_object=teacher_object)

@app.route('/login', methods=['get','post'])
def login():
    log=check_log()
    info=info_user()
    form1=['create']
    jinja={}
    jinja['search_form']=['create']
    if request.method=='POST':
        auth=authenticate(request.form['email'], request.form['password'])
        if len(auth)!=0:
            if auth[0][1]=='student':
                session['role']='student'
                session['id']=crud.get_id('students', 'user_id', auth[0][0])
                session['name']=crud.student_name(session['id'])
                return redirect(url_for('student_profile', student_id=session['id']))
            if auth[0][1]=='teacher':
                session['role']='teacher'
                session['id']=crud.get_id('teachers', 'user_id', auth[0][0])
                session['name']=crud.teacher_name(session['id'])
                return redirect(url_for('teacher_profile', teacher_id=session['id']))
            if auth[0][1]=='admin':
                session['role']='admin'
                session['id']=crud.get_id('administrators', 'user_id', auth[0][0])
                session['name']=crud.admin_name(session['id'])
                return redirect(url_for('administrator', admin_id=session['id']))
        else:
            form=['create']
            return render_template('login.html', log=log, info=info, form1=form1, form=form, jinja=jinja, note='Incorrect username or password' )
    return render_template('login.html', log=log, form1=form1, info=info, jinja=jinja)

@app.route('/logout')
def logout():
   session.pop('name','none') 
   session.pop('id','none') 
   session.pop('role','none') 
   return redirect(url_for('home'))

# admin features for courses:
@app.route('/administrator/<admin_id>' )
def administrator(admin_id): # showe administrator pages
    log=check_log()
    info=info_user()
    admin_id=admin_id    
    return render_template ('administrator.html',log=log, info=info, course_dict='', admin_id=admin_id, jinja='')

@app.route('/admin_courses',methods=['GET', 'POST'])
def admin_courses(): # courses information and actions for admin
    log=check_log()
    info=info_user()
    form=['create']
    if request.method=='POST':
        courses_list=crud.read_like('*', 'courses', 'name', request.form['search'].title())
        if len(courses_list)==0:
            return render_template('admin_courses.html',log=log, info=info, course_dict='', course_attend='', attend_update='', attend_date_update='', form=form, result='No such course was found', admin_id=session['id'])
        else:
            courses_object=create_courses_objects(courses_list)  
            return render_template('admin_courses.html',log=log, info=info, course_dict='', course_attend='', attend_update='', attend_date_update='', form=form, courses_objects=courses_object, admin_id=session['id'])
    return render_template('admin_courses.html', log=log, info=info, course_dict='', course_attend='', attend_update='', attend_date_update='', form=form, courses_teachers=create_courses_objects(crud.read_all('courses')), admin_id=session['id'])

@app.route('/course_info/<course_id>')
def course_info(course_id): # specific course information
    log=check_log()
    info=info_user()
    course_dict={}
    course_dict['link1']=['create']
    course_dict['id']=course_id
    course=crud.read_if('*',"courses","id", course_id)
    course=create_courses_objects(course)
    for c in course:
        if c.teacher_id[1]=='Not yet assigned':
            c.teacher_id=['','Not yet assigned- choose teacher']
            course_dict['teacher_update']=['create']
        else:
            course_dict['teacher_link']=['create']
    course_dict['course']=course
    course_dict['students_title']='Students: '
    course_dict['student_name']='Name'
    course_dict['student_grade']='Grade'
    students=crud.read_if('student_id, grade','students_courses', 'course_id', course_id)
    if len(students)==0:     
        course_dict['no_students']='There are no students enrolled to the course'
    else:
        students_names=[]
        for s in students:
            s_g=namedtuple('S_grade', ['id','name','grade'])
            s_g.id=s[0]
            s_g.name=crud.student_name(s[0])
            s_g.grade=s[1]
            students_names.append(s_g)
        course_dict['students']=students_names
        course_dict['no_students']=''
        course_dict['form']=['create']
        dates=crud.read_if('DISTINCT date', 'students_attendance', 'course_id', course_id)
        if len(dates)==0:
            course_dict['no_lesson']='No lessons found in the system'
        else:
            course_dict['link2']=['create']
            course_dict['link3']=['create']
    return render_template ('admin_courses.html', log=log, info=info, course_dict=course_dict, course_attend='', attend_update='', attend_date_update='', admin_id=session['id'])

@app.route('/attendance_course/<course_id>', methods=['get','post'])
def attendance_course(course_id): # View attendance for a specific course
    log=check_log()
    info=info_user()
    course_dict={}
    course_dict['id']=course_id
    course_dict['link1']=['create']
    course_dict['link2']=[]
    course_dict['link3']=['create']
    course_attend={}
    course_attend['form']=[]
    course_attend['course_id']=course_id   
    course_attend['course_name']=f"Attendance for {crud.course_name(course_id)}"  
    dates=crud.read_if('DISTINCT date', 'students_attendance', 'course_id', course_id)
    course_attend['chose_date']=['Choose a lesson:']
    course_attend['dates']=dates
    course_attend['select']=['create']
    average_attend=[]
    average_not_attend=[]
    average_unknown=[]
    attend=crud.read_if('student_id, date, attendance', 'students_attendance', 'course_id', course_id)
    for a in attend:
        if a[2]=='yes':
            average_attend.append(a)
        if a[2]=='no':
            average_not_attend.append(a)
        if a[2]=='unknown':
            average_unknown.append(a)
    try:
        course_attend['average_attend']=f"Course attendance average:  {round(len(average_attend)*100/(len(average_attend)+len(average_not_attend)))}%"
    except:
        course_attend['average_attend']='No record was found in the system for student attendance or non-attendance'
    course_attend['average_note']='*Excludes students with unknown status'
    if request.method=='GET':
        return render_template ('admin_courses.html', log=log, info=info, course_attend=course_attend, course_dict=course_dict, attend_update='', attend_date_update='', admin_id=session['id'])
    else:
        course_attend['form']=['create']
        course_attend['date']=request.form['chosen_date']
        course_attend['chosen_date']=f"{request.form['chosen_date']} attendance:"        
        course_attend['yes_title']='Students who ATTENDED the class:'
        course_attend['no_title']='Students who DID NOT attend the class:'
        course_attend['unknown_title']='Unknown:'
        course_attend['attend']=[]
        course_attend['not_attend']=[]
        course_attend['unknown']=[]
        for student in attend:
            if student[1]==request.form['chosen_date'] and student[2]=='yes': 
                s=(f"/student_info/{student[0]}",crud.student_name(student[0])) # יצירת הכתובת לתגית של קישור
                course_attend['attend'].append(s)
            if student[1]==request.form['chosen_date'] and student[2]=='no':
                s=(f"/student_info/{student[0]}",crud.student_name(student[0]))
                course_attend['not_attend'].append(s)
            if student[1]==request.form['chosen_date'] and student[2]=='unknown':
                s=(f"/student_info/{student[0]}",crud.student_name(student[0]))
                course_attend['unknown'].append(s)
        if len(course_attend['attend'])==0:
            course_attend['attend']=[['/admin_students','No students found']] 
        if len(course_attend['not_attend'])==0:
            course_attend['not_attend']=[['/admin_students','No students found']] 
        if len(course_attend['unknown'])==0:
            course_attend['unknown']=[['/admin_students','No students found']]        
        return render_template ('admin_courses.html', log=log, info=info, course_attend=course_attend, course_dict=course_dict, attend_update='', attend_date_update='', admin_id=session['id'])

@app.route('/update_course_attendance/<course_id>') 
def update_course_attendance(course_id): # Choosing a specific lesson to update attendance
    log=check_log()
    info=info_user()
    course_dict={}
    course_dict['id']=course_id
    course_dict['link1']=['create']
    course_dict['link2']=['create']
    course_dict['link3']=[]
    attend_update={}
    attend_update['id']=course_id
    attend_update['course_name']=f"Update attendance for {crud.course_name(course_id)}"
    dates=crud.read_if('DISTINCT date', 'students_attendance', 'course_id', course_id)
    attend_update['chose_date']=['Choose a lesson:']
    attend_update['dates']=dates
    return render_template('admin_courses.html', log=log, info=info, course_attend='', course_dict=course_dict, attend_update=attend_update, attend_date_update='', admin_id=session['id'])
                 
@app.route('/update_course_date_attendance/course_id=<course_id>date=<date>', methods=['get','post'])
def update_course_date_attendance(course_id, date): # update attendance for a specific lesson in a course 
    log=check_log()
    info=info_user()
    course_dict={}
    course_dict['id']=course_id
    course_dict['link1']=['create']
    course_dict['link2']=['create']
    course_dict['link3']=[]
    attend_update={}
    attend_update['id']=course_id
    attend_update['course_name']=f"Update attendance for {crud.course_name(course_id)}"
    dates=crud.read_if('DISTINCT date', 'students_attendance', 'course_id', course_id)
    attend_update['chose_date']=['Choose a lesson:']
    attend_update['dates']=dates
    attend_date_update={}
    attend_date_update['select']=['create']
    attend_date_update['title_date']=f"Attendance for {date}:"
    current_attend=crud.read_two_if('student_id, attendance','students_attendance','course_id', course_id, 'date', date)
    attend_date_update['students_attend']=[]
    for s_a in current_attend:
        student_a=namedtuple('S_Attend',['id','name','attend'])
        student_a.id=s_a[0]
        student_a.name=f"{crud.student_name(s_a[0])}:"
        student_a.attend={}
        student_a.attend['yes']=''
        student_a.attend['no']=''
        if s_a[1]=='yes':
            student_a.attend['yes']='checked'
        elif s_a[1]=='no':
            student_a.attend['no']='checked'
        attend_date_update['students_attend'].append(student_a)
    if request.method=='GET':
        return render_template('admin_courses.html', log=log, info=info, course_attend='', course_dict=course_dict, attend_update=attend_update, attend_date_update=attend_date_update, admin_id=session['id'])
    else: 
        answer=request.form['attendance']
        student_id=request.form['student_id']
        crud.update_three_if('students_attendance', 'attendance',f"'{answer}'", 'student_id', student_id, 'course_id', course_id, 'date', date ) 
        return redirect(url_for('update_course_date_attendance', course_id=course_id, date=date))

@app.route('/add_course', methods=['GET','POST'])
def add_course():
    log=check_log()
    info=info_user()
    if request.method=='POST':
        if request.form['new_name']=='':
            return render_template('add_course.html', log=log, info=info, course_dict='', admin_id=session['id'], note="Course Name is required fields")          
        crud.create('courses', 'name, description, teacher_id, start, day, time', f" '{request.form['new_name'].title()}', '{request.form['new_description']}', '{request.form['teacher_tid']}', '{request.form['new_start']}', '{request.form['new_day']}', '{request.form['new_time']}' ")
        return redirect(url_for('admin_courses'))
    else:
        return render_template('add_course.html', log=log, info=info, course_dict='', admin_id=session['id'], teachers_object=create_teachers_objects(crud.read_all('teachers')))

@app.route('/update_courses', methods=['GET', 'POST'])
def update_courses(): # Choosing a course to update 
    log=check_log()
    info=info_user()
    form=['create']
    if request.method=='POST':
        courses_list=crud.read_like('*', 'courses', 'name', request.form['search'].title())
        if len(courses_list)==0:
            return render_template('update_courses.html', log=log, info=info, admin_id=session['id'], form=form, chosen_course='', course_dict='', result='No such course was found')
        else:
            course_object=create_courses_objects(courses_list)  
            return render_template('update_courses.html', log=log, info=info, admin_id=session['id'], form=form, chosen_course='',teacher_info='', courses_objects=course_object, course_dict='')
    else:    
        return render_template('update_courses.html', log=log, info=info, form=form, admin_id=session['id'], chosen_course='',teacher_info='', courses=create_courses_objects(crud.read_all('courses')), course_dict='')

@app.route('/chosen_course/<course_id>', methods=['GET', 'POST'])
def chosen_course_update(course_id):
    log=check_log()
    info=info_user()
    form2=['create']
    chosen_course={}
    chosen_course['title_chosen']='Edit the Changes:'
    course=crud.read_if('*',"courses","id", course_id)
    course_info=create_courses_objects(course)
    for c in course_info:
        c.start=crud.read_if('start',"courses","id", course_id)[0]
    chosen_course['course_info']=course_info
    chosen_course['teachers']=create_teachers_objects(crud.read_all('teachers'))
    if request.method=='POST':
        name=request.form['name'].title()
        description=request.form['description']
        teacher_id=request.form['teacher_id']
        start=request.form['start']
        day=request.form['day']
        time=request.form['time']
        if name=='':
            return render_template('update_courses.html', log=log, info=info, admin_id=session['id'], form='', form2=form2 ,chosen_course=chosen_course,  course_dict='', note="Course Name is required fields")
        else:
            crud.update_if('courses', 'name, description, teacher_id, start, day, time', f"'{name}', '{description}', '{teacher_id}', '{start}', '{day}', '{time}'",'id', course_id)
            return redirect(url_for('course_info', course_id=course_id))
    else:
        return render_template('update_courses.html', log=log, info=info, admin_id=session['id'], form='', form2=form2 ,chosen_course=chosen_course, course_dict='') 

@app.route('/course_registration', methods=['GET', 'POST'])
def course_registrationt(): # Choosing a specific course for student registration 
    log=check_log()
    info=info_user()
    form=['create']
    if request.method=='POST':
        courses_list=crud.read_like('*', 'courses', 'name', request.form['search'].title())
        if len(courses_list)==0:
            return render_template('course_registration.html', log=log, info=info, admin_id=session['id'], form=form, course_dict='', result1='No such course was found')
        else:
            course_object=create_students_objects(courses_list) 
            return render_template('course_registration.html', log=log, info=info, admin_id=session['id'], form=form, course_dict='', course_objects=course_object)
    else:    
        return render_template('course_registration.html', log=log, info=info, admin_id=session['id'], form=form, course_dict='', courses=create_courses_objects(crud.read_all('courses')))

@app.route('/course_id_registration/<course_id>',  methods=['GET', 'POST'])
def course_id_registration(course_id): # Choosing students to registering to a chosen course
    log=check_log()
    info=info_user()
    form=['create']
    course_dict={}
    course_dict['form']=['create']
    students=create_students_objects(crud.read_all('students'))
    course_dict['students']=students
    course_dict['course_title']=f'Choose students for {crud.course_name(course_id)}:'
    if request.method=='POST':
        if 'form1' in request.form:
            return redirect(url_for('course_registrationt'))
        if 'form2' in request.form:
            students_list=crud.read_like('*', 'students', 'name', request.form['search'].title())
            if len(students_list)==0:
                return render_template('course_registration.html', log=log, info=info, admin_id=session['id'], form=form, course_dict=course_dict, result2='No such student was found')
            else:
                students_object=create_students_objects(students_list)
                course_dict['students']=students_object
                return render_template('course_registration.html', log=log, info=info, admin_id=session['id'], form=form, course_dict=course_dict)
        if 'form3' in request.form:
            students_ids=request.form.getlist('student_id')
            for student in students_ids:
                try:
                    crud.create('students_courses', 'student_id, course_id', f'{student}, {course_id}')
                except:
                    pass
            return redirect(url_for('course_info', course_id=course_id))
    return render_template('course_registration.html', log=log, info=info, admin_id=session['id'], form=form, course_dict=course_dict)

# admin features for students:
@app.route('/admin_students', methods=['GET', 'POST'])
def admin_students(): # students information and actions for admin
    log=check_log()
    info=info_user()
    form=['create']
    if request.method=='POST':
        students=crud.read_like('*', 'students', 'name', request.form['search'].title())
        if len(students)==0:
            return render_template('admin_students.html', log=log, info=info, admin_id=session['id'], form=form, student_attend='', student_dict='', result='No such studentd was found')
        else:
            student_object=create_students_objects(students)
            return render_template('admin_students.html', log=log, info=info, admin_id=session['id'], form=form, student_attend='', student_dict='', students_objects=student_object)
    return render_template('admin_students.html', log=log, info=info, admin_id=session['id'], form=form, student_attend='', student_dict='', students=create_students_objects(crud.read_all('students')))

@app.route('/student_info/<student_id>')
def student_info(student_id): # specific student information
    log=check_log()
    info=info_user()
    student_dict={}
    student_dict['link1']=['create']
    student_dict['id']=student_id
    student=crud.read_if('*',"students","id", student_id)
    student_object=create_students_objects(student)
    student_dict['courses_title']='Courses: '
    student_dict['course_name']='Name'
    student_dict['course_grade']='Grade'
    courses=crud.read_if('course_id, grade','students_courses', 'student_id', student_id)
    if len(courses)==0:     
        student_dict['courses']=''
        student_dict['no_courses']='The student is not enrolled for any of the courses'
        student_dict['form']=[]
    else:
        student_dict['link2']=['create']
        courses_names=[]
        for c in courses:
            c_g=namedtuple('C_grade', ['id','name','grade'])
            c_g.id=c[0]
            c_g.name=crud.course_name(c[0])
            c_g.grade=c[1]
            courses_names.append(c_g)
        student_dict['courses']=courses_names
        student_dict['no_courses']=''
        student_dict['form']=['create']
    return render_template('admin_students.html', log=log, info=info, admin_id=session['id'], student_object=student_object, student_dict=student_dict, student_attend='')

@app.route('/attendance_student/<student_id>', methods=['get','post'])
def attendance_student(student_id): # View attendance for a specific student
    log=check_log()
    info=info_user()
    student_dict={}
    student_dict['link1']=['create']
    student_dict['link2']=[]
    student_dict['link3']=['create']
    student_dict['id']=student_id
    student_attend={}
    student_attend['student_id']=student_id
    courses=crud.read_if('course_id', 'students_courses', 'student_id', student_id)
    courses_names=[]
    for c in courses:
            name=crud.course_name(c[0])
            course_name=[c[0],name]
            courses_names.append(course_name)
    student_attend['student_name']=f"{crud.student_name(student_id)} attendance"        
    student_attend['form1']=['create']
    student_attend['form2']=[]   
    student_attend['course_list']=courses_names
    if request.method=='POST':
        student_attend['form2']=['create']
        student_attend['course_id']=request.form['course_select']
        course_dates=crud.read_if('DISTINCT date', 'students_attendance', 'course_id', request.form['course_select'])
        if len(course_dates)==0:
            student_attend['average_attend']=f"No lessons were found in the system for {crud.course_name(request.form['course_select'])} course"
            student_attend['form2']=[]
        else:
            student_attend['course_dates']=course_dates
            attend=crud.read_three_if('date','students_attendance', 'student_id', student_id, 'course_id', request.form['course_select'], 'attendance', 'yes')
            try:
                student_attend['average_attend']=f"attendance average in {crud.course_name(request.form['course_select'])} course: {round(len(attend)*100/len(course_dates))}%"
            except:
                student_attend['average_attend']='No record was found in the system for student attendance or non-attendance'
            student_attend['average_note']='*Excludes lessons with udnknown status'
            student_attend['table_title']=f"Dates and attendance at {crud.course_name(request.form['course_select'])} course:"
            student_attend['date_title']='Dates'
            student_attend['attend_title']='Attendance'
            course_lessons=crud.read_two_if('date, attendance', 'students_attendance', 'student_id', student_id, 'course_id', request.form['course_select'])
            student_attend['lesson_info']=[]
            for c_l in course_lessons:
                date_attend=namedtuple('D_A',['date','c_id','attend'])
                date_attend.date=c_l[0]
                date_attend.c_id=request.form['course_select']
                date_attend.attend=c_l[1].title()
                student_attend['lesson_info'].append(date_attend)
        return render_template('admin_students.html', log=log, info=info, admin_id=session['id'], student_object='', student_attend=student_attend, student_dict=student_dict)
    else:
        return render_template('admin_students.html', log=log, info=info, admin_id=session['id'], student_object='', student_attend=student_attend, student_dict=student_dict)
        
@app.route('/update_student_attendance/<student_id>')
def update_student_attendance(student_id): # Choosing a specific course for a student to update attendance
    log=check_log()
    info=info_user()
    student_dict={}
    student_dict['link1']=['create']
    student_dict['link2']=['create']
    student_dict['link3']=[]
    student_dict['id']=student_id
    student_attend={}
    student_attend['update_title']=f"Uptade attendance for {crud.student_name(student_id)}"
    student_attend['courses_title']=['Choose a course:']
    courses=crud.read_if('course_id', 'students_courses', 'student_id', student_id)
    student_attend['courses']=[(course[0], crud.course_name(course[0])) for course in courses]
    return render_template ('admin_students.html', log=log, info=info, admin_id=session['id'], student_object='', student_attend=student_attend, student_dict=student_dict)

@app.route("/update_student_course_attendance/student_id=<student_id>course=<course_id>", methods=['get','post'])
def update_student_course_attendance(student_id, course_id): # update attendance for a specific student in a specific course
    log=check_log()
    info=info_user()
    student_dict={}
    student_dict['link1']=['create']
    student_dict['link2']=['create']
    student_dict['link3']=[]
    student_dict['id']=student_id
    student_attend={}
    student_attend['course_id']=course_id
    student_attend['update_title']=f"Uptade attendance for {crud.student_name(student_id)}"
    student_attend['courses_title']=['Choose a course:']
    courses=crud.read_if('course_id', 'students_courses', 'student_id', student_id)
    student_attend['courses']=[(course[0], crud.course_name(course[0])) for course in courses]    
    current_attend=crud.read_two_if('date, attendance','students_attendance', 'student_id', student_id, 'course_id', course_id)
    student_attend['attend_title']=f"Attendance for {crud.course_name(course_id)}:"
    student_attend['date_attend']=[]
    for c in current_attend:
        attend=namedtuple('DateAttend',['date','attend'])
        attend.date=c[0]
        attend.attend={}
        attend.attend['yes']=''
        attend.attend['no']=''
        if c[1]=='yes':
            attend.attend['yes']='checked'
        elif c[1]=='no':
            attend.attend['no']='checked'
        student_attend['date_attend'].append(attend)
    if request.method=='GET':
        return render_template ('admin_students.html', log=log, info=info, admin_id=session['id'], student_object='', student_attend=student_attend, student_dict=student_dict)
    else:
        crud.update_three_if('students_attendance', 'attendance', f"'{request.form['attendance']}'", 'student_id', student_id, 'course_id', course_id, 'date', request.form['date'])        
        return redirect(url_for('update_student_course_attendance', student_id=student_id, course_id=course_id))        
        
@app.route('/add_student', methods=['POST','GET'])
def add_student():
    log=check_log()
    info=info_user()
    if request.method=='POST':
        num_students=len(crud.read_all('students'))
        if request.form['new_name']=='' or request.form['new_email']=='' or request.form['new_phone']=='' :
            return render_template('add_student.html', log=log, info=info, admin_id=session['id'], student_dict='', note="Name, Email and Mobile number are required fields")
        else:
            check_students=crud.read_or_two('id', 'students', 'email', request.form['new_email'], 'phone', request.form['new_phone'])
            check_users=crud.read_if('id', 'new_users', 'username', request.form['new_email'])
            if len(check_students)==0 and len(check_users)==0:
                crud.create('new_users', 'username, role_id', f"'{request.form['new_email']}', '1'" )
                user_id=crud.read_if('id', 'new_users', 'username', request.form['new_email']) 
                crud.create('students', 'name, email, phone, user_id', f"'{request.form['new_name'].title()}','{request.form['new_email']}','{request.form['new_phone']}', '{user_id[0][0]}'")
                new_num=len(crud.read_all('students'))
                if new_num>num_students:
                    return redirect(url_for("admin_students"))
                else:
                    return render_template('add_student.html', log=log, info=info, admin_id=session['id'], student_dict='', note="A mistake occurred please try again")
            else:
                return render_template('add_student.html', log=log, info=info, admin_id=session['id'], student_dict='', note="Email or Mobile number already exists")       
    else:
        return render_template('add_student.html', log=log, info=info, admin_id=session['id'], student_dict='')

@app.route('/update_students', methods=['GET', 'POST'])
def update_students(): # choosing a student to update
    log=check_log()
    info=info_user()
    form=['create']
    if request.method=='POST':
        students_list=crud.read_like('*', 'students', 'name', request.form['search'].title())
        if len(students_list)==0:
            return render_template('update_students.html', log=log, info=info, admin_id=session['id'], form=form, student_dict='', result='No such student was found')
        else:
            student_object=create_students_objects(students_list) 
            return render_template('update_students.html', log=log, info=info, admin_id=session['id'], form=form, student_dict='', student_objects=student_object)
    else:    
        return render_template('update_students.html', log=log, info=info, admin_id=session['id'], form=form, student_dict='', students=create_students_objects(crud.read_all('students')))

@app.route('/chosen_student/<student_id>', methods=['GET', 'POST'])
def chosen_student_update(student_id):
    log=check_log()
    info=info_user()
    student_info=crud.read_if('*',"students","id", student_id)
    student_object=create_students_objects(student_info)
    if request.method=='POST':
        name=request.form['name'].title()
        email=request.form['email']
        phone=request.form['phone']
        if name=='' or email=='' or phone=='' :
            return render_template('update_students.html', log=log, info=info, admin_id=session['id'], student_dict='', title='Edit the Changes:', student_object=student_object, note="Name, Email and Mobile number are required fields")
        else:
            if student_object[0].name!=name:
                crud.update_if('students', 'name', f"'{name}'", 'id', student_id)
            if student_object[0].email!=email:
                check_students=crud.read_if('id', 'students', 'email', email)
                check_users=crud.read_if('id', 'new_users', 'username', email)
                if len(check_students)==0 and len(check_users)==0:
                    crud.update_if('new_users', 'username', f"'{email}'", 'id', student_object[0].user_id)
                    crud.update_if('students', 'email', f"'{email}'",'id', student_id)
                else:
                    return render_template('update_students.html', log=log, info=info, admin_id=session['id'], student_dict='', title='Edit the Changes:', student_object=student_object, note="Email already exists")  
            if student_object[0].phone!=phone:
                try:
                    crud.update_if('students', 'phone', f"'{phone}'",'id', student_id)
                except:
                    return render_template('update_students.html', log=log, info=info, admin_id=session['id'], student_dict='', title='Edit the Changes:', student_object=student_object, note="Mobile number already exists")  
            return redirect(url_for('student_info', student_id=student_id)) 
    else:
        return render_template('update_students.html', log=log, info=info, admin_id=session['id'], student_dict='', title='Edit the Changes:', student_object=student_object) 

@app.route('/student_registration', methods=['GET', 'POST'])
def student_registrationt():  # Choosing a specific student for course registration 
    log=check_log()
    info=info_user()
    form=['create']
    if request.method=='POST':
        students_list=crud.read_like('*', 'students', 'name', request.form['search'].title())
        if len(students_list)==0:
            return render_template('student_registration.html', log=log, info=info, admin_id=session['id'], form=form,   student_dict='', result1='No such student was found')
        else:
            student_object=create_students_objects(students_list) 
            return render_template('student_registration.html', log=log, info=info, admin_id=session['id'], form=form, student_dict='', student_objects=student_object)
    else:    
        return render_template('student_registration.html', log=log, info=info, admin_id=session['id'], form=form, student_dict='', students=create_students_objects(crud.read_all('students')))

@app.route('/student_id_registration/<student_id>',  methods=['GET', 'POST'])
def student_id_registration(student_id): # Choosing courses to registering to a chosen student
    log=check_log()
    info=info_user()
    form=['create']
    student_dict={}
    student_dict['form']=['create']
    courses=create_courses_objects(crud.read_all('courses'))
    student_dict['courses']=courses
    student_dict['student_title']=f'Choose courses for {crud.student_name(student_id)}:'
    if request.method=='POST':
        if 'form1' in request.form:
            return redirect(url_for('student_registrationt'))
        if 'form2' in request.form:
            courses_list=crud.read_like('*', 'courses', 'name', request.form['search'].title())
            if len(courses_list)==0:
                student_dict['courses']=[]
                return render_template('student_registration.html', log=log, info=info, admin_id=session['id'], form=form, student_dict=student_dict, result2='No such course was found')
            else:
                courses_object=create_courses_objects(courses_list)
                student_dict['courses']=courses_object
                return render_template('student_registration.html', log=log, info=info, admin_id=session['id'], form=form, student_dict=student_dict)
        if 'form3' in request.form:
            courses_ids=request.form.getlist('course_id')
            for course in courses_ids:
                try:
                    crud.create('students_courses', 'student_id, course_id', f'{student_id}, {course}')
                except:
                    pass
            return redirect(url_for('student_info',student_id=student_id))
    else:
        return render_template('student_registration.html', log=log, info=info, admin_id=session['id'], form=form, student_dict=student_dict)

# admin features for teachers:
@app.route('/admin_teachers',methods=['GET', 'POST'])
def admin_teachers(): # teachers information and actions for admin
    log=check_log()
    info=info_user()
    form=['create']
    if request.method=='POST':
        teachers=crud.read_like('*', 'teachers', 'name', request.form['search'].title())
        if len(teachers)==0:
            return render_template('admin_teachers.html', log=log, info=info, admin_id=session['id'], form=form, teacher_dict='', result='No such teacher was found')
        else:
            teachers_object=create_students_objects(teachers)
            return render_template('admin_teachers.html', log=log, info=info, admin_id=session['id'], form=form, teacher_dict='', teachers_objects=teachers_object)
    return render_template('admin_teachers.html', log=log, info=info, admin_id=session['id'], form=form, teacher_dict='', teachers_objects=create_teachers_objects(crud.read_all('teachers')))

@app.route('/teacher_info/<teacher_id>')
def teacher_info(teacher_id): # specific teacher information
    log=check_log()
    info=info_user()
    teacher_dict={}
    teacher_dict['link']=['create']
    teacher_dict['id']=teacher_id
    teacher=crud.read_if('*',"teachers","id", teacher_id)
    teacher_object=create_teachers_objects(teacher)
    teacher_dict['courses_title']='Courses:'
    teacher_dict['title_name']='Name'
    teacher_dict['title_grade']='Average grade*'
    teacher_dict['title_attend']='Average attendance*'
    courses=crud.read_if('id','courses', 'teacher_id', teacher_id)
    if len(courses)==0:     
        teacher_dict['courses']=''
        teacher_dict['no_courses']='The teacher is not associated with any of the courses'
    else:
        teacher_dict['form']=['create']
        teacher_dict['course_info']=[]
        for course in courses:
            info_course={}
            info_course['course_name']=crud.course_name(course[0])
            info_course['course_id']=course[0]
            course_grades=crud.read_if('grade', 'students_courses', 'course_id', course[0]) 
            info_course['grades']=[]              
            for grade in course_grades:            
                if type(grade[0])==int:
                    info_course['grades'].append(grade[0])
            if len(info_course['grades'])==0:
                info_course['grades_average']='No records was found in the system'
            else:
                info_course['grades_average']=f"{round(statistics.mean(info_course['grades']),2)}%"
            course_attend=crud.read_if('attendance', 'students_attendance', 'course_id', course[0])
            average_attend=[]
            average_not_attend=[]
            average_unknown=[]
            if len(course_attend)==0:
                info_course['average_attend']='There is no record in the system for lessons in this course'
            else:    
                for a in course_attend:
                    if a[0]=='yes':
                        average_attend.append(a)
                    if a[0]=='no':
                        average_not_attend.append(a)
                    if a[0]=='unknown':
                        average_unknown.append(a)
                try:
                    info_course['average_attend']=f"{round(len(average_attend)*100/(len(average_attend)+len(average_not_attend)))}%"
                except:
                    info_course['average_attend']='No record was found in the system for student attendance or non-attendance'
            teacher_dict['course_info'].append(info_course)
        teacher_dict['average_note']='*Excludes students with unknown status'
        teacher_dict['no_courses']=''
    return render_template('admin_teachers.html', log=log, info=info, admin_id=session['id'], teacher_object=teacher_object, teacher_dict=teacher_dict)

@app.route('/add_teacher', methods=['POST','GET'])
def add_teacher():
    log=check_log()
    info=info_user()
    if request.method=='POST':
        num_teachers=len(crud.read_all('teachers'))
        if request.form['new_name']=='' or request.form['new_email']=='' or request.form['new_phone']=='' :
            return render_template('add_teacher.html', log=log, info=info, admin_id=session['id'], teacher_dict='', note="Name, Email and Mobile number are required fields")
        else:
            check_teachers=crud.read_or_two('id', 'teachers', 'email', request.form['new_email'], 'phone', request.form['new_phone'])
            check_users=crud.read_if('id', 'new_users', 'username', request.form['new_email'])
            if len(check_teachers)==0 and len(check_users)==0:
                crud.create('new_users', 'username, role_id', f"'{request.form['new_email']}', '2'" )
                user_id=crud.read_if('id', 'new_users', 'username', request.form['new_email']) 
                crud.create('teachers', 'name, email, phone, user_id', f"'{request.form['new_name'].title()}','{request.form['new_email']}','{request.form['new_phone']}', '{user_id[0][0]}'")
                new_num=len(crud.read_all('teachers'))
                if new_num>num_teachers:
                    return redirect(url_for("admin_teachers"))
                else:
                    return render_template('add_teacher.html', log=log, info=info, admin_id=session['id'], teacher_dict='', note="A mistake occurred please try again")
            else:
                return render_template('add_teacher.html', log=log, info=info, admin_id=session['id'], teacher_dict='', note="Email or Mobile number already exists")
    else:
        return render_template('add_teacher.html', log=log, info=info, admin_id=session['id'], teacher_dict='')

@app.route('/update_teachers', methods=['GET', 'POST'])
def update_teachers(): # choosing a teacher to update
    log=check_log()
    info=info_user()
    form1=['create']
    if request.method=='POST':
        teachers_list=crud.read_like('*', 'teachers', 'name', request.form['search'].title())
        if len(teachers_list)==0:
            return render_template('update_teachers.html', log=log, info=info, admin_id=session['id'], form1=form1, teacher_dict='', result='No such teacher was found')
        else:
            teacher_object=create_teachers_objects(teachers_list)   
            return render_template('update_teachers.html', log=log, info=info, admin_id=session['id'], form1=form1, teacher_dict='', teacher_objects=teacher_object)
    else:    
        return render_template('update_teachers.html', log=log, info=info, admin_id=session['id'], form1=form1, teacher_dict='', teachers=create_teachers_objects(crud.read_all('teachers')))

@app.route('/chosen_teacher/<teacher_id>', methods=['GET', 'POST'])
def chosen_teacher_update(teacher_id):
    log=check_log()
    info=info_user()
    teacher_info=crud.read_if('*',"teachers","id", teacher_id)
    teacher_object=create_teachers_objects(teacher_info) 
    if request.method=='POST':
        name=request.form['name'].title()
        email=request.form['email']
        phone=request.form['phone']
        if name=='' or email=='' or phone=='' :
            return render_template('update_teachers.html', log=log, info=info, admin_id=session['id'], teacher_dict='', title='Edit the Changes:', teacher_object=teacher_object, note="Name, Email and Mobile number are required fields")
        else:
            if teacher_object[0].name!=name:
                    crud.update_if('teachers', 'name', f"'{name}'", 'id', teacher_id)
            if teacher_object[0].email!=email:
                check_teachers=crud.read_if('id', 'teachers', 'email', email)
                check_users=crud.read_if('id', 'new_users', 'username', email)
                if len(check_teachers)==0 and len(check_users)==0:
                    crud.update_if('new_users', 'username', f"'{email}'", 'id', teacher_object[0].user_id)
                    crud.update_if('teachers', 'email', f"'{email}'",'id', teacher_id)
                else:
                    return render_template('update_teachers.html', log=log, info=info, admin_id=session['id'], teacher_dict='', title='Edit the Changes:', teacher_object=teacher_object, note="Email already exists")  
            if teacher_object[0].phone!=phone:
                try:
                    crud.update_if('teachers', 'phone', f"'{phone}'",'id', teacher_id)
                except:
                    return render_template('update_teachers.html', log=log, info=info, admin_id=session['id'], teacher_dict='', title='Edit the Changes:', teacher_object=teacher_object, note="Mobile number already exists")  
            return redirect(url_for('teacher_info', teacher_id=teacher_id))
    else:
        return render_template('update_teachers.html', log=log, info=info, admin_id=session['id'], teacher_dict='', title='Edit the Changes:' ,teacher_object=teacher_object) 

# features for all users:
@app.route('/user_info_update/<user_id>', methods=['get', 'post'])
def user_info_update(user_id): # a user update his info
    log=check_log()
    info=info_user()
    jinja={}
    jinja['form1']=['create']
    jinja['user_id']=user_id
    if session['role']=='teacher':
        table_name='teachers'
        teacher_info=crud.read_if('*', table_name, 'id', user_id)
        jinja['user']=create_teachers_objects(teacher_info)  
    if session['role']=='student':
        table_name='students'
        student_info=crud.read_if('*', table_name, 'id', user_id)
        jinja['user']=create_students_objects(student_info)
    if session['role']=='admin':
        table_name='administrators'
        admin_info=crud.read_if('*', table_name, 'id', user_id)
        jinja['user']=create_admins_objects(admin_info)    
    if request.method=='GET':    
        return render_template('login.html', log=log, info=info, jinja=jinja)
    else:
        email=request.form['email']
        phone=request.form['phone']
        if email=='' or phone=='' :
            jinja['note']="Email and Mobile number are required fields"
            return render_template('login.html', log=log, info=info, jinja=jinja)
        if jinja['user'][0].email!=email:
            check_user_table=crud.read_if('id', table_name, 'email', email)
            check_new_users=crud.read_if('id', 'new_users', 'username', email)
            if len(check_user_table)==0 and len(check_new_users)==0:
                crud.update_if('new_users', 'username', f"'{email}'", 'id', jinja['user'][0].user_id)
                crud.update_if(table_name, 'email', f"'{email}'",'id', user_id)
            else:
                jinja['note']="Email already exists"
                return render_template('login.html', log=log, info=info, jinja=jinja)  
        if jinja['user'][0].phone!=phone:
            try:
                crud.update_if(table_name, 'phone', f"'{phone}'",'id', user_id)
            except:
                jinja['note']="Mobile already exists"
                return render_template('login.html', log=log, info=info, jinja=jinja)  
        if session['role']=='teacher':
            return redirect(url_for('teacher_profile', teacher_id=user_id))
        if session['role']=='student':
            return redirect(url_for('student_profile', student_id=user_id))
        if session['role']=='admin':
            return redirect(url_for('administrator', admin_id=user_id))

@app.route('/change_password/<user_id>', methods=['get','post'])
def change_password(user_id):
    log=check_log()
    info=info_user()
    jinja={}
    jinja['form2']=['create']
    jinja['user_id']=user_id
    if session['role']=='teacher':
        table_name='teachers'
        teacher_info=crud.read_if('*', table_name, 'id', user_id)
        jinja['user']=create_teachers_objects(teacher_info)  
    if session['role']=='student':
        table_name='students'
        student_info=crud.read_if('*', table_name, 'id', user_id)
        jinja['user']=create_students_objects(student_info)
    if session['role']=='admin':
        table_name='administrators'
        admin_info=crud.read_if('*', table_name, 'id', user_id)
        jinja['user']=create_admins_objects(admin_info)    
    if request.method=='GET':
        return render_template('login.html', log=log, info=info, jinja=jinja)
    else:
        old_password=crud.read_two_if('password', 'new_users', 'username', jinja['user'][0].email, 'id', jinja['user'][0].user_id)
        if old_password[0][0]!=request.form['old_password']:
            jinja['note']='Incorrect password'
            return render_template('login.html', log=log, info=info, jinja=jinja)
        else:
            if request.form['new_password']!=request.form['verification']:
                    jinja['note']='The new password and verification are not the same'
                    return render_template('login.html', log=log, info=info, jinja=jinja)
            else:
                crud.update_if('new_users','password', f"'{request.form['new_password']}'", 'id', jinja['user'][0].user_id)
                if session['role']=='teacher':
                    return redirect(url_for('teacher_profile', teacher_id=user_id))
                if session['role']=='student':
                    return redirect(url_for('student_profile', student_id=user_id))
                if session['role']=='admin':
                    return redirect(url_for('administrator', admin_id=user_id))

@app.route('/forgot_password', methods=['get','post']) 
def forgot_password():
    log=check_log()
    info=info_user()
    jinja={}
    jinja['form3']=['create']
    if request.method=='GET':        
        return render_template('login.html', log=log, info=info, jinja=jinja)
    else:
        username=crud.query(f"SELECT new_users.id, roles.type from new_users, roles WHERE new_users.username='{request.form['username']}'  AND roles.id=new_users.role_id") 
        if len(username)==0:
            jinja['note']='Username not exist'
            return render_template('login.html', log=log, info=info, jinja=jinja)
        else:
            if username[0][1]=='admin':
                table_name='administrators'
            else:
                table_name=f"{username[0][1]}s"
            user_id=crud.read_if('id', table_name, 'user_id', username[0][0])
            return redirect(url_for('forgot_password_user', user_id=user_id[0][0], table=table_name,new_user_id=username[0][0] ))

@app.route('/forgot_password/i=<user_id>t=<table>n=<new_user_id>', methods=['get','post']) 
def forgot_password_user(user_id, table, new_user_id): # Verification process to create new password for a user who forgot his password
    log=check_log()
    info=info_user()
    jinja={}
    jinja['form4']=['create']
    user_info=crud.read_if('name, phone', table, 'id', user_id)
    if user_info[0][1]=='':
        jinja['input_info']=['name', 'Enter your registration name']        
    else:
        jinja['input_info']=['phone', 'Enter mobile number']
    if request.method=='GET':
        return render_template('login.html', log=log, info=info, jinja=jinja)
    else:
        if 'phone' in request.form:
            if request.form['phone']!=user_info[0][1]:
                jinja['note']='Incorect mobile number'
                return render_template('login.html', log=log, info=info, jinja=jinja)
            jinja['form4']=''
            jinja['form5']=['create']
        if 'name' in request.form:
            if request.form['name'].title()!=user_info[0][0]:
                jinja['note']='Incorect name'
                return render_template('login.html', log=log, info=info, jinja=jinja)
            jinja['form4']=''
            jinja['form5']=['create']
        if 'password' in request.form:
            crud.update_if('new_users','password', f"'{request.form['password']}'", 'id', new_user_id)
            return redirect(url_for('login'))
        return render_template('login.html', log=log, info=info, jinja=jinja)

# admin features:
@app.route('/show_messages')
def show_messages(): # shows a list of messages 
    log=check_log()
    info=info_user()
    jinja={}
    jinja['form1']=['create']
    messages_list=crud.read_all('messages')
    if len(messages_list)==0:
        jinja['note']='No messages found'
    else:
        jinja['messages']=[]
        for message in messages_list:
            m=namedtuple('M_P',['id','message','status'])
            m.id=message[0]
            m.message=message[1]
            m.status=message[4].title()
            jinja['messages'].append(m)
    return render_template ('administrator.html',log=log, info=info, admin_id=session['id'], jinja=jinja)

@app.route('/add_message', methods=['get', 'post'])
def add_messages():
    log=check_log()
    info=info_user()
    jinja={}
    jinja['form2']=['create']
    courses=crud.read_all('courses')
    jinja['courses']=create_courses_objects(courses)
    current_time=datetime.datetime.now()
    current_time=current_time.strftime("%d/%m/%Y %H:%M")
    if request.method=='POST':
        loctions=request.form.getlist('choose_loction')
        if len(loctions)==0:
            jinja['note']='No location to post the message was chosen'
            return render_template ('administrator.html',log=log, info=info, admin_id=session['id'], jinja=jinja)
        else:
            try:
                crud.create('messages', 'message, time, status', f"'{request.form['message']}','{current_time}','{request.form['status']}'")
            except:
                jinja['note']='Message already posted'
                return render_template ('administrator.html',log=log, info=info, admin_id=session['id'], jinja=jinja)
            message_id=crud.read_three_if('id', 'messages', 'message', request.form['message'], 'time', current_time, 'status', 'Publish')
            if len(message_id)==0:
                return redirect(url_for('show_message', message_id=message_id))
            else:
                message_id=message_id[0][0]                
                for l in loctions:
                    try:
                        l=int(l)
                        crud.create('messages_courses', 'message_id, course_id', f"'{message_id}','{l}'")
                    except:
                        pass
                    if l=='home_page':
                        crud.update_if('messages', 'location', "'home_page'", 'id', message_id)
                    if l=='all_courses':
                        for course in jinja['courses']:
                                try:
                                    crud.create('messages_courses', 'message_id, course_id', f"'{message_id}','{course.tid}'" )
                                except:
                                    pass
            return redirect(url_for('show_message', message_id=message_id))
    else:
        return render_template ('administrator.html',log=log, info=info, admin_id=session['id'], jinja=jinja)      

@app.route('/show_message/<message_id>')
def show_message(message_id): #returns whether a message has been added or not
    log=check_log()
    info=info_user()
    jinja={}
    jinja['form3']=['create']
    if message_id=='[]':
        jinja['note']='Message added witout posting'
    else:
        message=crud.read_if('message','messages', 'id', message_id)
        if len(message)==0:
            jinja['note']='An error occurred while posting the message'
        else:
            jinja['note']=f'"{message[0][0]}" message added successfully'
            return message[0][1]
    return render_template ('administrator.html',log=log, info=info, admin_id=session['id'], jinja=jinja)

@app.route('/message_update/<message_id>', methods=['get','post'])
def message_update(message_id):
    log=check_log()
    info=info_user()
    jinja={}
    jinja['form4']=['create']
    courses=crud.read_all('courses')
    courses=create_courses_objects(courses)
    jinja['courses']=courses
    message=crud.read_if('*', 'messages', 'id', message_id)
    for m in message:
        jinja['message']=m[1]
        if m[2]=='home_page':
            jinja['home_page']='checked'
        else:
            jinja['home_page']=''
        if m[4]=='publish'.title():
            jinja['publish']='checked'
            jinja['no_publish']=''
        if m[4]=='not publish'.title():
            jinja['publish']=''
            jinja['no_publish']='checked'
    old_l=crud.read_if('course_id', 'messages_courses', 'message_id', message_id)
    old_location_id=[l[0] for l in old_l]
    delete=crud.read_two_if('course_id', 'messages_courses', 'message_id', message_id, 'status', 'Delete')
    delete_id=[d[0] for d in delete]
    if len(old_location_id)==0:
        jinja['all_courses']=''
    if len(courses)==len(old_location_id)-len(delete_id):
        jinja['all_courses']='checked'
    if 0 < len(old_location_id)-len(delete_id) < len(courses):
        jinja['all_courses']=''
        jinja['courses']=''
        jinja['chosen_course']=[]
        for course in courses:
            chosen={}
            if course.tid in old_location_id:
                if course.tid not in delete_id:
                    chosen['id']=course.tid
                    chosen['name']=crud.course_name(course.tid)
                    chosen['checked']='checked'
                    jinja['chosen_course'].append(chosen)
                else:
                    chosen['id']=course.tid
                    chosen['name']=crud.course_name(course.tid)
                    chosen['checked']=''
                    jinja['chosen_course'].append(chosen)
            else:
                chosen['id']=course.tid
                chosen['name']=crud.course_name(course.tid)
                chosen['checked']=''
                jinja['chosen_course'].append(chosen)
    if request.method=='POST':
        new_loctions=request.form.getlist('choose_loction')
        if len(new_loctions)==0:
            jinja['note']='No location to post the message was chosen'
            return render_template ('administrator.html',log=log, info=info, admin_id=session['id'], jinja=jinja)
        else:
            crud.update_if('messages', 'message, location, status',f"'{request.form['message']}', '','{request.form['status']}'", 'id', message_id)
            for new in new_loctions:
                try:
                    new=int(new)
                    if new in old_location_id:
                        crud.update_two_if('messages_courses', 'status', request.form['status'], 'message_id', message_id, 'course_id', new)
                    else:
                        crud.create('messages_courses', 'message_id, course_id', f"'{message_id}','{new}'")
                except:
                    pass
                if new=='home_page':
                    crud.update_if('messages', 'location', "'home_page'", 'id', message_id)
                if new=='all_courses':
                       for course in courses:
                            try:
                               crud.create('messages_courses', 'message_id, course_id, status', f"'{message_id}','{course.tid}','{request.form['status']}'")
                            except:
                               pass
            for old in old_location_id:
                if str(old) not in new_loctions:
                    crud.update_two_if('messages_courses', 'status', f"'Delete'", 'message_id', message_id, 'course_id', old)
        return redirect(url_for('message_update', message_id=message_id))
    else:
        return render_template ('administrator.html',log=log, info=info, admin_id=session['id'], jinja=jinja)   

@app.route('/advertising_courses')
def advertising_courses(): # shows a list of  publish courses 
    log=check_log()
    info=info_user()
    jinja={}
    jinja['form5']=['create']
    courses_list=crud.read_all('publish_courses')
    if len(courses_list)==0:
        jinja['note']='No courses found'
    else:
        jinja['courses']=[]
        for course in courses_list:
            c=namedtuple('C_P',['id','name','status'])
            c.id=course[0]
            c.name=course[1].title()
            c.status=course[4].title()
            jinja['courses'].append(c)
    return render_template ('administrator.html',log=log, info=info, admin_id=session['id'], jinja=jinja)

@app.route("/add_publish_course", methods=['get','post'])
def add_publish_course():
    log=check_log()
    info=info_user()
    jinja={}
    jinja['form6']=['create']
    if request.method=='POST':
        file = request.files['picture']
        if file.filename == '':
            jinja['note']='No file selected'
            return render_template ('administrator.html',log=log, info=info, admin_id=session['id'], jinja=jinja)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            if request.form['description']=='':
                description='Stiil not update'
            else:
                description=request.form['description']
            try:            
                crud.create('publish_courses','course_name, description, picture, status', f"'{request.form['course_name']}','{description}','{file.filename}','{request.form['status']}'")
                course_id=crud.read_two_if('id','publish_courses','course_name', request.form['course_name'], 'picture', file.filename)
                course_id=course_id[0][0]
                return redirect(url_for('show_course', course_id=course_id))
            except:
                jinja['note']='An error occurred while posting the message- Course already posted or There is a typo in the description'
                return render_template ('administrator.html',log=log, info=info, admin_id=session['id'], jinja=jinja)
        else:
            jinja['note']='This type of file  is not allowed'
            return render_template ('administrator.html',log=log, info=info, admin_id=session['id'], jinja=jinja)
    return render_template ('administrator.html',log=log, info=info, admin_id=session['id'], jinja=jinja)

@app.route('/show_course/<course_id>')
def show_course(course_id): #returns whether a course has been added or not
    log=check_log()
    info=info_user()
    jinja={}
    jinja['form7']=['create']
    course=crud.read_if('course_name, status','publish_courses', 'id', course_id)
    if len(course)==0:
        jinja['note']='An error occurred while posting the course'
    else:
        if course[0][1]=='Not Publish':
            jinja['note']=f"{course[0][0]} added witout posting "
        jinja['note']=f'{course[0][0]} course added successfully'
    return render_template ('administrator.html',log=log, info=info, admin_id=session['id'], jinja=jinja)

@app.route('/advertising_update/<course_id>', methods=['get','post'])
def advertising_update(course_id):
    log=check_log()
    info=info_user()
    jinja={}
    jinja['form8']=['create']
    info_course=crud.read_if('*', 'publish_courses','id', course_id)
    for c in info_course:
        jinja['name']=c[1]
        jinja['description']=c[2]
        jinja['picture']=c[3]
        if c[4]=='publish'.title():
            jinja['publish']='checked'
            jinja['no_publish']=''
        if c[4]=='not publish'.title():
            jinja['publish']=''
            jinja['no_publish']='checked'
    if request.method=='POST':
        file = request.files['picture']
        if file.filename=="":
            picture=jinja['picture']
        else:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                picture=file.filename
            else:
                jinja['note']='This type of file  is not allowed'
                return render_template ('administrator.html',log=log, info=info, admin_id=session['id'], jinja=jinja)
        if request.form['description']=='':
            description= 'Stiil not update'
        else:
            description=request.form['description']
        crud.update_if('publish_courses', 'course_name, description, picture, status', f"'{request.form['course_name']}','{description}','{picture}','{request.form['status']}'", 'id', course_id)
        return redirect(url_for('advertising_update', course_id=course_id))
    else:    
        return render_template ('administrator.html',log=log, info=info, admin_id=session['id'], jinja=jinja)

# student features:
@app.route('/student_profile/<student_id>', methods=['get', 'post'])
def student_profile(student_id):
    log=check_log()
    info=info_user()
    form2=["create"]
    jinja={}
    email=crud.read_if('email','students', 'id', student_id)
    if request.method=='POST':
        new_password=request.form['new_password']
        crud.update_if('new_users', 'password', new_password, 'username', email[0][0])
        return redirect(url_for('student_profile', student_id=student_id))
    else:
        password=crud.read_if('password', 'new_users', 'username', email[0][0])
        if password[0][0]=='123456':
            return render_template('login.html', log=log, info=info, form2=form2, jinja='', note='You need to change the initial password you received:')
        else:
            jinja['js']=['teacher','teacher_courses']
            jinja['section']=['create']
            return render_template('profile_student.html', log=log, info=info, jinja=jinja, hello= f"hello {crud.student_name(student_id)}") 

# teacher features:
@app.route('/teacher_profile/<teacher_id>', methods=['get', 'post'])
def teacher_profile(teacher_id): # a teacher user sees his profile
    log=check_log()
    info=info_user()
    form2=["create"]
    jinja={}
    email=crud.read_if('email','teachers', 'id', teacher_id)
    if request.method=='POST':
        new_password=request.form['new_password']
        crud.update_if('new_users', 'password', new_password, 'username', email[0][0])
        return redirect(url_for('teacher_profile', teacher_id=teacher_id))
    else:
        password=crud.read_if('password', 'new_users', 'username', email[0][0])
        if password[0][0]=='123456':
            return render_template('login.html', log=log, info=info, form2=form2, jinja='', note='You need to change the initial password you received:')
        else:
            jinja['js']=['teacher','teacher_courses']
            jinja['section']=['create']
            return render_template('profile_teacher.html', log=log, info=info, jinja=jinja) 

@app.route('/attendance/<course_id>', methods=['get', 'post'])
def course_attendance(course_id): # a teacher user mark attendance 
    log=check_log()
    info=info_user()
    jinja={}
    jinja['course_id']=course_id
    jinja['attend']=['create']
    jinja['attend_title']=f"Attendance for {crud.course_name(course_id)}"
    current_date=datetime.date.today()
    current_date=current_date.strftime("%d/%m/%Y")
    current_date=current_date.replace('/','-')
    jinja['current_date']=f"Date: {current_date}"
    teacher_id=crud.read_if('teacher_id', 'courses', 'id', course_id)
    jinja['teacher_id']=teacher_id[0][0]
    if request.method=='GET':
        students_ids=crud.read_if('student_id', 'students_courses', 'course_id', course_id)
        if len(students_ids)==0:
            jinja['no_students']=[f'There are no students enrolled to {crud.course_name(course_id)} course']
            jinja['link']='Back'
            return render_template ('profile_teacher.html', log=log, info=info, jinja=jinja)
        else:
            jinja['link']='Done'
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
            course_atten=crud.read_two_if('student_id, attendance','students_attendance','course_id', course_id, 'date', current_date)
            jinja['students_attend']=[]
            for s_a in course_atten:
                student_a=namedtuple('S_Attend',['id','name','attend'])
                student_a.id=s_a[0]
                student_a.name=f"{crud.student_name(s_a[0])}:"
                student_a.attend={}
                if s_a[1]=='yes':
                    student_a.attend['yes']='checked'
                    student_a.attend['no']=''
                elif s_a[1]=='no':
                    student_a.attend['yes']=''
                    student_a.attend['no']='checked'
                else:
                    student_a.attend['yes']=''
                    student_a.attend['no']=''
                jinja['students_attend'].append(student_a)
            return render_template ('profile_teacher.html', log=log, info=info, jinja=jinja)
    else:   
        if request.method=='POST':
            answer=request.form['attendance']
            student_id=request.form['student_id']
            crud.update_three_if('students_attendance', 'attendance',f"'{answer}'", 'student_id', student_id, 'course_id', course_id, 'date', current_date)    
            return redirect(url_for('course_attendance',course_id=course_id))

@app.route('/updeat_grade/<course_id>', methods=['get','post'])
def updeat_grade(course_id): # a teacher user update grade
    log=check_log()
    info=info_user()
    jinja={}
    jinja['grades']=['create']
    jinja['course_id']=course_id
    teacher_id=crud.read_if('teacher_id', 'courses', 'id', course_id)
    jinja['teacher_id']=teacher_id[0][0]
    jinja['grades_title']=f'Update grades for {crud.course_name(course_id)}:'
    if request.method=='GET':
        students_grades=crud.read_if('student_id, grade', 'students_courses', 'course_id', course_id)
        if len(students_grades)==0:
            jinja['no_students']=[f'There are no students enrolled to {crud.course_name(course_id)} course']
            jinja['link']='Back'
        else:
            jinja['link']='Done'
            jinja['students_grades']=[]
            for student in students_grades:
                inf=namedtuple('S_G',['id','name','grade'])
                inf.id=student[0]
                inf.name=crud.student_name(student[0])
                inf.grade=student[1]
                jinja['students_grades'].append(inf)                
        return render_template ('profile_teacher.html', log=log, info=info, jinja=jinja)
    else:
        crud.change_grade(request.form['grade'], request.form['student_id'], course_id)
        return redirect(url_for('updeat_grade',course_id=course_id))




           

