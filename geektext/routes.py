import io
from flask import Flask, flash, request, redirect, render_template, make_response, jsonify, url_for, send_file
from geektext import app, db, bcrypt
from geektext.models import *
from geektext.forms import RegistrationForm, LoginForm#, SearchForm
from geektext.models import User
from flask_login import login_user, current_user, logout_user, login_required
import json
from datetime import date, datetime
from falcon import errors, media


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
    book_comments = []
    for comment in book.comments:
        c = {
            'id' : comment.id,
            'contents' : comment.content,
            'rating' : comment.rating,
            'user_id' : comment.user_id,
            'date' : comment.creation_date,
            'username' : comment.user.username,
            'nickname' : comment.user.name,
            'anon' : comment.anon
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

    }

    response = make_response(jsonify(a))
    response.headers['Content-Type'] = 'application/json'
    response.headers['Access-Control-Allow-Origin'] = request.headers['Origin']
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

#RATE AND COMMENT


def update_average_rating(book_isbn):
    averageRating = db.session.query(db.func.avg(Comment.rating)).filter(Comment.book_isbn == book_isbn).scalar()
    db.session.execute("UPDATE book SET rating = :ar WHERE isbn = :bi", {'ar' : averageRating, 'bi' : book_isbn})


def update_numRatings(book_isbn):
    numRatings = db.session.query(db.func.count(Comment.rating)).filter(Comment.book_isbn == book_isbn).scalar()
    db.session.execute("UPDATE book SET numRatings = :nr WHERE isbn = :bi", {'nr' : numRatings, 'bi' : book_isbn})


def book_exists(book_isbn):
    return Book.query.get(book_isbn) is not None


def user_exists(user_id):
    return User.query.get(user_id) is not None


def book_purchased(user_id, book_isbn):
    u = User.query.get(user_id)
    for orderByUser in range(len(u.orders)):
        for bookInOrder in range(len(u.orders[orderByUser].books)):
            if u.orders[orderByUser].books[bookInOrder].isbn == book_isbn:
                return True
    return False


def rated_already(user_id, book_isbn):
    return db.session.query(db.func.count(Comment.user_id)).filter(Comment.user_id == user_id).filter(Comment.book_isbn == book_isbn).scalar() is not 0


@app.route('/insert-rating')
def open_ratings_page():
    return render_template("ratings.html")


@app.route('/rate-and-comment', methods=['POST', 'GET'])
def rate_and_comment():
    db.session.rollback()
    user_id = request.form['user_id']
    book_isbn = request.form['isbn']
    rating = request.form['rating']
    comment = request.form['comment']
    anon = request.form['anon']
    if book_exists(book_isbn) and user_exists(user_id):
        if book_purchased(user_id, int(book_isbn)):
            if not rated_already(user_id, book_isbn):
                r = Comment(user_id=user_id, content=comment, rating=rating, book_isbn=book_isbn)
                db.session.add(r)
            else:
                db.session.execute("UPDATE comment SET rating = :r, content = :c WHERE user_id = :ui AND book_isbn = :bi", {'r': rating, 'c': comment, 'ui': user_id, 'bi': book_isbn})
        else:
            flash("This book was not purchased.")
    else:
        if not user_exists(user_id):
            flash("This user does not exist.")
        if not book_exists(book_isbn):
            flash("The book was not found in the database.")
    update_average_rating(book_isbn)
    update_numRatings(book_isbn)
    db.session.commit()
    myBooks = Book.query.all()
    myRating = Comment.query.all()
    return render_template("test.html", myBooks=myBooks, myRating=myRating)


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


@app.route('/<int:book>/ratings')
def get_ratings(book):
    db.session.rollback()
    return Comment.query.filter_by(book_isbn=book)


@app.route('/comment/<int:user_id>', methods=['GET', 'POST', 'OPTIONS'])
def add_comment(user_id):
    if request.method == 'POST':
        db.session.rollback()
        comment = request.get_json()
        c = Comment(content=comment['content'], creation_date=datetime.now().strftime("%Y-%m-%d %H:%M"), book_isbn=comment['isbn'], rating=comment['rating'], user_id=comment['user_id'], anon=comment['anon'])
        if user_exists(c.user_id):
            if book_purchased(user_id, int(c.book_isbn)):
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
        response = make_response(jsonify("hello"))
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


@app.route("/add-to-cart/<int:user_id>", methods=['GET', 'POST', 'OPTIONS'])
def add_to_cart(user_id):
    if request.method == 'POST':
        response = make_response()
        data = request.get_json()
        #we need to add the new book to the shopping cart
        #data contains the information about the book that we need to add to the cart
        book_isbn = data["isbn"]
        #we need to check if there is a cookie with id of the cart. if not then we need to create a new cart
        if 'cart_id' in request.cookies:
            print("there is a cookie in the request")
            print(f"the cookie is {request.cookies.get('cart_id')}")
            cart_id = request.cookies.get("cart_id")
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
            response.set_cookie('cart_id', str(id))

    elif request.method == 'OPTIONS':
        response = make_response(jsonify(""))
        response.headers['Content-Type'] = 'application/json'
        response.headers['Access-Control-Allow-Origin'] = request.headers['Origin']
        response.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-PINGOTHER'
        response.headers['Access-Control-Max-Age'] = '86400'

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
