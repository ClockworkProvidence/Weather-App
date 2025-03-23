# Name: Steven Wang


import tkinter as tk
from tkinter import ttk
from tkinter import *

import geocoder

import requests
import json

pred_items = []
pred_items_verbose = []
latitude, longitude, address = None, None, None

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
    
def get_loc_data(country):
    lat = country['latitude']
    long = country['longitude']
    addr = f"{country['name']} {country['country_code']}"
    return lat, long, addr
    
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
                predictions_readable = [f"{guess['name']}, {guess['country']}" for guess in predictions]
            else:
                predictions_readable = []
            return predictions_readable, predictions
                
        else:
            return None, None
    
def update_pred(lst):
    # clear previous data 
    pred_lst.delete(0, 'end') 
   
    # put new data 
    for item in lst: 
        pred_lst.insert('end', item) 
        
def set_loc_text(text):
    location_entry.delete(0,END)
    location_entry.insert(0,text)
    pred_items.clear()
    pred_items_verbose.clear()
    update_pred(pred_items)
    return
        
def select_pred(event):
    global latitude, longitude, address
    
    if not event.widget.curselection():
        return
    ind = event.widget.curselection()[0]
    country = pred_items_verbose[ind]
    latitude, longitude, address = get_loc_data(country)
    print(latitude, longitude)
    set_loc_text(pred_items[ind])
    location_label.config(text=f"Finding Weather for: {address}")
    
def pred(event):
    if not event.widget.get():
        return
    if var1.get():
        return
    txt = event.widget.get()
    pred_items[:], pred_items_verbose[:] = get_pred(txt)
    update_pred(pred_items)


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

# Create a listbox widget
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
weather_button = tk.Button(root, text="See Weather")
weather_button.grid(row=3, columnspan=5)

# Create a label to display weather information
weather_label = tk.Label(root, text="")
weather_label.grid(row=4, columnspan=5)

root.eval('tk::PlaceWindow . center')

root.mainloop()