# Name: Steven Wang
# Disclaimer, the API can only be used 10,000 times each day

import tkinter as tk
from tkinter import ttk
from tkinter import *

import geocoder

import requests
import json

import openmeteo_requests
from openmeteo_sdk.Variable import Variable

import numpy as np

# Global Variables
openmeteo = openmeteo_requests.Client()
pred_items = []
pred_items_verbose = []
latitude, longitude= None, None

# Get Current User Location (Warning, using ip, may narrow only to city)
# Returns latitude, longitude, address
def get_curr_loc():
    curr_loc = geocoder.ip("me")
    if curr_loc.latlng:
        lat, long = curr_loc.latlng
        addr = curr_loc.address
        return lat, long, addr
    else:
        return None, None, None

# Get the latitude, longitude and address from country json data
# Returns latitude, longitude and address
def get_loc_data(country):
    lat = country['latitude']
    long = country['longitude']
    addr = f"{country['name']} {country.get('country_code', '')}"
    return lat, long, addr

# get the top 5 predicted locations from text in text field
# using open-meteo geocoding api
# returns readable country names, and their json data counter parts
def get_pred(text):
    if len(text) <= 1: 
        return [], []
    else:
        url = f"https://geocoding-api.open-meteo.com/v1/search?name={text}&count=5&language=en&format=json"
        response = requests.get(url)
        
        # Check if the response is successful
        if response.status_code == 200:
            data = response.json()
            predictions = data.get("results", [])
            if predictions != []:
                predictions_readable = [f"{guess['name']}, {guess.get('country', '')}" for guess in predictions]
            else:
                predictions_readable = []
            return predictions_readable, predictions
                
        else:
            return None, None

# Update the listbox we use for prediction displays
def update_pred(lst):
    # clear previous data 
    pred_lst.delete(0, 'end') 
   
    # put new data 
    for item in lst: 
        pred_lst.insert('end', item) 

# Set the entry box text to the selected name in the listbox
def set_loc_text(text):
    location_entry.delete(0,END)
    location_entry.insert(0,text)
    pred_items.clear()
    pred_items_verbose.clear()
    update_pred(pred_items)
    return
        
# Event handler for when a name in the list box is selected
def select_pred(event):
    global latitude, longitude
    
    if not event.widget.curselection():
        return
    ind = event.widget.curselection()[0]
    country = pred_items_verbose[ind]
    latitude, longitude, address = get_loc_data(country)
    print(latitude, longitude)
    set_loc_text(pred_items[ind])
    location_label.config(text=f"Finding Weather for: {address}")

# Event handler for search mode, calls geocoding API
def pred(event):
    if not event.widget.get() or var1.get():
        return
    txt = event.widget.get()
    pred_items[:], pred_items_verbose[:] = get_pred(txt)
    update_pred(pred_items)

# Event handler for coordinate mode, parses input for coordinate
def coord_parse(event):
    if not event.widget.get() or not var1.get():
        return
    txt = event.widget.get()
    try:
        location_label.config(text=f"Finding Weather for: {txt}")
        global latitude, longitude
        str_lat, str_long = txt.split(", ")
        latitude, longitude = (float(str_lat), float(str_long))
        print(latitude, longitude)
    except:
        location_label.config(text="Invalid Coordinate!")
        
def get_weather():
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min", "precipitation_probability_max"],
        "current": ["temperature_2m", "precipitation_probability", "weather_code", "apparent_temperature", "relative_humidity_2m"],
        "timezone": "auto",
        "forecast_days": 5
    }
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]
    
    current = response.Current()
    
    curr_temp = round(current.Variables(0).Value(), 2)

    curr_prec_prob = int(current.Variables(1).Value())

    curr_weather_code = int(current.Variables(2).Value())

    curr_apparent_temp = round(current.Variables(3).Value(), 2)
    
    curr_relative_humidity = int(current.Variables(4).Value())
    
    label, symbol = weather_code_translate(curr_weather_code)
    
    weather_label.config(text=label)
    weather_symbol.config(text=symbol)
    
    temperature.config(text=f"Temperature: {curr_temp}°C")
    
    ap_temperature.config(text=f"Apparent Temperature: {curr_apparent_temp}°C")
    
    rain_chance.config(text=f"Chance of Rain: {curr_prec_prob}%")
    
    humidity.config(text=f"Humidity: {curr_relative_humidity}%")

    pass

