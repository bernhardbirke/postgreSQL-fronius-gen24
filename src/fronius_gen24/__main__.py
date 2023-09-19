# from fronius_data_postgresql import FroniusToInflux
import yaml
import pytz
from astral.geocoder import database, lookup

from data import FroniusToPostgres
from config import Configuration

# initialize location
location = lookup("Vienna", database())
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
