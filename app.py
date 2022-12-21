from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
import bcrypt
from datetime import datetime
app = Flask(__name__)

# one or the other of these. Defaults to MySQL (PyMySQL)
# change comment characters to switch to SQLite

import cs304dbi as dbi
# import cs304dbi_sqlite3 as dbi
import waggle
import random
import json

app.secret_key = 'your secret here'
# replace that with a random key
app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

# For File Upload
app.config['UPLOADS'] = 'setup/uploads'
app.config['DEFAULT'] = 'setup/default'
app.config['MAX_CONTENT_LENGTH'] = 1*1024*1024 # 1 MB


####_____Login/Logout/Authorization Functions_____#### 

@app.route('/login/', methods=['GET', 'POST'])
def login():
    """
    Login Page
    """
    if request.method == 'GET':
        return render_template('login-bs.html')
    else:
        username = request.form['username']
        passwd = request.form['pass']
        conn = dbi.connect()
        curs = dbi.dict_cursor(conn)
        curs.execute('''SELECT user_id, hashed_pass
                        FROM user
                        WHERE username = %s''',
                    [username])
        row = curs.fetchone()
        if row is None:     # if username does not exist
            flash('Login incorrect. Try again or join.')
            return redirect(url_for('login'))
        stored = row['hashed_pass']
        hashed2 = bcrypt.hashpw(passwd.encode('utf-8'),stored.encode('utf-8'))
        hashed2_str = hashed2.decode('utf-8')
        if hashed2_str == stored:
            flash('successfully logged in as ' + username)
            session['username'] = username
            session['user_id'] = row['user_id']
            session['logged_in'] = True
            return redirect(url_for('homepage'))
        else:       # if password is incorrect
            flash('Login incorrect. Try again or join.')
            return redirect(url_for('login'))

@app.route('/logout/')
def logout():
    '''
    Logout Page
    '''
    try:
        if 'username' in session:
            username = session['username']
            session.pop('username')
            session.pop('user_id')
            session.pop('logged_in')
            flash('You have been logged out.')
            return redirect(url_for('login'))
        else:
            flash('You are not logged in. Please log in or join.')
            return redirect(url_for('login') )
    except Exception as err:
        flash('some kind of error '+str(err))
        return redirect( url_for('login'))

@app.route('/signup/', methods=['GET', 'POST'])
def signup():
    '''Sign up form '''
    if request.method == 'GET':
        return render_template('register.html')
    else: 
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')   
        first_name = request.form.get('first_name') 
        last_name = request.form.get('last_name') 
        class_year = request.form.get('class_year') 
        bio_text = request.form.get('bio_text') 
        strike = 0 
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        hashed_pass = hashed.decode('utf-8')
        conn = dbi.connect() 
        valid = waggle.insertUser(conn, email, hashed_pass, username, first_name, last_name, class_year, bio_text, strike)
        if valid:
            user_id = waggle.getUserID(conn, username)
            flash("Signup success")
            return redirect(url_for('login'))
        else: 
            flash('Username already in use, please choose new one')
            return render_template('register.html', email = email, password = password, first_name = first_name, last_name = last_name,class_year = class_year,bio_text = bio_text)

####_____Helper Functions_____#### 

def isLoggedIn():
    '''Helper function to determine if user is logged in'''
    user_id = session.get('user_id', '')
    if user_id == '':
        flash('You are logged out')
        return redirect(url_for('login'))   
    else:
        return user_id

def likedComments(user_id, comments):
    '''
    Take in a list of comments and check if if this user has liked these comments
    '''
    conn = dbi.connect() 
    likes = waggle.getLikedComments(conn, user_id)
    for comment in comments:
        comment_id = comment['comment_id']
        comment['isLiked'] = (comment_id in likes)
    return comments

def likedPosts(user_id, posts):
    '''
    Take in a list of comments and check if if this user has liked these comments
    '''
    conn = dbi.connect() 
    likes = waggle.getLikedPosts(conn, user_id)
    for post in posts:
        post_id = post['post_id']
        post['isLiked'] = (post_id in likes)
    return posts

def canDeletePosts(posts, user_id):
    '''
    Helper function to determine if current user can delete a post.
    Check if user_id is the author the post_id.
    '''
    conn = dbi.connect() 
    post_ids = waggle.getOwnPosts(conn, user_id)
    for post in posts:
        post_id = post['post_id']
        post['canDelete'] = (post_id in post_ids)
    return posts

