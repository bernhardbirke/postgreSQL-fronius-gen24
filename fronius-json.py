import requests
import time
import logging
import sys
from config import fronius_config, postgresql_config


def fronius_data(url):
    values = {}
    fronius_config = fronius_config()
    fronius_config["fronius_host"]
    try:
        url = "http://{}/solar_api/v1/GetPowerFlowRealtimeData.fcgi".format(
            fronius_config["fronius_host"]
        )  # noqa E501
        r = requests.get(url, timeout=fronius_config["frequency"] - 0.5)
        r.raise_for_status()
        powerflow_data = r.json()

        values["p_pv"] = powerflow_data["Body"]["Data"]["Site"]["P_PV"]
        values["p_grid"] = powerflow_data["Body"]["Data"]["Site"]["P_Grid"]
        values["p_akku"] = powerflow_data["Body"]["Data"]["Site"]["P_Akku"]
        values["p_load"] = -powerflow_data["Body"]["Data"]["Site"]["P_Load"]
        values["soc"] = powerflow_data["Body"]["Data"]["Inverters"]["1"].get("SOC")
        values["battery_mode"] = powerflow_data["Body"]["Data"]["Inverters"]["1"].get(
            "Battery_Mode"
        )
        values["e_day"] = (
            powerflow_data["Body"]["Data"]["Inverters"]["1"]["E_Day"] / 1000
        )

        # handling for null/None values
        for k, v in values.items():
            if v is None:
                values[k] = 0

    except requests.exceptions.Timeout:
        print(f"Timeout requesting {url}")
    except requests.exceptions.RequestException as e:
        print(f"requests exception {e}")

    return values
