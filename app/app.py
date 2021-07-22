from typing import List, Dict
import simplejson as json
from flask import Flask, request, Response, redirect
from flask import render_template
from flaskext.mysql import MySQL
from pymysql.cursors import DictCursor

app = Flask(__name__)
mysql = MySQL(cursorclass=DictCursor)

app.config['MYSQL_DATABASE_HOST'] = 'db'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_PORT'] = 3306
app.config['MYSQL_DATABASE_DB'] = 'deniroData'
mysql.init_app(app)


@app.route('/', methods=['GET'])
def index():
    user = {'username': 'Deniro Movies Project'}
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM tblDeniroImport')
    result = cursor.fetchall()
    return render_template('index.html', title='Home', user=user, movies=result)


@app.route('/view/<int:movie_id>', methods=['GET'])
def record_view(movie_id):
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM tblDeniroImport WHERE id=%s', movie_id)
    result = cursor.fetchall()
    return render_template('view.html', title='View Form', movie=result[0])


@app.route('/edit/<int:movie_id>', methods=['GET'])
def form_edit_get(movie_id):
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM tblDeniroImport WHERE id=%s', movie_id)
    result = cursor.fetchall()
    return render_template('edit.html', title='Edit Form', movie=result[0])


@app.route('/edit/<int:movie_id>', methods=['POST'])
def form_update_post(movie_id):
    cursor = mysql.get_db().cursor()
    inputData = (request.form.get('Title'), request.form.get('Year'), request.form.get('Score'),
                 movie_id)
    sql_update_query = """UPDATE tblDeniroImport t SET t.Title = %s, t.Year = %s, t.Score = %s WHERE t.id = %s """
    cursor.execute(sql_update_query, inputData)
    mysql.get_db().commit()
    return redirect("/", code=302)

@app.route('/movies/new', methods=['GET'])
def form_insert_get():
    return render_template('new.html', title='New Movie Form')


@app.route('/movies/new', methods=['POST'])
def form_insert_post():
    cursor = mysql.get_db().cursor()
    inputData = (request.form.get('Title'), request.form.get('Year'), request.form.get('Score'))
    sql_insert_query = """INSERT INTO tblDeniroImport (Title,Year,Score) VALUES (%s, %s,%s) """
    cursor.execute(sql_insert_query, inputData)
    mysql.get_db().commit()
    return redirect("/", code=302)

@app.route('/delete/<int:movie_id>', methods=['POST'])
def form_delete_post(movie_id):
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


@app.route('/api/v1/movies/', methods=['POST'])
def api_add() -> str:
    resp = Response(status=201, mimetype='application/json')
    return resp


@app.route('/api/v1/movies/<int:movie_id>', methods=['PUT'])
def api_edit(movie_id) -> str:
    resp = Response(status=201, mimetype='application/json')
    return resp


@app.route('/api/movies/<int:movie_id>', methods=['DELETE'])
def api_delete(movie_id) -> str:
    resp = Response(status=210, mimetype='application/json')
    return resp


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)