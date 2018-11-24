
import io
from flask import Flask, flash, request, redirect, render_template, make_response, jsonify, url_for, send_file, session
from geektext import app, db, bcrypt
from geektext.models import *
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
    response.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
    try:
        response.headers['Access-Control-Allow-Origin'] = request.headers['Origin']
    except:
        print("we have an error with heading 'Access-Control-Allow-Origin'")
        response.headers['Access-Control-Allow-Origin'] = 'http://geek.localhost.com:3000'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, X-Requested-With, Content-Type, Accept, Authorization'
    return response

def print_request(request):
    print("\n\n")
    print(100 * "-")
    print(100 * "-")
    print(60 * "-")
    print(f"request 'headers' {request.headers}")
    print(60 * "-")
    print(f"this is the request 'path' {request.path}")
    print(60 * "-")
    print(f"this is the request 'url' {request.url}")
    print(60 * "-")
    print(f"this is the request 'data' {request.data}")
    print(60 * "-")
    print(100 * "-")
    print(100 * "-")
    print("\n\n")

def print_response(response):
    print("\n\n")
    print(100 * "-")
    print(100 * "-")
    print(60 * "-")
    print("Printing the response")
    print(60 * "-")
    print("Headers:")
    for h in response.headers:
        print(h)
    print(60 * "-")
    print(f"Status Code: {response.status}")
    print(60 * "-")
    print(f"Json: {response.get_json()}")
    print(60 * "-")
    print(100 * "-")
    print(100 * "-")
    print("\n\n")


###
# Book Details
###

@app.route('/books/<int:page>/<int:per_page>')
def home(page, per_page):
    books = Book.query.order_by(Book.title).paginate(
        page=page, per_page=per_page)
    data = []
    for book in books.items:
        b = {'title': book.title,
             'isbn': book.isbn,
             'genre': book.genre,
             'rating': book.rating,
             'price': book.price,
             'img': url_for('static', filename=book.img),
             'author': book.authors[0].name,
             'description': book.book_description,
             'date': book.date_pub }
        data.append(b)
    json_res = {'books': data, 'totalNum': books.total}
    response = create_response_json(request=request, json=jsonify(json_res))
    response.set_cookie("sortBy", "title")
    return response


@app.route('/book/<int:isbn>')
def book_page(isbn):
    book = Book.query.filter_by(isbn=isbn).first()
    has_book = ""
    user_email = request.cookies.get('user')
    print(f"User Email is {user_email}")
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
            'nickname' : comment.user.nickname,
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
        'publisher' : book.pub_info,
        'date_pub' : book.date_pub,
        'hasBook' : has_book
        }
    response = create_response_json(request=request, json=jsonify(b))
    return response

@app.route('/author/<int:id>')
def author_page(id):
    author = Author.query.get_or_404(id)
    # we need to make a list of books by the author
    books = []
    for book in author.books:
        b = {
            'title': book.title,
            'isbn': book.isbn,
            'genre': book.genre,
            'rating': book.rating,
            'price': book.price,
            'img': url_for('static', filename=book.img),
            'author': book.authors[0].name,
            'author_id': book.authors[0].id,
            'description': book.book_description,
            'pub_info': book.pub_info,
            'date_pub': book.date_pub
        }
        books.append(b)
    # we need to send json to the ui
    a = {
        'name': author.name,
        'author_info': author.info,
        'books': books,
        'author_pic': author.img,
    }
    print(author.img)
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

def rated_already(user_id, book_isbn):
    return db.session.query(db.func.count(Comment.user_id)).filter(Comment.user_id == user_id).filter(Comment.book_isbn == book_isbn).scalar() is not 0


@app.route('/comment', methods=['POST', 'OPTIONS'])
def add_comment():
    if request.method == 'POST':
        db.session.rollback()
        print_request(request)
        if 'user' in request.cookies:
            comment = request.get_json()
            print(comment)
            user_email = request.cookies.get('user')
            print(f"User Email is {user_email}")
            user_id = User.query.with_entities(User.id).filter(User.email == user_email).scalar()
            print(f"User ID is {user_id}")
            c = Comment(content=comment['content'], creation_date=datetime.now().strftime("%Y-%m-%d %I:%M %p"), book_isbn=comment['isbn'], rating=comment['rating'], user_id=user_id, anon=comment['anon'])
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
        response = create_response_json(request=request)
    elif request.method == 'OPTIONS':
        response = create_response_options(request=request)
        print_request(request)
        print_response(response)
    return response

###
# BROWSING/SORTING:
###


# The route for /books already sorts them by title
"""@app.route('/book/by-title')
def browse_by_title():
    by_title = Book.query.order_by(Book.title)
    return render_template('by_title.html', title=by_title)
"""


