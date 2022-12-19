import os

os.system("mysql < create_tables.sql")
os.system("python insert_users.py")
os.system("python insert_profilePics.py")
os.system("mysql < insert_data.sql")
os.system("python insert_postPics.py")
