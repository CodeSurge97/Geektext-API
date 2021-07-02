from geektext import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#author_book_relationship is a table with two columns book_isbn and author_name
#it relates a book with the author that wrote it

author_book_relationship = db.Table('author_book_relationship',
    db.Column('book_isbn', db.BigInteger, db.ForeignKey('book.isbn'), primary_key=True),
    db.Column('author_name', db.String(100), db.ForeignKey('author.name'), primary_key=True)
)

#Author is a table that contains every author in the database
#The attributes are: name, info, and books

class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    info = db.Column(db.Text)
    img = db.Column(db.String(100))
    books = db.relationship('Book', secondary=author_book_relationship, backref=db.backref('authors'))

    def __repr__(self):
        return f"Author( name: '{self.name}' )"

#order_book_relationship is a table that relates an order with the books that is contains
#the attributes of order_book_relationship are: book_isbn, and order_id
order_book_relationship = db.Table('order_book_relationship',
    db.Column('book_isbn', db.BigInteger, db.ForeignKey('book.isbn'), primary_key=True),
    db.Column('order_id', db.Integer, db.ForeignKey('order.id'), primary_key=True)
)

#The Book table has the following attributes:
#isbn, title, date_pub, genre, rating, price, img, pub_info, book_description, comments, and authors.
#the authors of the book can be used like any other attribute because of the backref in the Author table.
class Book(db.Model):
    isbn = db.Column(db.BigInteger, primary_key=True)
    title = db.Column(db.String(100), unique=True, nullable=False)
    date_pub = db.Column(db.String(100))
    genre = db.Column(db.String(100))
    rating = db.Column(db.Float)
    numRatings = db.Column(db.BigInteger)
    price = db.Column(db.Float)
    img = db.Column(db.String(100))
    pub_info = db.Column(db.Text)
    book_description = db.Column(db.Text)
    comments = db.relationship('Comment', backref=db.backref('book'), lazy=True)
    carts = db.relationship('CartItem', backref=db.backref('book'), lazy=True)

    def __repr__(self):
        return f"Book( titel: '{self.title}' )"

#The Order table stores the transactions in the store
#the attributes of the Order table are: id, order_date, books, user_id, and you can also
#access the user that made the order because of the backref in the User table
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_date = db.Column(db.Date)
    books = db.relationship('Book', secondary=order_book_relationship)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f"Order( orderID: {self.id}, userID: {self.user_id}, date: {self.order_date})"

#The User table stores the users in the site
#the attributes of the User table are: id, name, username, email, password, address, orders, comments.
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(15), unique=True)
    name = db.Column(db.String(30), nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    address = db.Column(db.String)
    orders = db.relationship('Order', backref=db.backref('user'), lazy=True)
    comments = db.relationship('Comment', backref=db.backref('user'), lazy=True)
    credit_cards = db.relationship('CreditCard', backref=db.backref('user'), lazy=True)
    cart = db.relationship('Cart', backref=db.backref('user'), lazy=True)

    def __repr__(self):
        return f"User( email: '{self.email}', username: '{self.username}', password: '{self.password}')"


class CreditCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    card_type = db.Column(db.String(20))
    # I actually don't know if this cvv attribute shoult be a string or an Integer
    card_number = db.Column(db.String(20), unique=True)
    cvv = db.Column(db.Integer)
    exp_date = db.Column(db.Date)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f"CreditCard( card_number: '{self.card_number[:4]}', user: '{self.user.name}')"


#The Comment table stores the comments for each book
#the attributes of the Comment table are: id, content, creation_date, book_isbn, and user_id
#you can also access the user that made the comment and the book that the comment is about because of the relationships.
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    creation_date = db.Column(db.Text)
    rating = db.Column(db.Float)
    book_isbn = db.Column(db.BigInteger, db.ForeignKey('book.isbn'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    anon = db.Column(db.Integer)

    def __repr__(self):
        return f"Comment( commentID: '{self.id}', rating: '{self.rating}', content: '{self.content}', book: '{self.book_isbn}', userID: '{self.user_id}', anon: '{self.anon}')"


class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer)
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id'))
    book_isbn = db.Column(db.Integer, db.ForeignKey('book.isbn'))
    price = db.Column(db.Integer)

    def __repr__(self):
        return f"CartItem( id: '{self.id}', cart_id: '{self.cart_id}', book_isbn: '{self.book_isbn}', count: '{self.count}', price: '{self.price}')"

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.Date)
    cart_items = db.relationship('CartItem', backref=db.backref('cart'), lazy=True)

    def __repr__(self):
        return f"ShoppingCart( cart_id: '{self.id}', user_id: '{self.user_id}')"
