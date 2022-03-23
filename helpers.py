from gzip import decompress
from json import loads
from flask import session, request
from datetime import datetime, timezone
import time


import re

from requests import get
from urllib.request import urlopen
import json

from flask_session import Session

""" get_gzipped_json returns the json respone of an URL """
def get_gzipped_json(url):
    return loads(decompress(get(url).content))

""" get_filtered_cities return a filterd list of cities starting with the q input parameter """
def get_filtered_cities(cities, q):
    # Initializations
    filtered = []           # the filtered list
    max_to_return = 20      # max numnber of entries to return

    # Iterated on all cities
    for city in cities:
        if city["name"].lower().startswith(q.lower()):
            value = city["name"]
            value += "-" + city["country"]

            # Filter the double entries in list of cities
            already_added = False
            for f in filtered:
                if f.startswith(value):
                    already_added = True

            # If not already found add it
            if not already_added:
                if city["state"]:
                    value += "-" + city["state"]
                value += " (" + str(city["id"]) + ")"
                filtered.append(value)

            # If maximum reached return to caller
            if len(filtered) == max_to_return:
                return filtered
    return filtered

""" get_city_id extracts city ID from the string displayed to the user """
def get_city_id(j):
    m = re.search('\((.+)\)',j)
    if m:
        return m.group(1)
    # If no match then return "Not found"
    return "Not found"

""" get_city returns the city that match the city ID """
def get_city(id, cities):
    for city in cities:
        if str(city["id"]) == id:
            return city
    return {}

""" get_current_weather returns the weather of a city """
def get_current_weather(city, OPENWEATHER_API_KEY):

    # Extract lat and lon from city
    lat = str(city["coord"]["lat"])
    lon = str(city["coord"]["lon"])

    # Search prefered language
    supported_languages = ["en", "nl", "it", "fr"]
    lang = request.accept_languages.best_match(supported_languages)

    # Prepare URL
    url = "https://api.openweathermap.org/data/2.5/weather?lat=" + lat + "&lon=" + lon + "&appid=" + OPENWEATHER_API_KEY + "&lang=" + lang

    # Check if data is locally cached
    if session.get(url):
        stored = session.get(url)

        # If data is fresher than 1000 seconds then use the cached data
        if time.time() - stored["dt"] < 1000:
            return session.get(url)

    # If not cached or too old then recover the data from OpenWeather
    
    # Get response from URL
    response = urlopen(url)

    # Return in JSON format
    json_reponse = json.loads(response.read())

    # Store response for next time
    session[url] = json_reponse

    # Return json
    return json_reponse



""" prepare_display extracts from the weather data all fields that will be displayed """
def prepare_display(weather,id):
    display_weather = {}
    display_weather["id"] = id
    display_weather["city_name"] = weather["name"]
    display_weather["current_temperature"] = celsius(weather["main"]["temp"])
    display_weather["icon"] = "https://openweathermap.org/img/wn/" + weather["weather"][0]["icon"] + "@2x.png"
    display_weather["weather_description"] = weather["weather"][0]["description"]
    display_weather["feels_like"] = celsius(weather["main"]["feels_like"])
    display_weather["wind_speed"] = str(weather["wind"]["speed"] * 3600 / 1000)
    timezone = weather["timezone"]
    display_weather["sunrise"] = datetime.utcfromtimestamp(weather["sys"]["sunrise"]+timezone).strftime('%H:%M')
    display_weather["sunset"] = datetime.utcfromtimestamp(weather["sys"]["sunset"]+timezone).strftime('%H:%M')
    return display_weather

""" Convert UTC time to local time """
def utc_to_local(utc_dt, timezone):
    return utc_dt - timezone

""" celsius convert from kelvin to celsius """
def celsius(kelvin):
    return f"{kelvin-273.15:.1f}"

""" remenber_id store a city ID in the session data """
def remenber_id(id):
    if session.get("ids") is None:
        ids = []
    else:
        ids = session["ids"]

    if not id in ids:
        ids.append(id)
        session["ids"] = ids

""" forget_id remove a city ID from the session data """
def forget_id(to_forget):
    ids = []

    for id in session["ids"]:
        if id != to_forget:
            ids.append(id)

    session["ids"] = ids

""" recover_weathers retrieve the weather of all city ID stored in the session data """
def recover_weathers(cities, key):
    weathers = []

    for id in session["ids"]:
        """ Get City data """
        city = get_city(id, cities)

        """ Get City Weather """
        weather_json = get_current_weather(city, key)
        print(weather_json)

        """ Prepare Display """
        weather = prepare_display(weather_json, id)

        """ Add weahther city to weathers """
        weathers.append(weather)

    """ return to caller """
    #newlist = sorted(list_to_be_sorted, key=lambda d: d['name'])
    return sorted(weathers, key=lambda d: d["city_name"])
