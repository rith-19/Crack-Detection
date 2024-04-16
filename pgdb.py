import psycopg2

params = {
    'host': 'localhost',
    'user': 'root',  
    'password': 'admin',  
    'port': '3306'  
}

connection = psycopg2.connect(**params)
connection.autocommit = True  
cursor = connection.cursor()

database_name = 'ProjectSave'
cursor.execute(f"CREATE DATABASE {database_name}")

cursor.close()
connection.close()
