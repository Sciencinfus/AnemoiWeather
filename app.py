from flask import Flask, render_template, request, redirect
from helpers import get_gzipped_json, get_filtered_cities, get_id, get_city, get_current_weather, prepare_display

# Configure application
app = Flask(__name__)

# Define Openweather API Key
OPENWEATHER_API_KEY = "2a4682ad87a21f03c7bb1592ebe6b99d"

# Define Openweather list of Cities URI
OPENWEATHER_CITY = "https://bulk.openweathermap.org/sample/city.list.json.gz"

# Get Openweather cities list
cities = get_gzipped_json(OPENWEATHER_CITY)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/addcity", methods=["GET", "POST"])
def addcity():
    """Add a city in the list"""
    # POST
    if request.method == "POST":

        """ Recover id from Posted data """
        id = get_id(request.form.get("city"))

        """ Get City data """
        city = get_city(id, cities)

        """ Get City Weather """
        weather_json = get_current_weather(city, OPENWEATHER_API_KEY)

        """ Prepare Display """
        weather = prepare_display(weather_json)
        print(weather)

        """ Return to main page """
        return render_template("index.html",weather=weather)

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
