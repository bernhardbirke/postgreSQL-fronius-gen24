import pytest
import pytz
import datetime
import json
from astral.geocoder import database, lookup
from astral.sun import sun
from src.fronius_gen24.data import FroniusToPostgres
from src.fronius_gen24.config import Configuration
from src.fronius_gen24.postgresql_tasks import PostgresTasks
from src.fronius_gen24.exceptions import (
    WrongFroniusData,
    DataCollectionError,
    SunIsDown,
)


@pytest.fixture  # instance of Class FroniusToPostgres
def froniustopostgres():
    # instance of Configuration class
    config = Configuration()
    # instance of PostgresTasks
    client = PostgresTasks()
    # initialize location
    city = lookup("Vienna", database())
    # calculates the time of the sun in UTC
    location = sun(city.observer, date=datetime.date.today())
    # define endpoints for http requests
    fronius_config = config.fronius_config()
    endpoints = [
        f"http://{fronius_config['fronius_host']}/solar_api/v1/GetInverterRealtimeData.cgi",
        f"http://{fronius_config['fronius_host']}/solar_api/GetAPIVersion.cgi",
    ]
    # initialize timezone
    tz = pytz.timezone("Europe/Vienna")
    return FroniusToPostgres(config, client, location, endpoints, tz)


@pytest.fixture  # data response as transmitted by Fronius API V1
def responsedata():
    response = {
        "Body": {
            "Data": {
                "DAY_ENERGY": {"Unit": "Wh", "Values": {"1": 0}},
                "PAC": {"Unit": "W", "Values": {"1": 6442.39697265625}},
                "TOTAL_ENERGY": {"Unit": "Wh", "Values": {"1": 5350360.6883333335}},
                "YEAR_ENERGY": {"Unit": "Wh", "Values": {"1": 0}},
            }
        },
        "Head": {
            "RequestArguments": {"Scope": "System"},
            "Status": {"Code": 0, "Reason": "", "UserMessage": ""},
            "Timestamp": "2023-09-27T09:53:23+00:00",
        },
    }
    return response


def test_get_float_or_zero_1(froniustopostgres, responsedata):
    froniustopostgres.data = responsedata
    assert froniustopostgres.get_float_or_zero("PAC") == 6442.39697265625


def test_get_float_or_zero_2(froniustopostgres, responsedata):
    froniustopostgres.data = responsedata
    assert froniustopostgres.get_float_or_zero("TOTAL_ENERGY") == 5350360.6883333335


def test_translate_response_1(froniustopostgres, responsedata):
    froniustopostgres.data = responsedata
    response_object = froniustopostgres.translate_response()
    assert response_object["fields"]["PAC"] == 6442.39697265625


def test_translate_response_2(froniustopostgres, responsedata):
    froniustopostgres.data = responsedata
    response_object = froniustopostgres.translate_response()
    assert response_object["fields"]["TOTAL_ENERGY"] == 5350360.6883333335


# run at daytime, test will fail at nighttime
def test_sun_is_shining_1(froniustopostgres):
    assert froniustopostgres.sun_is_shining() == None


# run at nighttime, test will fail at daytime
def test_sun_is_shining_2(froniustopostgres):
    with pytest.raises(SunIsDown):
        froniustopostgres.sun_is_shining()


def test_get_response(mocker, froniustopostgres, responsedata):
    output = responsedata
    mocker.patch(
        "src.fronius_gen24.data.FroniusToPostgres.get_response", return_value=output
    )
    response_object = froniustopostgres.get_response()
    assert response_object["Body"]["Data"]["PAC"]["Values"]["1"] == 6442.39697265625


def test_run(mocker, froniustopostgres, responsedata):
    output = responsedata
    mocker.patch(
        "src.fronius_gen24.data.FroniusToPostgres.get_response", return_value=output
    )
    froniustopostgres.run()
    # TODO stop run after 30 sec.
    assert isinstance(froniustopostgres.data_id, int) and froniustopostgres.data_id > 0
