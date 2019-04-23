from flask import Flask
from flask import render_template, url_for, request, redirect
from firebase import firebase

import os
import sys
import hashlib


app = Flask(__name__, template_folder="front-end")
APP_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_PATH = os.path.join(APP_PATH, "../front-end")
app.static_folder = "static"

# fireabse setup
projectID = "https://goout-5cd6e.firebaseio.com/"
firebase = firebase.FirebaseApplication(projectID, None)


def generateEventID(title):
    # TODO: The generateEventID() method should return a number computed using event title, date, time and location.
    raw_eventID = title
    raw_eventID.encode("utf-8")

    eventID = hashlib.md5(raw_eventID.encode())

    return eventID.hexdigest()


def returnRSVPList(user):
  result = firebase.get("/users/"+user, "rsvped events")
  print(result, file=sys.stderr)
  if result==None:
    return []
  else:
    return result

app.jinja_env.globals.update(generateEventID=generateEventID)
app.jinja_env.globals.update(returnRSVPList=returnRSVPList)

@app.route("/")
def indexWebsite():
    return render_template("index.html")


@app.route("/userHome/<username>")
def serveUserHomePage(username):
    # TODO: Auth first
    result = firebase.get("/users", username)
    if result == None:
        # User does not exist.
        # TODO: Maybe have 404.html to show here.
        return "User does not exist."
    allEvents = firebase.get("/events", None)
    return render_template("userMainPage.html", username=username, allEvents=allEvents)


@app.route("/userAction/RSVP/<username>/<event>", methods=['POST'])
def rsvpToEvent(username, event):
  result = firebase.get("/events", event)
  eventID = generateEventID(event)
  listOfRSVP = firebase.get("/users/"+username, "rsvped events")
  if listOfRSVP == None:
    listOfRSVP = []
  if eventID not in listOfRSVP:
    listOfRSVP.append(eventID)
  firebase.put("/users/"+username, "rsvped events", listOfRSVP)
  RSVP = int(result['rsvp'])
  RSVP = RSVP + 1
  firebase.put("/events/" + event, "rsvp", RSVP)
  return redirect(url_for('serveUserHomePage', username=username))

@app.route("/userAction/RSVPCancel/<username>/<event>", methods=['POST'])
def cancelRSVP(username, event):
  eventID = generateEventID(event)
  listOfRSVP = returnRSVPList(username)
  listOfRSVP.remove(eventID)
  firebase.put("/users/"+username, "rsvped events", listOfRSVP)
  result = firebase.get("/events", event)
  RSVP = int(result['rsvp'])
  RSVP = RSVP - 1
  firebase.put("/events/" + event, "rsvp", RSVP)
  return redirect(url_for('serveUserHomePage', username=username))

@app.route("/managerHome/createEvent/<username>")
def serveCreateEventPage(username):
    return render_template("createEvent.html", username=username)


@app.route("/managerAction/addEvent/<username>", methods=['POST'])
def addEvent(username):
    # So the idea is that we have to create a event node using title as key (or maybe some number generated like title_id)
    title = request.form["title"]

    location = request.form["location"]
    date = request.form["date"]
    time = request.form["time"]
    description = request.form["description"]

    result = firebase.put("/events", title, generateEventID(title))
    # Then we will add rest of the attributes as their child.
    event_attributes = "/events/" + title


    firebase.put(event_attributes, "manager", username)
    firebase.put(event_attributes, "location", location)
    firebase.put(event_attributes, "date", date)
    firebase.put(event_attributes, "time", time)
    firebase.put(event_attributes, "description", description)
    firebase.put(event_attributes, "rsvp", 0)
    # Confirmation html
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
	    push = firebase.put('/users/'+ username,"password",password.hexdigest())
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
      #Push username and password to the database.
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
    if result['password'] == password.hexdigest():
      #auth success
      return redirect(url_for('serveUserHomePage', username=username))
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

# TODO: Keep track of authentication so the user cannot access the manager profile by directly typing the url.
@app.route("/managerHome/<username>")
def serveManagerHome(username):
    # TODO: Auth first
    result = firebase.get("/managers", username)
    if result == None:
        # Manager does not exist.
        # TODO: Maybe have 404.html to show here.
        return "Manager does not exist."
    allEvents = firebase.get("/events", None)
    return render_template("managerMainPage.html", username=username, allEvents=allEvents)


@app.route("/test")
def getUsers():
    title = "dance"
    location = "PMU"

    result = firebase.put('/users', user, pwd)

    result = firebase.get('/users', None)
    return str(result)
