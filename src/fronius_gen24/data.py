# coding: utf-8
import datetime
import logging
import sys
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
            False  # False means only save data when sun is shining
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
        return float(internal_data.get(value, {}).get("Values", 0).get("1", 0))

    def translate_response(self) -> list[dict]:
        scope = self.data["Head"]["RequestArguments"]["Scope"]
        timestamp = self.data["Head"]["Timestamp"]
        if scope == "System":
            return {
                "time": timestamp,
                "fields": {
                    "PAC": self.get_float_or_zero(
                        "PAC"
                    ),  # AC power (negative value for consuming power) in W
                    "TOTAL_ENERGY": self.get_float_or_zero(
                        "TOTAL_ENERGY"
                    ),  # AC Energy generated overall in Wh
                },
            }
        else:
            logging.error(f"Unknown data collection type: {scope}", exc_info=True)
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
        return get(url).json()

    def run(self) -> None:
        try:
            logging.info(f"Application started")
            while True:
                try:
                    self.sun_is_shining()
                    response = self.get_response(self.endpoint)
                    logging.debug(f"API Response: {response}")
                    self.data = response
                    collected_data = self.translate_response()
                    logging.debug(f"collected data: {collected_data}")
                    # insert commoninverterdata
                    self.data_id = self.client.insert_fronius_gen24(
                        collected_data["fields"]["PAC"],
                        collected_data["fields"]["TOTAL_ENERGY"],
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
                    logging.error("Exception: {}".format(e), exc_info=True)
                    sys.exit(1)

        except KeyboardInterrupt:
            logging.info("Stopping program.")
