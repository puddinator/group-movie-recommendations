import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

import datetime

os.chdir('/home/ubuntu/flaskapp')

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure to use SQLite database
usersdb = SQL("sqlite:///users.db")
productsdb = SQL("sqlite:///products.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Query database for username
        rows = usersdb.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username is unique
        if len(rows) == 1:
            return apology("username already used", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure email was submitted
        if not request.form.get("email"):
            return apology("must provide email", 400)

        if not any(c == '@' for c in request.form.get("email")):
            return apology("Email must contain @", 400)

        # Ensure passwords are same
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("password does not match", 400)

        usersdb.execute("INSERT INTO users(username, hash, email) VALUES (?, ?, ?)", request.form.get(
            "username"), generate_password_hash(request.form.get("password")), request.form.get("email"))

        id = usersdb.execute("SELECT id FROM users WHERE username = ?", request.form.get("username"))[0]
        print(id["id"])
        usersdb.execute("CREATE TABLE '{}' (product TEXT UNIQUE, price REAL)".format(id["id"]))

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Query database for username
        rows = usersdb.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 400)

        # Remember which user has logged in
        global username
        username = request.form.get("username")
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:

        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    # If coming from track.html
    if request.form.get("name") is not None:
        
        name = request.form.get("name")

        if not request.form.get("price"):
            return apology("must provide price", 400)
        price = request.form.get("price")
             
        # Add to track
        usersdb.execute("INSERT OR IGNORE INTO '{}' VALUES (?, ?)".format(session["user_id"]), name, price)
        usersdb.execute("UPDATE '{}' SET price = ? WHERE product=?".format(session["user_id"]), price, name)

        # Redirect user to home page
        return redirect("/")

    # Normal route
    else:
        names = []
        infos = []
        graphs = []
        trackednames = usersdb.execute("SELECT product FROM '{}'".format(session["user_id"]))
        trackedprices = usersdb.execute("SELECT price FROM '{}'".format(session["user_id"]))

        for trackedname in trackednames:
            names.append(trackedname["product"])
            infos.append(productsdb.execute("SELECT url, imageurl FROM ?", trackedname["product"])[0])
            graphs.append(productsdb.execute("SELECT date, price FROM ? WHERE date IS NOT NULL", trackedname["product"]))

        print(trackedprices)
        print(infos)
        
        return render_template("index.html", trackedprices=trackedprices, names=names, infos=infos, graphs=graphs)

@app.route("/search", methods=["GET"])
@login_required
def search():

    # User reached route with input
    if request.args.get("product") is not None:

        records = lookup(request.args.get("product"))

        # Redirect user to searched
        return render_template("searched.html", records=records)

    # User reached route with no input
    else:
        return render_template("search.html")

@app.route("/track", methods=["GET", "POST"])
@login_required
def track():

    if request.args.get("name") is not None:
        name = request.args.get("name")
        price = request.args.get("price")
        url = request.args.get("url")
        imageurl = request.args.get("imageurl")

        if productsdb.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", name) == []:
            productsdb.execute("CREATE TABLE ? (url TEXT, imageurl TEXT, date TEXT UNIQUE, price REAL)", name)
            productsdb.execute("INSERT INTO ? (url, imageurl) VALUES (?, ?)", name, url, imageurl)

        date = datetime.date.today()
        productsdb.execute("INSERT OR IGNORE INTO ? (date, price) VALUES (?, ?)", name, date, price)

        graph = productsdb.execute("SELECT date, price FROM ? WHERE date IS NOT NULL", name)
        
        # Redirect user to tracked
        return render_template("track.html", name=name, url=url, imageurl=imageurl, graph=graph)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return redirect("/search")

# @app.route("/trackadd", methods=["GET", "POST"])
# @login_required
# def trackadd():

#     if request.method == "POST":
#         link = request.args.get("link")
#         price = request.args.get("price")

#     # User reached route via GET (as by clicking a link or via redirect)
#     else:
#         return render_template("trackadd.html")

@app.route("/trackremove", methods=["GET", "POST"])
@login_required
def trackremove():

    if request.method == "POST":
        product = request.form.get("product")
        usersdb.execute("DELETE FROM '{}' WHERE product=?".format(session["user_id"]), product)
        return redirect("/")


    # User reached route via GET (as by clicking a link or via redirect)
    else:
        trackednames = usersdb.execute("SELECT product FROM '{}'".format(session["user_id"]))
        return render_template("trackremove.html", trackednames=trackednames)
