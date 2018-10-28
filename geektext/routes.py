import io
import sqlite3
from flask import Flask, flash, session, request, redirect, render_template, make_response, jsonify, url_for, send_file
from geektext import app, db, bcrypt
from geektext.models import *
from geektext.forms import RegistrationForm, LoginForm # SearchForm
from geektext.models import User
from flask_login import login_user, current_user, logout_user, login_required


def getLoginDetails():
    with sqlite3.connect('site.db') as conn:
        cur = conn.cursor()
        if 'email' not in session:
            loggedIn = False
            name = ''
            noOfItems = 0
        else:
            loggedIn = True
            cur.execute("SELECT id, name FROM user WHERE email = '" + session['email'] + "'")
            uid, name = cur.fetchone()
            cur.execute('SELECT count(isbn) FROM cart WHERE id = ' + str(uid))
            noOfItems = cur.fetchone()[0]
    conn.close()
    return loggedIn, name, noOfItems


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


# BROWSING/SORTING:


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


# PROFILE MANAGEMENT:


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(name=form.name.data, username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = User.query.filter_by(email=request.form['email']).first()
        if user is not None and bcrypt.check_password_hash(user.password, request.form['password']):
            session['logged_in'] = True
           # session['email'] = user
            login_user(user)
            print('You were logged in')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    flash('Logout successful')
    return redirect('root')

# SHOPPING CART:


@app.route("/addToCart/<int:isbn>")
def addToCart(isbn):
    if 'email' not in session:
        return redirect(url_for('login'))
    else:
        response = make_response()
        data = request.get_json()
        # we need to add the new book to the shopping cart
        # data contains the information about the book that we need to add to the cart
        book_isbn = data['isbn']
        # we need to check if there is a cookie with id of the cart. if not then we need to create a new cart
        if 'email' in session:
            print("there is a email in the request")
            print("the cookie is {request.cookies.get('email')}")
            cart_id = session["cart_id"]
            new_cart = Cart.query.get(cart_id)
            # now we need to know if the book is already in the cart or not
            added = False
            for item in new_cart.cart_items:
                if book_isbn == item.book_isbn:
                    print("The book {item.book.title} is already in the shopping cart")
                    # we need to add 1 to the count attribute in CartItem
                    item.count = item.count + 1
                    db.session.add(item)
                    db.session.commit()
                    added = True
                    break
            if not added:
                print("the book is not in the shopping cart")
                new_item = CartItem(count=1, cart_id=cart_id, book_isbn=book_isbn)
                db.session.add(new_item)
                db.session.commit()
                added = True
        else:
            print("there is no cookie")
            cart = request.get_json()
            # here we can check if the user is logged in and add the user_id to the cart
            # if there is no user_id, then just create a new empty cart.
            print("creating a new empty cart")
            c = Cart()
            # we need to add the new empty cart to the db so that it gets a unique id number
            db.session.add(c)
            db.session.commit()
            # now we can just set the cookie with the id number
            id = c.id
            print("the id of the new cart is", id)
            # add the book to the empty cart
            new_item = CartItem(count=1, cart_id=id, book_isbn=book_isbn)
            print("creating a new cart item to store the book\n", new_item)
            db.session.add(new_item)
            db.session.commit()
            response.set_cookie('cart_id', str(id))

        return response
        # productId = int(request.args.get('isbn'))
        # with sqlite3.connect('site.db') as conn:
        #     cur = conn.cursor()
        #     cur.execute("SELECT id FROM user WHERE email = '" + session['email'] + "'")
        #     userId = cur.fetchone()[0]
        #     db.session.add(productId)
        #     db.session.commit()
        #     try:
        #         cur.execute("INSERT INTO carts (userId, productId) VALUES (?, ?)", (userId, isbn))
        #         conn.commit()
        #         msg = "Added successfully"
        #     except:
        #         conn.rollback()
        #         msg = "Error occured"
        # conn.close()
        # return redirect(url_for('home'))


@app.route("/cart")
def cart():
    # if 'email' not in session:
    #     return redirect(url_for('login'))
    # loggedIn, firstName, noOfItems = getLoginDetails()
    # email = session['email']
    # with sqlite3.connect('site.db') as conn:
    #     cur = conn.cursor()
    #     cur.execute("SELECT id FROM user WHERE email = '" + email + "'")
    #     userId = cur.fetchone()[0]
    #     cur.execute("SELECT book.id, book.name, book.price, book.img FROM book, cart WHERE book.id = cart.productId AND cart.userId = " + str(userId))
    #     products = cur.fetchall()
    # totalPrice = 0
    # for row in products:
    #     totalPrice += row[2]
    return render_template("cart.html" )


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
