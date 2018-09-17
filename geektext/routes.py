from flask import Flask, render_template, Response, jsonify, url_for
from geektext import app, db
from geektext.models import *
import json

books = Book.query.all()

@app.route('/')
def home():
    return  render_template('home.html', books=books)

@app.route('/<book_title>')
def book_page(book_title):
    target = Book.query.filter(Book.title.like('%'+book_title+'%'))
    return render_template('book.html', book=target.first())
