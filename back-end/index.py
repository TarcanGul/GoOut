from flask import Flask
from flask import render_template
app = Flask(__name__)

@app.route("/")
def indexWebsite()
{
	return render_template("../front-end/index.html")
}
