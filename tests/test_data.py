import pytest
import pytz
from astral.geocoder import database, lookup
from src.fronius_gen24.data import FroniusToPostgres
from src.fronius_gen24.config import Configuration


@pytest.fixture  # instance of Class FroniusToPostgres
def froniustopostgres():
    # instance of Configuration class
    config = Configuration()
    # initialize location
    location = lookup("Vienna", database())
    # define endpoints for http requests
    fronius_config = config.fronius_config()
    endpoints = [
        f"http://{fronius_config['fronius_host']}/solar_api/v1/GetInverterRealtimeData.cgi",
        f"http://{fronius_config['fronius_host']}/solar_api/GetAPIVersion.cgi",
    ]
    # initialize timezone
    tz = pytz.timezone("Europe/Vienna")
    return FroniusToPostgres(config, location, endpoints, tz)


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


def t_sun_is_shining(froniustopostgres):
    assert froniustopostgres.sun_is_shining() == None


def t_run(mocker):
    output_list = [
        "Filesystem Size Used Avail Use% Mounted on",
        "rootfs 472G 128G 344G 28% /",
        "none 472G 128G 344G 28% /dev",
    ]
    output = "\n".join(output_list)
    mock_run = mocker.patch(
        "src.fronius_gen24.data.FroniusToPostgres.get_response", return_value=output
    )
    d = FroniusToPostgres(socket.gethostname())
    result = d.disk_free()
    percent = d.extract_percent(result)
    mock_run.assert_called_with("df -h")
    assert percent == "28%"
