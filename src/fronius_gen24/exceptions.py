# /exceptions.py


class WrongFroniusData(Exception):
    """Raised when wrong fronius data."""


class SunIsDown(Exception):
    """Raised when sun is down."""


class DataCollectionError(Exception):
    """Raised when an Error at Data Collection Occurs"""