def weather_code_translate(code):
    match code:
        case 0:
            return "Clear sky", "☀️"
        case 1:
            return "Mainly clear", "🌤️"
        case 2:
            return "partly cloudy", "🌥️"
        case 3:
            return "Overcast", "☁️"
        case 45:
            return "fog", "🌫️"
        case 48:
            return "Depositing rime fog", "🌫️"
        case 51:
            return "Light drizzle", "🌧️"
        case 53:
            return "Moderate drizzle", "🌧️"
        case 55:
            return "Dense drizzle", "🌧️"
        case 56:
            return "Light freezing drizzle", "🌨️"
        case 57:
            return "Dense freezing drizzle", "🌨️"
        case 61:
            return "Slight rain", "🌦️"
        case 63:
            return "Moderate rain", "🌧️"
        case 65:
            return "Heavy rain", "🌧️"
        case 66:
            return "Light freezing rain", "🌨️"
        case 67:
            return "Heavy freezing rain", "🌨️"
        case 71:
            return "Slight snow", "❄️"
        case 73:
            return "Moderate snow", "❄️"
        case 75:
            return "Heavy snow", "❄️"
        case 77:
            return "Snow grains", "❄️"
        case 80:
            return "Slight rain showers", "🌦️"
        case 81:
            return "Moderate rain showers", "🌧️"
        case 82:
            return "Violent rain showers", "🌧️"
        case 85:
            return "Light snow showers", "❄️"
        case 86:
            return "Heavy snow showers", "❄️"
        case 95:
            return "Slight/Moderate thunderstorm", "🌩️"
        case 96:
            return "Thunderstorm with slight hail", "⛈️"
        case 99:
            return "Thunderstorm with heavy hail", "⛈️"
        case _:
            return "unknown", "🤷‍♂️"


# Find current coordinate and Location
latitude, longitude, address = get_curr_loc()

# Create the main window
root = tk.Tk()
root.title("Weather App")

# Create label and entry field
location_label = tk.Label(root, text="Location:")
location_label.grid(row=0, column=0)
location_entry = tk.Entry(root, width=35)
location_entry.grid(row=0, column=1, columnspan=3)
location_entry.bind('<KeyRelease>', pred) 
location_entry.bind('<Return>', coord_parse)

# Create a listbox widget to house predicted names
pred_lst = Listbox(root, width=35, height=5, selectmode="single")
pred_lst.grid(row=1, column=1, columnspan=3)
pred_lst.bind("<<ListboxSelect>>", select_pred)

# Toggle Coordinate (Geolocating API does not work with coordinates, parse directly)
var1 = IntVar()
Checkbutton(root, text='Coordinate', variable=var1).grid(row=0, column=4)

# Create a label to display Location information
location_label = tk.Label(root, text="", width=50)
location_label.grid(row=2, columnspan=5)

if address == None:
    location_label.config(text="Could not find Current Location")
else:
    location_label.config(text=f"Finding Weather for: {address}")
    
# Create a button to find weather data (Default to current Location)
weather_button = tk.Button(root, text="See Weather", command=get_weather)
weather_button.grid(row=3, columnspan=5)

separator_1 = ttk.Separator(root, orient='horizontal')
separator_1.grid(row=4, columnspan=5, sticky="ew")

# Create labels to display weather information
weather_label = tk.Label(root, text="")
weather_label.grid(row=5, columnspan=5)

weather_symbol = tk.Label(root, text="", font=("Segoe UI Emoji", 50))
weather_symbol.grid(row=6, columnspan=5)

temperature = tk.Label(root, text="")
temperature.grid(row=9, column=0, columnspan=2)

ap_temperature = tk.Label(root, text="")
ap_temperature.grid(row=9, column=3, columnspan=2)

rain_chance = tk.Label(root, text="")
rain_chance.grid(row=10, column=0, columnspan=2)

humidity = tk.Label(root, text="")
humidity.grid(row=10, column=3, columnspan=2)

root.eval('tk::PlaceWindow . center')

root.mainloop()