import json
from functools import reduce
from datetime import datetime
import pandas as pd
from pathlib import Path

import logger as log
from driver_init import *
from driver_extract import *
from data_handling import *


logger = log.get_logger("main.py")
# Define config path and the competition
CONFIG_PATH = "config.json"
DRIVER_PATH = "driver_location.json"
KEY_PATH = "teams_correspondancy.xlsx"
# Define date format
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


if __name__ == "__main__":
    import subprocess

    with open(CONFIG_PATH) as config:
        config = json.load(config)
    # Define competitions you want the quotes
    competitions = [i for i in config["URLS"].keys()]
    competitions = ["ligue2", "laliga", "ligue1"]
    # Get the dataframe with the keys
    df_keys = pd.read_excel(KEY_PATH)
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

    # First get the date of the extraction
    now = datetime.now().strftime(DATE_FORMAT)
    dict_quotes = {}
    all_quotes = []
    df_failed = pd.DataFrame(columns=["league", "date"])
    # For all competitions - Extract the quote
    for competition, driver in dict_driver.items():
        logger.info(f"get_quotes for {competition}")
        # Extract quote for the competition
        dict_quotes[competition] = get_all_quotes(
            driver, config["URLS"][competition], config["CSS_SELECTORS"]
        )
        # Get URLS where we failed to get the quotes
        # You should create DB for log and take them from there but too much work
        failed_urls = [
            [i, [k for k, v in j.items() if len(v) == 0]]
            for i, j in dict_quotes.items()
        ]
        failed_urls = [{i[0]: [*i[1], now]} for i in failed_urls if len(i[1]) > 0]
        if failed_urls:
            failed_urls = reduce(lambda x, y: {**x, **y}, failed_urls)
            df_failed = pd.concat(
                [df_failed, pd.DataFrame(failed_urls).T], axis=0, ignore_index=True
            )

        # Standardize the quotes as dict of dataframes
        dict_quotes_std = standardize_quotes(
            dict_quotes[competition], config["COL_LOCATORS"]
        )
        # Concat all the quotes into 1 df
        all_quotes.append(concatenate_quotes(dict_quotes_std, df_keys))

    # Finally write the dataframes as csv
    logger.info("Writting data as csv")
    df_all_quotes = pd.concat(all_quotes, axis=0)
    df_all_quotes["date"] = now
    # Check if file exist otherwise append it
    filepath_all_quotes = Path("data/all_quotes.csv")
    file_exists = filepath_all_quotes.exists()
    df_all_quotes.to_csv(
        filepath_all_quotes,
        header=not file_exists,
        mode="a" if file_exists else "w",
        index=False,
    )
    # Check if file exist otherwise append it
    filepath_fail = Path("data/failed_urls.csv")
    file_exists = filepath_fail.exists()
    df_all_quotes.to_csv(
        filepath_fail,
        header=not file_exists,
        mode="a" if file_exists else "w",
        index=False,
    )