@app.route('/book/by-author/<int:page>/<int:per_page>')
def browse_by_author(page, per_page):
    authors = Author.query.order_by(Author.name).paginate(
        page=page, per_page=per_page)
    data = []
    num_of_books = 0;
    for author in authors.items:
        for book in author.books:
            print(f"this is the title: {book.title}")
            b = {'title': book.title,
                 'isbn': book.isbn,
                 'genre': book.genre,
                 'rating': book.rating,
                 'price': book.price,
                 'img': url_for('static', filename=book.img),
                 'author': book.authors[0].name,
                 'description': book.book_description, }
            num_of_books = num_of_books + 1
            data.append(b)
    json_res = {'books': data, 'totalNum': num_of_books}
    response = create_response_json(request=request, json=jsonify(json_res))
    response.set_cookie("sortBy", "author")
    print_response(response)
    return response


@app.route('/book/by-price-d/<int:page>/<int:per_page>')
def browse_by_descending_price(page, per_page):
    books_by_price = Book.query.order_by(Book.price.desc()).paginate(
        page=page, per_page=per_page)
    data = []
    for book in books_by_price.items:
        print(book)
        b = {'title': book.title,
             'isbn': book.isbn,
             'genre': book.genre,
             'rating': book.rating,
             'price': book.price,
             'img': url_for('static', filename=book.img),
             'author': book.authors[0].name,
             'description': book.book_description, }
        data.append(b)
    json_res = {'books': data, 'totalNum': books_by_price.total}
    response = create_response_json(request=request, json=jsonify(json_res))
    response.set_cookie("sortBy", "priceD")
    return response


@app.route('/book/by-price-a/<int:page>/<int:per_page>')
def browse_by_ascending_price(page, per_page):
    books_by_price = Book.query.order_by(Book.price).paginate(
        page=page, per_page=per_page)
    data = []
    for book in books_by_price.items:
        b = {'title': book.title,
             'isbn': book.isbn,
             'genre': book.genre,
             'rating': book.rating,
             'price': book.price,
             'img': url_for('static', filename=book.img),
             'author': book.authors[0].name,
             'description': book.book_description,
             }
        data.append(b)
    json_res = {'books': data, 'totalNum': books_by_price.total}
    response = create_response_json(request=request, json=jsonify(json_res))
    response.set_cookie("sortBy", "priceA")
    return response


@app.route('/book/by-rating-d/<int:page>/<int:per_page>')
def browse_by_descending_rating(page, per_page):
    books_by_rating = Book.query.order_by(Book.rating.desc()).paginate(
        page=page, per_page=per_page)
    data = []
    for book in books_by_rating.items:
        b = {'title': book.title,
             'isbn': book.isbn,
             'genre': book.genre,
             'rating': book.rating,
             'price': book.price,
             'img': url_for('static', filename=book.img),
             'author': book.authors[0].name,
             'description': book.book_description,
             }
        data.append(b)
    json_res = {'books': data, 'totalNum': books_by_rating.total}
    response = create_response_json(request=request, json=jsonify(json_res))
    response.set_cookie("sortBy", "ratingD")
    return response


@app.route('/book/by-rating-a/<int:page>/<int:per_page>')
def browse_by_ascending_rating(page, per_page):
    books_by_rating = Book.query.order_by(Book.rating).paginate(
        page=page, per_page=per_page)
    data = []
    for book in books_by_rating.items:
        b = {'title': book.title,
             'isbn': book.isbn,
             'genre': book.genre,
             'rating': book.rating,
             'price': book.price,
             'img': url_for('static', filename=book.img),
             'author': book.authors[0].name,
             'description': book.book_description,
             }
        data.append(b)
    json_res = {'books': data, 'totalNum': books_by_rating.total}
    response = create_response_json(request=request, json=jsonify(json_res))
    response.set_cookie("sortBy", "ratingD")
    return response



###
# Shopping Cart
###


@app.route("/get-cart")
def get_cart():
    data = []
    user_name = ""
    if 'user' in request.cookies:
        user_email = request.cookies.get('user')
        user = User.query.filter_by(email=user_email).first()
        if user is not None and user.cart is not []:
            user_name = user.name
            for item in user.cart[0].cart_items:
                book = Book.query.get(item.book_isbn)
                c = {
                    #Here you need to specify everyhting that you want in the shopping cart items
                    'count': item.count,
                    'book': book.title,
                    'img': book.img,
                    'isbn': book.isbn,
                    'price': book.price
                }
                data.append(c)
    json_data = {"items": data, "user_name": user_name}
    response = create_response_json(json=jsonify(json_data), request=request)
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


