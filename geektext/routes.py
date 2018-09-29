import io
from flask import Flask, request, render_template, make_response, jsonify, url_for, send_file
from geektext import app, db, bcrypt
from geektext.models import *
from geektext.forms import (RegistrationForm, LoginForm)
from geektext.models import User
from flask_login import login_user, current_user, logout_user, login_required

@app.route('/book/<int:isbn>')
def book_page(isbn):
    b = Book.query.filter_by(isbn=isbn)
    return render_template('book.html', book=b.first_or_404())

@app.route('/')
def home():
    books = Book.query.all()
    return render_template('index.html', books=books)


#SORTING STUFF:

@app.route('/author/<int:id>')
def author_page(id):
    a = Author.query.get_or_404(id)
    return render_template('author.html', author=a)

@app.route('/book/by-title')
def browse_by_title():
    by_title = Book.query.order_by(Book.title)
    return render_template('by_title.html', title=by_title)

@app.route ('/book/by-rating-d')
def browse_by_descending_rating():
    by_rating = Book.query.order_by(Book.rating.desc())
    return render_template('by_rating.html', rating=by_rating)

@app.route ('/book/by-rating-a')
def browse_by_ascending_rating():
    by_rating = Book.query.order_by(Book.rating)
    return render_template('by_rating.html', rating=by_rating)

#PROFILE MANAGEMENT STUFF

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
       return redirect('index.html')
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(name=form.name.data, username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect('login.html')
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('index.html')
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect('index.html')
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect('index.html')

"""
LEAVE THIS CODE AT THE END

@app.route('/books')
def home():
    books = Book.query.order_by(Book.date_pub).all()
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
"""

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
