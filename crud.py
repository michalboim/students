from setup_db import query

def read_all(table):
    return query(f"SELECT * FROM {table}")

def read_if(column, table, value, condition):
    return query(f"SELECT {column} FROM {table} WHERE {value}='{condition}'")

def read_two_if(column, table, value1, condition1, value2, condition2):
    return query(f"SELECT {column} FROM {table} WHERE {value1}='{condition1}' and {value2}='{condition2}'")

def read_three_if(column, table, value1, condition1, value2, condition2, value3, condition3):
    return query(f"SELECT {column} FROM {table} WHERE {value1}='{condition1}' and {value2}='{condition2}' and {value3}='{condition3}'")

def read_like(column, table, value, condition):
    return query(f"SELECT {column} FROM {table} WHERE {value} LIKE '{condition}%'")

def create(table, column, values):
    return query(f"INSERT INTO {table} ({column}) VALUES ({values})")

def update_if(table, column, new_value, value, condition):
    return query(f"UPDATE {table} SET ({column})=({new_value}) WHERE {value}='{condition}'")

def update_three_if(table, column, new_value, value1, condition1, value2, condition2, value3, condition3):
    return query(f"UPDATE {table} SET ({column})=({new_value}) WHERE {value1}='{condition1}' and {value2}='{condition2}' and {value3}='{condition3}'")

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

def change_grade(new_grade, student_id, course_id ):
    return query(f"UPDATE students_courses SET grade=({new_grade}) WHERE student_id='{student_id}' and course_id='{course_id}'")