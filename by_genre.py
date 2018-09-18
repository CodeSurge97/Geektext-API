"""
book browsing and sorting
___ browse books by genre. Browsing must contain cover, title, author, sales and price.
___ browse top sellers in our book store (chose a list of specific books to be in this listed)
___ browse by book sales (ascending /descending)
___ allow pagination based on 10 or 20 results.
___ sort by book title, author, price, sales and date.

"""

from flask import Flask, jsonify, json
import re

app = Flask(__name__)
print(__name__)

books = [
	{
		'title' : 'A Study in Scarlet',
		'author' : 'Arthur Conan Doyle',
		'price' : 17.99,
		'genre' : 'Mystery',
		'sales' : 5
	},
	{
		'title' : 'Alice\'s Adventures in Wonderland',
		'author' : 'Charles L Dodgson',
		'price' : 14.49,
		'genre' : 'Fiction',
		'sales' : 3
	},
	{
		'title' : 'The Prince',
		'author' : 'Niccolo Machiavelli',
		'price' : 12.49,
		'genre' : 'Political Books',
		'sales' : 3
	},
	{
		'title' : 'Trump: The Art of the Deal',
		'author' : 'Donald J Trump & Tony Schwartz',
		'price' : 9.99,
		'genre' : 'Political Books',
		'sales' : 1
	},
	{
		'title' : 'Leadership BS',
		'author' : 'Jeffrey Pfeffer',
		'price' : 29.99,
		'genre' : 'Self Help',
		'sales' : 6
	}
]


@app.route('/<genre>')
def by_genre(genre):
	"""
	returns all books that match a specified genre

	['GET'] request by client. 
	It's not a lenient search: 
	If client had a typo in the request, or searched for
	'Detective' instead of 'Detective Novels', no book
	objects will be returned.

	Paramteres: 
	genre: the specified genre to look for

	Returns:
	200: json objects that list all info about the books
	404: bad route
	"""

	return_value = {}
	for book in books:
		if book['genre'] == genre:
			return_value = {
				'title' : book['title'],
				'author' : book['author'],
				'price' : book['price'],
				'genre' : book['genre'],
				'sales' : book['sales']
			}
	return jsonify(return_value)


@app.route('/sales')
def by_rating():
	"""
	returns all books that are rated in the top 10%

	Paramteres: 

	Returns:
	200: json objects that list all info about the books
	404: bad route
	"""

	return_value = []
	for book in books:
		if float(book['sales']) >= _top_sellers():
			return_value.append({
				'title' : book['title'],
				'author' : book['author'],
				'price' : book['price'],
				'genre' : book['genre'],
				'sales' : book['sales']
			})
	return jsonify(return_value)


def _top_sellers():
	n = 0 #n counting books
	sum_books = 0
	for book in books:
		n += 1
		sum_books += book['sales']
	return (sum_books/n)


if __name__ == '__main__':
	app.debug = True
	app.run(port=5000)
