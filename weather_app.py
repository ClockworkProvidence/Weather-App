# Name: Steven Wang
# Disclaimer, the API can only be used 10,000 times each day

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox 
from tkinter.ttk import *
from tkinter import *

import tkcalendar
from datetime import datetime
from datetime import timedelta

import geocoder

import requests
import json

import openmeteo_requests
from openmeteo_sdk.Variable import Variable

import sqlite3

import csv

# Global Variables
openmeteo = openmeteo_requests.Client()

pred_items = []
pred_items_verbose = []

latitude, longitude= None, None

labels = []
symbols = []
temps = []
r_probs = []

Curr_win = None

# database attr
Curr_loc = None

Loc = None
Date = None
Dates = []
Code = None
Temp = None
Ap_temp = None
R_prob = None
Humid = None

connection = sqlite3.connect('weather_database.db')

cursor = connection.cursor()

create_table_query = '''
                        CREATE TABLE IF NOT EXISTS Weather (
                            location TEXT NOT NULL,
                            date TEXT NOT NULL,
                            weather_code INTEGER NOT NULL,
                            temperature REAL,
                            apparent_temperature REAL,
                            rain_prob INTEGER,
                            humidity INTEGER,
                            PRIMARY KEY (location, date)
                        );
                     '''

# Execute the SQL command
cursor.execute(create_table_query)

# Commit the changes
connection.commit()

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
    
def add_comma_if_exist(text):
    if text != '':
        text += ", "
    return text

# Get the latitude, longitude and address from country json data
# Returns latitude, longitude and address
def get_loc_data(country):
    lat = country['latitude']
    long = country['longitude']
    ad1 = country.get('admin1', '')
    if ad1 != '':
        ad1 += ' '
    addr = f"{country['name']} {ad1}{country.get('country_code', '')}"
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
                predictions_readable = [f"{guess['name']}, {add_comma_if_exist(guess.get('admin1', ''))}{guess.get('country', '')}" for guess in predictions]
            else:
                predictions_readable = []
            return predictions_readable, predictions
                
        else:
            return None, None

# Update the listbox we use for prediction displays
def update_pred(lst, preds):
    # clear previous data 
    preds.delete(0, 'end') 
   
    # put new data 
    for item in lst: 
        preds.insert('end', item) 

# Set the entry box text to the selected name in the listbox
def set_loc_text(text, entry, lst):
    entry.delete(0,END)
    entry.insert(0,text)
    pred_items.clear()
    pred_items_verbose.clear()
    update_pred(pred_items, lst)
    return
        
# Event handler for when a name in the list box is selected
def select_pred(event):
    global latitude, longitude, Curr_loc
    
    if not event.widget.curselection():
        return
    ind = event.widget.curselection()[0]
    country = pred_items_verbose[ind]
    latitude, longitude, address = get_loc_data(country)
    print(latitude, longitude)
    Curr_loc = address
    set_loc_text(pred_items[ind], location_entry, pred_lst)
    location_label.config(text=f"Finding Weather for: {address}")

# Event handler for search mode, calls geocoding API
def pred(event):
    if not event.widget.get() or var1.get():
        return
    txt = event.widget.get()
    pred_items[:], pred_items_verbose[:] = get_pred(txt)
    update_pred(pred_items, pred_lst)

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
        
def display_forcast(daily):
    
    weather_codes = daily.Variables(0)
    temps_max = daily.Variables(1)
    temps_min = daily.Variables(2)
    perc_probs = daily.Variables(3)
    
    for k in range(1, 6):
        i = k-1
        weather_code = int(weather_codes.Values(k))
        label, symbol = weather_code_translate(weather_code)
        labels[i].config(text=label)
        symbols[i].config(text=symbol)
        
        temp = f"{round(temps_max.Values(k), 1)} / {round(temps_min.Values(k), 1)}°C"
        temps[i].config(text=temp)
        
        perc_prob = f"precip: {int(perc_probs.Values(k))}%"
        r_probs[i].config(text=perc_prob)
        
def get_weather():
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min", "precipitation_probability_max"],
        "current": ["temperature_2m", "precipitation_probability", "weather_code", "apparent_temperature", "relative_humidity_2m"],
        "timezone": "auto",
        "forecast_days": 6
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
        
    daily = response.Daily()
    
    display_forcast(daily)
    
    create_in_db_curr(datetime.today().strftime('%Y-%m-%d'), curr_weather_code, curr_temp, \
                      curr_apparent_temp, curr_prec_prob, curr_relative_humidity)

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
        
