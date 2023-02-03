from setup_db import query

def read_all(table):
    return query(f"SELECT * FROM {table}")

def read_if(column, table, value, condition):
    return query(f"SELECT {column} FROM {table} WHERE {value}={condition}")

def create(table, column, values):
    return query(f"INSERT INTO {table} ({column}) VALUES ({values})")

