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


@app.route('/deletePost/<post_id>/<author_id>', methods=['POST'])
def deletePost(post_id, author_id):
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
    curs = dbi.dict_cursor(conn)
    curs.execute('''delete
                    from post
                    where post_id = %s''',
                    [post_id])
    conn.commit()
    flash('Deleted post with post_id {pid}'.format(pid=post_id))
    return redirect(url_for('homepage'))


@app.route('/search/', methods=["GET"])
def search():
    """
    Called when user searches for a Gaggle in the search bar. Returns a page of Gaggles 
    that have a name matching the keyword search.
    """
    conn = dbi.connect()
    query = request.args.get('search-query')
    results = waggle.searchGaggle(conn, query)
    print(results)
    if len(results) == 0:
        flash('No result found.')
        return redirect(url_for('homepage'))
    else:
        return render_template('testform.html', query = query, results = results)  


@app.route('/gaggle/<gaggle_name>')
def gaggle(gaggle_name):
    """
    Returns the page for the Gaggle with the given name. Page displays all posts in that Gaggle.
    """
    user_id = session.get('user_id', '')
    if user_id == '':
        flash('You are logged out')
        return redirect(url_for('login')) 
    else: 
        conn = dbi.connect() 
        gaggle = waggle.getGaggle(conn, gaggle_name)  
        posts = waggle.getGagglePosts(conn, gaggle_name)
        gaggle_id = waggle.getGaggleID(conn, gaggle_name)[0]['gaggle_id']
        isGosling = waggle.isGosling(conn, user_id, gaggle_id)
        if len(isGosling) == 0:
            joined = False
        else:
            joined = True
        print(joined)
        return render_template('group.html', gaggle = gaggle, posts = posts, joined = joined) 


@app.route('/user/<username>')
def user(username):
    """
    Returns the profile page of the user with the given username.
    """
    conn = dbi.connect()
    gaggles = waggle.getUserGaggle(conn, username)
    return render_template('user.html', username=username, gaggles=gaggles)


@app.route('/newpost/<gaggle_name>/<gaggle_id>/', methods=["POST"])
def addPost(gaggle_name, gaggle_id):
    """
    Called when user clicks the 'post' button on a Gaggle page. Inserts a new row
    in the 'post' table in the database.
    """
    conn = dbi.connect()
    content = request.form.get('content')
    if len(content) == 0:
        flash('Please enter some content.')
        return redirect(url_for('gaggle', gaggle_name=gaggle_name))
    else:
        poster_id = session.get('user_id', '')
        if poster_id != '':
            now = datetime.now()
            posted_date = now.strftime("%Y-%m-%d %H:%M:%S")
            try:
                curs = dbi.dict_cursor(conn)
                curs.execute('''INSERT INTO post(gaggle_id, poster_id, content, tag_id, posted_date)
                                VALUES(%s, %s, %s, %s, %s)''',
                            [gaggle_id, poster_id, content, None, posted_date])
                conn.commit()
            except Exception as e: 
                print(e)
                flash('Error:' +e)
            return redirect(url_for('gaggle', gaggle_name=gaggle_name))
        else:
            flash('You have been logged out.')
            return redirect(url_for('login'))

@app.route('/post/<post_id>', methods=['GET', 'POST']) #add hyperlink from group.html to post
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
        post = waggle.getOnePost(conn, post_id)
        comments = waggle.getPostComments(conn, post_id)
        if request.method == 'GET':
            return render_template('post.html', post = post, comments = comments)
        else:
            print(request.form)
            kind = request.form.get('submit')
            if kind == 'Comment':
                content = request.form['comment_content']  
                add_comment = waggle.addComment(conn, post_id, content, user_id, posted_date)
            else: 
                hasLiked = waggle.hasLiked(conn, post_id, user_id)
                if len(hasLiked) == 0:
                    interaction = waggle.likePost(conn, post_id, user_id, kind)   
                else:
                    flash(f"You have already {kind}d this post.")     
            return redirect( url_for('post', post_id = post_id ))
    
@app.route('/likeComment/<post_id>/<comment_id>', methods=['GET', 'POST'])
def likeComment(post_id, comment_id):
    """
    Called when user clicks the 'like' button on a comment. Inserts a new row in the
    comment_like table in the database.
    """
    user_id = session.get('user_id', '')
    conn = dbi.connect() 
    post = waggle.getOnePost(conn, post_id)
    comments = waggle.getPostComments(conn, post_id)    
    if request.method == 'GET':  
        return render_template('post.html', post = post, comments = comments) 
    else:     
        kind = request.form.get('submit')
        display = waggle.startCommentMetrics(conn, comment_id)
        hasLiked = waggle.hasLikedComment(conn, comment_id, user_id)
        if len(hasLiked) == 0:
            interaction = waggle.likeComment(conn, comment_id, user_id, kind)
            update = waggle.updateCommentMetrics(conn, comment_id, kind)
        else: 
            flash(f"You have already {kind}d this comment.")    
        return redirect( url_for('post', post_id = post_id ))

@app.route('/gaggle/members/<gaggle_name>')
def gaggleMembers(gaggle_name):
    """
    Returns a page with list of all members of the Gaggle with the given name.
    """
    conn = dbi.connect() 
    members = waggle.getMembers(conn, gaggle_name)  
    return render_template('groupMembers.html', gaggle_name = gaggle_name, members = members) 

@app.route('/gaggle/join/<gaggle_id>/<gaggle_name>', methods=['GET', 'POST'])
def joinGaggle(gaggle_id, gaggle_name):
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
            return redirect(url_for('gaggle', gaggle_name=gaggle_name))      
        else:  
            print(request.form.get('submit'))
            print("ifelse")
            if request.form.get('submit') == 'Join':
                print('joining')
                action = waggle.joinGaggle(conn, user_id, gaggle_id)
                print(action)
            else: 
                print('unjoining')
                action = waggle.unjoinGaggle(conn, user_id, gaggle_id) 
                print(action)              
            return redirect(url_for('gaggle', gaggle_name=gaggle_name))

@app.route('/edit_my_page/', methods=['GET', 'POST'])
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
         
@app.route('/my_gaggles/', methods=['GET', 'POST'])
def showMyGaggles():
    """
    Returns a page with list of all Gaggles created by the user. The user can delete
    their Gaggles and create new ones (to be implemented).
    """
    #not finished
    user_id = session.get('user_id', '')
    if user_id == '':
        flash('You are not logged in. Please log in or join.')
        return redirect(url_for('login'))
    username=session.get('username', '')
    conn= dbi.connect()
    gaggles = waggle.getGagglesOfAuthor(conn, user_id)
    if request.method=='GET':
        return render_template('show_my_gaggles.html', username=username, gaggles=gaggles)
    else:
        flash('To be implemented')
        return redirect(url_for('showMyGaggles'))

@app.route('/new_gaggle/', methods=['GET', 'POST'])
def createGaggle():
    """
    To be implemented
    """
    flash('To be implemented')
    return redirect(url_for('showMyGaggles'))

@app.before_first_request
def init_db():
    dbi.cache_cnf()
    db_to_use = 'waggle_db' 
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
