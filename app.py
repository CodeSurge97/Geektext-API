from flask import Flask, render_template

app = Flask(__name__)
"""
Using Pablo Mueller's dictionary
"""
inventory = {
	'books': {
		1: {
			'isbn'  : 12345,
			'title' : 'A Study in Scarlet',
			'author' : 'Arthur Conan Doyle',
			'price' : 17.99,
			'genre' : 'Mystery',
			'stock' : 5
		}
	}
}


@app.route('/')
def home():
    return render_template('add.html')

@app.route('/addItem/isbn')
def addItem():
    return render_template('add.html')

if __name__ == '__main__':
    app.run()
        


