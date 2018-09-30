import io
from flask import Flask, flash, request, redirect, render_template, make_response, jsonify, url_for, send_file
from geektext import app, db, bcrypt
from geektext.models import *
from geektext.forms import RegistrationForm, LoginForm#, SearchForm
from geektext.models import User
from flask_login import login_user, current_user, logout_user, login_required


@app.route('/home')
def home():
    books = Book.query.all()
    return render_template('index.html', books=books)


@app.route('/book/<int:isbn>')
def book_page(isbn):
    b = Book.query.filter_by(isbn=isbn)
    return render_template('book.html', book=b.first_or_404())


@app.route('/author/<int:id>')
def author_page(id):
    a = Author.query.get_or_404(id)
    return render_template('author.html', author=a)


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
    by_price = Book.query.order_by(Book.price.desc())
    return render_template('by_price.html', price=by_price)


@app.route('/book/by-price-a')
def browse_by_ascending_price():
    by_price = Book.query.order_by(Book.price)
    return render_template('by_price.html', price=by_price)


@app.route ('/book/by-rating-d')
def browse_by_descending_rating():
    by_rating = Book.query.order_by(Book.rating.desc())
    return render_template('by_rating.html', rating=by_rating)


@app.route ('/book/by-rating-a')
def browse_by_ascending_rating():
    by_rating = Book.query.order_by(Book.rating)
    return render_template('by_rating.html', rating=by_rating)

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

# SHOPPING CART:

"""
FIX THE LOGIC FOR THE ELSE AND RETURN STATEMENTS
@app.route('/addcart/<int:product_id>', methods=['GET', 'POST'])
def display(product_id):
    if Cart.query.filter_by(isbn=product_id).first() is None:   #query is empty - no isbn matches the product id
        return render_template('cart_notfound.html', message='A book with isbn {} does not exist'.format(product_id))
    else:
        #query to add the book to the user's shopping cart
    
    #render the shopping cart here:
    return render_template('post.html', in_cart=in_cart)
"""

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
