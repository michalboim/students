from flask import Flask, redirect, url_for, render_template, request, session
app = Flask(__name__)
from setup_db import query
import classes
import crud
from functions import create_courses_objects, create_students_objects, create_teachers_objects, courses_teachers, authenticate
from collections import namedtuple
import datetime, statistics

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

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

def chek_admin():#check if user is admin or not
    if "role" in session:
        if session['role']=='admin':
            admin_dict={}
            admin_dict['id']=session['id']
            admin_dict['link']=f"/administrator/{session['id']}"
            admin_dict['word']='Administrator'
            admin_dict['hello']=f"Hello {session['name']}- what do you want to do?"
            return admin_dict
        else:
            admin_dict=''
            return admin_dict

def users_details():
    details={}
    if "role" in session:
        details['role']=session['role']
        details['id']=session['id']
        details['name']=session['name']
    return details

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
    form1=['create']
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
            return render_template('login.html', log=log, admin_dict=admin_dict, form1=form1, note='Incorrect username or password' )
    return render_template('login.html', log=log, form1=form1, admin_dict=admin_dict)

@app.route('/logout')
def logout():
   session.pop('name','none') 
   session.pop('id','none') 
   session.pop('role','none') 
   return redirect(url_for('home'))

@app.route('/user_detail')
def user_detail():
    return users_details()

@app.route('/administrator/<admin_id>' )
def administrator(admin_id):
    log=check_log()
    admin_dict=chek_admin()    
    return render_template ('administrator.html',log=log, admin_dict=admin_dict, course_dict='')

@app.route('/admin_courses',methods=['GET', 'POST'])
def admin_courses(): # courses information and actions for admin
    log=check_log()
    admin_dict=chek_admin()
    form=['create']
    if request.method=='POST':
        courses_list=crud.read_like('*', 'courses', 'name', request.form['search'].title())
        if len(courses_list)==0:
            return render_template('admin_courses.html',log=log, admin_dict=admin_dict, course_dict='', course_attend='', attend_update='', attend_date_update='', form=form, result='No such course was found')
        else:
            courses_object=create_courses_objects(courses_list)
            for course in courses_object:
                course.teacher_id=crud.teacher_name(course.teacher_id)  
            return render_template('admin_courses.html',log=log, admin_dict=admin_dict, course_dict='', course_attend='', attend_update='', attend_date_update='', form=form, courses_objects=courses_object)
    return render_template('admin_courses.html', log=log, admin_dict=admin_dict, course_dict='', course_attend='', attend_update='', attend_date_update='', form=form, courses_teachers=courses_teachers())

@app.route('/course_info/<course_id>')
def course_info(course_id):
    log=check_log()
    admin_dict=chek_admin()
    course_dict={}
    course_dict['link1']=['create']
    course_dict['id']=course_id
    course=crud.read_if('*',"courses","id", course_id)
    course=create_courses_objects(course)
    for c in course:
        c.teacher_id=[c.teacher_id, crud.teacher_name(c.teacher_id)]
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
            course_dict['no_lesson']='No lesson found in the system'
        else:
            course_dict['link2']=['create']
            course_dict['link3']=['create']
    return render_template ('admin_courses.html', log=log, admin_dict=admin_dict, course_dict=course_dict, course_attend='', attend_update='', attend_date_update='')

@app.route('/attendance_course/<course_id>', methods=['get','post'])
def attendance_course(course_id): # View attendance for a specific course
    log=check_log()
    admin_dict=chek_admin()
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
        return render_template ('admin_courses.html', log=log, admin_dict=admin_dict, course_attend=course_attend, course_dict=course_dict, attend_update='', attend_date_update='')
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
        return render_template ('admin_courses.html', log=log, admin_dict=admin_dict, course_attend=course_attend, course_dict=course_dict, attend_update='', attend_date_update='')

@app.route('/update_course_attendance/<course_id>') 
def update_course_attendance(course_id): # chose lesson date to update attendance
    log=check_log()
    admin_dict=chek_admin()
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
    return render_template('admin_courses.html', log=log, admin_dict=admin_dict, course_attend='', course_dict=course_dict, attend_update=attend_update, attend_date_update='')
                 
@app.route('//update_course_date_attendance/course_id=<course_id>date=<date>', methods=['get','post'])
def update_course_date_attendance(course_id, date):
    log=check_log()
    admin_dict=chek_admin()
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
    if request.method=='GET':
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
        return render_template('admin_courses.html', log=log, admin_dict=admin_dict, course_attend='', course_dict=course_dict, attend_update=attend_update, attend_date_update=attend_date_update)
    else: 
        answer=request.form['attendance']
        student_id=request.form['student_id']
        crud.update_three_if('students_attendance', 'attendance',f"'{answer}'", 'student_id', student_id, 'course_id', course_id, 'date', date ) 
        return redirect(url_for('update_course_date_attendance', course_id=course_id, date=date))

