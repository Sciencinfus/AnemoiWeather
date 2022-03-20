from gzip import decompress
from json import loads
from flask import session
import re

from requests import get
from urllib.request import urlopen
import json

from flask_session import Session

def get_gzipped_json(url):
    return loads(decompress(get(url).content))

def get_filtered_cities(cities, q):
    filtered = []
    max_to_return = 10
    number_found = 0
    for city in cities:
        if city["name"].startswith(q):
            value = city["name"]
            if city["state"]:
                value += "-" + city["state"]
            value += "-" + city["country"]
            value += " (" + str(city["id"]) + ")"
            filtered.append(value)
            number_found += 1
            if number_found == max_to_return:
                return filtered
    return filtered

def get_city_id(j):
    m = re.search('\((.+)\)',j)
    if m:
        return m.group(1)
    return ""

def get_city(id, cities):
    for city in cities:
        if str(city["id"]) == id:
            return city
    return {}

def get_current_weather(city, OPENWEATHER_API_KEY):

    # Extract lat and lon from city
    lat = str(city["coord"]["lat"])
    lon = str(city["coord"]["lon"])

    # Prepare URL
    url = "https://api.openweathermap.org/data/2.5/weather?lat=" + lat + "&lon=" + lon + "&appid=" + OPENWEATHER_API_KEY

    # Get response from URL
    response = urlopen(url)

    # Return in JSON format
    return json.loads(response.read())

def prepare_display(weather,id):
    display_weather = {}
    display_weather["id"] = id
    display_weather["city_name"] = weather["name"]
    display_weather["current_temperature"] = celsius(weather["main"]["temp"])
    display_weather["icon"] = "https://openweathermap.org/img/wn/" + weather["weather"][0]["icon"] + "@2x.png"
    return display_weather

def celsius(kelvin):
    return f"{kelvin-273.15:.1f}"

def remenber_id(id):
    if session.get("ids") is None:
        ids = []
    else:
        ids = session["ids"]

    if not id in ids:
        ids.append(id)
        session["ids"] = ids

def forget_id(to_forget):
    ids = []

    print(session["ids"])
    print(to_forget)
    for id in session["ids"]:
        print(id)
        if id != to_forget:
            ids.append(id)

    print(ids)
    session["ids"] = ids

def recover_weathers(cities, key):
    weathers = []

    for id in session["ids"]:
        """ Get City data """
        city = get_city(id, cities)

        """ Get City Weather """
        weather_json = get_current_weather(city, key)

        """ Prepare Display """
        weather = prepare_display(weather_json, id)

        """ Add weahther city to weathers """
        weathers.append(weather)

    """ return to caller """
    return weathers
