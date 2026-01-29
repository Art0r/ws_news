from typing import Optional
from selenium import webdriver


def get_driver(url: Optional[str] = None) -> webdriver.Firefox:
    options = webdriver.FirefoxOptions()
    # options.page_load_strategy = "eager"
    # options.add_argument("--headless")

    driver = webdriver.Firefox(options=options)

    if url:
        driver.get(url)

    return driver
