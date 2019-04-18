from flask import Flask
from flask import render_template, url_for, request, redirect
from firebase import firebase

import os
import sys
import hashlib

app = Flask(__name__, template_folder="front-end")
APP_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_PATH = os.path.join(APP_PATH,"../front-end")
app.static_folder="static"

#fireabse setup
projectID = "https://goout-5cd6e.firebaseio.com/"
firebase = firebase.FirebaseApplication(projectID, None)



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

#TODO: Integrate manager sign up too maybe using a basic query string to understand whether if is the user signing up or manager. 
@app.route("/handleSignUp", methods=['POST'])
def handleSignUp():
  username = request.form['username']
  #check username
  result = firebase.get('/users', username)
  if result == None:
	  #Hashing the password in MD5
	  raw_password = request.form['password']
	  raw_password.encode("utf-8")
	  password = hashlib.md5(raw_password.encode())
	  #TODO: Push username and password to the database.
	  push = firebase.put('/users', username, password.hexdigest())
	  return redirect("/")

	#setup new html page that displays "ERROR: user already exists"
  return redirect("/")
  #return render_template("userAlreadyExist.html")

#TODO: Integrate manager sign in too maybe using a basic query string to understand whether if is the user signing in or manager. 
@app.route("/handleSignIn", methods=['POST'])
def handleSignIn():
  username = request.form['username']
  #check username
  result = firebase.get('/users', username)
  if result == None:
	  #user does not exist
	  #return render_template("userDoesNotExist.html")
	  return redirect("/auth")
  #otherwise, check password
  raw_password = request.form['password']
  raw_password.encode("utf-8")
  password = hashlib.md5(raw_password.encode())
  print(password.hexdigest(), file=sys.stderr)
  print(str(result), file=sys.stderr)
  if str(result) == password.hexdigest():
	  #auth success
	  return redirect("/")
  else:
  	  #auth fail
	  return "Password incorrect"

@app.route("/authManager")
def serveManagerAuth():
  return render_template("authManager.html")

@app.route("/test")
def getUsers():
	title = "dance"
	location = "PMU"


	result = firebase.put('/users', user, pwd)

	result = firebase.get('/users', None)
	return str(result)
