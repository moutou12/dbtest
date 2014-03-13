
import sqlite3
#import os.path
import os
from flask import Flask, request, session, g, redirect,url_for, abort, \
     render_template, flash

# create the application
app = Flask(__name__)
app.config.from_object(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'dbtest.db'),
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
     
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def connect_db():
#  connects to the specific database.
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def get_db():
#    """Opens a new database connection if there is none yet for the
#    current application context.

    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
#    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route('/')
def show_entries():
    db = get_db()
    cur = db.execute('select test_field, field_desc from system_type order by id desc')
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries)


@app.route('/add', methods=['GET','POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    if request.method == 'POST':
        db = get_db()
        db.execute('insert into system_type (test_field, field_desc) values (?, ?)',
                     [request.form['test_field'], request.form['field_desc']])
        db.commit()
        flash('New entry was successfully posted')
        return redirect(url_for('show_entries'))
    return render_template ('add_entries.html')

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.route('/find', methods=['GET','POST'])
def find_entry():
    if not session.get('logged_in'):
        abort(401)
    if request.method == 'POST':
        db = get_db()
        entries = query_db('select * from system_type where test_field = ?',
                     (request.form['xfield'],))
#        if entries is None:
        if not entries:
            flash ("No records found")
        else:
            global g_id
            g_id = entries[0]["id"]
        return render_template('find_entries.html', entries=entries)

    return render_template('find_entries.html')


@app.route('/delete', methods=['POST'])
def delete_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('delete from system_type where id = ?', [g_id])
    db.commit()
    flash('Entry was successfully deleted')
    return redirect(url_for('show_entries'))

@app.route('/modify', methods=['GET','POST'])
def modify_entry():
    if not session.get('logged_in'):
        abort(401)
    if request.method == 'POST':
        db = get_db()
        db.execute('update system_type set test_field = ?, field_desc = ? where id = ?', [request.form['test_field'], request.form['field_desc'],g_id])
        db.commit()
        flash('Entry was successfully updated')
        return redirect(url_for('show_entries'))
    if request.method == 'GET':
        db = get_db()
        entry = query_db("select * from system_type where id = ?", [g_id], one=True)
        return render_template("modify_entries.html", testfield=entry["test_field"], desc=entry["field_desc"])


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))


if __name__ == '__main__':
     init_db()
     app.run
#(port=8080, host='0.0.0.0')
