from typing import List, Dict
import simplejson as json
from flask import Flask, request, Response, redirect
from flask import render_template, g, session, url_for, flash
from flaskext.mysql import MySQL
from pymysql.cursors import DictCursor


app = Flask(__name__)
app.secret_key = 'brandonsecretkey'
mysql = MySQL(cursorclass=DictCursor)

app.config['MYSQL_DATABASE_HOST'] = 'db'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_PORT'] = 3306
app.config['MYSQL_DATABASE_DB'] = 'deniroData'
mysql.init_app(app)


class User:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __repr__(self):
        return f'<User: {self.username}>'


users = [User(id=1, username='Class', password='password')]


@app.before_request
def before_request():
    g.user = None

    if 'user_id' in session:
        user = [x for x in users if x.id == session['user_id']][0]
        g.user = user


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.pop('user_id', None)

        username = request.form['username']
        password = request.form['password']

        userlist = [x for x in users if x.username == username]
        if len(userlist) > 0:
            user = userlist[0]
        else:
            return redirect(url_for('login'))

        if user and user.password == password:
            session['user_id'] = user.id
            flash("Login Successful")
            return redirect(url_for('profile'))

        return redirect(url_for('login'))
    flash("Welcome! Please Login to Proceed!")
    return render_template('login.html')


@app.route('/profile')
def profile():
    if not g.user:
        return redirect(url_for('login'))

    return render_template('profile.html')


@app.route('/index', methods=['GET'])
def index():
    if not g.user:
        return redirect(url_for('login'))
    user = {'username': 'Deniro Movies Project'}
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM tblDeniroImport')
    result = cursor.fetchall()
    return render_template('index.html', title='Home', user=user, movies=result)


@app.route('/view/<int:movie_id>', methods=['GET'])
def record_view(movie_id):
    if not g.user:
        return redirect(url_for('login'))
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM tblDeniroImport WHERE id=%s', movie_id)
    result = cursor.fetchall()
    return render_template('view.html', title='View Form', movie=result[0])


@app.route('/edit/<int:movie_id>', methods=['GET'])
def form_edit_get(movie_id):
    if not g.user:
        return redirect(url_for('login'))
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM tblDeniroImport WHERE id=%s', movie_id)
    result = cursor.fetchall()
    return render_template('edit.html', title='Edit Form', movie=result[0])


@app.route('/edit/<int:movie_id>', methods=['POST'])
def form_update_post(movie_id):
    if not g.user:
        return redirect(url_for('login'))
    cursor = mysql.get_db().cursor()
    inputData = (request.form.get('Title'), request.form.get('Year'), request.form.get('Score'),
                 movie_id)
    sql_update_query = """UPDATE tblDeniroImport t SET t.Title = %s, t.Year = %s, t.Score = %s WHERE t.id = %s """
    cursor.execute(sql_update_query, inputData)
    mysql.get_db().commit()
    return redirect("/", code=302)


@app.route('/movies/new', methods=['GET'])
def form_insert_get():
    if not g.user:
        return redirect(url_for('login'))
    return render_template('new.html', title='New Movie Form')


@app.route('/movies/new', methods=['POST'])
def form_insert_post():
    if not g.user:
        return redirect(url_for('login'))
    cursor = mysql.get_db().cursor()
    inputData = (request.form.get('Title'), request.form.get('Year'), request.form.get('Score'))
    sql_insert_query = """INSERT INTO tblDeniroImport (Title,Year,Score) VALUES (%s, %s,%s) """
    cursor.execute(sql_insert_query, inputData)
    mysql.get_db().commit()
    return redirect("/", code=302)


@app.route('/delete/<int:movie_id>', methods=['POST'])
def form_delete_post(movie_id):
    if not g.user:
        return redirect(url_for('login'))
    cursor = mysql.get_db().cursor()
    sql_delete_query = """DELETE FROM tblDeniroImport WHERE id = %s """
    cursor.execute(sql_delete_query, movie_id)
    mysql.get_db().commit()
    return redirect("/", code=302)


@app.route('/api/v1/movies', methods=['GET'])
def api_browse() -> str:
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM tblDeniroImport')
    result = cursor.fetchall()
    json_result = json.dumps(result);
    resp = Response(json_result, status=200, mimetype='application/json')
    return resp


@app.route('/api/v1/movies/<int:movie_id>', methods=['GET'])
def api_retrieve(movie_id) -> str:
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM tblDeniroImport WHERE id=%s', movie_id)
    result = cursor.fetchall()
    json_result = json.dumps(result);
    resp = Response(json_result, status=200, mimetype='application/json')
    return resp


@app.route('/api/v1/movies', methods=['POST'])
def api_add() -> str:
    content = request.json
    cursor = mysql.get_db().cursor()
    inputData = (content['Title'], content['Year'], request.form.get('Score'))
    sql_insert_query = """INSERT INTO tblDeniroImport (Title,Year,Score) VALUES (%s, %s,%s) """
    cursor.execute(sql_insert_query, inputData)
    mysql.get_db().commit()
    resp = Response(status=201, mimetype='application/json')
    return resp


@app.route('/api/v1/movies/<int:movie_id>', methods=['PUT'])
def api_edit(movie_id) -> str:
    cursor = mysql.get_db().cursor()
    content = request.json
    inputData = (content['Title'], content['Year'], content['Score'], movie_id)
    sql_update_query = """UPDATE tblDeniroImport t SET t.Title = %s, t.Year = %s, t.Score = %s WHERE t.id = %s """
    cursor.execute(sql_update_query, inputData)
    mysql.get_db().commit()
    resp = Response(status=201, mimetype='application/json')
    return resp


@app.route('/api/v1/movies/<int:movie_id>', methods=['DELETE'])
def api_delete(movie_id) -> str:
    cursor = mysql.get_db().cursor()
    sql_delete_query = """DELETE FROM tblDeniroImport WHERE id = %s """
    cursor.execute(sql_delete_query, movie_id)
    mysql.get_db().commit()
    resp = Response(status=200, mimetype='application/json')
    return resp


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
