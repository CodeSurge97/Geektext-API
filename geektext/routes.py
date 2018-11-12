import io
from flask import Flask, flash, request, redirect, render_template, make_response, jsonify, url_for, send_file, session
from geektext import app, db, bcrypt
from geektext.models import *
from geektext.forms import RegistrationForm, LoginForm#, SearchForm
from geektext.models import User
from flask_login import login_user, current_user, logout_user, login_required
import json
from datetime import datetime

def create_response_options(request):
    response = make_response(jsonify(""))
    response.headers['Content-Type'] = 'application/json'
    response.headers['Access-Control-Allow-Credentials'] = "true"
    response.headers['Access-Control-Allow-Origin'] = request.headers['Origin']
    response.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-PINGOTHER'
    response.headers['Access-Control-Max-Age'] = '86400'
    return response

def create_response_json(request, json=""):
    response = make_response(json)
    response.headers['Content-Type'] = 'application/json'
    response.headers['Access-Control-Allow-Credentials'] = "true"
    try:
        response.headers['Access-Control-Allow-Origin'] = request.headers['Origin']
    except:
        print("we have an error with heading 'Access-Control-Allow-Origin'")
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response


def print_request(request):
    print("\n\n")
    print(100*"-")
    print(100*"-")
    print(60*"-")
    print(f"request 'headers' {request.headers}")
    print(60*"-")
    print(f"this is the request 'path' {request.path}")
    print(60*"-")
    print(f"this is the request 'url' {request.url}")
    print(60*"-")
    print(f"this is the request 'data' {request.data}")
    print(60*"-")
    print(100*"-")
    print(100*"-")
    print("\n\n")

def print_response(response):
    print("\n\n")
    print(100*"-")
    print(100*"-")
    print(60*"-")
    print("Printing the response")
    print(60*"-")
    print("Headers:")
    for h in response.headers:
        print(h)
    print(60*"-")
    print(f"Status Code: {response.status}")
    print(60*"-")
    print(f"Json: {response.get_json()}")
    print(60*"-")
    print(100*"-")
    print(100*"-")
    print("\n\n")

@app.route('/books')
def home():
    books = Book.query.order_by(Book.title).all()
    data = []
    for book in books:
        b = { 'title': book.title,
        'isbn': book.isbn,
        'genre': book.genre,
        'rating': book.rating,
        'numRatings': book.numRatings,
        'price' : book.price,
        'img' : url_for('static', filename=book.img),
        'author' : book.authors[0].name,
        'description' : book.book_description, }
        data.append(b)
    response = create_response_json(request=request, json=jsonify(data))
    response.set_cookie("sortBy", "title")
    return response


###
## Book Details
###


@app.route('/book/<int:isbn>')
def book_page(isbn):
    book = Book.query.filter_by(isbn=isbn).first()
    if 'user' in request.cookies:
        user_email = request.cookies.get('user')
        print(f"User Email is {user_email}")
        user_id = User.query.with_entities(User.id).filter(User.email == user_email).scalar()
        print(f"User id: {user_id}")
        has_book = has_book_update(user_id, int(isbn))
        print(f"Has book? {has_book}")
    #we need to create a dictionary or something for each comment and put it in a list and then put that in the comments of the book or something
    book_comments = []
    for comment in book.comments:
        c = {
            'id' : comment.id,
            'content' : comment.content,
            'rating' : comment.rating,
            'user_id' : comment.user_id,
            'date' : comment.creation_date,
            'username' : comment.user.username,
            'nickname' : comment.user.name,
            'anon' : comment.anon,
        }
        book_comments.append(c)
    b = {
        'title': book.title,
        'isbn': book.isbn,
        'genre': book.genre,
        'rating': book.rating,
        'numRatings': book.numRatings,
        'price' : book.price,
        'img' : url_for('static', filename=book.img),
        'author' : book.authors[0].name,
        'author_id' : book.authors[0].id,
        'author_info': book.authors[0].info,
        'description' : book.book_description,
        'comments' : book_comments,
        'pub_info' : book.pub_info,
        'date_pub' : book.date_pub,
        'hasBook' : has_book
        }
    response = create_response_json(request=request, json=jsonify(b))
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
            'pub_info' : book.pub_info,
            'date_pub' : book.date_pub
            }
        books.append(b)
    #we need to send json to the ui
    a = {
        'name' : author.name,
        'author_info' : author.info,
        'books' : books,
        'author_pic' : author.img,
    }
    response = create_response_json(request=request, json=jsonify(a))
    return response


