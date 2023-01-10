import cs304dbi as dbi
from datetime import datetime, timedelta

# ==========================================================
# The functions that do most of the work.

def getUserInfo(conn, username):
    '''returns user information based on username'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT first_name, last_name, class_year, bio_text
        FROM user
        WHERE username = %s''',
                 [username])
    return curs.fetchone()      

def getUserGaggle(conn, username):
    '''returns all gaggles that a user is a member of'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT gaggle_name
        FROM gosling 
        WHERE username = %s''',
                 [username]) #Get a list of all gaggle
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
        SELECT *
        FROM gaggle
        WHERE gaggle_name = %s''',
                 [gaggle_name])
    return curs.fetchone()      

def getMembers(conn, gaggle_name):
    '''returns all members of a gaggle based on the gaggle_name'''    
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT username
        FROM gosling 
        WHERE gaggle_name = %s''',
                 [gaggle_name])
    return curs.fetchall()  

def getPosts(conn, username):
    '''returns the latest 20 posts for homepage feed'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        select a.*, d.filename, exists(select username from post_like where post_id = a.post_id and username = %s) as isLiked
        from post a
        LEFT JOIN post_pics d
        USING (post_id)
        WHERE a.hidden = 'No'
        order by posted_date DESC
    ''', [username])
    return curs.fetchall()

def getPost(conn, post_id, username):
    '''Get post and username and gaggle_name based on post_id
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT a.*, d.filename as pic, exists(select username from post_like where post_id = %s and username = %s) as isLiked
        FROM post a
        LEFT JOIN post_pics d
        ON (a.post_id = d.post_id)
        WHERE a.post_id = %s''',
                 [post_id, username, post_id])
    result = curs.fetchone()
    print(result)
    return result

def getGagglePosts(conn, gaggle_name, username):
    '''returns all posts in a gaggle based on gaggle_name sorted by latest'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT a.*, d.filename as pic, exists(select username from post_like where post_id = a.post_id and username = %s) as isLiked
        FROM post a
        LEFT JOIN post_pics d
        ON (a.post_id = d.post_id)
        WHERE a.gaggle_name = %s
        order by posted_date DESC''',
                 [username, gaggle_name])
    all_posts = curs.fetchall()
    return all_posts

def getPostComments(conn, post_id, username):
    '''returns all comments on a post based on the post_id'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT a.*, exists(select username from comment_like where comment_id = a.comment_id and username = %s) as isLiked
        FROM comment a
        WHERE parent_comment_id IS NULL 
        AND post_id = %s
        ORDER BY a.posted_date DESC''',
                 [username, post_id])
    return curs.fetchall()      

def addComment(conn, post_id, parent_comment_id, content, username, posted_date):
    '''insert a new comment into the comment table'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        INSERT INTO comment(post_id, parent_comment_id, content, username, posted_date) 
        VALUES (%s,%s,%s,%s,%s) ''', 
                [post_id, parent_comment_id, content, username, posted_date])
    conn.commit()  # need this!   
    curs.execute('SELECT last_insert_id() as new_comment_id') #retrieve new comment_id
    row = curs.fetchone()
    comment_id = row['new_comment_id']
    #if this is a reply to a post
    if parent_comment_id is None:
        curs.execute('''
            UPDATE post
            SET replies = replies + 1
            WHERE post_id = %s''',
                    [post_id])
    #else it is a reply to a comment                
    else:
        addConvo(conn, parent_comment_id, comment_id)
        curs.execute('''
            UPDATE comment
            SET replies = replies + 1
            WHERE comment_id = %s''',
                    [parent_comment_id])                        
    conn.commit()       
    return comment_id
  
def likePost(conn, post_id, username):
    '''Record user's like of a post by 
    inserting the interaction into the post_like table'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        INSERT INTO post_like(post_id, username) 
        VALUES (%s,%s) ''', 
                [post_id, username])
    conn.commit()  # need this!
    return updatePostMetrics(conn, post_id)
  

