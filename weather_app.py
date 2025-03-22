# import module
from geopy.geocoders import Nominatim

# initialize Nominatim API (Has trouble with Canadian Postal code)
location = Nominatim(user_agent="weather_app")

coord = location.geocode("Erindale Park, Canada", exactly_one=True)
 
# printing address
print(coord.address)
 
# printing latitude and longitude
print("Latitude = ", coord.latitude, "\n")
print("Longitude = ", coord.longitude)