@app.route('/add_course', methods=['GET','POST'])
def add_course():
    log=check_log()
    admin_dict=chek_admin()
    if request.method=='POST':          
        crud.create('courses', 'name, description, teacher_id, start, day, time', f" '{request.form['new_name'].title()}', '{request.form['new_description']}', '{request.form['teacher_tid']}', '{request.form['new_start']}', '{request.form['new_day']}', '{request.form['new_time']}' ")
        return redirect(url_for('admin_courses'))
    else:
        return render_template('add_course.html', log=log, admin_dict=admin_dict, course_dict='', teachers_object=create_teachers_objects(crud.read_all('teachers')))

@app.route('/update_courses', methods=['GET', 'POST'])
def update_courses(): # chose course to update 
    log=check_log()
    admin_dict=chek_admin()
    form=['create']
    if request.method=='POST':
        courses_list=crud.read_like('*', 'courses', 'name', request.form['search'].title())
        if len(courses_list)==0:
            return render_template('update_courses.html', log=log, admin_dict=admin_dict, form=form, chosen_course='', course_dict='', result='No such course was found')
        else:
            course_object=create_courses_objects(courses_list)  
            return render_template('update_courses.html', log=log, admin_dict=admin_dict, form=form, chosen_course='',teacher_info='', courses_objects=course_object, course_dict='')
    else:    
        return render_template('update_courses.html', log=log, admin_dict=admin_dict, form=form, chosen_course='',teacher_info='', courses=courses_teachers(), course_dict='')

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
        return redirect(url_for('course_info', course_id=course_id))
    else:
        return render_template('update_courses.html', log=log, admin_dict=admin_dict, form='', form2=form2 ,chosen_course=chosen_course, teacher_info=teacher_info, course_dict='') 

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
            return redirect(url_for('course_info', course_id=course_id))
    return render_template('course_registration.html', log=log, admin_dict=admin_dict, form=form, course_dict=course_dict)

@app.route('/admin_students', methods=['GET', 'POST'])
def admin_students(): # students information and actions for admin
    log=check_log()
    admin_dict=chek_admin()
    form=['create']
    if request.method=='POST':
        students=crud.read_like('*', 'students', 'name', request.form['search'].title())
        if len(students)==0:
            return render_template('admin_students.html', log=log, admin_dict=admin_dict, form=form, student_attend='', student_dict='', result='No such studentd was found')
        else:
            student_object=create_students_objects(students)
            return render_template('admin_students.html', log=log, admin_dict=admin_dict, form=form, student_attend='', student_dict='', students_objects=student_object)
    return render_template('admin_students.html', log=log, admin_dict=admin_dict, form=form, student_attend='', student_dict='', students=create_students_objects(crud.read_all('students')))

@app.route('/student_info/<student_id>')
def student_info(student_id):
    log=check_log()
    admin_dict=chek_admin()
    student_dict={}
    student_dict['link1']=['create']
    student_dict['link2']=['create']
    student_dict['link3']=['create']
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
    return render_template('admin_students.html', log=log, admin_dict=admin_dict, student_object=student_object, student_dict=student_dict, student_attend='')