def likeComment(conn, comment_id, username):
    '''Record user's like of a comment by 
    inserting the interaction into the comment_like table'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        INSERT INTO comment_like(comment_id, username, kind) 
        VALUES (%s,%s,%s) ''', 
                [comment_id, username])         
    conn.commit()
    return updateCommentMetrics(conn, comment_id)        

def updateCommentMetrics(conn, comment_id):
    '''Update number of likes and dislikes of a comment'''
    curs = dbi.dict_cursor(conn)  
    curs.execute('''
        UPDATE comment
        SET likes = likes + 1
        WHERE comment_id = %s''',
                [comment_id])        
    conn.commit() 
    curs.execute('''
        SELECT comment_id, likes
        FROM comment
        WHERE comment_id = %s''',
                [comment_id])   
    result = curs.fetchone()
    return result

def updatePostMetrics(conn, post_id):
    '''Update number of likes and dislikes of a comment'''
    curs = dbi.dict_cursor(conn)  
    curs.execute('''
        UPDATE post
        SET likes = likes + 1
        WHERE post_id = %s''',
                [post_id])       
    conn.commit()  
    return post_id

def joinGaggle(conn, username, gaggle_name):
    '''Add a user into a gaggle member list'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        INSERT INTO gosling(username, gaggle_name) 
        VALUES (%s,%s) ''', 
                [username, gaggle_name])
    conn.commit()  # need this!   
    return {'gaggle_name':gaggle_name, 'result': 'Unjoin'}

def unjoinGaggle(conn, username, gaggle_name):
    '''Remove a user into a gaggle member list'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        DELETE FROM gosling
        WHERE username = %s
        AND gaggle_name = %s''', 
                [ username, gaggle_name])
    conn.commit()  # need this!   
    return {'gaggle_name':gaggle_name, 'result': 'Join'}

def isGosling(conn, username, gaggle_name):  
    '''Check if a user is in a gaggle member list'''  
    curs = dbi.dict_cursor(conn)  
    curs.execute('''
        SELECT a.username, b.unban_time
        FROM gosling a
        LEFT JOIN bad_gosling b
        USING (gaggle_name, username)
        WHERE username = %s
        AND gaggle_name = %s''',
                 [username, gaggle_name])   
    result = curs.fetchone()
    if result == None:
        return False
    else:
        unban_time = result['unban_time']
        if unban_time == None:
            return True
        elif unban_time < datetime.now():
            return True
        else:
            return False

def addPost(conn, gaggle_name, username, content, posted_date):
    '''
    Add new post into post table.
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        INSERT INTO post(gaggle_name, username, content, posted_date) 
        VALUES(%s, %s, %s, %s)''',
        [gaggle_name, username, content, posted_date])
    conn.commit()
    curs.execute('SELECT last_insert_id() as new_post_id') #retrieve new post_id
    row = curs.fetchone()
    post_id = row['new_post_id']
    return post_id 

def getComment(conn, comment_id, username):
    '''
    Retrieve comment info based on its comment_id.
    '''
    curs = dbi.dict_cursor(conn)  
    curs.execute('''
        SELECT a.*,  exists(select username from comment_like where comment_id = a.comment_id and username = %s) as isLiked
        FROM comment a
        WHERE a.comment_id = %s''',
                 [username, comment_id])     
    return curs.fetchone() 

def getReplies(conn, comment_id, username):  
    '''
    Retrieve replies to a comment based on its comment_id. 
    '''
    curs = dbi.dict_cursor(conn)  
    curs.execute('''
        SELECT a.*, exists(select username from comment_like where comment_id = a.comment_id and username = %s) as isLiked 
        FROM comment a
        WHERE a.parent_comment_id = %s
        ORDER BY posted_date desc''',
                 [username, comment_id])     
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

def getInvitees(conn, gaggle_name):
    '''
    Retrieve status of existing mod invitations for a gaggle based on its id. 
    '''
    curs = dbi.dict_cursor(conn)  
    curs.execute('''
        SELECT *
        FROM mod_invite 
        WHERE gaggle_name = %s
        ORDER BY posted_date''',
                [gaggle_name])  
    return curs.fetchall()

