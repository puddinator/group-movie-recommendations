from flask import Flask, flash, redirect, render_template, request, jsonify

from scraper import scrape_many

# Configure application
app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/results", methods=["GET"])
def results():
    number_of_accounts = int(request.args.get('number_of_accounts'))
    usernames = request.args.to_dict()
    if(number_of_accounts > 5 or len(usernames) > 6):
        return 0
    
    for key in list(usernames.keys()):
        if usernames[key] == 'undefined':
            usernames.pop(key)
    
    return scrape_many(usernames, number_of_accounts)