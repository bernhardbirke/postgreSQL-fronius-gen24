# from fronius_data_postgresql import FroniusToInflux
import yaml
from astral.geocoder import database, lookup

import pytz

# load main_config file
with open("main_config.yaml") as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

# initialize astral
location = lookup("Vienna", database())


tz = pytz.timezone("Europe/Vienna")
endpoints = [
    "http://172.30.1.11:5000/3PInverterData.json",
    "http://172.30.1.11:5000/CommonInverterData.json",
    "http://172.30.1.11:5000/MinMaxInverterData.json",
]

z = FroniusToInflux(client, location, endpoints, tz)
z.IGNORE_SUN_DOWN = True
z.run()
