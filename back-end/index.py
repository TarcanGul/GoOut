from flask import Flask
from flask import render_template, url_for
app = Flask(__name__, template_folder="front-end")
import os
APP_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_PATH = os.path.join(APP_PATH,"../front-end")
app.static_folder="static"

@app.route("/")
def indexWebsite():
	return render_template("index.html")


@app.route("/createEvent")
def serveCreateEventPage():
  return render_template("createEvent.html")

@app.route("/auth")
def serveAuthPage():
  return render_template("auth.html")