def modInvite(conn, gaggle_name, invitee, posted_date):
    '''
    Add valid username and corresponding gaggle_name into mod_invite table. 
    '''
    valid = False
    curs = dbi.dict_cursor(conn)  #check if user is already invited
    curs.execute('''
        SELECT *
        FROM mod_invite
        WHERE gaggle_name = %s
        AND invitee = %s''',
                 [gaggle_name, invitee]) 
    exists = curs.fetchall()
    if len(exists) == 0: #if not set invitation as pending
        if isGosling(conn, invitee, gaggle_name): #check if user is a group member
            valid = True
            curs.execute('''
                INSERT INTO mod_invite(gaggle_name, invitee, posted_date) 
                VALUES(%s,%s,%s)''',
                        [gaggle_name, invitee, posted_date])         
            conn.commit()  
            return valid
    return valid   

def getInvitation(conn, invitee):
    '''
    Retrieve mod invitations a user received.
    '''
    curs = dbi.dict_cursor(conn)  
    curs.execute('''
        SELECT gaggle_name
        FROM mod_invite 
        WHERE 
            status = 'Pending'
            AND invitee = %s''',
                 [invitee]) 
    return curs.fetchall()

def responseInvite(conn, gaggle_name, username, response):
    '''
    Update status of mod invitation response in mod_invite table.
    Add username and approriate gaggle_name into moderator table.
    '''
    curs = dbi.dict_cursor(conn)  
    curs.execute('''
        UPDATE mod_invite
        SET status = %s
        WHERE gaggle_name = %s
        AND invitee = %s''',
                [response, gaggle_name, username])
    conn.commit()  
    if response == 'Yes':
        curs.execute('''
            INSERT INTO moderator(gaggle_name, username)
            VALUES (%s, %s)''',
                        [gaggle_name, username]) 
        conn.commit()  
    return curs.fetchall()    

def searchPost(conn, query):
    '''returns all posts whose content match the query'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT *
        FROM post
        WHERE content LIKE %s''',
                 ["%"+query+"%"]) 
    return curs.fetchall() 

def searchComment(conn, query):
    '''returns all comments whose content match the query'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT *
        FROM comment
        WHERE content LIKE %s''',
                 ["%"+query+"%"]) 
    return curs.fetchall()   

def searchPeople(conn, query):
    '''returns all people whose names match the query'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT username from user 
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

def getBadUsers(conn, gaggle_name):
    '''
    Return users who have violation in the group.  
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT username 
        from bad_gosling
        WHERE gaggle_name = %s''',
                 [gaggle_name]) 
    return curs.fetchall()     

def banUser(conn, gaggle_name, username, reason, unban_time):
    '''
    Ban user from accessing the group
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        INSERT INTO bad_gosling(gaggle_name, username, reason, unban_time) VALUES (%s,%s,%s,%s)
        on duplicate key
        UPDATE reason = %s, unban_time = %s''',
                [gaggle_name, username, reason, unban_time, reason, unban_time])
    conn.commit()             
    return gaggle_name

def reinstateUser(conn, gaggle_name, username):
    '''
    Reinstate user from accessing the group
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        DELETE FROM bad_gosling
        WHERE gaggle_name = %s
        AND username = %s''',
                [gaggle_name, username])
    conn.commit()             
    return username

def getGagglesCreated(conn, username):
    '''
    Returns the gaggles that the username has created
    '''
    curs = dbi.dict_cursor(conn) 
    curs.execute('''select * from gaggle where author = %s''', [username])
    return curs.fetchall() 

# def getGagglesJoined(conn, username):
#     '''
#     Returns the gaggles that the username is apart of 
#     '''
#     curs = dbi.dict_cursor(conn)     
#     curs.execute('''
#         select * from gosling inner join gaggle
#         using (gaggle_name)
#         where username = %s
#         ''', [username])
#     return curs.fetchall()

def updateBio(conn, gaggle_name, new_group_bio):
    '''
        Edits gaggle's bio 
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        UPDATE gaggle
        SET description = %s
        WHERE gaggle_name = %s''',
                [new_group_bio, gaggle_name])
    conn.commit()
    return gaggle_name 

