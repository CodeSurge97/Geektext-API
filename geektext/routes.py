import io
from flask import Flask, flash, request, redirect, render_template, make_response, jsonify, url_for, send_file
from geektext import app, db, bcrypt
from geektext.models import *
from geektext.forms import RegistrationForm, LoginForm#, SearchForm
from geektext.models import User
from flask_login import login_user, current_user, logout_user, login_required


@app.route('/books')
def home():
    books = Book.query.order_by(Book.title).all()
    print("this is by publication date")
    print(books)
    data = []
    for book in books:
        b = { 'title': book.title,
        'isbn': book.isbn,
        'genre': book.genre,
        'rating': book.rating,
        'price' : book.price,
        'img' : url_for('static', filename=book.img),
        'author' : book.authors[0].name }
        data.append(b)
    response = make_response(jsonify(data))
    response.headers['Content-Type'] = 'application/json'
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response


@app.route('/book/<int:isbn>')
def book_page(isbn):
    book = Book.query.filter_by(isbn=isbn).first()
    #we need to create a dictionary or something for each comment and put it in a list and then put that in the comments of the book or something
    comments = []
    for comment in book.comments:
        c = {
            'id' : comment.id,
            'contents' : comment.content,
            'rating' : comment.rating,
            'user_id' : comment.user_id,
            'date' : comment.creation_date,
            'username' : comment.user.username

        }
        comments.append(c)

    b = {
        'title': book.title,
        'isbn': book.isbn,
        'genre': book.genre,
        'rating': book.rating,
        'price' : book.price,
        'img' : url_for('static', filename=book.img),
        'author' : book.authors[0].name,
        'author_id' : book.authors[0].id,
        'description' : book.book_description,
        'comments' : comments,
        'pub_info' : book.pub_info,
        'date_pub' : book.date_pub
        }
    response = make_response(jsonify(b))
    response.headers['Content-Type'] = 'application/json'
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response


@app.route('/author/<int:id>')
def author_page(id):
    author = Author.query.get_or_404(id)
    #we need to make a list of books by the author
    books = []
    for book in author.books:
        b = {
            'title': book.title,
            'isbn': book.isbn,
            'genre': book.genre,
            'rating': book.rating,
            'price' : book.price,
            'img' : url_for('static', filename=book.img),
            'author' : book.authors[0].name,
            'author_id' : book.authors[0].id,
            'description' : book.book_description,
            'comments' : comments,
            'pub_info' : book.pub_info,
            'date_pub' : book.date_pub
            }
        books.append(b)

    #we need to send json to the ui
    a = {
        'name' : author.name,
        'author_info' : author.info,
        'books' : books,

    }

    response = make_response(jsonify(a))
    response.headers['Content-Type'] = 'application/json'
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

#Comments and stuff

@app.route('/comment/<int:user_id>', methods=['GET', 'POST', 'OPTIONS'])
def add_comment(user_id):
    if request.method == 'POST':
        user = User.query.get_or_404(user_id)
        print("this is the data from react")
        print(request)
        response = make_response(jsonify("hello"))
        print(request.get_json())
    elif request.method == 'OPTIONS':
        print(40*"-")
        print("this is the request 'path'")
        print(request.path)
        print(40*"-")
        print("this is the request 'url'")
        print(request.url)
        print(40*"-")
        print("this is the request 'data'")
        print(request.data)
        print(40*"-")
        print("this is the request 'headers'")
        print(request.headers)
        print(40*"-")
        response = make_response(jsonify("Fuuuck"))
        response.headers['Content-Type'] = 'application/json'
        response.headers['Access-Control-Allow-Origin'] = request.headers['Origin']
        response.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-PINGOTHER'
        response.headers['Access-Control-Max-Age'] = '86400'
    return response

#BROWSING/SORTING:


@app.route('/book/by-title')
def browse_by_title():
    by_title = Book.query.order_by(Book.title)
    return render_template('by_title.html', title=by_title)


@app.route('/book/by-author')
def browse_by_author():
    by_author = Author.query.order_by(Author.name)
    return render_template('by_author.html', author=by_author)


@app.route('/book/by-price-d')
def browse_by_descending_price():
    books_by_price = Book.query.order_by(Book.price.desc())
    print("this is by price")
    print(books_by_price)
    data = []
    for book in books_by_price:
        b = { 'title': book.title,
        'isbn': book.isbn,
        'genre': book.genre,
        'rating': book.rating,
        'price' : book.price,
        'img' : url_for('static', filename=book.img),
        'author' : book.authors[0].name }
        data.append(b)
    response = make_response(jsonify(data))
    response.headers['Content-Type'] = 'application/json'
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response


@app.route('/book/by-price-a')
def browse_by_ascending_price():
    books_by_price = Book.query.order_by(Book.price)
    print("this is by price")
    print(books_by_price)
    data = []
    for book in books_by_price:
        b = { 'title': book.title,
        'isbn': book.isbn,
        'genre': book.genre,
        'rating': book.rating,
        'price' : book.price,
        'img' : url_for('static', filename=book.img),
        'author' : book.authors[0].name }
        data.append(b)
    response = make_response(jsonify(data))
    response.headers['Content-Type'] = 'application/json'
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response


@app.route ('/book/by-rating-d')
def browse_by_descending_rating():
    books_by_rating = Book.query.order_by(Book.rating.desc())
    print("this is by price")
    print(books_by_rating)
    data = []
    for book in books_by_rating:
        b = { 'title': book.title,
        'isbn': book.isbn,
        'genre': book.genre,
        'rating': book.rating,
        'price' : book.price,
        'img' : url_for('static', filename=book.img),
        'author' : book.authors[0].name }
        data.append(b)
    response = make_response(jsonify(data))
    response.headers['Content-Type'] = 'application/json'
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response


@app.route ('/book/by-rating-a')
def browse_by_ascending_rating():
    books_by_rating = Book.query.order_by(Book.rating)
    print("this is by price")
    print(books_by_rating)
    data = []
    for book in books_by_rating:
        b = { 'title': book.title,
        'isbn': book.isbn,
        'genre': book.genre,
        'rating': book.rating,
        'price' : book.price,
        'img' : url_for('static', filename=book.img),
        'author' : book.authors[0].name }
        data.append(b)
    response = make_response(jsonify(data))
    response.headers['Content-Type'] = 'application/json'
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

"""
FIXME
@app.route('/home', methods=['GET', 'POST'])
def search_bar():
    search = SearchForm(request.form)
    if request.method == 'POST':
        return search_results(search)
    return render_template('base.html', form=search)


@app.route('/results')
def search_results(search):
    results = []
    search_string = search.data['search']

    if search.data['search'] == '':
        query = db_session.query(Author)
        results = query.all()

    if not results:
        flash('No results found!')
        return redirect('/')
    else:
        # display results
        return render_template('results.html', results=results)
 """


#PROFILE MANAGEMENT:


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
       return redirect('home')
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(name=form.name.data, username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect('login')
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('home')
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect('home')
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    flash('Logout successful')
    return redirect('home')



"""
@app.route('/books/<isbn>')
def book_page(book_title):

    target = Book.query.filter(Book.title.like('%'+book_title+'%'))
    return render_template('book.html', book=target.first())

"""

"""
b = { 'title': book.title,
'isbn': book.isbn,
'date_pub' = book.date_pub,
'genre': book.genre,
'rating': book.rating,
'price' : book.price,
'img' : book.img,
'pub_info' : book.pub_info,
'book_description': book.book_description}
"""