@app.route('/attendance_student/<student_id>', methods=['get','post'])
def attendance_student(student_id): # View attendance for a specific student
    log=check_log()
    admin_dict=chek_admin()
    student_dict={}
    student_dict['link1']=['create']
    student_dict['link2']=[]
    student_dict['link3']=['create']
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
        if 'form1' in request.form:
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
                student_attend['average_note']='*Excludes students with udnknown status'
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
            return render_template('admin_students.html', log=log, admin_dict=admin_dict, student_object='', student_attend=student_attend, student_dict=student_dict)
        

        
        
        
        elif 'form2' in request.form:
            student_attend['course_id']=request.form['chosen_course_id']
            course_dates=crud.read_if('DISTINCT date', 'students_attendance', 'course_id', request.form['chosen_course_id'])
            student_attend['course_dates']=course_dates
            attend=crud.read_three_if('date','students_attendance', 'student_id', student_id, 'course_id', student_attend['course_id'], 'attendance', 'yes')
            student_attend['average_attend']=f"attendance average in {crud.course_name(student_attend['course_id'])} course: {round(len(attend)*100/len(course_dates))}%"            
            date=request.form['date_select']
            student_attend['course_name']=f"Choose a lesson for {crud.course_name(request.form['chosen_course_id'])}:"
            student_answer=crud.read_three_if('attendance','students_attendance', 'student_id', student_id, 'course_id', request.form['chosen_course_id'], 'date', date)
            if student_answer[0][0]=='yes':
                student_attend['answer']=f'The student attended in {date} lesson'
            elif student_answer[0][0]=='no':
                student_attend['answer']=f'The student did not attend in {date} lesson'
            else:
                student_attend['answer']=f"There is no reference to the student's participation in {date} lesson in the system"
            return render_template('admin_students.html', log=log, admin_dict=admin_dict, student_object='', student_attend=student_attend, student_dict=student_dict)
    else:
        return render_template('admin_students.html', log=log, admin_dict=admin_dict, student_object='', student_attend=student_attend, student_dict=student_dict)
    
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
            return render_template('add_student.html', log=log, admin_dict=admin_dict, student_dict='', note="A mistake occurred please try again")
    else:
        return render_template('add_student.html', log=log, admin_dict=admin_dict, student_dict='')

@app.route('/update_students', methods=['GET', 'POST'])
def update_students(): # chose student to update
    log=check_log()
    admin_dict=chek_admin()
    form=['create']
    if request.method=='POST':
        students_list=crud.read_like('*', 'students', 'name', request.form['search'].title())
        if len(students_list)==0:
            return render_template('update_students.html', log=log, admin_dict=admin_dict, form=form, student_dict='', result='No such student was found')
        else:
            student_object=create_students_objects(students_list) 
            return render_template('update_students.html', log=log, admin_dict=admin_dict, form=form, student_dict='', student_objects=student_object)
    else:    
        return render_template('update_students.html', log=log, admin_dict=admin_dict, form=form, student_dict='', students=create_students_objects(crud.read_all('students')))

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
          return render_template('update_students.html', log=log, admin_dict=admin_dict, student_dict='', title='Edit the Changes:', student_object=student_object, note="Email or Mobile number already exists")  
        return redirect(url_for('student_info', student_id=student_id))
    else:
        return render_template('update_students.html', log=log, admin_dict=admin_dict, student_dict='', title='Edit the Changes:', student_object=student_object) 

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
                student_dict['courses']=[]
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
            return redirect(url_for('student_info',student_id=student_id))
    else:
        return render_template('student_registration.html', log=log, admin_dict=admin_dict, form=form, student_dict=student_dict)

@app.route('/admin_teachers',methods=['GET', 'POST'])
def admin_teachers(): # teachers information and actions for admin
    log=check_log()
    admin_dict=chek_admin()
    form=['create']
    if request.method=='POST':
        teachers=crud.read_like('*', 'teachers', 'name', request.form['search'].title())
        if len(teachers)==0:
            return render_template('admin_teachers.html', log=log, admin_dict=admin_dict, form=form, teacher_dict='', result='No such teacher was found')
        else:
            teachers_object=create_students_objects(teachers)
            return render_template('admin_teachers.html', log=log, admin_dict=admin_dict, form=form, teacher_dict='', teachers_objects=teachers_object)
    return render_template('admin_teachers.html', log=log, admin_dict=admin_dict, form=form, teacher_dict='', teachers_objects=create_teachers_objects(crud.read_all('teachers')))

@app.route('/teacher_info/<teacher_id>')
def teacher_info(teacher_id):
    log=check_log()
    admin_dict=chek_admin()
    teacher_dict={}
    teacher_dict['link']=['create']
    teacher_dict['id']=teacher_id
    teacher=crud.read_if('*',"teachers","id", teacher_id)
    teacher_object=create_teachers_objects(teacher)
    teacher_dict['courses_title']='Courses: '
    courses=crud.read_if('id','courses', 'teacher_id', teacher_id)
    if len(courses)==0:     
        teacher_dict['courses']=''
        teacher_dict['no_courses']='The teacher is not associated with any of the courses'
    else:
        courses_names=[[c[0], crud.course_name(c[0])] for c in courses]
        teacher_dict['courses']=courses_names
        teacher_dict['no_courses']=''
    return render_template('admin_teachers.html', log=log, admin_dict=admin_dict, teacher_object=teacher_object, teacher_dict=teacher_dict)

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
            return render_template('add_teacher.html', log=log, admin_dict=admin_dict, teacher_dict='', note="Email or Mobile number already exists")
        new_num=len(crud.read_all('teachers'))
        if new_num>num_teachers:
            return redirect(url_for("admin_teachers"))
        else:
            return render_template('add_teacher.html', log=log, admin_dict=admin_dict, teacher_dict='', note="A mistake occurred please try again")
    else:
        return render_template('add_teacher.html', log=log, admin_dict=admin_dict, teacher_dict='')

