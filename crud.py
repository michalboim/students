from setup_db import query

def read_all(table):
    return query(f"SELECT * FROM {table}")

def read_if(column, table, value, condition):
    return query(f"SELECT {column} FROM {table} WHERE {value}='{condition}'")

def read_like(column, table, value, condition):
    return query(f"SELECT {column} FROM {table} WHERE {value} LIKE '{condition}%'")

def create(table, column, values):
    return query(f"INSERT INTO {table} ({column}) VALUES ({values})")

def update(table, column, new_value, tid):
    return query(f"UPDATE {table} SET ({column})=({new_value}) WHERE ID='{tid}'")

def student_name(student_id):
    name=read_if('name', 'students', 'id', student_id)
    name=name[0][0]
    return name
