from flask import Flask, jsonify, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flaskext.mysql import MySQL


app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-key'

app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_PORT'] = 3306
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'password'
app.config['MYSQL_DATABASE_DB'] = 'mydatabase'

mysql = MySQL(app)


@app.route('/', methods=['GET'])
def hello():
    return 'Hello, World'


@app.route('/api/books', methods=['GET'])
def get_books():
    cursor = mysql.connect().cursor()
    cursor.execute('SELECT * FROM books')
    books = cursor.fetchall()
    return jsonify(books)


@app.route('/api/books/<book_id>', methods=['GET'])
def get_book(book_id):
    cursor = mysql.connect().cursor()
    cursor.execute('SELECT * FROM books WHERE id=%s', book_id)
    book = cursor.fetchone()
    return jsonify(book)


@app.route('/greet', methods=['GET'])
def greet():
    name = request.args.get('name')
    return f'Hello, {name}!'


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(400)
def not_found(error):
    return jsonify({'error': 'Bad request'}), 404


@app.errorhandler(417)
def not_found(error):
    return jsonify({'error': 'Expectation Failed'}), 417


class BookForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    author = StringField('Author', validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.route('/book_test', methods=['POST'])
def book_test():
    book_form = BookForm(request.form)
    title = book_form.title
    if book_form.author:
        author = book_form.author
        return 'All ok'
    else:
        return 'Error, no author!'


@app.route('/api/books/add', methods=['POST'])
def add_book():
    book_form = BookForm(request.form)
    if book_form.validate():
        author = book_form.author
        title = book_form.title
        # logic to save book data to the database
        return jsonify({'message': 'Book created successfully'}), 201
    else:
        return jsonify({'error': 'Invalid data'}), 400


if __name__ == '__main__':
    app.run(debug=True)
