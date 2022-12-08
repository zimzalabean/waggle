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

app.secret_key = 'your secret here'
# replace that with a random key
app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

@app.route('/login/', methods=['GET', 'POST'])
def login():
    """
    Login Page
    """
    if request.method == 'GET':
        return render_template('login_form.html')
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

@app.route('/')
def homepage():
    """
    Main page. For now, contains a feed of all posts from all Gaggles.
    """
    conn = dbi.connect()
    username = session.get('username', '')
    logged = session.get('logged_in', False)
    if logged == False:
        flash('You are not logged in. Please log in or join.')
        return redirect(url_for('login'))
    else:
        gaggles = waggle.getUserGaggle(conn, username)
        posts_info = waggle.getPosts(conn)
        return render_template('main.html', gaggles = gaggles, username=username, posts=posts_info)


@app.route('/deletePost/<post_id>/<author_id>/<gaggle_name>')
def deletePost(post_id, author_id, gaggle_name):
    """
    Called when user presses "delete" button on a post. The post gets deleted from the database if 
    the post was written by the logged in user.
    """
    username = session.get('username', '')
    user_id = session.get('user_id', '')
    logged = session.get('logged_in', False)
    if logged == False:
        flash('You are not logged in. Please log in or join')
        return redirect(url_for('login'))
    if user_id != int(author_id):
        flash('You are not authorized to delete this post/comment.')
        return redirect(url_for('homepage'))
    conn = dbi.connect()    
    deleted = waggle.deletePost(conn, post_id)
    flash('Deleted post with post_id {pid}'.format(pid=post_id))
    #print(request.referrer)
    #return redirect(url_for('homepage'))
    return redirect(url_for('gaggle', gaggle_name=gaggle_name)) #redirects back to the gaggle page


@app.route('/search/', methods=["GET"])
def search():
    """
    Called when user searches for a Gaggle in the search bar. Returns a page of Gaggles 
    that have a name matching the keyword search.
    """
    conn = dbi.connect()
    query = request.args.get('search-query')
    kind = request.args.get('submit')
    print(query)
    if kind is None:
        results = waggle.searchGaggle(conn, query)     
    elif kind == 'Posts':
        query = request.args.get('query')
        results = waggle.searchPost(conn, query)
    elif kind == 'Comments':
        query = request.args.get('query')
        results = waggle.searchComment(conn, query)
    elif kind == 'Goslings':
        query = request.args.get('query')
        results = waggle.searchPeople(conn, query)
    else:
        query = request.args.get('query')
        results = waggle.searchGaggle(conn, query)
    return render_template('testform.html', query = query, results = results, kind = kind) 


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
        posts = waggle.getGagglePosts(conn, gaggle_name)
        for post in posts:
            post_id = post['post_id']
            post['canDelete'] = canDeletePost(post_id, user_id)
        gaggle_id = waggle.getGaggleID(conn, gaggle_name)[0]['gaggle_id']
        joined  = waggle.isGosling(conn, user_id, gaggle_id)
        return render_template('group.html', gaggle = gaggle, posts = posts, joined = joined, username=username)

@app.route('/user/<username>')
def user(username):
    """
    Returns the profile page of the user with the given username.
    """
    conn = dbi.connect()
    user_id = session.get('user_id', '')
    gagglesCreated = waggle.getGagglesCreated(conn, user_id)
    gagglesJoined = waggle.getGagglesJoined(conn, user_id)
    return render_template('user.html', username=username, gagglesCreated=gagglesCreated, gagglesJoined=gagglesJoined)


@app.route('/user/<username>/history/')
def history(username):
    """
    Returns the post, comment, and like/dislike history of the user with the given username.
    """
    conn = dbi.connect()
    user_id = session.get('user_id', '')
    posts = waggle.getUserPosts(conn, username)
    for post in posts:
            post_id = post['post_id']
            post['canDelete'] = canDeletePost(post_id, user_id)
    return render_template('history.html', username = username, posts = posts)