def updateGuidelines(conn, gaggle_name, position, new_group_guidelines):
    '''
        Edits gaggle's guidelines 
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        UPDATE gaggle
        SET guidelines = %s
        WHERE position = %s 
        AND gaggle_name = %s''',
                [new_group_guidelines, position, gaggle_name])
    conn.commit()
    return gaggle_name 

def createGaggle(conn, username, gaggle_name, description):
    '''
    Check if gaggle name is available, if so insert new gaggle in gaggle table
    '''
    curs = dbi.dict_cursor(conn)
    result = getGaggle(conn, gaggle_name)
    if result is None:
        valid = True
        curs.execute('''
            INSERT INTO gaggle(gaggle_name, author, description)
            VALUES(%s,%s,%s)''',
                    [gaggle_name, username, description])
        conn.commit()
    else:
        valid = False
    return valid

def getMyModGaggles(conn, username):
    '''
    Gets gaggles of which username is a mod of
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        select gaggle_name
        from moderator
        where username = %s
        ''', [username])
    return curs.fetchall()

def deleteGaggle(conn, gaggle_name):
    '''
    Delete gaggle based on its gaggle_name
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        DELETE FROM gaggle
        WHERE gaggle_name = %s''', [gaggle_name])
    conn.commit()    


def getCommentMetric(conn, comment_id):
    '''
    Return metrics of a comment based on its comment_id
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT comment_id, replies, likes 
        FROM comment
        WHERE comment_id = %s''', 
                [comment_id])   
    result = curs.fetchone()  
    return result

def getPostMetric(conn, post_id):
    '''
    Return metrics of a post based on its post_id
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT post_id, replies, likes 
        FROM post
        WHERE post_id = %s''', 
                [post_id])   
    result = curs.fetchone()  
    return result  

def getProfilePic(conn, username):
    '''
    Get user profile pic filename on their username 
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT filename FROM picfile 
        WHERE username = %s''',
        [username])
    return curs.fetchone()

def insertProfilePic(conn, username, filename):
    '''
    Insert new pic into user's profile table
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute(
                '''insert into picfile(username,filename) values (%s,%s)
                   on duplicate key update filename = %s''',
                [username, filename, filename])
    conn.commit()

def deactivateAccount(conn, username):
    '''
    Deactivate account and delete all data of a user based on their username
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        DELETE FROM 
        user
        WHERE username = %s''', [username])
    conn.commit()

def isAuthor(conn, username, gaggle_name):
    '''
    Check if this user is the author of this gaggle based on its gaggle_name
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT gaggle_name 
        FROM gaggle
        WHERE author = %s 
        AND gaggle_name = %s''',
        [username, gaggle_name])   
    if curs.fetchone() is None:
        return False
    else:
        return True   

def unlikeComment(conn, username, comment_id):
    '''Remove a user's like of a comment based on its comment_id
    and update like count '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        DELETE FROM comment_like
        WHERE 
        username = %s
        AND comment_id = %s''', 
                [username, comment_id])
    conn.commit()  # need this!   
    curs.execute('''
        UPDATE comment
        SET likes = likes - 1
        WHERE comment_id = %s''',
                [comment_id])
    conn.commit()
    print('decreases likes')
    return "Unliked"  

def unlikePost(conn, username, post_id):
    '''Remove a user's like of a post based on its post_id
    and update like count '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        DELETE FROM post_like
        WHERE 
        username = %s
        AND post_id = %s''', 
                [username, post_id])
    conn.commit()  # need this!   
    print('inserted')
    curs.execute('''
        UPDATE post
        SET likes = likes - 1
        WHERE post_id = %s''',
                [post_id])
    conn.commit()
    print('decreases likes')
    return "Unliked"

def getUserComments(conn, username):
    '''returns all of user's comments sorted by latest'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT a.*, b.username as username
        FROM comment a
        LEFT JOIN user b
        ON a.username = b.username
        WHERE username = %s
        ORDER BY posted_date desc
        ''', [username])
    all_comments = curs.fetchall()
    return all_comments

####_____To be used Functions for beta not yet tested_____#### 

def get_flagged_posts(conn, gaggle_name):
    '''
    Get flagged posts in a gaggle based on its gaggle_name
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        select a.*, b.content, b.username, c.username as reporter_username, d.username as reported_username
        from flag_post a
        left join post b 
        using (post_id)
        left join user c 
        on a.reporter_id = c.username
        left join user d
        ON b.username = d.username
        where b.gaggle_name = %s
        and a.mod_aprroved = 'Pending'
        order by a.flagged_date desc
        ''', [gaggle_name])
    return curs.fetchall()

def increment_flag(conn, post_id):
    '''
    Increment flag count for a post 
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        update post
        set flags = flags+1
        where post_id = %s
    ''', [post_id])
    conn.commit()

def increment_flag_reply(conn, comment_id):
    '''
    Increment flag count for a post 
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        update comment
        set flags = flags+1
        where comment_id = %s
    ''', [comment_id])
    conn.commit()


def increment_strikes(conn, username):
    '''
    Increment strikes count for a post
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        select strike
        from user
        where username = %s
    ''', [username])
    curr_strikes = curs.fetchone()['strike']
    res = ''
    if curr_strikes < 2:
        res = 'strike'
    else:
        res = 'ban'
    curs.execute('''
        update user
        set strike = strike+1
        where username = %s
    ''', [username])
    conn.commit()
    return res   

def getModOfGaggles(conn, gaggle_name):
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        select a.username, b.username
        from moderator a
        left join user b using (username)
        where gaggle_name = %s
    ''', [gaggle_name])
    return curs.fetchall()


