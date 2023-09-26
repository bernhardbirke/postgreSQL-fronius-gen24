# coding: utf-8
import datetime
import logging
from time import sleep
from typing import Any

from requests import get
from requests.exceptions import ConnectionError
from src.fronius_gen24.config import Configuration
from src.fronius_gen24.postgresql_tasks import PostgresTasks

from src.fronius_gen24.exceptions import (
    WrongFroniusData,
    DataCollectionError,
    SunIsDown,
)


class FroniusToPostgres:
    IGNORE_SUN_DOWN: bool = False

    def __init__(
        self,
        config: Configuration,
        client: PostgresTasks,
        location: dict[str],
        endpoint: str,
        tz: Any,
    ) -> None:
        self.config = config
        self.client = client
        self.location = location
        self.endpoint = endpoint
        self.tz = tz
        self.BACKOFF_INTERVAL: int = 30  # minimum interval between calls in seconds
        self.IGNORE_SUN_DOWN: bool = (
            False  # False means only log data when sun is shining
        )
        self.data: dict[Any, Any] = {}
        self.data_id: int = 0

    def get_float_or_zero(self, value: str) -> float:
        internal_data: dict[Any, Any] = {}
        try:
            internal_data = self.data["Body"]["Data"]
        except KeyError:
            logging.error("Response structure is not healthy", exc_info=True)
            raise WrongFroniusData("Response structure is not healthy.")
        return float(internal_data.get(value, {}).get("Value", 0))

    def translate_response(self) -> list[dict]:
        collection = self.data["Head"]["RequestArguments"]["DataCollection"]
        timestamp = self.data["Head"]["Timestamp"]
        if collection == "CommonInverterData":
            return [
                {
                    "measurement": "DeviceStatus",
                    "time": timestamp,
                    "fields": {
                        "ErrorCode": self.data["Body"]["Data"]["DeviceStatus"][
                            "ErrorCode"
                        ],
                        "LEDColor": self.data["Body"]["Data"]["DeviceStatus"][
                            "LEDColor"
                        ],
                        "LEDState": self.data["Body"]["Data"]["DeviceStatus"][
                            "LEDState"
                        ],
                        "MgmtTimerRemainingTime": self.data["Body"]["Data"][
                            "DeviceStatus"
                        ]["MgmtTimerRemainingTime"],
                        "StateToReset": self.data["Body"]["Data"]["DeviceStatus"][
                            "StateToReset"
                        ],
                        "StatusCode": self.data["Body"]["Data"]["DeviceStatus"][
                            "StatusCode"
                        ],
                    },
                },
                {
                    "measurement": collection,
                    "time": timestamp,
                    "fields": {
                        "FAC": self.get_float_or_zero("FAC"),
                        "IAC": self.get_float_or_zero("IAC"),
                        "IDC": self.get_float_or_zero("IDC"),
                        "PAC": self.get_float_or_zero(
                            "PAC"
                        ),  # AC power (negative value for consuming power) in W
                        "UAC": self.get_float_or_zero("UAC"),
                        "UDC": self.get_float_or_zero("UDC"),
                        "DAY_ENERGY": self.get_float_or_zero("DAY_ENERGY"),
                        "YEAR_ENERGY": self.get_float_or_zero("YEAR_ENERGY"),
                        "TOTAL_ENERGY": self.get_float_or_zero(
                            "TOTAL_ENERGY"
                        ),  # AC Energy generated overall in Wh
                    },
                },
            ]
        elif collection == "3PInverterData":
            return [
                {
                    "measurement": collection,
                    "time": timestamp,
                    "fields": {
                        "IAC_L1": self.get_float_or_zero("IAC_L1"),
                        "IAC_L2": self.get_float_or_zero("IAC_L2"),
                        "IAC_L3": self.get_float_or_zero("IAC_L3"),
                        "UAC_L1": self.get_float_or_zero("UAC_L1"),
                        "UAC_L2": self.get_float_or_zero("UAC_L2"),
                        "UAC_L3": self.get_float_or_zero("UAC_L3"),
                    },
                }
            ]
        else:
            logging.error(f"Unknown data collection type: {collection}", exc_info=True)
            raise DataCollectionError("Unknown data collection type.")

    def sun_is_shining(self) -> None:
        if (
            not self.IGNORE_SUN_DOWN
            and not self.location["sunrise"]
            < datetime.datetime.now(tz=self.tz)
            < self.location["sunset"]
        ):
            raise SunIsDown
        return None

    @staticmethod
    def get_response(url: str) -> Any:
        return get(url)

    def run(self) -> None:
        try:
            logging.info(f"Application started")
            while True:
                try:
                    self.sun_is_shining()
                    response = self.get_response(self.endpoint)
                    self.data = response  # .json()
                    collected_data = self.translate_response()
                    # insert commoninverterdata
                    self.data_id = self.client.insert_fronius_gen24(
                        collected_data[1]["fields"]["PAC"],
                        collected_data[1]["fields"]["IAC"],
                        collected_data[1]["fields"]["UAC"],
                        collected_data[1]["fields"]["FAC"],
                        collected_data[1]["fields"]["TOTAL_ENERGY"],
                    )
                    logging.info(f"Data written. Data id: {self.data_id}")
                    sleep(self.BACKOFF_INTERVAL)
                except SunIsDown:
                    logging.warning("No sun is shining. Waiting for sunrise")
                    sleep(60)
                    logging.info("Waited 60 seconds for sunrise")
                except ConnectionError:
                    logging.error("No Connection available", exc_info=True)
                    sleep(10)
                    logging.info("Waited 10 seconds for connection")
                except Exception as e:
                    self.data = {}
                    sleep(10)
                    logging.error("Exception: {}".format(e), exc_info=True)
                    print("Exception: {}".format(e))

        except KeyboardInterrupt:
            logging.info("Stopping program.")