@app.route("/add-to-cart", methods=['GET', 'POST', 'OPTIONS'])
def add_to_cart():
    response = create_response_json(request)
    if request.method == 'POST':
        print('*' * 100)
        print("the method is POST")
        data = request.get_json()
        response = create_response_json(request)
        print(f"adding the book with isbn: {data['isbn']}")
        if 'user' in request.cookies:
            print(f"The user is logged in with the email {request.cookies.get('user')}")
            user = User.query.filter_by(
                email=request.cookies.get('user')).first()
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
                    new_item = CartItem(
                        count=1, cart_id=user.cart[0].id, book_isbn=data["isbn"])
                    db.session.add(new_item)
                    db.session.commit()
                    for item in user.cart[0].cart_items:
                        print(item)
                    added = True
                print(f"Success {added}")
            elif user and not user.cart:
                if create_cart(user):
                    # add item to the new cart
                    new_item = CartItem(
                        count=1, cart_id=user.cart[0].id, book_isbn=data["isbn"])
                    db.session.add(new_item)
                    db.session.commit()
                    for item in user.cart[0].cart_items:
                        print(item)
        print('*' * 100)
    elif request.method == 'OPTIONS':
        print('*' * 100)
        print("the method is OPTIONS")
        response = create_response_options(request=request)
        print('*' * 100)
    return response

@app.route("/remove-from-cart", methods=['GET', 'POST', 'OPTIONS'])
def remove_from_cart():
    response = create_response_json(request)
    if request.method == 'POST':
        print('*' * 100)
        print("the method is POST")
        data = request.get_json()
        response = create_response_json(request)
        print(f"Removing the book with isbn: {data['isbn']}")
        if 'user' in request.cookies:
            print(f"The user is logged in with the email {request.cookies.get('user')}")
            user = User.query.filter_by(
                email=request.cookies.get('user')).first()
            print(user)
            if user and user.cart:
                print("The user has a cart")
                cart = user.cart[0]
                print(cart)
                print(f"Removing the book from the cart with id {cart.id}")
                removed = False
                for item in cart.cart_items:
                    print(item)
                    if data['isbn'] == item.book_isbn:
                        print("The book is in the shopping cart")
                        print("decrementing the count of the item")
                        if item.count > 1:
                            # This part works correctly
                            item.count = item.count - 1
                            db.session.commit()
                            removed = True
                        else:
                            # And for some reason the remove() funciton was not working, I think it is becasue remove works with a position
                            # but delete works with an instance of an object so you can use that instead
                            db.session.delete(item)
                            # Remember to commit after modifying the database
                            db.session.commit()
                            removed = True
                if not removed:
                    print(f"Cant find item with the isbn {data['isbn']}")
                print(f"Success {removed}")
        print('*' * 100)
    elif request.method == 'OPTIONS':
        print('*' * 100)
        print("the method is OPTIONS")
        # Here you need to add this function to avoid CORS problems. This is a really messy subject so just use the funcitons
        # create_response_options and create_response_json because you need those headers
        response = create_response_options(request=request)
        print('*' * 100)
    return response



# Fixing the search function
@app.route('/book/<book>', methods=['GET', 'POST'])
def search(book):
    print(book)
    query = '%' + book + '%'
    search = Book.query.filter(Book.title.ilike(query))
    books = []
    for book in search:
        b = {'title': book.title,
             'isbn': book.isbn,
             'genre': book.genre,
             'rating': book.rating,
             'price': book.price,
             'img': url_for('static', filename=book.img),
             'author': book.authors[0].name,
             'description': book.book_description, }
        books.append(b)
    json_res = {'books': books, 'totalNum': search.count()}
    response = create_response_json(request=request, json=jsonify(json_res))
    return response

###
# PROFILE MANAGEMENT STUFF
###



def GetUser(email):
    user = User.query.filter_by(email=email).first()
    return user.username


@app.route("/register", methods=['GET', 'POST', 'OPTIONS'])
def register():
    if request.method == 'POST':
        resp ={}
        data = request.get_json()
        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        #print(f"the email and the password are: {email}, {hashed_password}")
        if User.query.filter_by(email = data['email']).first() is None:
            if User.query.filter_by(username = data['username'] ).first() is None:
                if User.query.filter_by(nickname = data['nickname'] ).first() is None:
                    user = User( nickname=data['nickname'], name=data['name'], username=data['username'], email=data['email'], password=hashed_password, address=data['address'])
                    db.session.add(user)
                    db.session.commit()
                    resp["error"] = "null"
                    resp["registered"] = "true"
        else:
           print("the email and/or username already exists ")
           resp['error'] = "user already exists"
           resp['registered'] = "false"
        print(f"at the end")
        response = create_response_json(json=(jsonify(resp)), request=request)
        if(resp['registered'] == "true"):
            response.set_cookie("loggedin", "true")
            response.set_cookie("user", data["email"])
    elif request.method == 'OPTIONS':
        response = create_response_options(request=request)
    return response


