import asyncio
import logging
import time
from urllib.parse import urlparse

import validators
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
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
        self.options.add_argument("--mute-audio")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        prefs = {"download.default_directory": "/tmp/"}
        self.options.add_experimental_option("prefs", prefs)
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.set_page_load_timeout(15)
        self.target = None

    # def _refresh_driver(self) -> None:
    #     self.driver.quit()
    #     self.driver = webdriver.Chrome(options=self.options)

    async def navigate(self, target: str) -> float:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self.navigate_sync, target)

    def navigate_sync(self, target: str) -> float:
        # if self.target is not None and target != self.target:
        #     self._refresh_driver()
        start_time = time.perf_counter()
        self.target = target
        try:
            self.driver.get(target)
        except TimeoutException:
            logger.warning(f"Timeout fetching {target}")
        end_time = time.perf_counter()
        return end_time - start_time

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
        return set(
            link
            for link in links
            if validators.url(link) and not self._is_local_url(link)
        )

    def _is_local_url(self, url: str) -> bool:
        host = urlparse(url).hostname
        return host in {"localhost", "0.0.0.0"} or (
            host is not None and host.startswith("127.")
        )

    def close(self) -> None:
        self.driver.quit()
