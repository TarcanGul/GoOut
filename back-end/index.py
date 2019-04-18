from flask import Flask
from flask import render_template, url_for, request
import os
import sys
import hashlib

app = Flask(__name__, template_folder="front-end")
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
  if request.method == 'GET':
    return render_template("auth.html")

@app.route("/handlesignup", methods=['POST'])
def handleSignUp():
  username = request.form['username']
  #Hashing the password in MD5
  raw_password = request.form['password']
  raw_password.encode("utf-8")
  password = hashlib.md5(raw_password.encode())
  #TODO: Push username and password to the database. 
  return "<h1>" + username + "</h1>\n" + "<h2>" + password.hexdigest() + "</h2>"

