from flask import Flask, render_template, Response, jsonify, url_for
import json

app = Flask(__name__)
data = open("books.json", "r")
books = json.load(data)
data.close()

@app.route('/')
def home():
    return  render_template('home.html', books=books)

@app.route('/<book_title>')
def book_page(book_title):
    target = {}
    for book in books:
        if book_title in book["title"]:
            target = book
    return render_template('book.html', book=target)