def info_msg():
    messagebox.showinfo("Info", "The Product Manager Accelerator Program is designed to support PM professionals " + \
                                "through every stage of their careers. From students looking for entry-level jobs to Directors " + \
                                "looking to take on a leadership role, our program has helped over hundreds of students fulfill " + \
                                "their career aspirations." + \
                                "\n\n" + \
                                "Our Product Manager Accelerator community are ambitious and committed. Through our program " + \
                                "they have learnt, honed and developed new PM and leadership skills, giving them a strong " + \
                                "foundation for their future endeavors.")
    
def create_in_db_curr(date, code, temp, ap_temp, r_prob, humid):
    global Curr_loc
    
    insert_query = '''
                   INSERT OR IGNORE INTO Weather (location,
                   date, weather_code, temperature, 
                   apparent_temperature, rain_prob, humidity) 
                   VALUES (?, ?, ?, ?, ?, ?, ?);
                   '''
                   
    weather_data = (Curr_loc, str(date), code, temp, ap_temp, r_prob, humid)
    cursor.execute(insert_query, weather_data)
    connection.commit()
    
    

# ---------------------------- for CRUD --------------------------------------

# Event handler for when a name in the list box is selected
def crud_select_pred(event, crud_loc, crud_p_lst, alert):
    global Loc
    
    if not event.widget.curselection():
        return
    ind = event.widget.curselection()[0]
    country = pred_items_verbose[ind]
    _, _, address = get_loc_data(country)
    Loc = address
    set_loc_text(pred_items[ind], crud_loc, crud_p_lst)
    alert.config(text=f"Entered Location: {address}")

# Event handler for search mode, calls geocoding API
def crud_pred(event, crud_p_lst):
    if not event.widget.get() or var1.get():
        return
    txt = event.widget.get()
    pred_items[:], pred_items_verbose[:] = get_pred(txt)
    update_pred(pred_items, crud_p_lst)
    
def date_range(start, stop, alert):
    global Dates # Should default to []
    
    Dates = []
    diff = (stop-start).days
    for i in range(diff+1):
        day = start + timedelta(days=i)
        Dates.append(day)
    if Dates:
        alert.config(text=f"Entering {len(Dates)}days of Data")
    else:
        alert.config(text="Check if end date is later than start date")
        
def date_entry_handling(event, alert):
    global Date
    date = event.widget.get_date()
    Date = date
    alert.config(text=f"Entered: {date} for date")
        
def entry_handling(event, alert):
    global Code, Temp, Ap_temp, R_prob, Humid
    if not event.widget.get():
        return
    txt = event.widget.get()
    try:
        txt = float(txt)
    except ValueError:
        alert.config(text=f"Entered: {txt}, this is not valid, please enter a number")
        return
    
    name = event.widget.extra
    match name:
        case "Weather Code":
            txt = int(txt)
            if (txt < 0) or (txt > 99):
                alert.config(text=f"Weather code can only be between 0-99")
            else:
                Code = txt
                alert.config(text=f"Entered: {txt} for weather code")
        case "Temperature":
            Temp = txt
            alert.config(text=f"Entered: {txt} for temperature")
        case "Apparent Temperature":
            Ap_temp = txt
            alert.config(text=f"Entered: {txt} for apparent temperature")
        case "Rain_chance":
            txt = int(txt)
            R_prob = txt
            alert.config(text=f"Entered: {txt} for rain chance")
        case "Humidity":
            txt = int(txt)
            Humid = txt
            alert.config(text=f"Entered: {txt} for humidity")
        case _:
            pass
        
def create_in_db(alert):
    global Loc, Dates, Code, Temp, Ap_temp, R_prob, Humid
    
    if Loc and Dates and Code:
        
        insert_query = '''
                       INSERT OR IGNORE INTO Weather (location,
                       date, weather_code, temperature, 
                       apparent_temperature, rain_prob, humidity) 
                       VALUES (?, ?, ?, ?, ?, ?, ?);
                       '''
                       
        for date in Dates:
            weather_data = (Loc, str(date), Code, Temp, Ap_temp, R_prob, Humid)
            cursor.execute(insert_query, weather_data)
            connection.commit()
        
        Dates = []
        Loc, Code, Temp, Ap_temp, R_prob, Humid = None, None, None, None, None, None
        
    else:
        alert.config(text=f"Data missing, at least enter location, dates and weather code")
        
def add_name_if_exist(data, name):
    data = str(data)
    if data:
        return f"{name}: {data} \n"
    else:
        return ''
        