@app.route('/newpost/', methods=["POST"])
def addPost():
    """
    Called when user clicks the 'post' button on a Gaggle page. Inserts a new row
    in the 'post' table in the database.
    """
    conn = dbi.connect()
    content = request.form.get('content')
    gaggle_id = request.form.get('gaggle_id')
    gaggle_name = request.form.get('gaggle_name')
    now = datetime.now()
    posted_date = now.strftime("%Y-%m-%d %H:%M:%S")
    if len(content) == 0:
        flash('Please enter some content.')
        return redirect(url_for('gaggle', gaggle_name=gaggle_name))
    else:
        poster_id = session.get('user_id', '')
        valid = waggle.isGosling(conn, poster_id, gaggle_id)
        if poster_id != '':
            if valid:
                try:
                    print(posted_date)
                    add = waggle.addPost(conn, gaggle_id, poster_id, content, None, posted_date)
                except Exception as e: 
                    print(e)
                    flash('Error:' +e)
            else:
                flash('You must be a gosling of this gaggle to perform this action.')
            return redirect(url_for('gaggle', gaggle_name=gaggle_name))    
        else:
            flash('You have been logged out.')
            return redirect(url_for('login'))

@app.route('/post/<post_id>/', methods=['GET', 'POST']) #add hyperlink from group.html to post
def post(post_id):
    """
    Returns the page for the specific post with the given post_id.
    """
    now = datetime.now()
    posted_date = now.strftime("%Y-%m-%d %H:%M:%S")
    user_id = session.get('user_id', '')
    if user_id == '':
        flash('You have been logged out.')
        return redirect(url_for('login'))      
    else:   
        conn = dbi.connect() 
        post = waggle.getPost(conn, post_id)
        post['canDelete'] = canDeletePost(post_id, user_id)
        gaggle_id = post['gaggle_id']
        comments = waggle.getPostComments(conn, post_id)
        valid = waggle.isGosling(conn, user_id, gaggle_id)
        if request.method == 'GET':
            return render_template('post.html', post = post, comments = comments, valid = valid)
        else:
            kind = request.form.get('submit')
            if kind == 'Comment':
                content = request.form['comment_content'] 
                parent_comment_id = None 
                add_comment = waggle.addComment(conn, post_id, parent_comment_id, content, user_id, posted_date)
            else:
                valid = waggle.likePost(conn, post_id, user_id, kind)
                if valid: 
                    print("updated")
                else:
                    flash("You have already {kind}d this post.".format(kind=kind))                    
            return redirect(url_for('post', post_id = post_id ))
    
@app.route('/likeComment/<post_id>/<comment_id>', methods=['GET', 'POST'])
def likeComment(post_id, comment_id):
    """
    Called when user clicks the 'like' button on a comment. Inserts a new row in the
    comment_like table in the database.
    """
    user_id = session.get('user_id', '')
    conn = dbi.connect() 
    post = waggle.getPost(conn, post_id)
    comments = waggle.getPostComments(conn, post_id)    
    if request.method == 'GET':  
        return render_template('post.html', post = post, comments = comments) 
    else:     
        kind = request.form.get('submit')
        valid = waggle.likeComment(conn, comment_id, user_id, kind)
        if valid: 
            print('updated comment like/dislike')
        else: 
            flash(f"You have already {kind}d this comment.".format(kind=kind))    
        return redirect( url_for('post', post_id = post_id ))

@app.route('/gaggle/<gaggle_name>/members/')
def gaggleMembers(gaggle_name):
    """
    Returns a page with list of all members of the Gaggle with the given name.
    """
    conn = dbi.connect() 
    members = waggle.getMembers(conn, gaggle_name)  
    return render_template('groupMembers.html', gaggle_name = gaggle_name, members = members) 

