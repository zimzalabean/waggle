import os

os.system("mysql < create_user.sql")
os.system("python insert_users.py")
os.system("mysql < create_gaggle.sql")
os.system("mysql < create_comment.sql")
os.system("mysql < create_post_metrics.sql")
os.system("mysql < create_post_likes.sql")