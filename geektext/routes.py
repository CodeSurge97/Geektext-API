import io
from flask import Flask, flash, request, redirect, render_template, make_response, jsonify, url_for, send_file, session
from geektext import app, db, bcrypt
from geektext.models import *
from geektext.forms import RegistrationForm, LoginForm#, SearchForm
from geektext.models import User
from flask_login import login_user, current_user, logout_user, login_required
import json
from datetime import date


@app.route('/books')
def home():
    books = Book.query.order_by(Book.title).all()
    data = []
    for book in books:
        b = { 'title': book.title,
        'isbn': book.isbn,
        'genre': book.genre,
        'rating': book.rating,
        'price' : book.price,
        'img' : url_for('static', filename=book.img),
        'author' : book.authors[0].name,
        'description' : book.book_description, }
        data.append(b)
    response = make_response(jsonify(data))
    if "loggedin" in request.cookies:
        print(f"hello {request.cookies['loggedin']}")
    else:
        print("no cookies")
    if "loggedin" in session:
        print(f"hello {session['loggedin']}")
    else:
        print("no sessionxs")
    response.headers['Content-Type'] = 'application/json'
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response


@app.route('/book/<int:isbn>')
def book_page(isbn):
    book = Book.query.filter_by(isbn=isbn).first()
    #we need to create a dictionary or something for each comment and put it in a list and then put that in the comments of the book or something
    book_comments = []
    for comment in book.comments:
        c = {
            'id' : comment.id,
            'contents' : comment.content,
            'rating' : comment.rating,
            'user_id' : comment.user_id,
            'date' : comment.creation_date,
            'username' : comment.user.username

        }
        book_comments.append(c)

    b = {
        'title': book.title,
        'isbn': book.isbn,
        'genre': book.genre,
        'rating': book.rating,
        'price' : book.price,
        'img' : url_for('static', filename=book.img),
        'author' : book.authors[0].name,
        'author_id' : book.authors[0].id,
        'author_info': book.authors[0].info,
        'description' : book.book_description,
        'comments' : book_comments,
        'pub_info' : book.pub_info,
        'date_pub' : book.date_pub
        }
    response = make_response(jsonify(b))
    response.headers['Content-Type'] = 'application/json'
    response.headers['Access-Control-Allow-Origin'] = request.headers['Origin']
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

    response = make_response(jsonify(a))
    response.headers['Content-Type'] = 'application/json'
    response.headers['Access-Control-Allow-Origin'] = request.headers['Origin']
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

#Comments and stuff
def print_request(request):
    print(100*"-")
    print(session)
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

@app.route('/comment/<int:user_id>', methods=['GET', 'POST', 'OPTIONS'])
def add_comment(user_id):
    if request.method == 'POST':
        print_request(request)
        user = User.query.get(user_id)
        comment = request.get_json()
        c = Comment(content=comment['content'], creation_date=date.today(), book_isbn=comment['isbn'], rating=comment['rating'], user_id=comment['user_id'])
        print(c)
        db.session.add(c)
        db.session.commit()
        response = make_response(jsonify("hello"))
    elif request.method == 'OPTIONS':
        print_request(request)
        response = make_response(jsonify(""))
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
    authors = Author.query.order_by(Author.name)
    data = []
    for author in authors:
        print(f"this is the name of the author {author.name}")
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
    response = make_response(jsonify(data))
    response.headers['Content-Type'] = 'application/json'
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
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
    response = make_response(jsonify(data))
    response.headers['Content-Type'] = 'application/json'
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
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
    response = make_response(jsonify(data))
    response.headers['Content-Type'] = 'application/json'
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
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
    response = make_response(jsonify(data))
    response.headers['Content-Type'] = 'application/json'
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

@app.route("/get-cart/<int:id>", methods=['GET', 'POST', 'OPTIONS'])
def get_cart(id):
    response = make_response()
    if request.method == 'GET':
        if 'cart_id' in session:
            cart_id = session["cart_id"]
            cart = Cart.query.get(cart_id)
            data = []
            for item in cart.cart_items:
                c = {
                    'count': item.count,
                    'book': item.book_isbn
                }
                data.append(c)
        else:
            cart_id = id
            cart = Cart.query.get(cart_id)
            data = []
            for item in cart.cart_items:
                c = {
                    'count': item.count,
                    'book': item.book_isbn
                }
                data.append(c)
        response = make_response(jsonify(data))
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
    elif request.method == 'OPTIONS':
        response = make_response(jsonify(""))
        response.headers['Content-Type'] = 'application/json'
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
        response.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-PINGOTHER'
        response.headers['Access-Control-Max-Age'] = '86400'
    return response

@app.route("/add-to-cart/<int:user_id>", methods=['GET', 'POST', 'OPTIONS'])
def add_to_cart(user_id):
    if request.method == 'POST':
        response = make_response()
        print_request(request)
        data = request.get_json()
        #we need to add the new book to the shopping cart
        #data contains the information about the book that we need to add to the cart
        book_isbn = data["isbn"]
        #we need to check if there is a cookie with id of the cart. if not then we need to create a new cart
        if True:
            print("there is a cookie in the request")
            print(f"the cookie is {request.cookies.get('cart_id')}")
            cart_id = user_id
            cart = Cart.query.get(cart_id)
            #now we need to know if the book is already in the cart or not
            added = False
            for item in cart.cart_items:
                if book_isbn == item.book_isbn:
                    print(f"The book {item.book.title} is already in the shopping cart")
                    #we need to add 1 to the count attribute in CartItem
                    item.count = item.count + 1
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
            #here we can check if the user is logged in and add the user_id to the cart
            #if there is no user_id, then just create a new empty cart.
            print("creating a new empty cart")
            c = Cart()
            #we need to add the new empty cart to the db so that it gets a unique id number
            db.session.add(c)
            db.session.commit()
            #now we can just set the cookie with the id number
            id = c.id
            print(f"the id of the new cart is {id}")
            #add the book to the empty cart
            new_item = CartItem(count=1, cart_id=id, book_isbn=book_isbn)
            print(f"creating a new cart item to store the book \n{new_item}")
            db.session.commit()
            session['cart_id'] = id
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
    elif request.method == 'OPTIONS':
        response = make_response(jsonify(""))
        response.headers['Content-Type'] = 'application/json'
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
        response.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-PINGOTHER'
        response.headers['Access-Control-Max-Age'] = '86400'

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


#PROFILE MANAGEMENT STUFF

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
    if request.method == 'POST':
        resp = {}
        data = request.get_json()
        email = data["email"]
        password = data["password"]
        print(f"the email and the password are: {email}, {password}")
        if User.query.filter_by(email = email).first() is not None:
            u = User.query.filter_by(email = email).first()
            if u.password == password:
                print("the user exist and the password is correct")
                resp['error'] = "null"
                resp['loggedin'] = "true"
            else:
                print("the user exist but the password is wrong")
                resp['error'] = "wrong password"
                resp['loggedin'] = "false"
        else:
            print("the user does not exist")
            resp['error'] = "email doesn't exist"
            resp['loggedin'] = "false"
        print(f"at the end")
        response = make_response((jsonify(resp), 201))
        if(resp['loggedin'] == "true"):
            print("setting the cookie")
            response.set_cookie("loggedin", "true")
            session['user'] = email
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
        print(response.headers)
    elif request.method == 'OPTIONS':
        response = make_response(jsonify(""))
        response.headers['Content-Type'] = 'application/json'
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
        response.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-PINGOTHER'
    print(f"this is the response for the login {response.data}")
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
