from flask import Flask, render_template, make_response, jsonify, url_for, send_file
from geektext import app, db
from geektext.models import *
import io

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

@app.route('/books/<isbn>')
def book_page(book_title):

    target = Book.query.filter(Book.title.like('%'+book_title+'%'))
    return render_template('book.html', book=target.first())



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