@app.route('/gaggle/<gaggle_name>/join/', methods=['GET', 'POST'])
def joinGaggle(gaggle_name):
    """
    Called when a user clicks on the 'join' button on a Gaggle page. Inserts a new row
    in the gosling table in the database. If user is already a member, then the
    button functions as an 'unjoin'.
    """
    conn = dbi.connect() 
    user_id = session.get('user_id', '')
    if user_id == '':
        flash('You have been logged out.')
        return redirect(url_for('login')) 
    else:
        if request.method == 'GET':
            return redirect(url_for('gaggle', gaggle_name = gaggle_name))      
        else:  
            gaggle_id = request.form.get('gaggle_id')
            if request.form.get('submit') == 'Join':
                action = waggle.joinGaggle(conn, user_id, gaggle_id)
                print(action)
            else: 
                action = waggle.unjoinGaggle(conn, user_id, gaggle_id) 
                print(action)              
            return redirect(url_for('gaggle', gaggle_name=gaggle_name))

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
    conn = dbi.connect()
    user_info = waggle.getUserInfo(conn, user_id)
    if request.method == 'GET':
        return render_template('edit_user_info.html', user=user_info)
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
            new_ln = request.form['first_name']
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
        flash('Your information was successfully updated.')
        return redirect(url_for('editMyPage'))
         
@app.route('/dashboard/', methods=['GET'])
def dashboard():
    """
    Show dashboard where you can choose to edit information about groups you've created or moderate your gaggles.
    """
    user_id = isLoggedIn()
    conn = dbi.connect() 
    gaggles = waggle.getGagglesCreated(conn, user_id)
    gaggle = gaggles[0]
    gaggle_id = gaggle['gaggle_id']
    invitees = waggle.getInvitees(conn, gaggle_id)
    return render_template('gaggleDashboard.html', gaggles = gaggles, gaggle = gaggle, invitees = invitees)

def getRepliesThread(comment_id, thread):  
    '''Helper function to get all the parent comment_id of the input comment_id.'''
    conn = dbi.connect() 
    parent_comment = waggle.getParentComment(conn, comment_id)
    print("current_thread" + str(thread))
    if len(parent_comment) == 0:
        return thread 
    else:
        parent_comment_id = parent_comment[0]['parent_comment_id'] 
        thread.append(parent_comment_id)
        return getRepliesThread(parent_comment_id, thread)

@app.route('/reply/<comment_id>', methods=['GET', 'POST'])
def addReply(comment_id):
    """
    Show original post and entire conversation thread of the comment you're replying to.
    Update the parent comment's replies when you reply. 
    """
    now = datetime.now()
    posted_date = now.strftime("%Y-%m-%d %H:%M:%S")
    user_id = session.get('user_id', '')
    if user_id == '':
        flash('You are logged out')
        return redirect(url_for('login'))      
    else:   
        conn = dbi.connect() 
        comment = waggle.getComment(conn, comment_id)[0]
        post_id = comment['post_id']
        post = waggle.getPost(conn, post_id)
        parent_comment_id = comment['comment_id']
        valid = canIntComment(parent_comment_id, user_id)
        replies = waggle.getReplies(conn, comment_id)
        thread = [parent_comment_id]
        chain = getRepliesThread(parent_comment_id, thread)
        comment_chain_id = [x for x in chain if x is not None][::-1]
        comment_chain = [waggle.getComment(conn, id)[0] for id in comment_chain_id]
        if request.method == 'GET':
            return render_template('reply.html', comment_chain = comment_chain, parent_comment = comment, replies = replies, post = post, valid = valid)
        else:
            kind = request.form.get('submit')
            if kind == 'Reply':
                content = request.form['comment_content']  
                add_comment = waggle.addComment(conn, post_id, parent_comment_id, content, user_id, posted_date)
            return redirect( url_for('addReply', comment_id = comment_id )) 


@app.route('/signup/', methods=['GET', 'POST'])
def signup():
    '''Sign up form '''
    if request.method == 'GET':
        return render_template('signup.html')
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
            flash("Signup success")
            return redirect(url_for('login'))
        else: 
            flash('Username already in use, please choose new one')
            return render_template('signup.html', email = email, password = password, first_name = first_name, last_name = last_name,class_year = class_year,bio_text = bio_text)

@app.route('/invitemod/', methods=['GET', 'POST'])
def inviteMod():
    '''Display gaggles you've created with the status of your mod invitation.
    Let you send mod invitation to users for your specified gaggle.'''
    user_id = isLoggedIn()
    conn = dbi.connect()     
    gaggles = waggle.getInvitees(conn, user_id)     
    if request.method == 'GET':
        return render_template('invite_mod.html', gaggles = gaggles)
    else: 
        invitee_username = request.form.get('invitee_username')
        gaggle_id = request.form.get('gaggle_id')
        validInvite = waggle.modInvite(conn, gaggle_id, invitee_username)
        if validInvite:
            flash('Invitation sent')
        else:
            flash('Invitation already pending')
        return redirect(url_for('inviteMod'))

