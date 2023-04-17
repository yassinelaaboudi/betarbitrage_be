import json
from datetime import datetime
import pandas as pd
import numpy as np

import logger as log
from driver_init import *
from driver_extract import *
from data_handling import *


logger = log.get_logger("main.py")
# Define config path and the competition
CONFIG_PATH = "config.json"
DRIVER_PATH = "driver_location.json"
# Define date format
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


if __name__ == "__main__":
    with open(CONFIG_PATH) as config:
        config = json.load(config)
    import subprocess

    competitions = [i for i in config["URLS"].keys()]
    competitions = ["jupilerproleague", "ligue2"]
    dict_driver = {}
    for competition in competitions:
        try:
            logger.info("try getting the driver if exist")
            dict_driver[competition] = get_driver(competition, config)
        except ImportError as err:
            logger.info("driver not exist - create new one")
            subprocess.call(["python", "driver_init.py", competition])
            dict_driver[competition] = get_driver(competition, config)
        except Exception as err:
            logger.exception("investigate")
            print(err)

    dict_quotes = {}
    for competition, driver in dict_driver.items():
        logger.info("get_quotes for competition")

        dict_quotes[competition] = get_all_quotes(
            driver, config["URLS"][competition], config["CSS_SELECTORS"]
        )

    with open("all_quotes.json", "w") as f:
        json.dump(dict_quotes, f, indent=4)

