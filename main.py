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
    competitions = [i for i in config['URLS'].keys()]
    competitions = ['laliga','ligue2']

    for competition in competitions:
        subprocess.call(["python", "driver_init.py", competition])
        driver = get_driver(competition, config, path_driver_location=DRIVER_PATH)

    # # Open json config file
    # with open(CONFIG_PATH) as config:
    #     config = json.load(config)
    # # Get keys between each teams
    # df_keys = pd.read_excel("teams_correspondancy.xlsx")
    # # Define competitions
    # competitions = [i for i in config["URLS"].keys()]
    # # define Date
    # now = datetime.now()
    # df_all_quotes = pd.DataFrame()
    # for competition in competitions:
    #     if competition not in ["ligue2", "laliga", "bundesliga"]:
    #         continue

    #     logger.info(f"GETTING {competition}")
    #     driver = get_driver(competition, config, path_driver_location=DRIVER_PATH)
    #     driver.maximize_window()
    #     dict_quotes = get_all_quotes(
    #         driver, config["URLS"][competition], config["CSS_SELECTORS"]
    #     )
    #     dict_quotes_sc = standardize_quotes(dict_quotes, config["COL_LOCATORS"])
    #     df_quotes = concatenate_quotes(dict_quotes_sc, df_keys=df_keys)
    #     df_quotes["competition"] = competition
    #     df_quotes["date"] = now
    #     df_all_quotes = pd.concat([df_all_quotes, df_quotes], axis=0)

    # df_all_quotes.to_csv("all_quotes.csv")

