from flask import Flask, jsonify, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, DecimalField, DateTimeField
from wtforms.validators import DataRequired
from flaskext.mysql import MySQL


app = Flask(__name__)

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
    return jsonify({'error': 'Bad request'}), 400


@app.errorhandler(417)
def not_found(error):
    return jsonify({'error': 'Expectation Failed'}), 417


class BookForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    author = StringField('Author', validators=[DataRequired()])
    publication_date = DateField('publication_date')
    price = DecimalField('price')
    created_at = DateTimeField('created_at')
    updated_at = DateTimeField('updated_at')
    submit = SubmitField('Submit')


@app.route('/api/books/add', methods=['POST'])
def add_book():
    book_form = BookForm(request.form)
    if book_form.validate():
        author = book_form.author
        title = book_form.title
        publication_date = book_form.publication_date.data or None
        price = book_form.price.data or None
        created_at = book_form.created_at.data or None
        updated_at = book_form.updated_at.data or None

        # logic to save book data to the database
        db = mysql.connect()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO BOOKS (title, author, publication_date, price, created_at, updated_at)
            VALUES (%s,%s,%s,%s,%s,%s)
            """, [title, author, publication_date, price, created_at, updated_at])
        db.commit()

        return jsonify({'message': 'Book created successfully'}), 201
    else:
        return jsonify({'error': 'Invalid data'}), 400


if __name__ == '__main__':
    app.run(debug=True)
