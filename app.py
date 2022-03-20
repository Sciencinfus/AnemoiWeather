from flask import Flask, render_template, request, redirect, session
from helpers import get_gzipped_json, get_filtered_cities, get_id, get_city
from helpers import get_current_weather, prepare_display, recover_weathers, remenber_id
from flask_session import Session

# Configure application
app = Flask(__name__)

# Configure session
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Define Openweather API Key
OPENWEATHER_API_KEY = "2a4682ad87a21f03c7bb1592ebe6b99d"

# Define Openweather list of Cities URI
OPENWEATHER_CITY = "https://bulk.openweathermap.org/sample/city.list.json.gz"

# Get Openweather cities list
cities = get_gzipped_json(OPENWEATHER_CITY)

@app.route("/")
def index():
    if session.get("id") is None:
        return render_template("index.html")
    else:
        """ Recover weathers """
        weathers = recover_weathers(session.get("id"), cities, OPENWEATHER_API_KEY)

        """ Return to main page """
        return render_template("index.html",weathers=weathers)

@app.route("/addcity", methods=["GET", "POST"])
def addcity():
    """Add a city in the list"""
    # POST
    if request.method == "POST":

        """ Recover id from Posted data """
        id = get_id(request.form.get("city"))

        """ Store City id """
        remenber_id(id)
        print (session["id"])

        """ Recover weathers """
        weathers = recover_weathers(id, cities, OPENWEATHER_API_KEY)

        """ Return to main page """
        return render_template("index.html",weathers=weathers)

    # GET
    return render_template("addcity.html")

@app.route("/search")
def search():
    q = request.args.get("q")
    if q:
        choices = get_filtered_cities(cities, q)
    else:
        choices = []
    return render_template("search.html", choices=choices)
