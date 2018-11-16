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
        a.books.append(b)
        db.session.add(b)
        if len(Author.query.filter_by(name = a.name).all()):
            db.session.add(a)
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

    db.session.commit()

    #now we can add some credit credit cards


    #now we can add some credit credit cards


create()
addFromJson()
