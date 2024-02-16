## Purpose

A python programm to read Data from a Fronius GEN24 inverter using http Requests.
The Data is then saved to a postgreSQL Database.

### necessary modules

For all necessary modules refer to `requirements.txt`.

python requests module to handle http requests.

    pip install requests

module to parse `main_config.yaml`:

    pip install pyyaml

Astral is a python package for calculating the times of various aspects of the sun and moon.
(https://astral.readthedocs.io/en/latest/)

    pip3 install astral

Module to handel time zone conversions:

    pip install pytz

Module to run the tests

    pip install pytest

Module to mock the api response for the test environment

    pip install pytest-mock

Module for typechecking

    pip install mypy

Module to use postgreSQL

    pip install psycopg2 or pip install psycopg2-binary

### Environment files

In `database.ini` the connection details of postgresql and the fronius inverter are stored:

```
[postgresql]
host=localhost
database=my_database
user=my_username
password=my_postgresql_pw
```

In `main_config.yaml` connection configurations are stored.

### saved data

Value name | specific data | unit | type Description

PAC | integer | W | AC power (negative value for consuming power)

TOTAL_ENERGY | unsigned number | Wh | AC Energy generated overall GEN24/Tauro: supported since 1.14(updated every
5min)

#### To connect to mqtt or influx databases please refer to the following solutions:

https://github.com/akleber/mqtt-connectors/blob/master/fronius-connector.py
https://github.com/szymi-/fronius-to-influx/blob/master/src/fronius_to_influx.py