def addNotif(conn, username, content, kind, source, id, noti_time, status):
    '''
    add notifications
    '''
    status = 'pending'
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        INSERT INTO notifs(username, content, kind, source, id, noti_time, status)
        VALUES(%s,%s,%s,%s,%s,%s,%s)''',
                [username, content, kind, source, id, noti_time, status])
    conn.commit()

def updateNotifStatus(conn, notif_id):
    status = 'seen'
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        UPDATE notifs set status = %s 
        WHERE notif_id = %s''',
                [status, notif_id])
    conn.commit()

def getNotifs(conn, username):
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT * 
        FROM notifs
        WHERE status = 'pending'
        AND username = %s''',
                [username])
    return curs.fetchall()    

def addConvo(conn, parent_comment_id, comment_id):
    curs = dbi.dict_cursor(conn)
    #insert the first parent-child relationship
    curs.execute('''    
    INSERT INTO convos(anc_id, des_id)
    VALUES (%s, %s)''',
                [parent_comment_id, comment_id])
    conn.commit()
    #find all ancestors of parent and add ancestor-descendant relationship
    curs.execute('''    
    INSERT INTO convos(anc_id, des_id)    
    SELECT c.anc_id, c.des_id FROM (
        SELECT a.anc_id, b.des_id
        FROM convos a
        LEFT JOIN convos b
        ON a.des_id = b.anc_id
        WHERE a.des_id = %s) c ''',
        [parent_comment_id])
    conn.commit()

def getConvo(conn, comment_id, username):
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT a.anc_id, b.*, c.username, exists(select username from comment_like where comment_id = b.comment_id and username = %s) as isLiked 
        FROM convos a
        LEFT JOIN comment b
        ON a.anc_id = b.comment_id
        LEFT JOIN user c
        ON b.username = c.username
        WHERE a.des_id = %s
        ORDER BY posted_date asc''',
                [username, comment_id])
    return curs.fetchall()        
   

def deleteComment(conn, comment_id, post_id):
    '''
    Delete comment 
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''delete
                    from comment
                    where comment_id = %s''',
                    [comment_id])
    conn.commit()
    curs.execute('''
            UPDATE post
            SET replies = replies - 1
            WHERE post_id = %s''',
                    [post_id])
    conn.commit()
    return comment_id

