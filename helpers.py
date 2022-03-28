from gzip import decompress
from json import loads
from flask import session, request
from datetime import datetime, timezone
from requests import get
from urllib.request import urlopen
from flask_session import Session

import time
import pycountry
import re
import json

# This function returns the json response of an URL


def get_gzipped_json(url):
    return loads(decompress(get(url).content))


# This function returns a filterd list of cities starting with the q input parameter
def get_filtered_cities(cities, q, c):
    # Initializations
    filtered = []           # the filtered list
    max_to_return = 20      # max numnber of entries to return

    # Iterated on all cities
    for city in cities:
        if city["name"].lower().startswith(q.lower()):
            if c == "" or c == city["country"]:
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


# This function extracts city ID from the string displayed to the user
def get_city_id(j):
    m = re.search('\((.+)\)', j)
    if m:
        return m.group(1)
    # If no match then return "Not found"
    return "Not found"


# This function returns the city that match the city ID
def get_city(id, cities):
    for city in cities:
        if str(city["id"]) == id:
            return city
    return {}


# This function returns the weather of a city
def get_current_weather(city, OPENWEATHER_API_KEY):

    # Extract lat and lon from city
    lat = str(city["coord"]["lat"])
    lon = str(city["coord"]["lon"])

    # Search prefered language
    # supported_languages = ["en", "nl", "it", "fr"]
    # lang = request.accept_languages.best_match(supported_languages)

    # Prepare URL
    # url = "https://api.openweathermap.org/data/2.5/weather?lat=" + lat + \
    #    "&lon=" + lon + "&appid=" + OPENWEATHER_API_KEY + "&lang=" + lang

    exclude = "minutely,alerts"
    url = "https://api.openweathermap.org/data/2.5/onecall?lat=" + lat + \
        "&lon=" + lon + "&exclude=" + exclude + "&appid=" + \
        OPENWEATHER_API_KEY
        #+ "&lang=" + lang

    # Check if data is locally cached
    if session.get(url):
        stored = session.get(url)

        # If data is fresher than 1000 seconds then use the cached data
        if time.time() - stored["current"]["dt"] < 1000:
            return session.get(url)

    # If not cached or too old then recover the data from OpenWeather

    # Get response from URL
    response = urlopen(url)

    # Convert to JSON format
    json_reponse = json.loads(response.read())

    # Store response for next time
    session[url] = json_reponse

    # Return json
    return json_reponse


# This function returns an array of all country codes in cities
def get_countries():
    return list(pycountry.countries)


# This function extracts from the weather data all fields that will be displayed
def prepare_display(weather, id, city):
    display_weather = {}
    display_weather["id"] = id
    display_weather["city_name"] = city["name"]
    display_weather["current_temp"] = temp(weather["current"]["temp"])
    display_weather["icon"] = "https://openweathermap.org/img/wn/" + weather["current"]["weather"][0]["icon"] + "@2x.png"
    display_weather["weather_description"] = weather["current"]["weather"][0]["description"]
    display_weather["feels_like"] = temp(weather["current"]["feels_like"])
    display_weather["wind_speed"] = speed(weather["current"]["wind_speed"])
    timezone = weather["timezone_offset"]
    display_weather["wind_direction"] = wind_direction(weather["current"]["wind_deg"])
    display_weather["sunrise"] = datetime.utcfromtimestamp(weather["current"]["sunrise"] + timezone).strftime('%H:%M')
    display_weather["sunset"] = datetime.utcfromtimestamp(weather["current"]["sunset"] + timezone).strftime('%H:%M')
    tmp = []
    # Store the hourly weather for next 24h (every 3 hours)
    for i in range(1, 25, 3):
        h = weather["hourly"][i]
        hourly_data = {}
        hourly_data["time"] = datetime.utcfromtimestamp(h["dt"] + timezone).strftime('%H:%M')
        hourly_data["temp"] = temp(h["temp"])
        hourly_data["icon"] = "https://openweathermap.org/img/wn/" + h["weather"][0]["icon"] + "@2x.png"
        tmp.append(hourly_data)
    display_weather["hourly"] = tmp
    return display_weather


# This function converts UTC time to local time
def utc_to_local(utc_dt, timezone):
    return utc_dt - timezone


# This function converts wind speed for meter/second to km/h
def speed(ms):
    return f"{ms * 3600 / 1000:.1f}"


# This function converts wind direction from degree to plain text
def wind_direction(deg):
    index = round(deg / 45)
    text = ["N", "NE", "E", "SE", "S", "SW", "W", "NW", "N"]
    return text[index]


# This function converts from kelvin to temp
def temp(kelvin):
    if session.get("unit") == "C":
        return f"{kelvin-273.15:.1f}"
    else:
        return f"{((kelvin-273.15)*1.8)+32:.1f}"


# This function stores a city ID in the session data
def remenber_id(id):
    if session.get("ids") is None:
        ids = []
    else:
        ids = session["ids"]

    if not id in ids:
        ids.append(id)
        session["ids"] = ids


# This function removes a city ID from the session data
def forget_id(to_forget):
    ids = []

    for id in session["ids"]:
        if id != to_forget:
            ids.append(id)

    session["ids"] = ids


# This function retrieves the weather of all city ID stored in the session data
def recover_weathers(cities, key):
    weathers = []

    for id in session["ids"]:
        """ Get City data """
        city = get_city(id, cities)

        """ Get City Weather """
        weather_json = get_current_weather(city, key)

        """ Prepare Display """
        weather = prepare_display(weather_json, id, city)

        """ Add weahther city to weathers """
        weathers.append(weather)

    """ return to caller """
    return sorted(weathers, key=lambda d: d["city_name"])
