import json
import pathlib
import os
from urllib3.exceptions import MaxRetryError
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebDriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import InvalidSessionIdException
from selenium.webdriver.remote.errorhandler import (
    NoSuchElementException,
    TimeoutException,
    ElementClickInterceptedException,
    StaleElementReferenceException,
    NoSuchWindowException,
)
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
import logger as log

logger = log.get_logger("driver init")


def expand_starcasino(driver):
    """
    Expend all dates on starcasino to display all quotes
    """
    # Go to the French Language Page
    logger.info("Starcasino - get the french page")
    driver.implicitly_wait(2)
    language_button = driver.find_element_by_css_selector(
        ".css-pe3ddf.css-pe3ddf.css-pe3ddf"
    )
    if language_button.text != "FR":
        language_button.click()
        driver.find_element_by_xpath('//li[@data-value="FR"]').click()

    logger.info("expand dates on starcasino")
    driver.implicitly_wait(2)
    selector = "._asb_events-tree-table-node-CH--expansion-panel-title, ._asb_events-tree-table-node-DT--expansion-panel-title, ._asb_events-tree-table-node-SP--expansion-panel-title, ._asb_results-table--expansion-panel-title, ._asb_toto-jackpots-tree--expansion-panel-header"
    els = driver.find_elements(By.CSS_SELECTOR, value=selector)
    for i in els:
        try:
            i.find_element_by_css_selector(".asb-icon-arrow-down").click()
            logger.info("found 1 elements to drag down")
        except NoSuchElementException:
            logger.warning("did not find any element to drag down")
        except ElementClickInterceptedException:
            logger.warning("Impossible to click on the element")
        except StaleElementReferenceException:
            logger.warning("It seems all data have been expanded - Double Check after")


def set_chrome_properties(headless):
    """
    Function used to set the chrome properties of a selenium web driver
    Avoid repetetion where we instantiate it or when creating a remote one
    """
    chrome_options = Options()
    # Avoid certificates errors
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    if headless is True:
        chrome_options.add_argument("--headless=new")
    # Check with this options for further uses
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # chrome_options.add_argument("--remote-debugging-port=9222")
    # Make sure it doesn't close windows when code is executed
    chrome_options.add_experimental_option("detach", True)

    return chrome_options


def init_driver(
    dict_url, dict_cookies, headless=False, path_chromedriver="chrome_driver.exe"
):
    """
    Initializes a Selenium driver and opens all URLs from a dictionary in separate tabs.
    If dict_cookies is not empty the driver will click automatically on the cookies button on the website to accept all cookies
    If the website is "starcasino", the page will be expanded to show all available sports.

    Args:
    - dict_url (dict): A dictionary containing the names of websites as keys and their corresponding URLs as values.
    - dict_cookies (dict): A dictionary containing the names of websites as keys and their corresponding cookie IDs as values.

    Returns:
    - driver (webdriver.Chrome): A Selenium Chrome driver object.
    """
    # Instantiate a driver
    logger.info("Instantiate driver")
    # Get the chrome options
    chrome_options = set_chrome_properties(headless)
    # Instantiate driver
    driver = webdriver.Chrome(
        path_chromedriver,
        options=chrome_options,
        service_args=["--verbose", "--log-path=test.log"],
    )

    for name, url in dict_url.items():
        logger.info(f"get {name}")
        # Get the URL
        driver.get(url)
        # open a new tab
        driver.execute_script("window.open('');")
        # switch to the new tab
        driver.switch_to.window(driver.window_handles[-1])

    # close the last empty tab
    driver.close()

    for index, (name, url) in enumerate(dict_url.items()):
        if dict_cookies.get(name) is not None:
            logger.info(f"accept cookies {name}")
            driver.switch_to.window(driver.window_handles[index])
            driver.find_element(by=By.ID, value=dict_cookies[name]).click()

        if name == "starcasino":
            driver.switch_to.window(driver.window_handles[index])
            expand_starcasino(driver)

    logger.info(f"driver instanciated with all urls")

    return driver


def get_driver(competition, path_driver_location="driver_location.json"):
    """
    get an existing driver for a given competition
    return a driver object
    """
    # Get all the drivers wich are open
    # if the file does not exist raise an import error too

    with open(path_driver_location, "r") as f:
        dict_driver_location = json.load(f)

    try:
        # Get info to open the driver
        command_executor = dict_driver_location[competition]["command_executor"]
        session_id = dict_driver_location[competition]["session_id"]
    except KeyError:
        raise ImportError("The driver does not exist")

    try:
        logger.info("Looking for an existing driver")
        # If the driver already exist for a competition - Get it
        chrome_options = set_chrome_properties(headless=True)
        # Get the remote driver
        driver = webdriver.Remote(
            command_executor=command_executor,
            desired_capabilities=chrome_options.to_capabilities(),
        )
        driver.close()
        driver.session_id = session_id
        driver.title
        logger.info("driver already exist")
    # If raise an error
    except (
        MaxRetryError,
        UnboundLocalError,
        NoSuchWindowException,
        InvalidSessionIdException,
    ):
        raise ImportError("Impossible to get the driver")
    return driver


if __name__ == "__main__":
    # when you instantiate more than 1 driver in a loop, only the last one created
    # can be recovered from another python terminal
    # To change this behaviour you can launch the program from the terminal directly
    import argparse

    # Get the path of config and driver_location
    PATH_CONFIG = "config.json"
    PATH_DRIVER_LOCATION = "driver_location.json"
    PATH_CHROME_DRIVER = "chromedriver.exe"
    if os.name != "nt":
        PATH_CHROME_DRIVER = "/usr/local/bin/chromedriver"

    # Instantiate parser
    parser = argparse.ArgumentParser(description="Launch selenium webdriver")
    # Add one argument to enter to the program
    parser.add_argument(
        "competition",
        type=str,
        help="name of the competition where creating the driver",
    )
    # Get the args from the terminal
    args = parser.parse_args()

    # Get the parameters from config
    with open(PATH_CONFIG) as f:
        config = json.load(f)
    dict_url = config["URLS"][args.competition]
    dict_cookies = config["COOKIES_REF"]

    # Instantiate the driver
    logger.info(f"Instantiate driver for {args.competition}")
    driver = init_driver(
        dict_url, dict_cookies, headless=True, path_chromedriver=PATH_CHROME_DRIVER
    )
    # get the information from the driver and copy them to the driver_location.json
    command_executor = driver.command_executor._url
    session_id = driver.session_id

    # Write driver coordinates into json PATH_DRIVER_LOCATION
    logger.info("Writing driver coordinates")
    try:
        with open(PATH_DRIVER_LOCATION, "r") as f:
            dict_location = json.load(f)
    except FileNotFoundError:
        logger.error("Driver Location File does not exist")
        dict_location = {}

    dict_location[args.competition] = {
        "command_executor": command_executor,
        "session_id": session_id,
        "status": "active",
    }
    with open(PATH_DRIVER_LOCATION, "w") as f:
        json.dump(dict_location, f, indent=4)
    logger.info("Driver coordinates written")
