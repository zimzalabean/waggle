import bcrypt
import cs304dbi as dbi

users = [{'email':'ldau@wellesley.edu', 'pass':'pass12345', 'username':'ldau', 'first_name':'Lan', 'last_name':'Dau', 
        'year':'2023', 'bio':'', 'strikes':0},
        {'email':'mp2@wellesley.edu', 'pass':'12345678', 'username':'mp2', 'first_name':'Malika', 'last_name':'Parkhomchuk', 
        'year':'2023', 'bio':'', 'strikes':0},
        {'email':'ab6@wellesley.edu', 'pass':'12345678', 'username':'ab6', 'first_name':'Anna', 'last_name':'Boland', 
        'year':'2024', 'bio':'', 'strikes':0},
        {'email':'ir101@wellesley.edu', 'pass':'ggez', 'username':'ir101', 'first_name':'Indira', 'last_name':'Ruslanova', 
        'year':'2025', 'bio':'', 'strikes':0},
        {'email':'hs1@wellesley.edu', 'pass':'passpass', 'username':'hs1', 'first_name':'Heidi', 'last_name':'Salgado', 
        'year':'2023', 'bio':'', 'strikes':0}]


def insert_users(conn):
    for user in users:
        hashed = bcrypt.hashpw(user['pass'].encode('utf-8'), bcrypt.gensalt())
        stored = hashed.decode('utf-8')
        curs = dbi.cursor(conn)
        try:
            curs.execute("""INSERT INTO user(user_id,email,hashed_pass,username,first_name,last_name,class_year,bio_text,strike)
                        VALUES(null,%s,%s,%s,%s,%s,%s,%s,%s)""",
                        [user['email'], stored, user['username'], user['first_name'], user['last_name'], user['year'], 
                        user['bio'],user['strikes']])
            conn.commit()
        except Exception as err:
            print('something went wrong', repr(err))


if __name__ == '__main__':
    dbi.cache_cnf()
    conn = dbi.connect()
    insert_users(conn)