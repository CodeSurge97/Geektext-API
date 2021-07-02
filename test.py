import json
from geektext.models import *
from geektext import db, bcrypt
from datetime import date
from random import *

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
    d = date(year=randint(1999,2017), day=randint(1,27), month=randint(1,12))
    d.isoformat()
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
        if len(Author.query.filter_by(name=a.name).all()) < 1:
            a.books.append(b)
            db.session.add(a)
            #print(f"adding author {a.name}")
        else:
            a = Author.query.filter_by(name=a.name).first()
            a.books.append(b)
        db.session.commit()
        #print(f"adding book {b.title}")

    #Create some users
    ps1 = bcrypt.generate_password_hash('1234567').decode('utf-8')
    ps2 = bcrypt.generate_password_hash('28974293').decode('utf-8')
    ps3 = bcrypt.generate_password_hash('787324').decode('utf-8')
    ps4 = bcrypt.generate_password_hash('23948529').decode('utf-8')
    ps5 = bcrypt.generate_password_hash('564564').decode('utf-8')
    users = [ User(name='Tomas Ortega', nickname='Toms', username='tomsOrtega', email='torte007@fiu.edu', password=ps1, address='7 Pumpkin Hill St. Fresh Meadows, NY 11365'),
            User(name='Pavlina Richards', nickname='pavv', username='anserinepavlina', email='pavlina_donald@gmail.com', password=ps2, address='9607 Wentworth Drive Muskogee, OK 74403'),
            User(name="Jose O'Connor", nickname='ElJose', username='ashystephen', email='stephenoconnor17@gmail.com', password=ps3, address='6 SE. Cherry Hill Ave. Glendale, AZ 85302'),
            User(name='Justyne Henrietta', nickname='Just-Justyne', username='boldjustyne', email='crunchyjustyne@gmail.com', password=ps4, address='65 Fremont Lane Lady Lake, FL 32159'),
            User(name='Augustina Collins', nickname='Augustina', username='augustinacollins60', email='almondyaugustina@gmail.com', password=ps5, address='40 Bohemia Rd. Muskego, WI 53150'),
            User(name='Aiysha Flynn', nickname='Flynn_', username='flynnAiysha', email='flynnAiysha@fiu.edu', password=ps1, address='7 Pumpkin Hill St. Fresh Meadows, NY 11365'),
            User(name='Jasper Kaiser', nickname='Kaiser', username='kaiserJasper', email='kaiserJasper@gmail.com', password=ps2, address='9607 Wentworth Drive Muskogee, OK 74403'),
            User(name="Osian Parks", nickname='Osian11', username='Parks', email='parksandrecreation@gmail.com', password=ps3, address='6 SE. Cherry Hill Ave. Glendale, AZ 85302'),
            User(name='Albi Montgomery', nickname='Montgomery-Montgomery', username='montgomery', email='Montgomery@gmail.com', password=ps4, address='65 Fremont Lane Lady Lake, FL 32159'),
            User(name='Chace Millington', nickname='ChaceTheRapper', username='millington9898', email='mling998@gmail.com', password=ps5, address='40 Bohemia Rd. Muskego, WI 53150')]
    for u in users:
        db.session.add(u)
        #print(f"adding user {u.name}")
    comments = ["I am ready to meet my Maker. Whether my Maker is prepared for the great ordeal of meeting me is another matter.",
                "I feel sorry for people who don't drink. When they wake up in the morning, that's as good as they're going to feel all day.",
                "Don't want to close my eyes I don't want to fall asleep Cause I'd miss you babe And I don't want to miss a thing Cause even when I dream of you The sweetest dream will never do I'd still miss you babe And I don't want to miss a thing.",
                "I like to wax my legs and stick the hair on my back. Why? Because it keeps my back warm. There's method in my madness.",
                "Let me take a nap... great shot, anyway.",
                "My 40 year old child rates this shot very incredible!!",
                "My inheritance is a fairytale, and I want to cut back. For all lovely ambition, my friend.",
                "Little afraid its eat looked now. Very ye lady girl them good me make. It hardly cousin me always. An shortly village is raising we shewing replied",
                "Full he none no side. Uncommonly surrounded considered for him are its. It we is read good soon. My to considered delightful invitation announcing of no decisively boisterous.",
                "Far concluded not his something extremity. Want four we face an he gate. On he of played he ladies answer little though nature. Blessing oh do pleasure as so formerly."
                "Last Christmas, I gave you my car. But the very next day, you threw it away. This year, to save me from tears. I'll give it to Kristen Stewart",
                "Hello world",
                "This is the best book",
                "All these comments are so random",
                "These comments are really really random",
                "The banana drops deep as does my compass. I never drink, 'cause to drink is the friend of gyrocompass. Beyond the walls of jugs, life is defined.",
                "What more could you ask for? The cool banana? You complain about snow. I gotta love it though - somebody still speaks for the piano.",
                "A pointy pineapple is quite the snapple.",
                "I can't take the volume, can't take the map. I woulda tried to taste I guess I got no sap."]
    num_of_books = len(Book.query.order_by(Book.title).all())
    array_of_isbns = []
    for book in Book.query.order_by(Book.title).all():
        array_of_isbns.append(book.isbn)

    def update_average_rating(book_isbn):
        averageRating = db.session.query(db.func.avg(Comment.rating)).filter(Comment.book_isbn == book_isbn).scalar()
        db.session.execute("UPDATE book SET rating = :ar WHERE isbn = :bi", {'ar' : averageRating, 'bi' : book_isbn})


    def update_numRatings(book_isbn):
        numRatings = db.session.query(db.func.count(Comment.rating)).filter(Comment.book_isbn == book_isbn).scalar()
        db.session.execute("UPDATE book SET numRatings = :nr WHERE isbn = :bi", {'nr' : numRatings, 'bi' : book_isbn})

    for i in range(5, 10):
        order2 = Order(order_date=date.today())
        for book in Book.query.order_by(Book.title):
            order2.books.append(book)
        users[i].orders.append(order2)
        for book in Book.query.order_by(Book.title).all():
            if randint(1, 100) < 60:
                content = comments[randint(0, len(comments) - 2)]
                c = Comment(content=content, creation_date=get_random_date().strftime("%Y-%m-%d %I:%M %p"), book_isbn=book.isbn, rating=randint(1,5), user_id=users[i].id, anon=randint(1,3))
                db.session.add(c)
                update_numRatings(book.isbn)
                update_average_rating(book.isbn)
    #now we can add some orders
    order2 = Order(order_date=date.today())
    for book in Book.query.order_by(Book.title):
        order2.books.append(book)
    users[0].orders.append(order2)
    db.session.add(order2)
    order1 = Order(order_date=date.today())
    order1.books.append(Book.query.filter_by(title="The Outsider").first())
    order1.books.append(Book.query.filter_by(title="Harry Potter and the Sorcerer's Stone").first())
    users[3].orders.append(order1)
    db.session.add(order1)
    order3 = Order(order_date=date.today())
    order3.books.append(Book.query.filter_by(title="Cracking the Coding Interview: 189 Programming Questions and Solutions").first())
    users[1].orders.append(order3)
    db.session.add(order3)

    db.session.commit()

    #now we can add some credit credit cards


    #now we can add some credit credit cards


create()
addFromJson()
