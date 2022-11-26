import cs304dbi as dbi

# ==========================================================
# The functions that do most of the work.
def getUserID(conn, username):
    '''returns user_id based on username'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT user_id
        FROM user 
        WHERE username = %s''',
                 [username])
    return curs.fetchone()    

def getUserInfo(conn, user_id):
    '''returns user information based on user_id'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT first_name, last_name, class_year, bio_text
        FROM user
        WHERE user_id = %s''',
                 [user_id])
    return curs.fetchone()      

def getUserGaggle(conn,username):
    '''returns all gaggles that a user is a member of'''
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
    '''returns all gaggles whose names match the query'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT * from gaggle 
        WHERE gaggle_name LIKE %s''',
                 ["%"+query+"%"]) 
    return curs.fetchall()    

def getGaggle(conn, gaggle_name):
    '''returns information about a gaggle based on its gaggle_name'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT a.*, b.username
        FROM gaggle a
        LEFT JOIN user b
        ON (a.author_id = b.user_id)
        WHERE gaggle_name = %s''',
                 [gaggle_name])
    return curs.fetchone()      

def getGagglesOfAuthor(conn, user_id):
    '''returns all gaggles that a user has created'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        select * from gaggle where author_id = %s''', [user_id])
    return curs.fetchall()

def getPosts(conn):
    '''returns the latest 20 posts for homepage feed'''
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
    '''returns information about a post based on the post_id and its metrics. 
    We will optimize and modularize this function in alpha phase'''
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
    '''returns gaggle_id based on gaggle_name'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT gaggle_id
        FROM gaggle 
        WHERE gaggle_name = %s''',
                 [gaggle_name])
    return curs.fetchall()  

def getGagglePosts(conn, gaggle_name):
    '''returns all posts in a gaggle based on gaggle_name sorted by latest'''
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
    '''returns all comments on a post based on the post_id'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT a.*, b.username, c.num_likes, c.num_dislikes
        FROM comment a
        LEFT JOIN user b
        ON a.commentor_id = b.user_id
        LEFT JOIN comment_like_count c
        ON a.comment_id = c.comment_id
        WHERE parent_comment_id IS NULL 
        AND post_id = %s
        ORDER BY a.posted_date desc''',
                 [post_id])
    return curs.fetchall()      

def addComment(conn, post_id, parent_comment_id, content, commentor_id, posted_date):
    '''insert a new comment into the comment table'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        INSERT INTO comment(parent_comment_id, post_id, content, commentor_id, posted_date) 
        VALUES (%s,%s,%s,%s,%s) ''', 
                [parent_comment_id, post_id, content, commentor_id, posted_date])
    conn.commit()  # need this!   
    return commentor_id
  
def likePost(conn, post_id, user_id, kind):
    '''Record user's like/dislike of a post by 
    inserting the interaction into the post_like table'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        INSERT INTO post_like(post_id, user_id, kind) 
        VALUES (%s,%s,%s) ''', 
                [post_id, user_id, kind])
    conn.commit()  # need this!   
    return post_id     

def likeComment(conn, comment_id, user_id, kind):
    '''Record user's like/dislike of a comment by 
    inserting the interaction into the comment_like table'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        INSERT INTO comment_like(comment_id, user_id, kind) 
        VALUES (%s,%s,%s) ''', 
                [comment_id, user_id, kind])
    conn.commit()  # need this!   
    return comment_id  

def getMembers(conn, gaggle_name):
    '''returns all members of a gaggle based on the gaggle_name'''    
    curs = dbi.dict_cursor(conn)
    gaggle_id = getGaggleID(conn, gaggle_name)[0]['gaggle_id']
    curs.execute('''
        SELECT username
        FROM gosling 
        LEFT JOIN user 
        USING (user_id)
        WHERE gaggle_id = %s''',
                 [gaggle_id])
    return curs.fetchall()  

def hasLiked(conn, post_id, user_id):
    '''Checks if a user has liked a post'''
    curs = dbi.dict_cursor(conn)  
    curs.execute('''
        SELECT * from post_like 
        WHERE post_id = %s
        AND user_id = %s''',
                 [post_id, user_id]) 
    return curs.fetchall()    

def hasLikedComment(conn, comment_id, user_id):
    '''Checks if a user has liked a comment'''
    curs = dbi.dict_cursor(conn)  
    curs.execute('''
        SELECT * from comment_like 
        WHERE comment_id = %s
        AND user_id = %s''',
                 [comment_id, user_id]) 
    return curs.fetchall()  

