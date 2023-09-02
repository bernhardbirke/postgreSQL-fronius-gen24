import os
from configparser import ConfigParser
from dev.definitions import ROOT_DIR

url_to_database = os.path.join(ROOT_DIR, "database.ini")


def fronius_config(filename=url_to_database, section="fronius"):
    """define the details of a connection to the fronius api based on database.ini"""
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section
    fronius_con = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            fronius_con[param[0]] = param[1]
    else:
        raise Exception(f"Section {section} not found in the {filename} file")

    return fronius_con


def postgresql_config(filename=url_to_database, section="postgresql"):
    """define the details of a database connection based on database.ini"""
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception(f"Section {section} not found in the {filename} file")

    return db
