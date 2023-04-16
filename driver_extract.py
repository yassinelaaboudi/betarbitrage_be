from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.errorhandler import (
    NoSuchElementException,
    TimeoutException,
    ElementClickInterceptedException,
    StaleElementReferenceException,
)
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
import logger as log

logger = log.get_logger("driver extract")


def get_quotes(driver, url, css_selector, max_wait=15):
    """
    Extracts quotes from one web page using a Selenium WebDriver.

    Args:
        driver (selenium.webdriver): A Selenium WebDriver object.
        url: URL of the website to get the quote
        css_selector: the CSS Selector allowing to get the quote
        max_wait : The maximum amount of time to wait for each page to load before giving up (in seconds).
    
    Returns:
        list of all quotes with team name etc... from the url  
    """
    logger.info(f"get quotes for {url}")
    if url != driver.current_url:
        logger.error(f"URL - {url} is not active on the driver")
        logger.info(f"{url} - {driver.current_url}")
        raise ValueError("URL is not active on the driver")

    # Ensure that the element exist on the webpage - wait max_wait seconds
    try:
        WebDriverWait(driver, max_wait).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
        )
    except TimeoutException:
        logger.warning("Can not get the quote - try maximising window")
        driver.maximize_window()
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
            )
        except TimeoutException:
            raise NoSuchElementException(f"Unable to get the quotes for {url}")

    # find all elements regarding their CSS_SELECTORS
    elements = driver.find_elements_by_css_selector(css_selector)

    try:
        return [i.text.split("\n") for i in elements]
    except StaleElementReferenceException:
        # You should refresh the driver, let's try after
        # Make it recursive maybe - or max_try = 3
        logger.error("probleme identifié mais non résolu")
        raise StaleElementReferenceException


def get_all_quotes(driver, dict_url, dict_selectors, max_wait=15):
    """
    Extracts quotes from web pages using a Selenium WebDriver.

    Args:
        driver (selenium.webdriver): A Selenium WebDriver object.
        dict_url (dict): A dictionary mapping page names to their URLs.
        dict_selectors (dict): A dictionary mapping page names to CSS selectors for the desired quote elements.
        max_wait (int, optional): The maximum amount of time to wait for each page to load before giving up (in seconds).

    Returns:
        dict: A dictionary mapping page names to DataFrames containing the extracted quotes.
    """
    dict_quotes = {}

    for index, (name, url) in enumerate(dict_url.items()):
        # Go to the correct window
        driver.switch_to.window(driver.window_handles[index])
        # Get the CSS selector for each url
        if name in dict_selectors:
            css_selector = dict_selectors[name]
        else:
            logger.error(f"{name} doesnt have any selector parametrized")
            continue
        # get the quotes
        try:
            quotes = get_quotes(driver, url, css_selector, max_wait)
        # refresh the page and retry if StaleElementReferenceException
        except StaleElementReferenceException:
            driver.refresh()
            logger.warning("refreshing the driver")
            quotes = get_quotes(driver, url, css_selector, max_wait)

        if quotes is not None:
            dict_quotes[name] = quotes
        else:
            logger.error(f"error while getting the quotes for {name}")

    return dict_quotes