# def getRepliesThread(comment_id, thread):  
#     '''Helper function to get all the parent comment_id of the input comment_id.'''
#     conn = dbi.connect() 
#     parent_comment = waggle.getParentComment(conn, comment_id)
#     print("current_thread" + str(thread))
#     if len(parent_comment) == 0:
#         return thread 
#     else:
#         parent_comment_id = parent_comment[0]['parent_comment_id'] 
#         thread.append(parent_comment_id)
#         return getRepliesThread(parent_comment_id, thread)

####_____Homepage Functions_____####

@app.route('/')
def homepage():
    """
    Main page. For now, contains a feed of all posts from all Gaggles.
    """
    conn = dbi.connect()
    user_id = isLoggedIn()
    username = session.get('username', '')
    logged = session.get('logged_in', False)
    if logged == False:
        flash('You are not logged in. Please log in or join.')
        return redirect(url_for('login'))
    else:
        gaggles = waggle.getUserGaggle(conn, username)
        posts_info = waggle.getPosts(conn)
        posts = likedPosts(user_id, canDeletePosts(posts_info, user_id))
        return render_template('main.html',  gaggles = gaggles, username=username, posts=posts, user_id = user_id)

####_____Search Functions_____####

@app.route('/search/', methods=["GET"])
def search():
    """
    Called when user searches for aanything in the search bar. Returns any matched 
    under different filter that have a name matching the keyword search.
    """
    conn = dbi.connect()
    user_id = isLoggedIn()
    query = request.args.get('search-query')
    gaggles = waggle.searchGaggle(conn, query)
    posts = waggle.searchPost(conn, query)
    comments = waggle.searchComment(conn, query)
    users = waggle.searchPeople(conn, query)
    return render_template('search-bs.html', query = query, gaggles = gaggles, posts = posts, comments = comments, users = users, user_id = user_id)

####_____Post Functions_____#### 

@app.route('/delete/post', methods=["POST"])
def removePost():
    """
    Called when user presses "delete" button on a post. The post gets deleted from the database if 
    the post was written by the logged in user.
    """
    user_id = isLoggedIn()
    data = request.get_json()
    post_id = data['post_id']
    print(post_id)
    conn = dbi.connect()    
    deleted_post_id = waggle.deletePost(conn, post_id)
    print(deleted_post_id)
    return jsonify({'post_id':deleted_post_id})   

@app.route('/user/<username>/history/')
def history(username):
    """
    Returns the post, comment, and like/dislike history of the user with the given username.
    """
    conn = dbi.connect()
    user_id = session.get('user_id', '')
    posts = canDeletePosts(waggle.getUserPosts(conn, username),user_id)
    posts = likedPosts(user_id, posts)
    comments = likedComments(user_id,waggle.getUserComments(conn, user_id))
    return render_template('history.html', username = username, posts = posts, comments = comments, user_id=user_id)

@app.route('/user/history/')
def personalHistory():
    """
    Returns the post, comment, and like/dislike history of the user with the given username.
    """
    conn = dbi.connect()
    user_id = isLoggedIn()
    username = session.get('username', '')
    return redirect(url_for('history', username = username))

@app.route('/addPost/', methods=["POST"])
def postGroup():
    """
    Called when user clicks the 'post' button on a Gaggle page. Inserts a new row
    in the 'post' table in the database.
    """
    conn = dbi.connect()
    user_id = isLoggedIn()
    #data = request.get_json()
    content = request.form.get('content')
    gaggle_id = request.form.get('gaggle_id')
    fname = request.files.get('postFile')
    print(fname)
    now = datetime.now()
    posted_date = now.strftime("%Y-%m-%d %H:%M:%S")
    if len(content) != 0:
        poster_id = session.get('user_id', '')
        post_id = waggle.addPost(conn, gaggle_id, poster_id, content, None, posted_date)
        ## ADD PIC ##
        if fname is not None:
            user_filename = fname.filename
            ext = user_filename.split('.')[-1]
            filename = secure_filename('post_{}.{}'.format(post_id,ext))
            pathname = os.path.join(app.config['UPLOADS'],filename)
            fname.save(pathname)
            conn = dbi.connect()
            curs = dbi.dict_cursor(conn)
            curs.execute(
                    '''insert into post_pics(post_id,filename) values (%s,%s)
                    on duplicate key update filename = %s''',
                    [post_id, filename, filename])
            conn.commit()
        #############
        post = waggle.getPost(conn, post_id)
        post['canDelete'] = True
        return jsonify({'new_post': render_template('new_post.html', new_post=post)})

