## Purpose

A python programm to read Data from a Fronius GEN24 inverter using http Requests.
The Data is then saved to a postgreSQL Database.

### This work is based on the following solutions

https://github.com/akleber/mqtt-connectors/blob/master/fronius-connector.py

https://github.com/szymi-/fronius-to-influx/blob/master/src/fronius_to_influx.py

### necessary modules

python requests module to handle http requests.

    $ pip install requests

module to parse `config.yaml`:

    $ pip install pyyaml

Astral is a python package for calculating the times of various aspects of the sun and moon.
(https://astral.readthedocs.io/en/latest/)

    $ pip3 install astral

### Environment

In `database.ini` the connection details of postgresql and the fronius inverter are stored.
