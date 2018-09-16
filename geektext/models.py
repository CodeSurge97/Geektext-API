from geektext import db

#relationship table between Author and Book. since it is a many to many relaitonship we need a new table called publish

publish = db.Table('publish',
    db.Column('book_isbn', db.BigInteger, db.ForeignKey('book.isbn')),
    db.Column('author_name', db.String(100), db.ForeignKey('author.name'))
)

class Author(db.Model):
    name = db.Column(db.String(100), primary_key=True)
    info = db.Column(db.Text)
    books = db.relationship('Book', secondary=publish, backref=db.backref('authors'))

    def __repr__(self):
        return f"Author( name: '{self.name}' )"

transactions = db.Table('transactions',
    db.Column('book_isbn', db.BigInteger, db.ForeignKey('book.isbn'), primary_key=True),
    db.Column('order_id', db.Integer, db.ForeignKey('order.id'), primary_key=True)
)

class Book(db.Model):
    isbn = db.Column(db.BigInteger, primary_key=True)
    title = db.Column(db.String(100), unique=True, nullable=False)
    date_pub = db.Column(db.Date)
    genre = db.Column(db.String(100))
    rating = db.Column(db.Integer)
    price = db.Column(db.Float)
    img = db.Column(db.String(100))
    pub_info = db.Column(db.Text)
    book_description = db.Column(db.Text)
    comments = db.relationship('Comment', backref=db.backref('book'), lazy=True)

    def __repr__(self):
        return f"Book( titel: '{self.title}' )"

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_date = db.Column(db.Date)
    books = db.relationship('Book', secondary=transactions)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f"Order( orderID: {self.id}, userID: {self.user_id}, date: {self.order_date})"

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    address = db.Column(db.String, nullable=False)
    orders = db.relationship('Order', backref='user', lazy=True)
    comments = db.relationship('Comment', backref=db.backref('user'), lazy=True)

    def __repr__(self):
        return f"User( email: '{self.email}', username: '{self.username}')"

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    creation_date = db.Column(db.Date)
    book_isbn = db.Column(db.BigInteger, db.ForeignKey('book.isbn'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f"Comment( commentID: '{self.id}', book: '{self.book_isbn}', userID: '{self.user_id}')"
