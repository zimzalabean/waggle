import cs304dbi as dbi

# ==========================================================
# The functions that do most of the work.
def getUserID(conn, username):
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT user_id
        FROM user 
        WHERE username = %s''',
                 [username])
    return curs.fetchone()    

def getUserGaggle(conn,username):
    '''Returns a dictionary of actors, with their name, nm (actor id), \
        and a list of movies they acted in, based in an actor's exact nm.
    '''
    user_id = getUserID(conn, username)['user_id']
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT a.gaggle_id, b.gaggle_name 
        FROM gosling a 
        LEFT JOIN gaggle b 
        USING (gaggle_id) 
        WHERE a.user_id = %s''',
                 [user_id]) #Get a list of all gaggle
    return curs.fetchall()

def getPosts(conn):
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        select * from post limit 20
    ''')
    return curs.fetchall()

def searchGaggle(conn, query):
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT * from gaggle 
        WHERE gaggle_name LIKE %s''',
                 ['%'+query+'%']) 
    return curs.fetchall()    

def getGaggle(conn, gaggle_name):
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT *
        FROM gaggle 
        WHERE gaggle_name = %s''',
                 [gaggle_name])
    return curs.fetchone()      