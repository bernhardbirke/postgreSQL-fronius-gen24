# from fronius_data_postgresql import FroniusToInflux
import os
import pytz
import datetime
import logging
from astral.geocoder import database, lookup
from astral.sun import sun

from dev.definitions import ROOT_DIR
from src.fronius_gen24.postgresql_tasks import PostgresTasks
from src.fronius_gen24.data import FroniusToPostgres
from src.fronius_gen24.config import Configuration

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

# instance of PostgresTasks class
client = PostgresTasks()

# define endpoints for http requests
endpoint: str = f"http://{fronius_config['fronius_host']}/solar_api/v1/GetInverterRealtimeData.cgi?Scope=Device&DataCollection=CommonInverterData"
#   f"http://{fronius_config['fronius_host']}/solar_api/GetAPIVersion.cgi",

# initialize logging
loggingFile: str = os.path.join(ROOT_DIR, "fronius_gen24.log")

# config of logging module (DEBUG / INFO / WARNING / ERROR / CRITICAL)
logging.basicConfig(
    level=logging.INFO,
    filename=loggingFile,
    encoding="utf-8",
    filemode="a",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


ftop = FroniusToPostgres(config, client, location, endpoint, tz)
ftop.IGNORE_SUN_DOWN = True
ftop.run()


# TODO: stop testing of ftop.run() after a certain time
