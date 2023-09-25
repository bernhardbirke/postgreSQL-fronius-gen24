# from fronius_data_postgresql import FroniusToInflux
import pytz
import datetime
from astral.geocoder import database, lookup
from astral.sun import sun


from data import FroniusToPostgres
from config import Configuration

# initialize location
city = lookup("Vienna", database())
# calculates the time of the sun in UTC
location = sun(city.observer, date=datetime.date.today())

# initialize timezone
tz = pytz.timezone("Europe/Vienna")

# instance of Configuration class
config = Configuration()
# load fronius connection configuration
fronius_config = config.fronius_config()

# define endpoints for http requests
endpoints = [
    f"http://{fronius_config['fronius_host']}/solar_api/v1/GetInverterRealtimeData.cgi",
    f"http://{fronius_config['fronius_host']}/solar_api/GetAPIVersion.cgi",
]

ftop = FroniusToPostgres(config, location, endpoints, tz)
ftop.IGNORE_SUN_DOWN = True
ftop.run()


# TODO: add logging, add testing of ftop.run()
