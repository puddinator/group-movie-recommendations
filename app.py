from flask import Flask, flash, redirect, render_template, request, jsonify

from scraper import scrape

# Configure application
app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/results", methods=["GET"])
def results():
    number_of_accounts = request.args.get('number_of_accounts')
    username_1 = request.args.get('username_1')
    result = scrape(username_1)
    
    return result