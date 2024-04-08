import asyncio
import logging

import validators
from selenium.common.exceptions import StaleElementReferenceException
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebScraper:
    # Modified from https://www.webscrapingapi.com/python-headless-browser

    def __init__(self) -> None:
        self.options = Options()
        self.options.add_argument("--headless")
        prefs = {"download.default_directory": "/tmp/"}
        self.options.add_experimental_option("prefs", prefs)
        self.driver = webdriver.Chrome(options=self.options)
        self.target = None

    # def _refresh_driver(self) -> None:
    #     self.driver.quit()
    #     self.driver = webdriver.Chrome(options=self.options)

    async def navigate(self, target: str) -> None:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self.navigate_sync, target)

    def navigate_sync(self, target: str) -> None:
        # if self.target is not None and target != self.target:
        #     self._refresh_driver()
        self.target = target
        self.driver.get(target)

    def extract_raw_data(self) -> str:
        return self.driver.page_source

    def find_element(
        self, selector: str, selector_type: By = By.TAG_NAME
    ) -> list[WebElement]:
        return self.driver.find_element(selector_type, selector)

    def extract_rendered_text(self) -> str:
        return self.find_element("body").text

    def find_elements(
        self, selector: str, selector_type: By = By.TAG_NAME
    ) -> list[WebElement]:
        return self.driver.find_elements(selector_type, selector)

    def find_all_links(self) -> set[str]:
        links = []
        for link in self.find_elements("a"):
            try:
                href = link.get_attribute("href")
                if href is not None:
                    links.append(href)
            except StaleElementReferenceException:
                logger.info(f"Stale reference exception: {self.target}")
        return set(link for link in links if validators.url(link))
