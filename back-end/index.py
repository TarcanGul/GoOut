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

def generateEventID(title):
  return ord(title[0]) * 37

@app.route("/")
def indexWebsite():
	return render_template("index.html")


@app.route("/managerHome/createEvent/<username>")
def serveCreateEventPage(username):
  return render_template("createEvent.html", username=username)

@app.route("/managerAction/addEvent/<username>", methods=['POST'])
def addEvent(username):
  #So the idea is that we have to create a event node using title as key (or maybe some number generated like title_id)
  title = request.form["title"]

  result = firebase.put("/events", title, generateEventID(title))
  #Then we will add rest of the attributes as their child.
  event_attributes = "/events/" + title
  
  location = request.form["location"]
  date = request.form["date"]
  time = request.form["time"]
  description = request.form["description"]

  firebase.put(event_attributes, "manager", username)
  firebase.put(event_attributes, "location", location)
  firebase.put(event_attributes, "date", date)
  firebase.put(event_attributes, "time", time)
  firebase.put(event_attributes, "description", description)
  #Confirmation html
  return redirect(url_for('serveManagerHome', username=username))

@app.route("/auth")
def serveAuthPage():
  if request.method == 'GET':
    return render_template("auth.html")

@app.route("/handleSignUp", methods=['POST'])
def handleSignUp():
  
  #Getting auth variable from query string
  auth = request.args.get("auth")
  username = request.form['username']

  #If auth is for user
  if auth == 'u':
    
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
  #If auth is for manager
  elif auth == 'm':
    result = firebase.get('/managers', username)
    if result == None:
      raw_password = request.form['password']
      raw_password.encode("utf-8")
      password = hashlib.md5(raw_password.encode())
      #TODO: Push username and password to the database.
      push = firebase.put('/managers', username, password.hexdigest())
      return redirect("/")
    #Error: Manager name already exists.
    return redirect("/")
  return "Auth error"
    

  

@app.route("/handleSignIn", methods=['POST'])
def handleSignIn():

  auth = request.args.get("auth")
  username = request.form['username']
   #If auth is for user
  if auth == 'u':
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

   #If auth is for manager
  elif auth == 'm':
    result = firebase.get('/managers', username)
    if result == None:
      #manager does not exist
      #return render_template("managerDoesNotExist.html")
      return redirect("/auth")
    #otherwise, check password
    raw_password = request.form['password']
    raw_password.encode("utf-8")
    password = hashlib.md5(raw_password.encode())
    print(password.hexdigest(), file=sys.stderr)
    print(str(result), file=sys.stderr)
    if str(result) == password.hexdigest():
      #auth success
      return redirect(url_for('serveManagerHome', username=username))
    else:
        #auth fail
      return "Password incorrect"
  
  #if url error
  return "Bad sign in request"

@app.route("/authManager")
def serveManagerAuth():
  return render_template("authManager.html")

#TODO: Keep track of authentication so the user cannot access the manager profile by directly typing the url. 
@app.route("/managerHome/<username>")
def serveManagerHome(username):
  #TODO: Auth first
  result = firebase.get("/managers", username)
  if result == None:
    #Manager does not exist.
    #TODO: Maybe have 404.html to show here.
    return "Manager does not exist."
  return render_template("managerMainPage.html", username=username)

@app.route("/test")
def getUsers():
	title = "dance"
	location = "PMU"


	result = firebase.put('/users', user, pwd)

	result = firebase.get('/users', None)
	return str(result)
