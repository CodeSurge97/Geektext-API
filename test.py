import json
from geektext.models import *
from geektext import db
from datetime import date
import random

data = open("books.json", "r")
books = json.load(data)
data.close()

def create():
    db.session.rollback()
    db.drop_all()
    print("Removing all the tables in the database")
    db.create_all()
    print("creating new tables")

def get_random_date():
    d = date(year=random.randint(1999,2018), day=random.randint(1,30), month=random.randint(1,12))
    return d

def addFromJson():
    db.session.rollback()
    #Create some books and authors
    for book in books:
        #Create a new book b published on date d and with a price of p
        d = get_random_date()
        p = float(book["price"])
        b = Book(isbn=book["isbn"], genre=book["genre"], title=book["title"], img=book["img"], date_pub=d, price=p, book_description=book["description"], pub_info=book["publishing_info"], rating=book["rating"])
        #Create a new author a
        a = Author(name=book["author"], info=book['author_info'], img=book['author_pic'])
        #Declare that author a wrote the book b
        db.session.add(b)
        print(f"the length is: {len(Author.query.filter_by(name = a.name).all())}")
        if len(Author.query.filter_by(name = a.name).all()) < 1:
            print("adding a new author")
            db.session.add(a)
            a.books.append(b)
        else:
            print("the author already exists")
            a = Author.query.filter_by(name = a.name).first()
            a.books.append(b)
        db.session.commit()
        print(f"adding book {b.title}")

    #Create some users
    user1 = User(name='Tomas Ortega', username='tomsOrtega', email='torte007@fiu.edu', password='1234567', address='7 Pumpkin Hill St. Fresh Meadows, NY 11365')
    user2 = User(name='Pavlina Richards', username='anserinepavlina', email='pavlina_donald@gmail.com', password='28974293', address='9607 Wentworth Drive Muskogee, OK 74403')
    user3 = User(name="Jose O'Connor", username='ashystephen', email='stephenoconnor17@gmail.com', password='787324', address='6 SE. Cherry Hill Ave. Glendale, AZ 85302')
    user4 = User(name='Justyne Henrietta', username='boldjustyne', email='crunchyjustyne@gmail.com', password='23948529', address='65 Fremont Lane Lady Lake, FL 32159')
    user5 = User(name='Augustina Collins', username='augustinacollins60', email='almondyaugustina@gmail.com', password='564564', address='40 Bohemia Rd. Muskego, WI 53150')
    db.session.add(user1)
    print(f"adding user {user1.name}")
    db.session.add(user2)
    print(f"adding user {user2.name}")
    db.session.add(user3)
    print(f"adding user {user3.name}")
    db.session.add(user4)
    print(f"adding user {user4.name}")
    db.session.add(user5)
    print(f"adding user {user5.name}")

    #now we can add some orders
    order1 = Order(order_date=date.today())
    order1.books.append(Book.query.filter_by(title="The Outsider").first())
    order1.books.append(Book.query.filter_by(title="Harry Potter and the Sorcerer's Stone").first())
    user4.orders.append(order1)
    db.session.add(order1)
    order2 = Order(order_date=date.today())
    order2.books.append(Book.query.filter_by(title="Cracking the Coding Interview: 189 Programming Questions and Solutions").first())
    order2.books.append(Book.query.filter_by(title="Harry Potter and the Sorcerer's Stone").first())
    order2.books.append(Book.query.filter_by(title="Crazy Rich Asians").first())
    user1.orders.append(order2)
    db.session.add(order2)
    order3 = Order(order_date=date.today())
    order3.books.append(Book.query.filter_by(title="Cracking the Coding Interview: 189 Programming Questions and Solutions").first())
    user2.orders.append(order3)
    db.session.add(order3)

    #add some comments
    isbn = Book.query.filter_by(title="Cracking the Coding Interview: 189 Programming Questions and Solutions").first().isbn
    comment1 = Comment(content="the book is great I love it!", creation_date=date.today(), rating=3.2)
    comment1.book_isbn = isbn
    comment1.user_id = user4.id
    db.session.add(comment1)
    print(Comment.query.filter_by(book_isbn=isbn).first())

    isbn2 = Book.query.filter_by(title="The Outsider").first().isbn
    comment2 = Comment(content="This book is soo scary", creation_date=date.today(), rating=4.5)
    comment2.book_isbn = isbn2
    comment2.user_id = user1.id
    db.session.add(comment2)

    comment3 = Comment(content="Hello world!", creation_date=date.today(), book_isbn=isbn, rating=4)
    comment3.user_id = user2.id
    db.session.add(comment3)


    isbn4 = Book.query.filter_by(title="Pet Sematary").first().isbn
    comment4 = Comment(content="Hello from the other side!!", creation_date=date.today(), book_isbn=isbn4, rating=2)
    comment4.user_id = user5.id
    db.session.add(comment4)

    isbn5 = Book.query.filter_by(title="Pet Sematary").first().isbn
    comment5 = Comment(content="Ans barbieren tal spurenden gewandert ins geschickt hemdarmel schreiben. Regnete wimpern se fadelte kleinen ri. Meisten stopfen beinahe braunen am se. Mu stunden beinahe filzhut konntet im er. Aufmerksam ein und dammerigen dazwischen todesfalle hab. Halboffene aufgespart vorsichtig tat frohlicher tag vom. Langweilig te marktplatz neidgefuhl ordentlich hausdacher am zu messingnen. ", creation_date=date.today(), book_isbn=isbn5, rating=4.3)
    comment5.user_id = user5.id
    db.session.add(comment5)

    isbn6 = Book.query.filter_by(title="A Study in Scarlet").first().isbn
    comment6 = Comment(content="Dame kinn so es tust. Eigentlich an zu hufschmied verdrossen. Wei regen zog schlo vom das nahen. Der hierin tat soviel gehabt keinem und. Horen woher recht so la wills. Dus gemessen schlafen behalten gerechte gar launisch das sie reinlich. ", creation_date=date.today(), book_isbn=isbn6, rating=4)
    comment6.user_id = user3.id
    db.session.add(comment6)

    isbn7 = Book.query.filter_by(title="Cracking the Coding Interview: 189 Programming Questions and Solutions").first().isbn
    comment7 = Comment(content="Hausdacher nachmittag erkundigte flo hob kindlichen. Nachdem traurig dritten das meinung standen von ihn auf ubrigen.", creation_date=date.today(), book_isbn=isbn, rating=5)
    comment7.user_id = user2.id
    db.session.add(comment7)
    db.session.commit()

    #new cart
    c = Cart()
    db.session.add(c)
    db.session.commit()

    #now we can add some credit credit cards


create()
addFromJson()