def read_in_db(alert, r_msg):
    global Loc, Date
    
    if Loc and Date:
        
        read_query = "SELECT * FROM Weather WHERE location = ? AND date = ?;"
        weather_data = (Loc, str(Date))
        cursor.execute(read_query, weather_data)
        connection.commit()
        records = cursor.fetchall()
        if records != []:
            record = records[0]
            txt = f"{add_name_if_exist(record[0], 'Location')}\
                    {add_name_if_exist(record[1], 'Date')}\
                    {add_name_if_exist(record[2], 'Weather code')}\
                    {add_name_if_exist(record[3], 'Temperature')}\
                    {add_name_if_exist(record[4], 'Apparent temperature')}\
                    {add_name_if_exist(record[5], 'Rain probability')}\
                    {add_name_if_exist(record[6], 'Humidity')}"
            r_msg.config(text=txt)
        else:
            alert.config(text="Could not find data")
        Loc = None
        Date = None
        
    else:
        alert.config(text="Data missing, at least enter location and date")
        
def update_in_db(alert):
    global Loc, Date, Code, Temp, Ap_temp, R_prob, Humid
    
    if Loc and Date and Code:
        
        read_query = "SELECT * FROM Weather WHERE location = ? AND date = ?;"
        weather_data = (Loc, str(Date))
        cursor.execute(read_query, weather_data)
        connection.commit()
        records = cursor.fetchall()
        if records != []:
            update_query = '''
                           UPDATE Weather
                           SET weather_code = ?, temperature = ?, 
                           apparent_temperature = ?, rain_prob = ?, humidity = ?
                           WHERE location = ? AND date = ?;
                           '''
                       
            weather_data = (Code, Temp, Ap_temp, R_prob, Humid, Loc, str(Date))
            cursor.execute(update_query, weather_data)
            connection.commit()
            
            alert.config(text=f"Data at {Loc}, {Date} has been Updated")
            
            Loc, Date, Code, Temp, Ap_temp, R_prob, Humid = None, None, None, None, None, None, None
        else:
            alert.config(text="Could not find data")
        
    else:
        alert.config(text=f"Data missing, at least enter location, dates and weather code")

def delete_in_db(alert):
    global Loc, Date
    
    if Loc and Date:
        read_query = "SELECT * FROM Weather WHERE location = ? AND date = ?;"
        weather_data = (Loc, str(Date))
        cursor.execute(read_query, weather_data)
        connection.commit()
        records = cursor.fetchall()
        if records != []:
            delete_query = "DELETE FROM Weather WHERE location = ? AND date = ?;"
            weather_data = (Loc, str(Date))
            cursor.execute(delete_query, weather_data)
            connection.commit()
            alert.config(text=f"Data at {Loc}, {Date} has been deleted")
            Loc = None
            Date = None
        else:
            alert.config(text="Could not find data")
        
        
    else:
        alert.config(text="Data missing, at least enter location and date")
    
def destroy_win():
    global Curr_win
    if Curr_win:
        Curr_win.destroy()
    Curr_win = None

def open_C_window():
    global Curr_win
    
    destroy_win()
     
    # Toplevel object which will 
    # be treated as a new window
    c_win = Toplevel(root)
    
    Curr_win = c_win
    
    c_win.geometry(f"+{root.winfo_x()}+{root.winfo_y()}")
 
    # sets the title of the
    # Toplevel widget
    c_win.title("Create Records")
 
    # A Label widget to show in toplevel
    record_label = Label(c_win, text ="Create Records")
    record_label.grid(row=0, columnspan=3)
    
    c_label_1 = tk.Label(c_win, text="Location:")
    c_label_1.grid(row=1, column=0)
    c_location = tk.Entry(c_win, width=35)
    c_location.grid(row=1, column=1, columnspan=3)
    
    c_p_lst = Listbox(c_win, width=35, height=5, selectmode="single")
    c_p_lst.grid(row=2, column=1, columnspan=3)
    
    c_location.bind('<KeyRelease>', lambda event: crud_pred(event, c_p_lst))
    c_p_lst.bind("<<ListboxSelect>>", lambda event: crud_select_pred(event, c_location, c_p_lst, c_alert))
    
    c_separator_1 = ttk.Separator(c_win, orient='horizontal')
    c_separator_1.grid(row=3, columnspan=4, sticky="ew")
    
    c_date1 = tkcalendar.DateEntry(c_win)
    c_date1.grid(row=4, column=0, columnspan=2)

    c_date2 = tkcalendar.DateEntry(c_win)
    c_date2.grid(row=4, column=2, columnspan=2)

    c_date_but = Button(c_win, text='Find range', command=lambda: date_range(c_date1.get_date(), c_date2.get_date(), c_alert))
    c_date_but.grid(row=5, columnspan=4)
    
    c_label_texts = ["Weather Code", "Temperature", "Apparent Temperature", "Rain_chance", "Humidity"]
    c_labels = []
    c_entries = []
    
    for i in range(5):
        txt = c_label_texts[i][:]
        c_label = tk.Label(c_win, text=txt + ':')
        c_label.grid(row=6 + i, column=0)
        c_labels.append(c_label)
        
        c_entry = tk.Entry(c_win, width=35)
        c_entry.bind('<Return>', lambda event: entry_handling(event, c_alert))
        c_entry.extra = txt
        c_entry.grid(row=6 + i, column=1, columnspan=3)
        c_entries.append(c_entries)
        
    c_alert = tk.Label(c_win, text="")
    c_alert.grid(row=11, columnspan=4)
    
    c_enter_but = Button(c_win, text='Enter Data', command=lambda: create_in_db(c_alert))
    c_enter_but.grid(row=12, columnspan=4)
    
    c_win.mainloop()
    
