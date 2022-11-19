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
    if request.method == 'GET':
        return render_template('login_form.html')
    else:
        username=request.form['username']
        passwd=request.form['pass']
        conn = dbi.connect()
        curs = dbi.dict_cursor(conn)
        curs.execute('''SELECT user_id,hashed_pass
                        FROM user
                        WHERE username = %s''',
                    [username])
        row = curs.fetchone()
        if row is None:
            # Same response as wrong password,
            # so no information about what went wrong
            flash('login incorrect. Try again or join')
            return redirect(url_for('login'))
        stored = row['hashed_pass']
        hashed2 = bcrypt.hashpw(passwd.encode('utf-8'),stored.encode('utf-8'))
        hashed2_str = hashed2.decode('utf-8')
        if hashed2_str == stored:
            flash('successfully logged in as '+username)
            session['username'] = username
            session['logged_in'] = True
            return redirect(url_for('homepage'))
        else:
            flash('login incorrect. Try again or join')
            return redirect(url_for('login'))

@app.route('/logout/')
def logout():
    try:
        if 'username' in session:
            username = session['username']
            session.pop('username')
            session.pop('logged_in')
            flash('You are logged out')
            return redirect(url_for('login'))
        else:
            flash('you are not logged in. Please login or join')
            return redirect(url_for('login') )
    except Exception as err:
        flash('some kind of error '+str(err))
        return redirect( url_for('login'))

@app.route('/')
def homepage():
    conn = dbi.connect()
    username = session.get('username', '')
    logged = session.get('logged_in', False)
    if logged == False:
        return redirect(url_for('login'))
    else:
        gaggles = waggle.getUserGaggle(conn, username)
        posts_info = waggle.getPosts(conn)
        return render_template('main.html', gaggles = gaggles, username=username, posts=posts_info)

@app.route('/search/', methods=["GET"])
def search():
    conn = dbi.connect()
    query = request.args.get('search-query')
    results = waggle.searchGaggle(conn, query)
    if len(results) == 0:
        flash('No result found')
        #should access session to get what page they were querying on and redirect to that page
        return render_template('main.html')
    else:
        return render_template('results.html', query = query, results = results)

@app.route('/gaggle/<gaggle_name>')
def gaggle(gaggle_name):
    conn = dbi.connect() 
    gaggle = waggle.getGaggle(conn, gaggle_name)  
    posts = waggle.getGagglePosts(conn, gaggle_name)
    return render_template('group.html', gaggle = gaggle, posts = posts) 
    # posts = waggle.getGagglePosts(conn, gaggle_name)
    # return render_template('gaggle.html', gaggle = gaggle, posts = posts)

@app.route('/user/<username>')
def user(username):
    conn = dbi.connect()
    gaggles = waggle.getUserGaggle(conn, username)
    return render_template('user.html', username=username, gaggles=gaggles)

@app.route('/newpost/<gaggle_name>/<gaggle_id>/', methods=["POST"])
def addPost(gaggle_name, gaggle_id):
    conn = dbi.connect()
    content = request.form.get('content')
    if len(content) == 0:
        flash('Please enter some content')
        return redirect(url_for('gaggle', gaggle_name=gaggle_name))
    else:
        poster_id = session.get('username')
        now = datetime.now()
        posted_date = now.strftime("%Y-%m-%d %H:%M:%S")
        #check last post_id
        try: 
            curs.execute('''INSERT INTO post(gaggle_id, poster_id, content, tag_id, posted_date) VALUES(%s, %s, %s, %s, %s)''',
                        [gaggle_id, poster_id, content, NULL, posted_date])
            conn.commit()
            curs.execute('select last_insert_id()')
            row = curs.fetchone()
            print('New Post Id: ', row[0])
        except:
            flash('some other error!')
        return redirect(url_for('gaggle', gaggle_name=gaggle_name))

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
    app.run('0.0.0.0',port)
