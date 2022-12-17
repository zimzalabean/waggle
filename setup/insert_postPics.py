'''Populates the post_pic table from images in the 'uploads' directory.
'''

import os
import cs304dbi as dbi

def do_files(dirname, conn, func):
    '''iterates over all files in the 'uploads' directory
    invoking function on conn, the full pathname, the filename and the
    digits before the dot that indicate the user_id
    '''
    for name in os.listdir(dirname):
        path = os.path.join(dirname, name)
        if os.path.isfile(path) and name.startswith('post_'):
            print(name)
            with open(path,'rb') as f:
                print('{} of size {}'
                      .format(path,os.fstat(f.fileno()).st_size))
            post_id,ext = name.split('.')
            post_id = post_id.split('_')[1]
            if post_id.isdigit():
                func(conn, path, name, post_id)
    
def insert_picfile(conn, path, name, post_id):
    '''Insert name into the post_pic table under key post_id.'''
    curs = dbi.cursor(conn)
    try:
        curs.execute('''insert into post_pics(post_id,filename) values (%s,%s)
                        on duplicate key update filename = %s''',
                     [post_id,name,name])
        conn.commit()
    except Exception as err:
        print('Exception on insert of {}: {}'.format(name, repr(err)))

if __name__ == '__main__':
    dbi.cache_cnf()
    conn = dbi.connect()
    do_files('uploads', conn, insert_picfile)