###
## Rate and comments
###


def has_book_update(user_id, book_isbn):
    if book_purchased(user_id, int(book_isbn)):
        return "true"
    return "false"

def update_average_rating(book_isbn):
    averageRating = db.session.query(db.func.avg(Comment.rating)).filter(Comment.book_isbn == book_isbn).scalar()
    db.session.execute("UPDATE book SET rating = :ar WHERE isbn = :bi", {'ar' : averageRating, 'bi' : book_isbn})


def update_numRatings(book_isbn):
    numRatings = db.session.query(db.func.count(Comment.rating)).filter(Comment.book_isbn == book_isbn).scalar()
    db.session.execute("UPDATE book SET numRatings = :nr WHERE isbn = :bi", {'nr' : numRatings, 'bi' : book_isbn})


def book_purchased(user_id, book_isbn):
    u = User.query.get(user_id)
    for orderByUser in range(len(u.orders)):
        for bookInOrder in range(len(u.orders[orderByUser].books)):
            if u.orders[orderByUser].books[bookInOrder].isbn == book_isbn:
                return True
    return False


def books_purchased(user_email):
    user_id = User.query.with_entities(User.id).filter(User.email == user_email).scalar()
    u = User.query.get(user_id)
    booksPurchased = []
    for orderByUser in range(len(u.orders)):
        for bookInOrder in range(len(u.orders[orderByUser].books)):
            booksPurchased.append(u.orders[orderByUser].books[bookInOrder].isbn)
    return booksPurchased


def rated_already(user_id, book_isbn):
    return db.session.query(db.func.count(Comment.user_id)).filter(Comment.user_id == user_id).filter(Comment.book_isbn == book_isbn).scalar() is not 0


@app.route('/<int:user_id>/<int:book_isbn>/delete', methods=['DELETE', 'GET'])
def delete_rating(user_id, book_isbn):
    db.session.rollback()
    db.session.execute("DELETE FROM comment WHERE user_id = :uid AND book_isbn= :isbn", {'uid' : user_id, 'isbn' : book_isbn})
    update_average_rating(book_isbn)
    update_numRatings(book_isbn)
    db.session.commit()
    myBooks = Book.query.all()
    myRating = Comment.query.all()
    return render_template("test.html", myBooks=myBooks, myRating=myRating)


@app.route('/comment', methods=['POST', 'OPTIONS'])
def add_comment():
    if request.method == 'POST':
        db.session.rollback()
        response = create_response_json(request=request)
        print_request(request)
        print_response(response)
        if 'user' in request.cookies:
            comment = request.get_json()
            print(comment)
            user_email = request.cookies.get('user')
            print(f"User Email is {user_email}")
            user_id = User.query.with_entities(User.id).filter(User.email == user_email).scalar()
            print(f"User ID is {user_id}")
            c = Comment(content=comment['content'], creation_date=datetime.now().strftime("%Y-%m-%d %H:%M"), book_isbn=comment['isbn'], rating=comment['rating'], user_id=user_id, anon=comment['anon'])
            if not rated_already(c.user_id, int(c.book_isbn)):
                print(c)
                db.session.add(c)
            else:
                db.session.execute(
                    "UPDATE comment SET rating = :r, content = :c, anon = :a WHERE user_id = :ui AND book_isbn = :bi",
                    {'r': c.rating, 'c': c.content, 'a': c.anon, 'ui': c.user_id, 'bi': c.book_isbn})
            update_average_rating(c.book_isbn)
            update_numRatings(c.book_isbn)
        db.session.commit()
    elif request.method == 'OPTIONS':
        response = create_response_options(request=request)
        print_request(request)
        print_response(response)
    return response

