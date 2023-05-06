from setup_db import query

def read_all(table):
    return query(f"SELECT * FROM {table}")

def read_if(column, table, value, condition):
    return query(f"SELECT {column} FROM {table} WHERE {value}='{condition}'")

def read_two_if(column, table, value1, condition1, value2, condition2):
    return query(f"SELECT {column} FROM {table} WHERE {value1}='{condition1}' and {value2}='{condition2}'")

def read_three_if(column, table, value1, condition1, value2, condition2, value3, condition3):
    return query(f"SELECT {column} FROM {table} WHERE {value1}='{condition1}' and {value2}='{condition2}' and {value3}='{condition3}'")

def read_or_two(column, table, value1, condition1, value2, condition2):
    return query(f"SELECT {column} FROM {table} WHERE {value1}='{condition1}' or {value2}='{condition2}'")

def read_like(column, table, value, condition):
    return query(f"SELECT {column} FROM {table} WHERE {value} LIKE '{condition}%'")

def create(table, column, values):
    return query(f"INSERT INTO {table} ({column}) VALUES ({values})")

def update_if(table, column, new_value, value, condition):
    return query(f"UPDATE {table} SET ({column})=({new_value}) WHERE {value}='{condition}'")

def update_three_if(table, column, new_value, value1, condition1, value2, condition2, value3, condition3):
    return query(f"UPDATE {table} SET ({column})=({new_value}) WHERE {value1}='{condition1}' and {value2}='{condition2}' and {value3} ='{condition3}'")

def student_name(student_id):
    name=read_if('name', 'students', 'id', student_id)
    name=name[0][0]
    return name

def teacher_name(teacher_id):
    name=read_if('name', 'teachers', 'id', teacher_id)
    name=name[0][0]
    return name

def course_name(course_id):
    name=read_if('name', 'courses', 'id', course_id)
    name=name[0][0]
    return name

def admin_name(admin_id):
    name=read_if('name', 'administrators', 'id', admin_id)
    name=name[0][0]
    return name

def student_id(email):
    '''get email and return id from students table'''
    name=read_if('id', 'students', 'email', email)
    name=name[0][0]
    return name

def teacher_id(email):
    '''get email and return id from teachers table'''
    name=read_if('id', 'teachers', 'email', email)
    name=name[0][0]
    return name

def get_id(table, value, condition):
    '''get user id'''
    user_id=read_if('id',table, value, condition)
    user_id=user_id[0][0]
    return user_id

def admin_id(email):
    '''get email and return id from administrators table'''
    name=read_if('id', 'administrators', 'email', email)
    name=name[0][0]
    return name

def change_grade(new_grade, student_id, course_id ):
    return query(f"UPDATE students_courses SET grade=({new_grade}) WHERE student_id='{student_id}' and course_id='{course_id}'")

def delete(table, value, condition):
    return query(f"DELETE FROM {table} WHERE {value}='{condition}'")