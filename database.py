import random
import pymysql
from db_config import host, user, password, db_name

try:
    connection = pymysql.connect(
        host=host,
        port=3306,
        user=user,
        password=password,
        database=db_name,
        cursorclass=pymysql.cursors.DictCursor
    )
    print("Connection was established.")
except Exception as exp:
    print(f"Connection wasn't established due to {exp}.")


def insert_into_table(table_name, longitude, latitude, capacity, input_capacity, output_capacity):
    with connection.cursor() as cursor:
        insert_query = f"INSERT INTO {table_name} (longitude, latitude, capacity, input_capacity, output_capacity)" \
                       f"VALUES ('{longitude}', '{latitude}', '{capacity}', '{input_capacity}', '{output_capacity}');"
        cursor.execute(insert_query)
        connection.commit()


def get_all_rows_from_table(table_name):
    with connection.cursor() as cursor:
        insert_query = f"SELECT * FROM {table_name};"
        cursor.execute(insert_query)
        return cursor.fetchall()


def get_column_row_from_db(table_name, column, id_name, id_value):
    connection.ping()
    with connection.cursor() as cursor:
        insert_query = f"SELECT {column} FROM {table_name} " \
                       f"WHERE {id_name} = {id_value};"
        cursor.execute(insert_query)
        return cursor.fetchone()[column]


def update_value_in_db(table_name, column, value, id_name, id_value, is_commit=False):
    connection.ping()
    try:
        with connection.cursor() as cursor:
            insert_query = f"UPDATE {table_name} " \
                           f"SET {column} = {value} " \
                           f"WHERE {id_name} = {id_value};"
            cursor.execute(insert_query)
            if is_commit:
                connection.commit()
    except:
        connection.rollback()


def get_random_coordinates(longitude_int, latitude_int,
                           longitude_boundary_lower, longitude_boundary_upper,
                           latitude_boundary_lower, latitude_boundary_upper) -> list:
    longitude = random.randint(longitude_boundary_lower, longitude_boundary_upper)
    latitude = random.randint(latitude_boundary_lower, latitude_boundary_upper)
    first_coordinate = longitude_int
    second_coordinate = latitude_int
    first_coordinate += longitude / (10 ** 6)
    second_coordinate += latitude / (10 ** 6)
    return [round(first_coordinate, 6), round(second_coordinate, 6)]
