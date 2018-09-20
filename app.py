from flask import Flask, session, redirect, url_for, escape, request
from flask import render_template
from datetime import datetime

app = Flask(__name__)
"""
Using Pablo Mueller's dictionary
"""
books = [
	{
		'title' : 'A Study in Scarlet',
		'author' : 'Arthur Conan Doyle',
		'price' : 17.99,
		'genre' : 'Mystery',
		'sales' : 5,
        'isbn'  : 12345
	},
	{
		'title' : 'Alice\'s Adventures in Wonderland',
		'author' : 'Charles L Dodgson',
		'price' : 14.49,
		'genre' : 'Fiction',
		'sales' : 3,
        'isbn'  : 12346
	},
	{
		'title' : 'The Prince',
		'author' : 'Niccolo Machiavelli',
		'price' : 12.49,
		'genre' : 'Political Books',
		'sales' : 3,
        'isbn'  : 12347
	},
	{
		'title' : 'Trump: The Art of the Deal',
		'author' : 'Donald J Trump & Tony Schwartz',
		'price' : 9.99,
		'genre' : 'Political Books',
		'sales' : 1,
        'isbn'  : 12348
	},
	{
		'title' : 'Leadership BS',
		'author' : 'Jeffrey Pfeffer',
		'price' : 29.99,
		'genre' : 'Self Help',
		'sales' : 6,
        'isbn'  : 12349
	}
]

@app.route("/cart/<isbn>", methods=["GET", "POST"])
def addItem():
    """
    This is a method to add items to a shopping
    cart. It will find the id requested and add
    the items to the list.

    """