@app.route('/addComment/', methods=["POST"])
def addComment():
    """
    Called when user clicks the 'Comment' button on a Gaggle page. Inserts a new row
    in the 'comment' table in the database.
    """
    conn = dbi.connect()
    data = request.get_json()
    content = data['content']
    post_id = data['post_id']
    now = datetime.now()
    posted_date = now.strftime("%Y-%m-%d %H:%M:%S")
    if len(content) != 0:
        commentor_id = session.get('user_id', '')
        comment_id = waggle.addComment(conn, post_id, None, content, commentor_id, posted_date)
        comment = waggle.getComment(conn, comment_id)
        return jsonify({'new_comment': render_template('new_comment.html', comment=comment)})         

@app.route('/deleteComment/', methods=["POST"])
def removeComment():
    user_id = isLoggedIn()
    data = request.get_json()
    comment_id = data['comment_id']
    conn = dbi.connect()    
    deleted_comment_id = waggle.deleteComment(conn, comment_id)
    print(deleted_comment_id)
    return jsonify({'comment_id':deleted_comment_id})


@app.route('/post/<post_id>/', methods=['GET']) #add hyperlink from group-bs.html to post
def post(post_id):
    """
    Returns the page for the specific post with the given post_id.
    """
    user_id = isLoggedIn()   
    username = session.get('username')
    conn = dbi.connect() 
    #get post infos and check user's previous interaction
    post = waggle.getPost(conn, post_id)
    post['canDelete'] = (user_id == post['poster_id'])
    post['isLiked'] = waggle.hasLikedPost(conn, user_id, post_id)
    gaggle_id = post['gaggle_id']
    #get gaggle from post
    curs = dbi.dict_cursor(conn)
    curs.execute('''SELECT *
                    FROM gaggle
                    WHERE gaggle_id = %s''',[gaggle_id])
    gaggle = curs.fetchone()
    #get post comments
    comments = likedComments(user_id, waggle.getPostComments(conn, post_id))
    valid = waggle.isGosling(conn, user_id, gaggle_id) #can user reply to post
    isAuthor = waggle.isAuthor(conn,user_id, gaggle_id)
    return render_template('post.html', post = post, comments = comments, valid = valid, username=username, user_id=user_id, isAuthor = isAuthor, gaggle = gaggle)

@app.route('/likePost/', methods=['POST'])
def likePost():
    """
    Receive a request from AJAX to modify a like status with a comment.
    AJAX send a data with comment_id and "kind" that indicate this is a Like or Unlike request
    """
    user_id = isLoggedIn()
    username = session.get('username','') #your username
    conn = dbi.connect()  
    if request.method == 'POST': 
        data = request.get_json()
        print(data)
        post_id = data['post_id']
        poster_id = data['poster_id']
        unliking = waggle.hasLikedPost(conn, user_id, post_id)
        if unliking: #User has liked a comment and is unliking it
            kind = 'Unlike'
            waggle.unlikePost(conn, user_id, post_id)
        else:
            kind = 'Like'
            waggle.likePost(conn, post_id, user_id, kind)
            notif = f"{username} has liked your post:"
            noti_time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            noti_kind = 'liked'
            source = 'post'
            status = 'pending'
            waggle.addNotif(conn, poster_id, notif, noti_kind, source, post_id, noti_time, status)
        metric = waggle.getPostMetric(conn, post_id)
        metric['kind'] = kind
        return jsonify(metric)

@app.route('/report/', methods=['POST'])
def report():
    '''
    If a user is logged in then the function checks if they already reported this post,
    if not then it inserts a new flag into a flag_post table and updates
    flags count for a post in post table.
    '''
    reporter_id = isLoggedIn()
    username = session.get('username')
    data = request.get_json()
    post_id = data['post_id']
    reason = data['reason']
    print(reason)
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    curs.execute('''SELECT *
                    FROM flag_post
                    WHERE post_id = %s and reporter_id = %s''',[post_id, reporter_id])
    res = curs.fetchone()
    # if res is not None: 
    flagged_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #insert into flag_post table
    curs.execute('''insert into flag_post (post_id, reporter_id, reason, flagged_date, mod_aprroved)
                        values (%s,%s,%s,%s,'Pending')''',[post_id, reporter_id,reason,flagged_date])
    conn.commit()
    print('reported')
    return jsonify({'reported': post_id, 'reason': reason})