@app.route("/billing", methods=['GET', 'POST', 'OPTIONS'])
def billing():
    if request.method == 'POST':
        resp = {}
        data = request.get_json()
        user = User.query.filter_by(username=data['username']).first()
        date_object = datetime.strptime(data['exp_date'], "%m/%Y").date()
        if CreditCard.query.filter_by(card_number=data['card_number']).first() is None:
            credit = CreditCard(card_type=data["card_type"], cvv=data["cvv"], card_number=data["card_number"], exp_date=date_object, user_id=user.id)
            db.session.add(credit)
            db.session.commit()
            resp['error'] = "null"
            resp['validated'] = "true"
        else:
           print("Card Number already exists ")
           resp['error'] = " card already exists"
           resp['validated'] = "false"
        print(f"at the end")
        response = create_response_json(json=(jsonify(resp)), request=request)
        if(resp['validated'] == "true"):
            print("setting the cookie")
            response.set_cookie("validated", "true")
        response.headers['Access-Control-Allow-Origin'] = 'http://geek.localhost.com:3000'
        print(response.headers)
    elif request.method == 'OPTIONS':
        response = create_response_options(request=request)
    return response

@app.route("/login", methods=['GET', 'POST', 'OPTIONS'])
def login():
    if request.method == 'POST':
        resp = {}
        data = request.get_json()
        user = User.query.filter_by(email = data["email"]).first()
        if user is not None:
            if bcrypt.check_password_hash(user.password, data['password']):
                resp['error'] = "null"
                resp['loggedin'] = "true"
                resp['username'] = GetUser(user.email)
            else:
                resp['error'] = "wrong password"
                resp['loggedin'] = "false"
        else:
            resp['error'] = "email doesn't exist"
            resp['loggedin'] = "false"
        response = create_response_json(json=(jsonify(resp)), request=request)
        if(resp['loggedin'] == "true"):
            response.set_cookie("loggedin", "true")
            response.set_cookie("user", user.email)
    elif request.method == 'OPTIONS':
        response = create_response_options(request=request)
    return response

@app.route('/user/<username>')
def UserProfile(username):
    #if 'loggedin' in session:
    #response.get_cookie('user')
    user = User.query.filter_by(username=username).first()
    credit_cards = []
    for credit_card in user.credit_cards:
        c = {
            'card_number' : credit_card.card_number,
        }
        credit_cards.append(c)

    u = {
    'nickname': user.nickname,
    'name': user.name,
    'username': user.username,
    'email': user.email,
    'address': user.address,
    'credit_cards': credit_cards
    }
    response = create_response_json(json=(jsonify(u)), request=request)
    return response


@app.route("/Edit_Profile", methods=['GET', 'POST', 'OPTIONS'])
def EditProfile():
    if request.method == 'POST':
        resp = {}
        data = request.get_json()
        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        #print(f"the email and the password are: {email}, {hashed_password}")
        user = User.query.filter_by(username = data['old_username'] ).first()
        if user.username == data['new_username']:
            user.nickname == data['nickname']
            user.name = data['name']
            user.email = data['email']
            user.password = hashed_password
            user.address = data['address']
            db.session.add(user)
            db.session.commit()
            resp['error'] = "null"
            resp['updated'] = "true"
        if user.email == data['email']:
            user.nickname == data['nickname']
            user.name = data['name']
            user.username = data['new_username']
            user.password = hashed_password
            user.address = data['address']
            db.session.add(user)
            db.session.commit()
            resp['error'] = "null"
            resp['updated'] = "true"
        if user.nickname == data['nickname']:
            user.name = data['name']
            user.username = data['new_username']
            user.email = data['email']
            user.password = hashed_password
            user.address = data['address']
            db.session.add(user)
            db.session.commit()
            resp['error'] = "null"
            resp['updated'] = "true"

        elif User.query.filter_by(email = data['email']).first() is None:
            if User.query.filter_by(username = data['new_username'] ).first() is None:
                user.name = data['name']
                user.username = data['new_username']
                user.email = data['email']
                user.password = hashed_password
                user.address = data['address']
                db.session.add(user)
                db.session.commit()
                resp['error'] = "null"
                resp['updated'] = "true"
        else:
           print("the email and/or username already exists ")
           resp['error'] = "user already exists"
           resp['updated'] = "false"
        print(f"at the end")
        response = create_response_json(json=(jsonify(resp)), request=request)
        if(resp['updated'] == "true"):
            response.set_cookie("loggedin", "true")
            response.set_cookie("user", user.email)
    elif request.method == 'OPTIONS':
        response = create_response_options(request=request)
    return response


@app.route("/logout")
def logout():
    if 'loggedin' in session:
        resp['error'] = 'null'
        resp['loggedin'] = 'false'
        response = make_response((jsonify(resp), 201))
    return response
