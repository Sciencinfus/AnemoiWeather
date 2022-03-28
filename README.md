# Introduction

This project is the final assignment done in the frame of the 2022 CS50's Introduction to Computer Science.

My software enables users to display general and detailed weather data related to a set of cities.

I have made the project alone without the help of others classmates.

# Technologies used
Flask, Python, HTML, CSS, JavaScript, JSON

The weather data comes from https://openweathermap.org/. The free of charge subscription enables access to
- World coverage with more than 200.000 cities
- Update every 10 minutes
- 60 calls/minute and 1,000,000 calls/month which is more than enough for my project size

# Functionalities
The following functionalities are implemented:
- Index page that displays the set of selected cities with the main data weathers
- Detail page that displays more detailed weather data about a city with the next 24h forecast
- Addition of a new city
- Deletion of an existing city
- Unit used for display temperatures (Celsius/Fahrenheit)

# Technical Architecture

The following files are used by the software:
- main folder:
  - app.py
  - helpers.py
  - requirement.txt  
- folder static
  - facicon.ico:
  - styles.css
- templates
  - addcity.html
  - delcity.html
  - details.html
  - index.html
  - layout.html
  - search.html

## Main folder

**app.py** contains all routes in the application:
- "/" main page
- "/details"  detail page
- "/switch"   switch between Celsius/Fahrenheit
- "/addcity"  add a city
- "/delcity"  remove a city

**helpers.py** contains all function used in the application

- get_gzipped_json:  This function returns the json response of an URL
- get_filtered_cities: This function returns a filtered list of cities starting with the q input parameter
- get_city_id: This function extracts city ID from the string displayed to the user
- get_city: This function returns the city that match the city ID
- def get_current_weather: This function returns the weather of a city
- get_countries: This function returns an array of all country codes in cities
- prepare_display: This function extracts from the weather data all fields that will be displayed
- utc_to_local: This function converts UTC time to local time
- speed: This function converts wind speed from meter/second to km/h
- wind_direction: This function converts wind direction from degree to plain text
- temp: This function converts from kelvin to temp
- remenber_id: This function stores a city ID in the session data
- forget_id: This function removes a city ID from the session data
- recover_weathers: This function retrieves the weather of all city ID stored in the session data

## templates folder
- addcity.html:   defines the page used to add a city
- delcity.html:   defines the page used to remove a city
- details.html:   defines the page used to display weather details about a city
- index.html:     defines the main page
- layout.html:    defines all HTML code common to all pages
- search.html:    defines the dynamic options used in search.html