####_____Comment/Replies Functions_____####
@app.route('/likeComment/', methods=['POST'])
def likeComment(): #if comment isn't liked then insert like else unlike
    """
    Receive a request from AJAX to modify a like status with a comment.
    AJAX send a data with comment_id and "kind" that indicate this is a Like or Unlike request
    """    
    user_id = isLoggedIn()
    username = session.get('username','')
    conn = dbi.connect()  
    if request.method == 'POST': 
        data = request.get_json()
        comment_id = data['comment_id']
        unliking = waggle.hasLikedCmt(conn, user_id, comment_id)
        if unliking: #User has liked a comment and is unliking it
            kind = 'Unlike'
            waggle.unlikeComment(conn, user_id, comment_id)
        else:
            kind = 'Like'
            waggle.likeComment(conn, comment_id, user_id, kind)
            commentor_id = data['commentor_id']
            notif = f"{username} has liked your reply:"
            noti_time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            noti_kind = 'liked'
            source = 'comment'
            status = 'pending'
            waggle.addNotif(conn, commentor_id, notif, noti_kind, source, comment_id, noti_time, status)
        metric = waggle.getCommentMetric(conn, comment_id)
        metric['kind'] = kind
        print(metric)
        return jsonify(metric)

@app.route('/reply/<comment_id>', methods=['GET', 'POST'])
def addReply(comment_id):
    """
    Show original post and entire conversation thread of the comment you're replying to.
    Update the parent comment's replies when you reply. 
    """
    posted_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_id = isLoggedIn()   
    username = session.get('username')
    conn = dbi.connect() 
    #=============================================
    # get information about the comment and check if current user has liked it
    comment = waggle.getComment(conn, comment_id)
    comment['isLiked'] = waggle.hasLikedCmt(conn, user_id, comment_id)
    #==============================================
    # get the post the comment originates from
    post_id = comment['post_id']
    post = waggle.getPost(conn, post_id)
    gaggle_id = post['gaggle_id']
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT *
        FROM gaggle
        WHERE gaggle_id = %s''',
                 [gaggle_id]) 
    gaggle = curs.fetchone() 
    isAuthor = waggle.isAuthor(conn,user_id, gaggle_id)
    #=============================================
    comment_chain = likedComments(user_id, waggle.getConvo(conn, comment_id)) #this is the previous comment chain
    replies = likedComments(user_id, waggle.getReplies(conn, comment_id))
    if request.method == 'GET':
        return render_template('reply.html', gaggle = gaggle, comment_chain = comment_chain, parent_comment = comment, replies = replies, post = post, username=username, user_id = user_id, isAuthor = isAuthor)
    else: #reply
        kind = request.form.get('submit')
        content = request.form['comment_content']  
        parent_comment_id = comment['comment_id']
        add_comment = waggle.addComment(conn, post_id, parent_comment_id, content, user_id, posted_date)
        return redirect( url_for('addReply', comment_id = comment_id )) 


####_____User Profile Functions_____#### 

@app.route('/user/edit/', methods=['GET', 'POST'])
def editMyPage():
    """
    Returns a page where a user can edit their profile information.
    Updates the user table in the database.
    """
    user_id = session.get('user_id', '')
    if user_id == '':
        flash('You are not logged in. Please log in or join.')
        return redirect(url_for('login'))
    username = session.get('username')
    conn = dbi.connect()
    user_info = waggle.getUserInfo(conn, user_id)
    if request.method == 'GET':
        return render_template('edit_account_info-bs.html', user=user_info, username=username,user_id=user_id)
        # return render_template('edit_user_info.html', user=user_info, username=username,user_id=user_id)

    else:
        new_fn, new_ln, new_cy, new_bio = '', '', '', ''
        if request.form['first_name'] != '':
            new_fn = request.form['first_name']
            curs = dbi.dict_cursor(conn)
            curs.execute('''UPDATE user
                            SET first_name = %s
                            WHERE user_id = %s''',
                        [new_fn,user_id])
            conn.commit()
        if request.form['last_name'] != '':
            new_ln = request.form['last_name']
            curs = dbi.dict_cursor(conn)
            curs.execute('''UPDATE user
                            SET last_name = %s
                            WHERE user_id = %s''',
                        [new_ln,user_id])
            conn.commit()
        if request.form['class_year'] != '':
            new_cy = request.form['class_year']
            curs = dbi.dict_cursor(conn)
            curs.execute('''UPDATE user 
                            SET class_year = %s
                            WHERE user_id = %s''',
                        [new_cy,user_id])
            conn.commit()
        if request.form['bio_text'] != '':
            new_bio = request.form['bio_text']
            curs = dbi.dict_cursor(conn)
            curs.execute('''UPDATE user
                            SET bio_text = %s
                            WHERE user_id = %s''',
                        [new_bio,user_id])
            conn.commit()
        

@app.route('/upload/', methods=["GET", "POST"])
def file_upload():
    '''
    Allow user to upload their file and insert it into the database (profile picture specifically)
    '''
    user_id = session.get('user_id', '')
    if user_id == '':
        flash('You are not logged in. Please log in or join.')
        return redirect(url_for('login'))
    username = session.get('username')
    conn = dbi.connect()    
    if request.method == 'GET':
        return redirect(url_for('editMyPage'))
    else:
        try:
            imageFile = request.files['pic']
            user_filename = imageFile.filename
            ext = user_filename.split('.')[-1]
            filename = secure_filename('{}.{}'.format(user_id,ext))
            pathname = os.path.join(app.config['UPLOADS'],filename)
            imageFile.save(pathname)
            waggle.insertProfilePic(conn, user_id, filename)
            flash('Upload successful.')
            return redirect(url_for('editMyPage'))
        except Exception as err:
            flash('Upload failed: {why}'.format(why=err))
            return redirect(url_for('editMyPage'))
   
@app.route('/user/<username>')
def user(username):
    """
    Returns the profile page of the user with the given username.
    """
    conn = dbi.connect()
    user_id = isLoggedIn() #get current_user id
    uid = waggle.getUserID(conn, username)['user_id'] #get uid of person in question
    gagglesCreated = waggle.getGagglesCreated(conn, uid)
    gagglesJoined = waggle.getGagglesJoined(conn, uid)
    for gaggle in gagglesJoined:
        gaggle['isAuthor'] = waggle.isAuthor(conn, uid, gaggle['gaggle_id'])
    userInfo = waggle.getUserInfo(conn, uid)
    isPersonal = False
    if user_id == uid: #if uid of person in question matches current user
        isPersonal = True
    return render_template('user-bs.html', username=username, gagglesCreated=gagglesCreated, gagglesJoined=gagglesJoined, isPersonal = isPersonal, userInformation=userInfo, user_id=uid)

@app.route('/profile/')
def profile():
    """
    Returns the profile page of the user logged in
    """
    username = session.get('username')
    return redirect(url_for('user', username=username))

@app.route('/pic/<user_id>')
def profilePic(user_id):
    """
    Retrieves the profile pic of the user from the database or the default photo
    """
    conn = dbi.connect()
    profilePic = waggle.getProfilePic(conn, user_id)
    if(profilePic is None): #sets the default photo if user's profile pic doesn't exist
        filename = 'profile.jpeg'
        return send_from_directory(app.config['DEFAULT'],filename)
    else: 
        return send_from_directory(app.config['UPLOADS'], profilePic['filename'])

@app.route('/post_pic/<filename>')
def postPic(filename):
    """
    Retrieves the profile pic of the user from the database or the default photo
    """
    conn = dbi.connect()
    if filename is not None:
        return send_from_directory(app.config['UPLOADS'],filename)
    
def canIntComment(comment_id, user_id):
    '''
    Helper function to determine if current user can interact with the comment.
    Check if user_id is a member of the group that the comment was made in.
    '''
    conn = dbi.connect()
    gaggle_id = waggle.getCommentGaggle(conn, comment_id)
    valid = waggle.isGosling(conn, user_id, gaggle_id)
    return valid


@app.route('/blockUser/<username>', methods=["POST"])
def blockUser(username):
    pass

@app.route('/deactivate/')
def deactivateAccount():
    '''
    Deactivate account
    ''' 
    conn = dbi.connect()
    try:
        uid = session['user_id']
        deleted = waggle.deactivateAccount(conn, uid)
        if 'username' in session:
            username = session['username']
            session.pop('username')
            session.pop('user_id')
            session.pop('logged_in')
            return redirect(url_for('login'))
    except Exception as err:
        flash('some kind of error '+str(err))
        return redirect( url_for('login'))


####_____Gaggle Functions_____#### 

@app.route('/gaggle/<gaggle_name>')
def gaggle(gaggle_name):
    """
    Returns the page for the Gaggle with the given name. Page displays all posts in that Gaggle.
    """
    user_id = session.get('user_id', '')
    username = session.get('username', '')
    logged = session.get('logged_in', False)
    if user_id == '':
        flash('You are logged out')
        return redirect(url_for('login')) 
    else: 
        conn = dbi.connect() 
        gaggle = waggle.getGaggle(conn, gaggle_name) 
        print(gaggle['guidelines']) 
        if gaggle['guidelines'] is None:
            gaggle['guidelines'] = 'No guidelines specified for this gaggle.'
        posts = likedPosts(user_id, waggle.getGagglePosts(conn, gaggle_name))
        print(gaggle['guidelines'])
        posts = canDeletePosts(posts, user_id)
        gaggle_id = waggle.getGaggleID(conn, gaggle_name)['gaggle_id']
        joined  = waggle.isGosling(conn, user_id, gaggle_id)
        isAuthor = waggle.isAuthor(conn,user_id, gaggle_id)
        mods = waggle.getModOfGaggles(conn, gaggle_id)
        return render_template('group-bs.html', gaggle = gaggle, posts = posts, joined = joined, isAuthor = isAuthor, username=username, user_id = user_id, mods=mods)

@app.route('/gaggle/<gaggle_name>/members/')
def gaggleMembers(gaggle_name):
    """
    Returns a page with list of all members of the Gaggle with the given name.
    """
    user_id = isLoggedIn()
    conn = dbi.connect() 
    members = waggle.getMembers(conn, gaggle_name)  
    username = session.get('username')
    return render_template('members-bs.html', gaggle_name = gaggle_name, members = members, username=username, user_id = user_id) 

@app.route('/gaggle/join/', methods=['POST'])
def joinGroup():
    """
    Called when a user clicks on the 'join' button on a Gaggle page. Inserts a new row
    in the gosling table in the database. If user is already a member, then the
    button functions as an 'unjoin'.
    """
    conn = dbi.connect() 
    user_id = isLoggedIn()    
    data = request.get_json()
    print(data)
    gaggle_id = data['gaggle_id']
    print(gaggle_id)
    if waggle.isGosling(conn, user_id, gaggle_id):
        action = waggle.unjoinGaggle(conn, user_id, gaggle_id) 
    else: 
        action = waggle.joinGaggle(conn, user_id, gaggle_id)      
    print(action)         
    return jsonify(action)

@app.route('/creator/<gaggle_name>', methods=['GET', 'POST'])
def editGaggle(gaggle_name):
    '''
    Edit Gaggle information 
    '''
    conn = dbi.connect() 
    if request.method == 'GET':
        return redirect(url_for('dashboard'))
    else:
        new_bio, new_guidelines = '', ''
        gaggle_id = waggle.getGaggleID(conn, gaggle_name)['gaggle_id']
        if request.form['description'] != '':
            new_bio = request.form['description']
            waggle.updateBio(conn, gaggle_id, new_bio)
        if request.form['guidelines'] != '':
            new_guidelines = request.form['guidelines']
            waggle.updateGuidelines(conn, gaggle_id, new_guidelines)
        flash('Your information was successfully updated.')
        return redirect(url_for('dashboard')) 

@app.route('/inviteUser/<gaggle_name>', methods=['POST'])
def inviteUser(gaggle_name):
    conn = dbi.connect() 
    invitee_username = ''
    if request.form['invitee_username'] != '':
        invitee_username = request.form['invitee_username']
        gaggle_id = waggle.getGaggleID(conn, gaggle_name)['gaggle_id']
        validInvite = waggle.modInvite(conn, gaggle_id, invitee_username)
        if validInvite:
            flash('Invitation sent')
        else:
            flash('Invitation already pending or User is not apart of gaggle group')
    return redirect(url_for('dashboard'))
    

@app.route('/delete/<gaggle_id>', methods=['GET', 'POST'])
def deleteGaggle(gaggle_id):
    '''
    Deletes gaggle.
    '''
    user_id = isLoggedIn()
    username = session.get('username',)
    conn = dbi.connect() 
    gagglesCreated = waggle.getGagglesCreated(conn, user_id)
    gagglesJoined = waggle.getGagglesJoined(conn, user_id)
    isPersonal = True
    if request.method == 'GET':
        return render_template('user-bs.html', username=username, gagglesCreated=gagglesCreated, gagglesJoined=gagglesJoined, isPersonal = isPersonal, user_id = user_id)
    else:
        delete = waggle.deleteGaggle(conn, gaggle_id)
        flash('Successfully deleted gaggle')
        return redirect(url_for('user', username = username))

@app.route('/creator/', methods=['GET', 'POST'])
def createGaggle():
    '''
    Create gaggle.
    '''
    user_id = isLoggedIn()
    conn = dbi.connect() 
    username = session.get('username')
    if request.method == 'GET':
        return render_template('createGaggleForm.html', user_id = user_id, username = username)
    else:
        gaggle_name = request.form.get('gaggle_name')           
        description = request.form.get('description') 
        if len(gaggle_name) > 0: 
            valid = waggle.createGaggle(conn, user_id, gaggle_name, description)
            if valid:
                gaggle_id = waggle.getGaggleID(conn, gaggle_name)['gaggle_id']
                action = waggle.joinGaggle(conn, user_id, gaggle_id)
                return redirect(url_for('gaggle', gaggle_name = gaggle_name))  
            else:
                flash("gaggle name already existed")
                return render_template('createGaggleForm.html', user_id = user_id, username = username)
        else:
            flash('gaggle name cannot be empty')
            return render_template('createGaggleForm.html', user_id = user_id, username = username)

@app.route('/unjoinGaggle/<username>/<gaggle_id>/<gaggle_name>', methods=['POST'])
def unJoinGaggle(username,gaggle_id, gaggle_name):
    """
    Removes user from the Gaggle member list
    """
    conn = dbi.connect()
    user_id = session.get('user_id', '')
    logged = session.get('logged_in', False)
    if logged == False:
        flash('You are not logged in. Please log in or join')
        return redirect(url_for('login'))
    deleted = waggle.unjoinGaggle(conn, user_id, gaggle_id) 
    flash('Successfully left {gaggle_name}'.format(gaggle_name=gaggle_name))
    return redirect(url_for('user', username=username)) 


####_____Moderator Functions to be implemented in beta phase not tested _____####

@app.route('/invitemod/', methods=['GET', 'POST'])
def inviteMod():
    '''Display gaggles you've created with the status of your mod invitation.
    Let you send mod invitation to users for your specified gaggle.'''
    user_id = isLoggedIn()
    username = session.get('username')
    conn = dbi.connect()     
    gaggles = waggle.getInvitees(conn, user_id)     
    if request.method == 'GET':
        return render_template('invite_mod.html', gaggles = gaggles, username=username, user_id = user_id)
    else: 
        invitee_username = request.form.get('invitee_username')
        gaggle_id = request.form.get('gaggle_id')
        validInvite = waggle.modInvite(conn, gaggle_id, user_id, invitee_username)
        if validInvite:
            flash('Invitation sent')
        else:
            flash('Invitation already pending')
        return redirect(url_for('inviteMod'))

@app.route('/modqueue/', methods=['GET', 'POST'])
def modqueue():
    logged_in = session.get('logged_in', False)
    if logged_in != False:
        username = session.get('username')
        user_id = session.get('user_id')
        
        conn = dbi.connect()
        gaggles = waggle.getMyModGaggles(conn, user_id)
        if len(gaggles) > 0:
            gaggle_id = gaggles[0]['gaggle_id']
            flagged = waggle.get_flagged_posts(conn, gaggle_id)
            pending, approved = [], []
            for flag in flagged:
                if flag['mod_aprroved']=='Pending':
                    pending.append(flag)
                else:
                    approved.append(flag)
            if request.method == 'POST':
                gaggle_id, gaggle_name = request.form.get('chosen_gaggle').split('_')[0], request.form.get('chosen_gaggle').split('_')[1]
                flagged = waggle.get_flagged_posts(conn, gaggle_id)
                pending, approved = [], []
                for flag in flagged:
                    if flag['mod_aprroved']=='Pending':
                        pending.append(flag)
                    else:
                        approved.append(flag)
            else:
                gaggle_name = gaggles[0]['gaggle_name']
            return render_template('modqueue.html', gaggles=gaggles, gaggle_id=gaggle_id, pending = pending, approved = approved, username=username, user_id = user_id, chosenGaggle = gaggle_name)
        else:
            flash('You are not a moderator yet')
            return redirect(request.referrer)
    else:
        flash('You are not logged in. Please login or join.')
        return redirect(url_for('login'))

@app.route('/modapprove/<post_id>/<reported_user_id>', methods=['POST'])
def modapprove(post_id, reported_user_id):
    approval = request.form.get('submit')
    conn = dbi.connect()
    if approval == 'Yes':
        curs = dbi.dict_cursor(conn)
        curs.execute('''
            update flag_post
            set mod_aprroved = 'Yes'
            where post_id = %s and reporter_id = %s
        ''', [post_id, reported_user_id])
        conn.commit()
        waggle.increment_flag(conn, post_id)
        res = waggle.increment_strikes(conn, reported_user_id)
        if res == 'ban':
            flash('user needs to get banned')
    else:
        curs = dbi.dict_cursor(conn)
        curs.execute('''
            update flag_post
            set mod_aprroved = 'No'
            where post_id = %s and reporter_id = %s
        ''', [post_id, reported_user_id])
        conn.commit()
    return redirect(url_for('modqueue'))

@app.route('/invitation/', methods=['GET', 'POST'])
def response_invite():
    '''Display invitations to become moderators and let you respond.'''
    user_id = isLoggedIn()
    conn = dbi.connect() 
    invitations = waggle.getInvitation(conn, user_id)
    if request.method == 'GET':
        return render_template('invitation.html', invitations = invitations, user_id = user_id)
    else:
        response = request.form.get('submit')
        gaggle_id = request.form.get('gaggle_id')
        responded =  waggle.responseInvite(conn, gaggle_id, user_id, response)
        return redirect(url_for('response_invite'))  

@app.route('/notif/', methods=['GET','POST'])
def notif():
    ''' View notifications '''
    user_id = isLoggedIn()
    conn = dbi.connect()
    username = session.get('username', '')
    notifs = formatNotif(waggle.getNotifs(conn, user_id))
    if request.method == 'GET':
        return render_template('notifications.html', notifs = notifs, user_id = user_id, username = username)
    else:
        data = request.get_json()
        notif_id = data['notif_id']
        #check if notif is already seen in case duplicating
        curs = dbi.dict_cursor(conn)
        curs.execute('''
        SELECT status from notifs
        WHERE notif_id = %s''',
                [notif_id])
        result = curs.fetchone()
        if result['status'] == 'pending':        
            waggle.updateNotifStatus(conn, notif_id)
            return jsonify({'result': 'updated', 'notif_id': notif_id})
        else:
            return 'ok'


def formatNotif(notifs):
    conn = dbi.connect() 
    for notif in notifs:
        source = notif['source']
        kind = notif['kind']
        source_id = notif['id']
        if kind == 'liked':
            if source == 'comment':
                comment = waggle.getComment(conn, source_id)
                content = comment['content']
            else:
                post = waggle.getPost(conn, source_id)
                content = post['content']
        else: #has to be a comment       
            reply = waggle.getComment(conn, source_id)
            content = reply['content']
        preview = content    
        if len(content) > 280: #shorten preview
            preview = content[:280] + "..."
        notif['preview'] = preview
    return notifs        


####_____Moderator/Creator Functions_____####

@app.route('/dashboard/', methods=['GET'])
def dashboard():
    """
    Show dashboard where you can choose to edit information about groups you've created or moderate your gaggles.
    """
    user_id = isLoggedIn()
    conn = dbi.connect() 
    username = session.get('username', '')
    hasGaggle = False  
    gaggles = waggle.getGagglesCreated(conn, user_id)
    if len(gaggles) > 0:
        gaggle = gaggles[0]
        gaggle_id = gaggle['gaggle_id']         
        hasGaggle = True
    else:
        flash('You are not a creator of any gaggles yet. Want to create one?')
        return redirect(url_for('createGaggle'))
    if request.method == 'GET':
        return render_template('dashboard.html', hasGaggle = hasGaggle, gaggles = gaggles, gaggle = gaggle, user_id = user_id, username = username)


@app.before_first_request
def init_db():
    dbi.cache_cnf()
    # set this local variable to 'wmdb' or your personal or team db
    db_to_use = 'ab6_db' 
    dbi.use(db_to_use)
    print('will connect to {}'.format(db_to_use))

if __name__ == '__main__':
    import sys, os
    if len(sys.argv) > 1:
        # arg, if any, is the desired port number
        port = int(sys.argv[1])
        assert(port>1024)
    else:
        port = os.getuid()
    app.debug = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run('0.0.0.0',port)
