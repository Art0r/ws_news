from selenium.webdriver.support.wait import WebDriverWait
from ws_news.types import HtmlTag
from typing import Optional, Tuple
from selenium import webdriver


def get_xpath(html_tag: HtmlTag) -> str:
    query = [
        f"contains(@class, '{attr}')" for attr in html_tag._class.split(" ")]
    aggregated_query = " and ".join(query)

    xpath = f"//{html_tag._tag}[{aggregated_query}]"
    return xpath


def get_driver(url: Optional[str] = None) -> Tuple[webdriver.Firefox, WebDriverWait]:
    options = webdriver.FirefoxOptions()
    # options.page_load_strategy = "eager"
    # options.add_argument("--headless")

    driver = webdriver.Firefox(options=options)

    if url:
        driver.get(url)

    wait = WebDriverWait(driver, 10)

    return driver, wait