def isLoggedIn():
    '''Helper function to determine if user is logged in'''
    user_id = session.get('user_id', '')
    if user_id == '':
        flash('You are logged out')
        return redirect(url_for('login'))   
    else:
        return user_id


@app.route('/invitation/', methods=['GET', 'POST'])
def response_invite():
    '''Display invitations to become moderators and let you respond.'''
    user_id = isLoggedIn()
    conn = dbi.connect() 
    invitations = waggle.getInvitation(conn, user_id)
    if request.method == 'GET':
        return render_template('invitation.html', invitations = invitations)
    else:
        response = request.form.get('submit')
        gaggle_id = request.form.get('gaggle_id')
        responded =  waggle.responseInvite(conn, gaggle_id, user_id, response)
        return redirect(url_for('response_invite'))  

def canDeletePost(post_id, user_id):
    '''
    Helper function to determine if current user can delete a post.
    Check if user_id is the author the post_id.
    '''
    conn = dbi.connect() 
    post = waggle.getPost(conn, post_id)
    poster_id = post['poster_id']
    if user_id == poster_id:
        return True
    else: 
        return False

def canIntComment(comment_id, user_id):
    '''
    Helper function to determine if current user can interact with the comment.
    Check if user_id is a member of the group that the comment was made in.
    '''
    conn = dbi.connect()
    gaggle_id = waggle.getCommentGaggle(conn, comment_id)
    valid = waggle.isGosling(conn, user_id, gaggle_id)
    return valid

@app.route('/<gaggle_name>/mod/users', methods=['GET', 'POST'])
def modUserList(gaggle_name):
    '''
    Display users who have strikes in group. 
    Allow you to ban/reinstate their access to the group.
    '''
    user_id = isLoggedIn()
    conn = dbi.connect() 
    gaggle_id = waggle.getGaggleID(conn, gaggle_name)[0]['gaggle_id']
    users = waggle.getBadUsers(conn, gaggle_id)
    if request.method == 'GET':
        return render_template('moderator.html', gaggle_name = gaggle_name, gaggle_id = gaggle_id, users = users)
    else:
        kind = request.form.get('submit')
        username = request.form.get('username')
        if kind == 'Ban':
            ban = waggle.banUser(conn, gaggle_id, username)
        else:
            reinstate = waggle.reinstateUser(conn, gaggle_id, username)    
        return redirect(url_for('modUserList', gaggle_name = gaggle_name))

@app.route('/modqueue/', methods=['GET', 'POST'])
def modqueue():
    logged_in = session.get('logged_in', False)
    if logged_in != False:
        user_id = session.get('user_id')
        gaggle_id = 'None'
        conn = dbi.connect()
        gaggles = waggle.getMyModGaggles(conn, user_id)
        if request.method == 'GET':
            return render_template('modqueue.html', gaggles=gaggles, gaggle_id=gaggle_id, flagged = [])
        else:
            gaggle_id = request.form.get('chosen_gaggle')
            flagged = waggle.get_flagged_posts(conn, gaggle_id)
            return render_template('modqueue.html', gaggles=gaggles, gaggle_id=gaggle_id, flagged = flagged)
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