@app.route('/update_teachers', methods=['GET', 'POST'])
def update_teachers(): # chose teacher to update
    log=check_log()
    admin_dict=chek_admin()
    form1=['create']
    if request.method=='POST':
        teachers_list=crud.read_like('*', 'teachers', 'name', request.form['search'].title())
        if len(teachers_list)==0:
            return render_template('update_teachers.html', log=log, admin_dict=admin_dict, form1=form1, teacher_dict='', result='No such teacher was found')
        else:
            teacher_object=create_teachers_objects(teachers_list)   
            return render_template('update_teachers.html', log=log, admin_dict=admin_dict, form1=form1, teacher_dict='', teacher_objects=teacher_object)
    else:    
        return render_template('update_teachers.html', log=log, admin_dict=admin_dict, form1=form1, teacher_dict='', teachers=create_teachers_objects(crud.read_all('teachers')))

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
            return render_template('update_teachers.html', log=log, admin_dict=admin_dict, teacher_dict='', title='Edit the Changes:' ,teacher_object=teacher_object, note="Email or Mobile number already exists")
        return redirect(url_for('teacher_info', teacher_id=teacher_id))
    else:
        return render_template('update_teachers.html', log=log, admin_dict=admin_dict, teacher_dict='', title='Edit the Changes:' ,teacher_object=teacher_object) 

@app.route('/teachers')
def show_teachers():
    log=check_log()
    admin_dict=chek_admin()
    teachers=crud.read_all('teachers')
    return render_template('teachers.html', log=log, admin_dict=admin_dict, teachers=create_teachers_objects(teachers))

@app.route('/teacher/<teacher_id>',  methods=['GET', 'POST'])
def teacher_info_a(teacher_id):
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
                elif s_a[1]=='no':
                    student_a.attend['yes']=''
                    student_a.attend['no']='checked'
                else:
                    student_a.attend['yes']=''
                    student_a.attend['no']=''
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
            elif s_a[1]=='no':
                student_a.attend['yes']=''
                student_a.attend['no']='checked'
            else:
                student_a.attend['yes']=''
                student_a.attend['no']=''
            students_attend.append(student_a)
        dates_dict={}
        dates_dict['form']=['create']
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
    
@app.route('/student_profile/<student_id>', methods=['get', 'post'])
def student_profile(student_id):
    log=check_log()
    admin_dict=chek_admin()
    form2=["create"]
    email=crud.read_if('email','students', 'id', student_id)
    if request.method=='POST':
        new_password=request.form['new_password']
        crud.update_if('users', 'password', new_password, 'student_user', email[0][0])
        return redirect(url_for('student_profile', student_id=student_id))
    else:
        password=crud.read_if('password', 'users', 'student_user', email[0][0])
        if password[0][0]=='123456':
            return render_template('login.html', log=log, admin_dict=admin_dict, form2=form2, note='You need to change the initial password you received:')
        return render_template('home.html', log=log, admin_dict=admin_dict, hello= f"hello {crud.student_name(student_id)}") 

@app.route('/teacher_profile/<teacher_id>', methods=['get', 'post'])
def teacher_profile(teacher_id):
    log=check_log()
    admin_dict=chek_admin()
    form2=["create"]
    email=crud.read_if('email','teachers', 'id', teacher_id)
    if request.method=='POST':
        new_password=request.form['new_password']
        crud.update_if('users', 'password', new_password, 'teacher_user', email[0][0])
        return redirect(url_for('teacher_profile', teacher_id=teacher_id))
    else:
        password=crud.read_if('password', 'users', 'teacher_user', email[0][0])
        if password[0][0]=='123456':
            return render_template('login.html', log=log, admin_dict=admin_dict, form2=form2, note='You need to change the initial password you received:')
        return render_template('home.html', log=log, admin_dict=admin_dict, hello= f"hello {crud.teacher_name(teacher_id)}") 

@app.route('/messages')
def messages():
    all_messages=crud.read_all('messages')
    messages_list=[message[0] for message in all_messages]
    return messages_list

@app.route('/add', methods=['post'])
def add():
    crud.create('messages', 'message',request.json['message'] ) 
    return 'ok'

@app.route('/num_messages')
def num_messages():
    return str(len(crud.read_all('messages')))