###
## BROWSING/SORTING:
###


#The route for /books already sorts them by title


@app.route('/book/by-author')
def browse_by_author():
    authors = Author.query.order_by(Author.name)
    data = []
    for author in authors:
        for book in author.books:
            print(f"this is the title: {book.title}")
            b = { 'title': book.title,
            'isbn': book.isbn,
            'genre': book.genre,
            'rating': book.rating,
            'price' : book.price,
            'img' : url_for('static', filename=book.img),
            'author' : book.authors[0].name }
            data.append(b)
    response = create_response_json(request=request, json=jsonify(data))
    response.set_cookie("sortBy", "author")
    return response

@app.route('/book/by-price-d')
def browse_by_descending_price():
    books_by_price = Book.query.order_by(Book.price.desc())
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
    response = create_response_json(request=request, json=jsonify(data))
    response.set_cookie("sortBy", "priceD")
    return response

@app.route('/book/by-price-a')
def browse_by_ascending_price():
    books_by_price = Book.query.order_by(Book.price)
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
    response = create_response_json(request=request, json=jsonify(data))
    response.set_cookie("sortBy", "priceA")
    return response

@app.route ('/book/by-rating-d')
def browse_by_descending_rating():
    books_by_rating = Book.query.order_by(Book.rating.desc())
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
    response = create_response_json(request=request, json=jsonify(data))
    response.set_cookie("sortBy", "ratingD")
    return response

@app.route ('/book/by-rating-a')
def browse_by_ascending_rating():
    books_by_rating = Book.query.order_by(Book.rating)
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
    response = create_response_json(request=request, json=jsonify(data))
    response.set_cookie("sortBy", "ratingD")
    return response


###
## Shopping Cart
###


@app.route("/get-cart/<int:id>", methods=['GET', 'POST', 'OPTIONS'])
def get_cart(id):
    response = create_response_json(request)
    if request.method == 'GET':
        data = []
        if 'user' in request.cookies:
            user_email = request.cookies.get('user')
            user = User.query.filter_by(email=user_email).first()
            if user is not None and user.cart is not []:
                for item in cart.cart_items:
                    book = Book.query.get(item.book_isbn)
                    c = {
                        'count': item.count,
                        'book': book.title
                    }
                    data.append(c)
        response = create_response_json(json=jsonify(data), request=request)
    elif request.method == 'OPTIONS':
        response = create_response_options(request=request)
    return response

def create_cart(user):
    try:
        if user.cart:
            print("The user has one or more shopping carts")
            for cart in user.cart:
                print(cart)
            return True
        else:
            print("Creating a new cart for the user")
            cart = Cart(user_id=user.id)
            db.session.add(cart)
            db.session.commit()
            return True
    except:
        db.session.rollback()
        print("Error: Unable to create new cart for the user")
        return False

