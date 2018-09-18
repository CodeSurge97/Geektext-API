from flask import Flask
from flask import render_template
from datetime import datetime
from request import request

app = Flask(__name__)

@app.route("/hello/<name>")
def whats_up(name):
    return render_template(
        "boiler.html",
        name=name,
        date=datetime.now()
    )

@app.route("/addItem", methods=["GET", "POST"])
def addItem():
    if request.method == "POST":
        name = request.form['name']
        price = float(request.form['price'])
        description = request.form['description']
        stock = int(request.form['stock'])
        categoryId = int(request.form['category'])