@app.route('/flag_post/<post_id>/<author_id>/<gaggle_name>', methods=['GET', 'POST'])
def flagPost(post_id, author_id, gaggle_name):
    '''
    If a user is logged in then the function checks if they already reported this post,
    if not then it inserts a new flag into a flag_post table and updates
    flags count for a post in post table.
    '''
    logged_in = session.get('logged_in', False)
    if logged_in:
        reporter_id = session.get('user_id')
        conn = dbi.connect()
        curs = dbi.dict_cursor(conn)
        curs.execute('''SELECT *
                        FROM flag_post
                        WHERE post_id = %s and reporter_id = %s''',[post_id, reporter_id])
        res = curs.fetchone()
        if request.method == 'GET':
            if res is not None:
                flash('You have already reported this post')
                return redirect(request.referrer)
            else:
                return render_template('flag_post.html', post_id=post_id, author_id=author_id, gaggle_name=gaggle_name)
        else:
            flagged_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            reason = request.form['reason']
            print(res)
            #insert into flag_post table
            curs.execute('''insert into flag_post (post_id, reporter_id, reason, flagged_date, mod_aprroved)
                                values (%s,%s,%s,%s,'Pending')''',[post_id, reporter_id,reason,flagged_date])
            #update post table
            #curs.execute('''update post set flags=flags+1 where post_id=%s''', [post_id])
            conn.commit()
            flash('You have successfully reported a post {pid}'.format(pid=post_id))
            return redirect(url_for('gaggle', gaggle_name=gaggle_name))
    else:
        flash('You are not logged in. Please login or join.')
        return redirect(url_for('login'))

@app.route('/gaggle/search/', methods=["GET"])
def searchGaggle():
    """
    Called when user searches for a Gaggle in the search bar. Returns a page of Gaggles 
    that have a name matching the keyword search.
    """
    conn = dbi.connect()
    query = request.args.get('search-query')
    kind = request.args.get('submit')
    gaggle_id = request.args.get('gaggle_id')
    gaggle_name = request.args.get('gaggle_name')
    if kind is None:
        results = waggle.searchGaggle(conn, query)     
    elif kind == 'Posts':
        query = request.args.get('query')
        results = waggle.searchPost(conn, query)
    elif kind == 'Comments':
        query = request.args.get('query')
        results = waggle.searchComment(conn, query)
    else:
        query = request.args.get('query')
        results = waggle.searchPost(conn, query)
    return render_template('gaggleSearchResults.html', query = query, results = results, kind = kind, gaggle_id = gaggle_id, gaggle_name = gaggle_name) 

@app.route('/creator/', methods=['GET', 'POST'])
def createGaggle():
    '''
    Create gaggle.
    '''
    user_id = isLoggedIn()
    conn = dbi.connect() 
    if request.method == 'GET':
        return render_template('dashboard.html')
    else:
        gaggle_name = request.form.get('gaggle_name')           
        description = request.form.get('description') 
        if len(gaggle_name) > 0: 
            valid = waggle.updateBio(conn, user_id, gaggle_name, description)
            if valid:
                return redirect(url_for('gaggle', gaggle_name = gaggle_name))  
            else:
                flash("gaggle name already existed")
                return redirect(url_for('createGaggle'))
        else:
            flash('gaggle name cannot be empty')
            return redirect(url_for('createGaggle'))

@app.route('/creator/<gaggle_name>', methods=['GET', 'POST'])
def myGaggle(gaggle_name):
    '''
    Show gaggles you've created, toggle to change gaggle. Default view is first gaggle. 
    '''
    user_id = isLoggedIn()
    conn = dbi.connect() 
    gaggles = waggle.getGagglesCreated(conn, user_id)
    gaggle_id = waggle.getGaggleID(conn, gaggle_name)[0]['gaggle_id']
    invitees = waggle.getInvitees(conn, gaggle_id)
    gaggle = waggle.getGaggle(conn, gaggle_name)
    if request.method == 'GET':
        return render_template('gaggleDashboard.html', gaggles = gaggles, gaggle = gaggle, invitees = invitees)
    else:
        kind = request.form.get('submit')
        if kind == 'Change':
            gaggle_name = request.form.get('new_gaggle_name')           
        elif kind == 'Update':
            new_group_bio = request.form.get('content') 
            updated = waggle.updateBio(conn, gaggle_id, new_group_bio)
        else:
            invitee_username = request.form.get('invitee_username')
            validInvite = waggle.modInvite(conn, gaggle_id, invitee_username)
            if validInvite:
                flash('Invitation sent')
            else:
                flash('Invitation already pending')
        return redirect(url_for('myGaggle', gaggle_name = gaggle_name))        
                    

@app.before_first_request
def init_db():
    dbi.cache_cnf()
    # set this local variable to 'wmdb' or your personal or team db
    db_to_use = 'ldau_db' 
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