@app.route("/add-to-cart/<int:user_id>", methods=['GET', 'POST', 'OPTIONS'])
def add_to_cart(user_id):
    response = create_response_json(request)
    if request.method == 'POST':
        print('*'*100)
        print("the method is POST")
        data = request.get_json()
        response = create_response_json(request)
        print(f"adding the book with isbn: {data['isbn']}")
        if 'user' in request.cookies:
            print(f"The user is logged in with the email {request.cookies.get('user')}")
            user = User.query.filter_by(email=request.cookies.get('user')).first()
            print(user)
            if user and user.cart:
                print("The user has a cart")
                cart = user.cart[0]
                print(cart)
                print(f"Adding the book to the cart with id {cart.id}")
                added = False
                for item in cart.cart_items:
                    print(item)
                    if data['isbn'] == item.book_isbn:
                        print("The book is already in the shopping cart")
                        print("incrementing the count of the item")
                        item.count = item.count + 1
                        db.session.commit()
                        added = True
                if not added:
                    print(f"Cant find item with the isbn {data['isbn']}")
                    print("Creating a new item with the isbn")
                    new_item = CartItem(count=1, cart_id=user.cart[0].id, book_isbn=data["isbn"])
                    db.session.add(new_item)
                    db.session.commit()
                    for item in user.cart[0].cart_items:
                        print(item)
                    added = True
                print(f"Success {added}")
            elif user and not user.cart:
                if create_cart(user):
                    #add item to the new cart
                    new_item = CartItem(count=1, cart_id=user.cart[0].id, book_isbn=data["isbn"])
                    db.session.add(new_item)
                    db.session.commit()
                    for item in user.cart[0].cart_items:
                        print(item)
        print('*'*100)
    elif request.method == 'OPTIONS':
        print('*'*100)
        print("the method is OPTIONS")
        print('*'*100)
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

###
##PROFILE MANAGEMENT STUFF
###

@app.route("/register", methods=['GET', 'POST', 'OPTIONS'])
def register():
    if current_user.is_authenticated:
       return redirect('home')
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(name=form.name.data, username=form.username.data, email=form.email.data, password=hashed_password, address=form.home_address.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect('billing')
    return render_template('register.html', title='Register', form=form)

@app.route("/billing", methods=['GET', 'POST'])
def billing():
    form = BillingForm()
    if form.validate_on_submit():
        Credit = CreditCard(card_type=form.card_type.data, cvv=form.cvv.data, card_number=form.card_number.data, exp_date=form.exp_date.data, user_id=current_user.user_id)
        db.session.add(Credit)
        db.session.commit()
        return redirect('home')
    return render_template('billing.html', form=form)

@app.route("/login", methods=['GET', 'POST', 'OPTIONS'])
def login():
    response = make_response()
    if request.method == 'POST':
        resp = {}
        data = request.get_json()
        user = User.query.filter_by(email = data["email"]).first()
        if user is not None:
            if user.password == data["password"]:
                resp['error'] = "null"
                resp['loggedin'] = "true"
            else:
                resp['error'] = "wrong password"
                resp['loggedin'] = "false"
        else:
            resp['error'] = "email doesn't exist"
            resp['loggedin'] = "false"
        response = create_response_json(json=(jsonify(resp)), request=request)
        if(resp['loggedin'] == "true"):
            booksPurchased = books_purchased(data["email"])
            print(f"Books purchased: {booksPurchased}")
            response.set_cookie("loggedin", "true")
            response.set_cookie("user", data["email"])
            #response.set_cookie("books", f"{booksPurchased}", domain='geek.localhost.com')
            email = request.cookies.get('user')
            print(f"User email is {email}")
            #print(f"Books {email} purchased are {books}")
    elif request.method == 'OPTIONS':
        response = create_response_options(request=request)
    return response

@app.route('/user/<username>', methods=['GET', 'POST'])
def UserProfile(username):
    user = User.query.filter_by(username=username).first()
    return render_template('profile.html', user=user)

@app.route("/Edit_Profile", methods=['GET', 'POST'])
@login_required
def EditProfile():
    form = EditUserProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.username = form.username.data
        current_user.email = form.email.data
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        current_user.password = hashed_password
        current_user.address = form.home_address.data
        #user = User(name=form.name.data, username=form.username.data, email=form.email.data, password=form.password.data, address=form.home_address.data)
        db.session.add(current_user)
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('UserProfile', username=current_user.username))
    form.name.data = current_user.name
    form.username.data = current_user.username
    form.email.data = current_user.email
    form.password.data = current_user.password
    form.home_address.data = current_user.address
    return render_template('edit_profile.html', form=form)


@app.route("/logout")
def logout():
    logout_user()
    flash('Logout successful')
    return redirect('home')