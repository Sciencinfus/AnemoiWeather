from flask import Flask, render_template, request, redirect, session
from helpers import get_gzipped_json, get_filtered_cities, get_city_id, get_city
from helpers import get_current_weather, prepare_display, recover_weathers, remenber_id
from helpers import forget_id
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

    if session.get("ids") is None:
        return render_template("index.html")
    else:
        """ Recover weathers """
        weathers = recover_weathers(cities, OPENWEATHER_API_KEY)
        print(weathers)

        """ Return to main page """
        return render_template("index.html",weathers=weathers)


@app.route("/addcity", methods=["GET", "POST"])
def addcity():
    """Add a city in the list"""
    # POST
    if request.method == "POST":

        """ Recover id from Posted data """
        city_id = get_city_id(request.form.get("city"))

        """ Store City id """
        remenber_id(city_id)

        """ Recover weathers """
        weathers = recover_weathers(cities, OPENWEATHER_API_KEY)

        """ Return to main page """
        return render_template("index.html",weathers=weathers)

    # GET
    return render_template("addcity.html")

@app.route("/delcity", methods=["GET", "POST"])
def delcity():
    print("entering del")
    if request.method == "POST":

        """ Recover id from Posted data """
        id = request.form.get("delete")
        print(id)

        """ Remove City id """
        forget_id(id)

        """ Recover weathers """
        weathers = recover_weathers(cities, OPENWEATHER_API_KEY)

        """ Return to main page """
        return render_template("index.html",weathers=weathers)

@app.route("/search")
def search():
    q = request.args.get("q")
    if q:
        choices = get_filtered_cities(cities, q)
    else:
        choices = []
    return render_template("search.html", choices=choices)
