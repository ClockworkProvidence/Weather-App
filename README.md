# Weather-App

The following project is a weather app, it is part of a tech assessment for PM Accelerator, this project is an attempt for PART TWO of the assessment, where CRUD functionality, Exports, and additional API application was a core part of the functionality.

To run the App, simply run the attached python file with python3. Note that the project contains a number of libraries, and should be installed beforehand. Do note that since a number of functionalities of the app are API based, the run time of certain elements may fluctuate with connection speed.

The main GUI is designed with the python tkinter package. The main function of the app is to provide location based weather reporting, by default, the user's current location is preloaded using ipinfo.io API. There is also a search bar, where location names can be entered, powered by open-meteo's geocoding API (note the API cannot do canadian Postal codes). You can also toggle the coordinates feature to search by the coordinates directly.

The weather report contains all the essential information and also a five day forcast. Each time the see weather button is pressed, the current day weather data is recorded.

There are also menu button to access the information page, and the pages for the CRUD functionalty of the records.

# Reflection

The project manages to function, and all features are accounted for, however the time constrains did leave organization much to be desired.

The code not partitioned particularly elegantly, and much of it is redundant, chiefly the CRUD functions sections. Variable naming conventions drifted over time, and large sections largely do not have explainitory comments.

Future improvement would include class based structures, a more object based approach, and cleaner overall presentation.