def open_R_window():
    
    global Curr_win
    
    destroy_win()
    # Toplevel object which will 
    # be treated as a new window
    r_win = Toplevel(root)
    
    Curr_win = r_win
    
    r_win.geometry(f"+{root.winfo_x()}+{root.winfo_y()}")
 
    # sets the title of the
    # Toplevel widget
    r_win.title("Read Records")
 
    # A Label widget to show in toplevel
    record_label = Label(r_win, text ="Read Records")
    record_label.grid(row=0, columnspan=3)
    
    r_label_1 = tk.Label(r_win, text="Location:")
    r_label_1.grid(row=1, column=0)
    r_location = tk.Entry(r_win, width=35)
    r_location.grid(row=1, column=1, columnspan=3)
    
    r_p_lst = Listbox(r_win, width=35, height=5, selectmode="single")
    r_p_lst.grid(row=2, column=1, columnspan=3)
    
    r_location.bind('<KeyRelease>', lambda event: crud_pred(event, r_p_lst))
    r_p_lst.bind("<<ListboxSelect>>", lambda event: crud_select_pred(event, r_location, r_p_lst, r_alert))
    
    r_separator_1 = ttk.Separator(r_win, orient='horizontal')
    r_separator_1.grid(row=3, columnspan=4, sticky="ew")
    
    r_date = tkcalendar.DateEntry(r_win)
    r_date.bind("<<DateEntrySelected>>", lambda event: date_entry_handling(event, r_alert))
    r_date.grid(row=5, columnspan=4)
    
    r_alert = tk.Label(r_win, text="")
    r_alert.grid(row=6, columnspan=4)
    
    r_enter_but = Button(r_win, text='Read Data', command=lambda: read_in_db(r_alert, r_message))
    r_enter_but.grid(row=7, columnspan=4)
    
    r_message = Message(r_win, text="", width=300)
    r_message.grid(row=8, columnspan=4,)
    
    r_win.mainloop()

def open_U_window():
    global Curr_win
    
    destroy_win()
     
    # Toplevel object which will 
    # be treated as a new window
    u_win = Toplevel(root)
    
    Curr_win = u_win
    
    u_win.geometry(f"+{root.winfo_x()}+{root.winfo_y()}")
 
    # sets the title of the
    # Toplevel widget
    u_win.title("Create Records")
 
    # A Label widget to show in toplevel
    record_label = Label(u_win, text ="Create Records")
    record_label.grid(row=0, columnspan=3)
    
    u_label_1 = tk.Label(u_win, text="Location:")
    u_label_1.grid(row=1, column=0)
    u_location = tk.Entry(u_win, width=35)
    u_location.grid(row=1, column=1, columnspan=3)
    
    u_p_lst = Listbox(u_win, width=35, height=5, selectmode="single")
    u_p_lst.grid(row=2, column=1, columnspan=3)
    
    u_location.bind('<KeyRelease>', lambda event: crud_pred(event, u_p_lst))
    u_p_lst.bind("<<ListboxSelect>>", lambda event: crud_select_pred(event, u_location, u_p_lst, u_alert))
    
    u_separator_1 = ttk.Separator(u_win, orient='horizontal')
    u_separator_1.grid(row=3, columnspan=4, sticky="ew")
    
    u_date = tkcalendar.DateEntry(u_win)
    u_date.bind("<<DateEntrySelected>>", lambda event: date_entry_handling(event, u_alert))
    u_date.grid(row=4, columnspan=4)
    
    u_label_texts = ["Weather Code", "Temperature", "Apparent Temperature", "Rain_chance", "Humidity"]
    u_labels = []
    u_entries = []
    
    for i in range(5):
        txt = u_label_texts[i][:]
        u_label = tk.Label(u_win, text=txt + ':')
        u_label.grid(row=5 + i, column=0)
        u_labels.append(u_label)
        
        u_entry = tk.Entry(u_win, width=35)
        u_entry.bind('<Return>', lambda event: entry_handling(event, u_alert))
        u_entry.extra = txt
        u_entry.grid(row=5 + i, column=1, columnspan=3)
        u_entries.append(u_entries)
        
    u_alert = tk.Label(u_win, text="")
    u_alert.grid(row=10, columnspan=4)
    
    u_enter_but = Button(u_win, text='Update Data', command=lambda: update_in_db(u_alert))
    u_enter_but.grid(row=11, columnspan=4)
    
    u_win.mainloop()

