import pytest
import pytz
import datetime
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
    return {
        "Body": {
            "Data": {
                "DAY_ENERGY": {"Unit": "Wh", "Value": 1393.2},
                "DeviceStatus": {
                    "ErrorCode": 0,
                    "LEDColor": 2,
                    "LEDState": 0,
                    "MgmtTimerRemainingTime": -1,
                    "StateToReset": "false",
                    "StatusCode": 7,
                },
                "FAC": {"Unit": "Hz", "Value": 49.969999999999999},
                "IAC": {"Unit": "A", "Value": 0.35999999999999999},
                "IDC": {"Unit": "A", "Value": 0.32000000000000001},
                "PAC": {"Unit": "W", "Value": 84},
                "TOTAL_ENERGY": {"Unit": "Wh", "Value": 1734796.1200000001},
                "UAC": {"Unit": "V", "Value": 232.40000000000001},
                "UDC": {"Unit": "V", "Value": 399.89999999999998},
                "YEAR_ENERGY": {"Unit": "Wh", "Value": 322593.5},
            }
        },
        "Head": {
            "RequestArguments": {
                "DataCollection": "CommonInverterData",
                "DeviceClass": "Inverter",
                "DeviceId": "1",
                "Scope": "Device",
            },
            "Status": {"Code": 0, "Reason": "", "UserMessage": ""},
            "Timestamp": "2019-06-12T15:31:03+02:00",
        },
    }


def test_get_float_or_zero_1(froniustopostgres, responsedata):
    froniustopostgres.data = responsedata
    assert froniustopostgres.get_float_or_zero("PAC") == 84


def test_get_float_or_zero_2(froniustopostgres, responsedata):
    froniustopostgres.data = responsedata
    assert froniustopostgres.get_float_or_zero("TOTAL_ENERGY") == 1734796.1200000001


def test_translate_response_1(froniustopostgres, responsedata):
    froniustopostgres.data = responsedata
    response_object = froniustopostgres.translate_response()
    assert response_object[1]["fields"]["PAC"] == 84


def test_translate_response_2(froniustopostgres, responsedata):
    froniustopostgres.data = responsedata
    response_object = froniustopostgres.translate_response()
    assert response_object[1]["fields"]["TOTAL_ENERGY"] == 1734796.1200000001


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
    assert response_object["Body"]["Data"]["PAC"]["Value"] == 84


def test_run(mocker, froniustopostgres, responsedata):
    output = responsedata
    mocker.patch(
        "src.fronius_gen24.data.FroniusToPostgres.get_response", return_value=output
    )
    response_object = froniustopostgres.get_response()
    assert response_object["Body"]["Data"]["PAC"]["Value"] == 84
