import os

os.system("mysql < create_tables.sql")
os.system("python insert_users.py")
os.system("mysql < insert_data.sql")
