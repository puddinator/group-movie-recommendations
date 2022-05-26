from flask import Flask, flash, redirect, render_template, request, session

from helpers import get_url

# Configure application
app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/loading", methods=["POST"])
def loading():
    return render_template("loading.html")

@app.route("/results", methods=["POST"])
def results():
    return render_template("results.html")