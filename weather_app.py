# Name: Steven Wang

import requests
import tkinter as tk
from tkinter import messagebox

import geocoder

# Get Current User Location (Warning, using ip, may narrow only to city)
def get_curr_loc():
    curr_loc = geocoder.ip("me")
    if curr_loc.latlng:
        latitude, longitude = curr_loc.latlng
        address = curr_loc.address
        return latitude, longitude, address
    else:
        return None

# Create the main window
root = tk.Tk()
root.title("Weather App")

root.eval('tk::PlaceWindow . center')

# Create label and entry field
location_label = tk.Label(root, text="Location:")
location_label.grid(row=0)
location_entry = tk.Entry(root)
location_entry.grid(row=0, column=1)

curr_loc = get_curr_loc()
if curr_loc != None:
    latitude, longitude, address = curr_loc
else:
    latitude, longitude, address = None

# Create a label to display Location information
Location_label = tk.Label(root, text=f"Finding Weather for: {address}")
Location_label.grid(row=2, columnspan=2)

# Create a label to display weather information
weather_label = tk.Label(root, text="")
weather_label.grid(row=3, columnspan=2)

# Create a button to find weather data (Default to current Location)
weather_button = tk.Button(root, text="See Weather")
weather_button.grid(row=1, columnspan=2)

root.mainloop()