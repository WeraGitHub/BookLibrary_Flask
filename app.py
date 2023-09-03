from flask import Flask, jsonify, request, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, DecimalField, DateTimeField
# from wtforms.validators import DataRequired   # not used, because it was causing problems
from flaskext.mysql import MySQL
import json


app = Flask(__name__)

app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_PORT'] = 3306
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'password'
app.config['MYSQL_DATABASE_DB'] = 'mydatabase'

app.config['SECRET_KEY'] = 'super-key'  # needed for updating the db


mysql = MySQL(app)


@app.route('/', methods=['GET'])
def hello():
    return 'Hello, World'


def process_books(raw_books):
    processed_books = []
    for book in raw_books:
        processed_book = {
            'id': book[0],
            'title': book[1],
            'author': book[2],
            'publication_date': book[3],
            'price': book[4],
            'created_at': book[5],
            'updated_at': book[6]
        }
        processed_books.append(processed_book)
    return processed_books


@app.route('/books', methods=['GET'])
def books():
    raw_all_books = json.loads(get_books().data)  # Deserialize JSON data
    all_books = process_books(raw_all_books)
    return render_template('books.html', books=all_books)


@app.route('/api/books', methods=['GET'])
def get_books():
    cursor = mysql.connect().cursor()
    cursor.execute('SELECT * FROM books')
    all_books = cursor.fetchall()
    return jsonify(all_books)


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
    return jsonify({'error': 'Bad request'}), 400


@app.errorhandler(417)
def not_found(error):
    return jsonify({'error': 'Expectation Failed'}), 417


class BookForm(FlaskForm):
    # the validation didn't work even when the data provided was correct.
    # title = StringField('title', validators=[DataRequired()])
    # author = StringField('author', validators=[DataRequired()])
    title = StringField('title')
    author = StringField('author')
    publication_date = DateField('publication_date')
    price = DecimalField('price')
    created_at = DateTimeField('created_at')
    updated_at = DateTimeField('updated_at')
    submit = SubmitField('Submit')


@app.route('/api/books/add', methods=['POST'])
def add_book():
    book_form = BookForm(request.form)
    # if book_form.validate():
    if book_form.title.data is not None and book_form.author.data is not None:
        author = book_form.author.data
        title = book_form.title.data
        publication_date = book_form.publication_date.data or None
        price = book_form.price.data or None

        # logic to save book data to the database
        db = mysql.connect()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO books (title, author, publication_date, price)
            VALUES (%s,%s,%s,%s)
            """, [title, author, publication_date, price])
        db.commit()

        return jsonify({'message': 'Book created successfully'}), 201
    else:
        return jsonify({'error': 'Invalid data'}), 400


if __name__ == '__main__':
    app.run(debug=True)