def startCommentMetrics(conn, comment_id):
    '''Check if a comment has any like/dislike.
    Starts a new like/dislike count for a comment if it hasn't existed'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT * from comment_like 
        WHERE comment_id = %s''',
                 [comment_id])     
    result = curs.fetchall()
    if len(result) == 0:             
        curs.execute('''
            INSERT INTO comment_like_count(comment_id, num_likes, num_dislikes) 
            VALUES (%s,%s,%s) ''', 
                    [comment_id, 0, 0])
        conn.commit()  # need this!   
    return comment_id      

def commentMetrics(conn, comment_id):
    '''Returns number of likes and dislikes of a comment based on a comment_id'''
    curs = dbi.dict_cursor(conn)  
    curs.execute('''
        SELECT * from comment_like_count 
        WHERE comment_id = %s''',
                 [comment_id])     
    return curs.fetchall()  

def updateCommentMetrics(conn, comment_id, kind):
    '''Update number of likes and dislikes of a comment'''
    curs = dbi.dict_cursor(conn)  
    if kind == 'Like':
        curs.execute('''
            UPDATE comment_like_count SET num_likes = num_likes + 1 
            WHERE comment_id = %s''',
                    [comment_id]) 
    else:
        curs.execute('''
            UPDATE comment_like_count SET num_dislikes = num_dislikes + 1 
            WHERE comment_id = %s''',
                    [comment_id])            
    conn.commit()  
    return comment_id 

def joinGaggle(conn, user_id, gaggle_id):
    '''Add a user into a gaggle member list'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        INSERT INTO gosling(user_id, gaggle_id) 
        VALUES (%s,%s) ''', 
                [user_id, gaggle_id])
    conn.commit()  # need this!   
    return "Joined "

def unjoinGaggle(conn, user_id, gaggle_id):
    '''Remove a user into a gaggle member list'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        DELETE FROM gosling
        WHERE user_id = %s
        AND gaggle_id = %s''', 
                [ user_id, gaggle_id])
    conn.commit()  # need this!   
    return "Unjoined"

def isGosling(conn, user_id, gaggle_id):  
    '''Check if a user is in a gaggle member list'''  
    curs = dbi.dict_cursor(conn)  
    curs.execute('''
        SELECT * from gosling
        WHERE user_id = %s
        AND gaggle_id = %s''',
                 [user_id, gaggle_id])     
    return curs.fetchall()      

def addPost(conn, gaggle_id, poster_id, content, tag_id, posted_date ):
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        INSERT INTO post(gaggle_id, poster_id, content, tag_id, posted_date, likes, dislikes, flags) 
        VALUES(%s, %s, %s, %s, %s, 0, 0, 0)''',
                [gaggle_id, poster_id, content, tag_id, posted_date])
    conn.commit()
    return poster_id 


def getComment(conn, comment_id):
    curs = dbi.dict_cursor(conn)  
    curs.execute('''
        SELECT * 
        FROM comment
        WHERE comment_id = %s''',
                 [comment_id])     
    return curs.fetchall() 

def getReplies(conn, comment_id):  
    curs = dbi.dict_cursor(conn)  
    curs.execute('''
        SELECT * 
        FROM comment
        WHERE parent_comment_id = %s''',
                 [comment_id])     
    return curs.fetchall()    

def getParentComment(conn , comment_id):
    curs = dbi.dict_cursor(conn)  
    curs.execute('''
        SELECT parent_comment_id 
        FROM comment
        WHERE comment_id = %s''',
                 [comment_id]) 
    return curs.fetchall()
                   
def insertUser(conn, email,hashed_pass,username,first_name,last_name,class_year,bio_text,strike):
    curs = dbi.dict_cursor(conn)  
    curs.execute('''
        SELECT username
        FROM user
        WHERE username = %s''',
                 [username]) 
    exist = curs.fetchall()
    if len(exist) == 0:
        valid = True    
        curs.execute("""INSERT INTO user(email,hashed_pass,username,first_name,last_name,class_year,bio_text,strike)
                    VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""",
                    [email,hashed_pass,username,first_name,last_name,class_year,bio_text,strike])
        conn.commit()
    else:
        valid = False                 
    return valid 
