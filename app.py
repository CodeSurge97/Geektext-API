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
		'stock' : 5,
        'isbn'  : 12345
	},
	{
		'title' : 'Alice\'s Adventures in Wonderland',
		'author' : 'Charles L Dodgson',
		'price' : 14.49,
		'genre' : 'Fiction',
		'stock' : 3,
        'isbn'  : 12346
	},
	{
		'title' : 'The Prince',
		'author' : 'Niccolo Machiavelli',
		'price' : 12.49,
		'genre' : 'Political Books',
		'stock' : 3,
        'isbn'  : 12347
	},
	{
		'title' : 'Trump: The Art of the Deal',
		'author' : 'Donald J Trump & Tony Schwartz',
		'price' : 9.99,
		'genre' : 'Political Books',
		'stock' : 1,
        'isbn'  : 12348
	},
	{
		'title' : 'Leadership BS',
		'author' : 'Jeffrey Pfeffer',
		'price' : 29.99,
		'genre' : 'Self Help',
		'stock' : 6,
        'isbn'  : 12349
	}
]

@app.route('/')
def home():
    return render_template('cart.html')

@app.route("/addItem/<int:isbn>", methods=["GET", "POST"])
def addItem(isbn):
    if request.method == "POST":
        title = request.form['title']
        author = request.form('author')
        price = float(request.form['price'])
        genre = request.form['genre']
        stock = int(request.form['stock'])
        isbn = int(request.form['isbn'])
        session['cart'].append(isbn)
        print session

        flash("Successfully added to cart.")
        return redirect("addItem")

if __name__ == '__main__':
    app.run()
        


