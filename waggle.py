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

def searchGaggle(conn, query):
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT * from gaggle 
        WHERE gaggle_name LIKE %s''',
                 ["%"+query+"%"]) 
    return curs.fetchall()    

def getGaggle(conn, gaggle_name):
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT *
        FROM gaggle 
        WHERE gaggle_name = %s''',
                 [gaggle_name])
    return curs.fetchone()      


def getPosts(conn):
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        select * 
        from post 
        order by posted_date DESC
        limit 20 
    ''')
    posts = curs.fetchall()
    post_ids = [post['post_id'] for post in posts]
    all_posts = []
    for pid in post_ids:
        all_posts.append(getOnePost(conn, pid))
    return all_posts

def getOnePost(conn, post_id):
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        select * from post where post_id = %s
    ''', [post_id])
    post_info = curs.fetchone()
    curs.execute('''
        select count(*) as num
        from post_like
        where post_id = %s and kind = 'Like'
        group by user_id
    ''', [post_id])
    likes = curs.fetchone()
    curs.execute('''
        select count(*) as num
        from post_like
        where post_id = %s and kind = 'Dislike'
        group by user_id
    ''', [post_id])
    dislikes = curs.fetchone()
    curs.execute('''
        select username from user where user_id = %s
    ''', [post_info['poster_id']])
    author = curs.fetchone()
    curs.execute('''
        select gaggle_name from gaggle where gaggle_id = %s
    ''', [post_info['gaggle_id']])
    gaggle = curs.fetchone()
    if likes:
        post_info['likes'] = likes['num']
    else:
        post_info['likes'] = 0
    if dislikes:
        post_info['dislikes'] = dislikes['num']
    else:
        post_info['dislikes'] = 0
    post_info['author'] = author['username']
    post_info['gaggle'] = gaggle['gaggle_name']
    return post_info

def getGaggleID(conn, gaggle_name):
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT gaggle_id
        FROM gaggle 
        WHERE gaggle_name = %s''',
                 [gaggle_name])
    return curs.fetchall()  

def getGagglePosts(conn, gaggle_name):
    gaggle_id = getGaggleID(conn, gaggle_name)[0]['gaggle_id']
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT *
        FROM post
        WHERE gaggle_id = %s
        order by posted_date DESC''',
                 [gaggle_id])
    posts = curs.fetchall()
    post_ids = [post['post_id'] for post in posts]
    all_posts = []
    for pid in post_ids:
        all_posts.append(getOnePost(conn, pid))
    return all_posts

def getPostComments(conn, post_id):
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT *
        FROM comment
        WHERE parent_comment_id IS NULL 
        AND post_id = %s''',
                 [post_id])
    return curs.fetchall()      

def addComment(conn, post_id, content, commentor_id, posted_date):
    curs = dbi.cursor(conn)
    curs.execute('''
        INSERT INTO comment(post_id, content, commentor_id, posted_date) 
        VALUES (%s,%s,%s,%s) ''', 
                [post_id, content, commentor_id, posted_date])
    conn.commit()  # need this!   
    return commentor_id
  
def likePost(conn, post_id, user_id, kind):
    curs = dbi.cursor(conn)
    curs.execute('''
        INSERT INTO post_like(post_id, user_id, kind) 
        VALUES (%s,%s,%s,%s) ''', 
                [post_id, user_id, kind])
    conn.commit()  # need this!   
    return post_id     

def likeComment(conn, comment_id, user_id, kind):
    curs = dbi.cursor(conn)
    curs.execute('''
        INSERT INTO comment_like(post_id, user_id, kind) 
        VALUES (%s,%s,%s,%s) ''', 
                [comment_id, user_id, kind])
    conn.commit()  # need this!   
    return comment_id  