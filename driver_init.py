import json
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


def init_driver(dict_url, dict_cookies):
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
    logger.info("Initialise driver")
    chrome_options = Options()
    # Avoid certificates errors
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

    # Make sure it doesn't close windows when code is executed
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome("chromedriver.exe", options=chrome_options)

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


def get_driver(competition, dict_config, path_driver_location="driver_location.json"):
    """
    Instantiate or get an existing driver for a given competition
    return a driver object
    """
    # Get all the drivers wich are open
    with open(path_driver_location, "r") as f:
        dict_driver_location = json.load(f)
    try:
        command_executor = dict_driver_location[competition]["command_executor"]
        session_id = dict_driver_location[competition]["session_id"]
        desired_capabilities = dict_driver_location[competition]["desired_capabilities"]
    except KeyError:
        dict_driver_location[competition] = {}
        command_executor, session_id = (
            "http://www.example.com",
            "",
        )

    try:
        logger.info("Looking for an existing driver")
        # If the driver already exist for a competition - Get it
        driver = webdriver.Remote(
            command_executor=command_executor, desired_capabilities={},
        )
        driver.close()
        driver.session_id = session_id
        driver.title
        logger.info("driver already exist")
    # If not existing Create new one
    except (
        MaxRetryError,
        UnboundLocalError,
        NoSuchWindowException,
        InvalidSessionIdException,
    ):
        logger.warning("Session does not exist - create new one")
        # Case when starting new session
        driver = init_driver(
            dict_config["URLS"][competition], dict_config["COOKIES_REF"]
        )

    finally:
        logger.info("Updating driver location")
        # Update driver data
        dict_driver_location[competition][
            "command_executor"
        ] = driver.command_executor._url
        dict_driver_location[competition]["session_id"] = driver.session_id
        dict_driver_location[competition]["status"] = "active"

    # Update the Location of the driver
    with open(path_driver_location, "w") as f:
        json.dump(dict_driver_location, f, indent=4)
        logger.info(
            f"driver coord updated {driver.session_id}-{driver.command_executor._url}"
        )

    return driver


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description="Launch selenium webdriver")
    # Ajout d'un argument pour la chaîne de caractères en entrée
    parser.add_argument(
        "competition",
        type=str,
        help="name of the competition where creating the driver",
    )
    # Récupération des arguments en ligne de commande
    args = parser.parse_args()

    with open("config.json") as f:
        config = json.load(f)

    driver = get_driver(args.competition, dict_config=config)

    # test = "test2"
    # # Test with 1 webdriver
    # if test == "test1":
    #     driver = get_driver("laliga", dict_config=config)
    # elif test == "test2":
    #     for compet in ["laliga", "ligue2"]:
    #         driver = get_driver(compet, dict_config=config)
    #         driver.close()