def getAllInvitees(conn, username):
    '''
    Returns all the invitees status sent by specified user
    '''
    curs = dbi.dict_cursor(conn)  
    curs.execute('''
        SELECT b.username, a.gaggle_name, a.status
        FROM mod_invite as a 
        LEFT JOIN user as b ON (a.invitee = b.username)
        LEFT JOIN gaggle c USING (gaggle_name)
        WHERE c.username_id= %s''',[username])  
    return curs.fetchall()

def getNotifsCount(conn, username):
    curs = dbi.dict_cursor(conn)  
    curs.execute('''
        SELECT COUNT(*) as count
        FROM notifs
        WHERE status = 'pending' 
        AND username= %s''',
                    [username])  
    result = curs.fetchone()    
    return result['count']

def report(conn,post_id, reporter_id,reason,flagged_date):
    '''insert a new report'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''insert into flag_post(post_id, reporter_id, reason, flagged_date, mod_aprroved)
                        values (%s,%s,%s,%s,'Pending')''',
                        [post_id, reporter_id,reason,flagged_date])
    conn.commit()  # need this! 
    increment_flag(conn, post_id)

def reportReply(conn,comment_id, reporter_id,reason,flagged_date):
    '''insert a new report'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''insert into flag_comment(comment_id, reporter_id, reason, flagged_date, mod_aprroved)
                        values (%s,%s,%s,%s,'Pending')''',
                        [comment_id, reporter_id,reason,flagged_date])
    conn.commit()  # need this! 
    increment_flag_reply(conn, comment_id)


def getReport(conn, report_id):
    '''
    get report
    '''
    curs = dbi.dict_cursor(conn)  
    curs.execute('''
        SELECT a.*, b.username
        FROM flag_post a
        LEFT JOIN user b
        ON a.reporter_id = b.username
        WHERE a.report_id= %s''',[report_id])  
    return curs.fetchone()    


def removeMod(conn, gaggle_name, username):
    '''Remove a user into a gaggle member list'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        DELETE FROM moderator
        WHERE username = %s
        AND gaggle_name = %s''', 
                [username, gaggle_name])
    conn.commit()  # need this!   
    return {'gaggle_name':gaggle_name, 'result': 'removed'}    

def removeInvite(conn, gaggle_name, username):
    '''Remove a user into a gaggle member list'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        DELETE FROM mod_invite
        WHERE invitee = %s
        AND gaggle_name = %s''', 
                [username, gaggle_name])
    conn.commit()  # need this!   
    return {'gaggle_name':gaggle_name, 'result': 'removed'}     


def isBanned(conn, username, gaggle_name):
    curs = dbi.dict_cursor(conn)  
    curs.execute('''
        SELECT username
        FROM bad_gosling
        WHERE username= %s
        AND gaggle_name = %s''',[username, gaggle_name])  
    result = curs.fetchone()  
    if result == None:
        return False
    return True


def modReview(conn, report_id, approval):
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        update flag_post
        set mod_aprroved = %s
        where report_id = %s
    ''', [approval, report_id])
    conn.commit()


def hidePost(conn, post_id):
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        INSERT INTO hidden_post(post_id) VALUES (%s)
        ''', [post_id])
    conn.commit() 


def hideComment(conn, comment_id):
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        INSERT INTO hidden_comment(comment_id) VALUES (%s)
        ''', [comment_id])
    conn.commit()       

def block(conn, username, blocked_username):
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        INSERT INTO blocked(username, blocked_username) VALUES (%s, %s)
        ''', [username, blocked_username])
    conn.commit() 

def isBlocked(conn, username, view_username):
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        select username from blocked where
        username = %s
        AND blocked_username = %s
        ''', [view_username, username])
    if curs.fetchone() != None:
        return True
    return False    


def bookmark(conn, username, post_id):
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        select username from bookmark 
        where username = %s
        AND post_id = %s''', 
                [username, post_id])   
    curs.execute('''
        INSERT INTO bookmark(username, post_id) 
        VALUES (%s,%s) ''', 
                [username, post_id])
    conn.commit()  # need this!   