def open_D_window():
    global Curr_win
    
    destroy_win()
    # Toplevel object which will 
    # be treated as a new window
    d_win = Toplevel(root)
    
    Curr_win = d_win
    
    d_win.geometry(f"+{root.winfo_x()}+{root.winfo_y()}")
 
    # sets the title of the
    # Toplevel widget
    d_win.title("Delete Records")
 
    # A Label widget to show in toplevel
    record_label = Label(d_win, text ="Delete Records")
    record_label.grid(row=0, columnspan=3)
    
    d_label_1 = tk.Label(d_win, text="Location:")
    d_label_1.grid(row=1, column=0)
    d_location = tk.Entry(d_win, width=35)
    d_location.grid(row=1, column=1, columnspan=3)
    
    d_p_lst = Listbox(d_win, width=35, height=5, selectmode="single")
    d_p_lst.grid(row=2, column=1, columnspan=3)
    
    d_location.bind('<KeyRelease>', lambda event: crud_pred(event, d_p_lst))
    d_p_lst.bind("<<ListboxSelect>>", lambda event: crud_select_pred(event, d_location, d_p_lst, d_alert))
    
    d_separator_1 = ttk.Separator(d_win, orient='horizontal')
    d_separator_1.grid(row=3, columnspan=4, sticky="ew")
    
    d_date = tkcalendar.DateEntry(d_win)
    d_date.bind("<<DateEntrySelected>>", lambda event: date_entry_handling(event, d_alert))
    d_date.grid(row=5, columnspan=4)
    
    d_alert = tk.Label(d_win, text="")
    d_alert.grid(row=6, columnspan=4)
    
    d_enter_but = Button(d_win, text='Delete Data', command=lambda: delete_in_db(d_alert))
    d_enter_but.grid(row=7, columnspan=4)
    
    d_win.mainloop()

def export_db():
    cursor.execute("SELECT * FROM Weather;")
    with open("weather_data.csv", "w", newline='') as csv_file:
        csv_w = csv.writer(csv_file)
        csv_w.writerow([i[0] for i in cursor.description]) # write headers
        csv_w.writerows(cursor)

# Find current coordinate and Location
latitude, longitude, address = get_curr_loc()
Curr_loc = address

# Create the main window
root = tk.Tk()
root.title("Weather App - Steven Wang")

menu_bar = Menu(root)

root.config(menu=menu_bar) 

records = Menu(menu_bar) 
menu_bar.add_cascade(label='Records', menu=records)
records.add_command(label ='Create Records', command = open_C_window)
records.add_command(label ='Read Records', command = open_R_window)
records.add_command(label ='Update Records', command = open_U_window)
records.add_command(label ='Delete Records', command = open_D_window)

records.add_command(label ='Export Records', command = export_db)

info = Menu(menu_bar)
menu_bar.add_command(label ="Info", command = info_msg)

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

separator_2 = ttk.Separator(root, orient='horizontal')
separator_2.grid(row=11, columnspan=5, sticky="ew")

forcast_label = tk.Label(root, text="5-Day Forecast")
forcast_label.grid(row=12, columnspan=5)

for i in range(5):
    label = tk.Label(root, text="")
    label.grid(row=13, column=i)
    symbol = tk.Label(root, text="", font=("Segoe UI Emoji", 20))
    symbol.grid(row=14, column=i)
    temp = tk.Label(root, text="")
    temp.grid(row=15, column=i)
    r_prob = tk.Label(root, text="")
    r_prob.grid(row=16, column=i)
    labels.append(label)
    symbols.append(symbol)
    temps.append(temp)
    r_probs.append(r_prob)

root.eval('tk::PlaceWindow . center')

root.mainloop()