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

def getUserPosts(conn, username):
    '''returns all of a user's posts sorted by latest'''
    user_id = getUserID(conn, username)['user_id']
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT a.*, b.username as author, c.gaggle_name as gaggle
        FROM post a
        LEFT JOIN user b
        ON (a.poster_id = b.user_id)
        LEFT JOIN gaggle c
        ON (a.gaggle_id = c.gaggle_id)
        WHERE poster_id = %s
        order by posted_date DESC''',
                 [user_id])
    all_posts = curs.fetchall()
    # post_ids = [post['post_id'] for post in posts]
    # all_posts = []
    # for pid in post_ids:
    #     all_posts.append(getPost(conn, pid))
    return all_posts

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
        select a.*, b.username as author, c.gaggle_name as gaggle 
        from post a
        left join user b
        on (a.poster_id = b.user_id)
        left join gaggle c
        on (a.gaggle_id = c.gaggle_id)
        order by posted_date DESC
        limit 20 
    ''')
    return curs.fetchall()

def getPost(conn, post_id):
    '''Get post and username and gaggle_name based on post_id
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT a.*, b.username as author, c.gaggle_name as gaggle
        FROM post a
        LEFT JOIN user b
        ON (a.poster_id = b.user_id)
        LEFT JOIN gaggle c
        ON (a.gaggle_id = c.gaggle_id)
        WHERE a.post_id = %s''',
                 [post_id])
    result = curs.fetchone()
    return result

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
        SELECT a.*, b.username as author, c.gaggle_name as gaggle
        FROM post a
        LEFT JOIN user b
        ON (a.poster_id = b.user_id)
        LEFT JOIN gaggle c
        ON (a.gaggle_id = c.gaggle_id)
        WHERE c.gaggle_id = %s
        order by posted_date DESC''',
                 [gaggle_id])
    all_posts = curs.fetchall()
    #post_ids = [post['post_id'] for post in posts]
    #all_posts = []
    #for pid in post_ids:
        #all_posts.append(getPost(conn, pid))
    return all_posts

def getPostComments(conn, post_id):
    '''returns all comments on a post based on the post_id'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT a.*, b.username
        FROM comment a
        LEFT JOIN user b
        ON a.commentor_id = b.user_id
        WHERE parent_comment_id IS NULL 
        AND post_id = %s
        ORDER BY a.posted_date DESC''',
                 [post_id])
    return curs.fetchall()      

def addComment(conn, post_id, parent_comment_id, content, commentor_id, posted_date):
    '''insert a new comment into the comment table'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        INSERT INTO comment(post_id, parent_comment_id, content, commentor_id, posted_date, likes, dislikes, flags) 
        VALUES (%s,%s,%s,%s,%s,0,0,0) ''', 
                [post_id, parent_comment_id, content, commentor_id, posted_date])
    conn.commit()  # need this!   
    return commentor_id
  
def likePost(conn, post_id, user_id, kind):
    '''Record user's like/dislike of a post by 
    inserting the interaction into the post_like table'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT * FROM post_like
        WHERE post_id = %s
        AND user_id = %s''', 
                [post_id, user_id])
    exists = curs.fetchall()
    if len(exists) == 0:
        valid = True
        curs.execute('''
            INSERT INTO post_like(post_id, user_id, kind) 
            VALUES (%s,%s,%s) ''', 
                    [post_id, user_id, kind])
        conn.commit()  # need this!
        updatePostMetrics(conn, post_id, kind)
    else:
        if exists[0]['kind'] != kind:
            #if there is a like/dislike already but the user wants to change it to the opposite value
            valid = True
            curs.execute('''update post_like
                        set kind= %s
                        where post_id=%s and user_id=%s''', [kind, post_id, user_id])
            if kind == 'Like':
                #increment like and decrement dislike
                curs.execute('''
                    UPDATE post
                    SET likes = likes + 1, dislikes = dislikes - 1
                    WHERE post_id = %s''',
                            [post_id])
            else:
                #increment dislike and decrement like
                curs.execute('''
                    UPDATE post
                    SET likes = likes - 1, dislikes = dislikes + 1
                    WHERE post_id = %s''',
                            [post_id])
            conn.commit()
        else:
            valid = False
    return valid   

def likeComment(conn, comment_id, user_id, kind):
    '''Record user's like/dislike of a comment by 
    inserting the interaction into the comment_like table'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT * FROM comment_like 
        WHERE comment_id = %s
        AND user_id = %s''', 
                [comment_id, user_id])
    exists = curs.fetchall()
    if len(exists) == 0:
        valid = True
        curs.execute('''
            INSERT INTO comment_like(comment_id, user_id, kind) 
            VALUES (%s,%s,%s) ''', 
                    [comment_id, user_id, kind])         
        conn.commit()
        updateCommentMetrics(conn, comment_id, kind)  
    else:
        if exists[0]['kind'] != kind:
            valid = True
            curs.execute('''update comment_like
                        set kind= %s
                        where comment_id=%s and user_id=%s''', [kind, comment_id, user_id])
            if kind == 'Like':
                #increment like and decrement dislike
                curs.execute('''
                    UPDATE comment
                    SET likes = likes + 1, dislikes = dislikes - 1
                    WHERE comment_id = %s''',
                            [comment_id])
            else:
                #increment dislike and decrement like
                curs.execute('''
                    UPDATE comment
                    SET likes = likes - 1, dislikes = dislikes + 1
                    WHERE comment_id = %s''',
                            [comment_id])
            conn.commit()
        else:
            valid = False
    return valid 

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
     
def commentMetrics(conn, comment_id):
    '''Returns number of likes and dislikes of a comment based on a comment_id'''
    curs = dbi.dict_cursor(conn)  
    curs.execute('''
        SELECT likes, dislikes from comment
        WHERE comment_id = %s''',
                 [comment_id])     
    return curs.fetchall()

def updateCommentMetrics(conn, comment_id, kind):
    '''Update number of likes and dislikes of a comment'''
    curs = dbi.dict_cursor(conn)  
    if kind == 'Like':
        curs.execute('''
            UPDATE comment
            SET likes = likes + 1
            WHERE comment_id = %s''',
                    [comment_id])
    else:
        curs.execute('''
            UPDATE comment
            SET dislikes = dislikes + 1 
            WHERE comment_id = %s''',
                    [comment_id])            
    conn.commit()  
    return comment_id 

def updatePostMetrics(conn, post_id, kind):
    '''Update number of likes and dislikes of a comment'''
    curs = dbi.dict_cursor(conn)  
    if kind == 'Like':
        curs.execute('''
            UPDATE post
            SET likes = likes + 1
            WHERE post_id = %s''',
                    [post_id])
    else:
        curs.execute('''
            UPDATE post
            SET dislikes = dislikes + 1 
            WHERE post_id = %s''',
                    [post_id])            
    conn.commit()  
    return post_id

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
    result = len(curs.fetchall())
    if result == 0:
        return False
    else:
        return True   

def addPost(conn, gaggle_id, poster_id, content, tag_id, posted_date):
    '''
    Add new post into post table.
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        INSERT INTO post(gaggle_id, poster_id, content, tag_id, posted_date, likes, dislikes, flags) 
        VALUES(%s, %s, %s, %s, %s, 0, 0, 0)''',
        [gaggle_id, poster_id, content, tag_id, posted_date])
    conn.commit()
    return poster_id 


def getComment(conn, comment_id):
    '''
    Retrieve comment info based on its comment_id.
    '''
    curs = dbi.dict_cursor(conn)  
    curs.execute('''
        SELECT * 
        FROM comment
        WHERE comment_id = %s''',
                 [comment_id])     
    return curs.fetchall() 

def getReplies(conn, comment_id):  
    '''
    Retrieve replies to a comment based on its comment_id. 
    '''
    curs = dbi.dict_cursor(conn)  
    curs.execute('''
        SELECT * 
        FROM comment
        WHERE parent_comment_id = %s''',
                 [comment_id])     
    return curs.fetchall()    

def getParentComment(conn , comment_id):
    '''
    Retrieve parent comment of a reply based on its comment_id.
    '''
    curs = dbi.dict_cursor(conn)  
    curs.execute('''
        SELECT parent_comment_id 
        FROM comment
        WHERE comment_id = %s''',
                 [comment_id]) 
    return curs.fetchall()
                   
def insertUser(conn, email,hashed_pass,username,first_name,last_name,class_year,bio_text,strike):
    '''
    Add user information into the user table. 
    '''
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

def getInvitees(conn, user_id):
    '''
    Retrieve status of existing mod invitations. 
    '''
    curs = dbi.dict_cursor(conn)  
    gaggles = getGagglesOfAuthor(conn, user_id)  
    for gaggle in gaggles:
        curs.execute('''
            SELECT b.username, a.accepted 
            FROM 
            mod_invite a
            LEFT JOIN user b
            ON (a.invitee_id = b.user_id)
            WHERE a.gaggle_id= %s''',
                    [gaggle['gaggle_id']]) 
        gaggle['invitees'] = curs.fetchall()          
    return gaggles

def modInvite(conn, gaggle_id, username):
    '''
    Add valid username and corresponding gaggle_id into mod_invite table. 
    '''
    invitee_id = getUserID(conn, username)['user_id']
    curs = dbi.dict_cursor(conn)  
    curs.execute('''
        SELECT *
        FROM mod_invite
        WHERE gaggle_id = %s
        AND invitee_id = %s''',
                 [gaggle_id, invitee_id]) 
    exists = curs.fetchall()
    if len(exists) == 0:
        valid = True
        accepted = 'Pending'
        curs.execute('''
            INSERT INTO mod_invite(gaggle_id, invitee_id, accepted) 
            VALUES(%s,%s, %s)''',
                    [gaggle_id, invitee_id, accepted])         
        conn.commit()  
    else:
        valid = False 
    return valid   

def getInvitation(conn, invitee_id):
    '''
    Retrieve mod invitations a user received.
    '''
    curs = dbi.dict_cursor(conn)  
    curs.execute('''
        SELECT a.gaggle_id, b.gaggle_name
        FROM mod_invite a 
        LEFT JOIN gaggle b 
        USING (gaggle_id)
        WHERE 
            a.accepted = 'Pending'
            AND a.invitee_id = %s''',
                 [invitee_id]) 
    return curs.fetchall()

def responseInvite(conn, gaggle_id, user_id, response):
    '''
    Update status of mod invitation response in mod_invite table.
    Add user_id and approriate gaggle_id into moderator table.
    '''
    curs = dbi.dict_cursor(conn)  
    curs.execute('''
        UPDATE mod_invite
        SET accepted = %s
        WHERE gaggle_id = %s
        AND invitee_id = %s''',
                [response, gaggle_id, user_id])
    conn.commit()  
    if response == 'Yes':
        curs.execute('''
            INSERT INTO moderator(gaggle_id, user_id)
            VALUES (%s, %s)''',
                        [gaggle_id, user_id]) 
        conn.commit()  
    return curs.fetchall()    

def searchPost(conn, query):
    '''returns all posts whose content match the query'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT * from post 
        WHERE content LIKE %s''',
                 ["%"+query+"%"]) 
    return curs.fetchall() 

def searchComment(conn, query):
    '''returns all comments whose content match the query'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT * from comment
        WHERE content LIKE %s''',
                 ["%"+query+"%"]) 
    return curs.fetchall()   

def searchPeople(conn, query):
    '''returns all people whose names match the query'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT * from user 
        WHERE username LIKE %s''',
                 ["%"+query+"%"]) 
    return curs.fetchall()   

def deletePost(conn, post_id):
    '''
    Delete post
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''delete
                    from post
                    where post_id = %s''',
                    [post_id])
    conn.commit()
    return post_id

def getBadUsers(conn, gaggle_id):
    '''
    Return users who have violation in the group.  
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT * from bad_gosling
        WHERE gaggle_id = %s''',
                 [gaggle_id]) 
    return curs.fetchall()     

def banUser(conn, gaggle_id, username):
    '''
    Ban user from accessing the group
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        UPDATE bad_gosling
        SET ban_status = 'Yes'
        WHERE gaggle_id = %s
        AND username = %s''',
                [gaggle_id, username])
    conn.commit()             
    return username

def reinstateUser(conn, gaggle_id, username):
    '''
    Reinstate user from accessing the group
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        UPDATE bad_gosling
        SET ban_status = 'No'
        WHERE gaggle_id = %s
        AND username = %s''',
                [gaggle_id, username])
    conn.commit()             
    return username

def getCommentGaggle(conn, comment_id):
    '''Return gaggle this comment is from'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT b.gaggle_id 
        FROM comment a
        LEFT JOIN post b
        USING (post_id)
        WHERE a.comment_id = %s''',
                 [comment_id]) 
    result = curs.fetchall()  
    return result[0]['gaggle_id']