from abc import ABC, abstractmethod
from queue import SimpleQueue
from time import sleep
from typing import List, Type

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import ElementClickInterceptedException

from ws_news.article import AbcArticle, CNNArticle
from ws_news.helpers import get_xpath, get_driver
from ws_news.types import HtmlTag


class AbcNews(ABC):
    _base_url: str
    _article_class: Type[AbcArticle]
    _article_link: HtmlTag
    _next_page: HtmlTag
    _maximum_depth: int
    _current_depth: int
    _driver: WebDriver
    _articles_queue: SimpleQueue[Type[AbcArticle]]

    def __init__(self, maximum_depth: int = 2):
        self._maximum_depth = maximum_depth
        self._current_depth = 0
        self._driver = get_driver()
        self._articles_queue = SimpleQueue()

    @abstractmethod
    def get_search_url(self, search_text: str) -> str:
        raise Exception("Not implemented")

    def get_articles_queue(self) -> SimpleQueue[Type[AbcArticle]]:
        return self._articles_queue

    def go_to_search_page(self, search_text: str) -> str:
        url = self.get_search_url(search_text)

        self._driver.get(url)
        return self._driver.page_source

    def go_to_next_page(self):
        try:
            xpath = get_xpath(self._next_page)
            wait = WebDriverWait(self._driver, 10)
            next_button: WebElement = wait.until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )

            self._driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});",
                next_button,
            )

            sleep(0.5)

            next_button.click()
        except ElementClickInterceptedException as e:
            print(
                "Ocorreu um erro ao ir para a página seguinte: {0} | Pagina atual: {1}".format(
                    e, self._current_depth
                )
            )
            self._driver.close()

    def fetch_articles(self, search: str) -> None:
        try:
            self.go_to_search_page(search)

            while self._current_depth < self._maximum_depth:
                xpath = get_xpath(self._article_link)

                wait = WebDriverWait(self._driver, 10)
                elements: List[WebElement] = wait.until(
                    EC.presence_of_all_elements_located((By.XPATH, xpath))
                )

                if len(elements) <= 0:
                    print("Nenhum artigo encontrado")

                for element in elements:
                    self._articles_queue.put(
                        self._article_class(
                            url=element.get_attribute("href") or "",
                            headline=element.get_attribute("title") or "",
                        )
                    )

                self.go_to_next_page()
                self._current_depth += 1

            self._driver.close()

        except Exception as e:
            print(e)
            self._driver.close()


# class EstadaoNews(AbcNews):
#     _base_url = "https://www.estadao.com.br"
#     _articles_attr = {"class": "image-noticias"}
#     _article_class = EstadaoArticle
#     _navigation_attr = {"class": "container-pagination"}
#     _next_page_attr = {"class": "arrow right "}
#
#     def get_search_url(self, search_text: str) -> str:
#         query = {"query": search_text}
#         return self._base_url + "/busca?token=" + json.dumps(query)
#
#
# class GUmNews(AbcNews):
#     _base_url = "https://g1.globo.com"
#     _articles_attr = {"class": "widget--info__media"}
#     _article_class = GUmArticle
#     _navigation_attr = {"class": "pagination"}
#     _next_page_attr = {"class": "pagination__load-more"}
#
#     def get_search_url(self, search_text: str) -> str:
#         return self._base_url + "/busca/?q=" + search_text
#
#
class CNNNews(AbcNews):
    _base_url = "https://www.cnnbrasil.com.br"
    _article_link = HtmlTag(_class="flex shrink-0 items-center", _tag="a")
    _article_class = CNNArticle
    _next_page = HtmlTag(
        _class="inline-flex items-center px-2 py-1 text-red-600", _tag="a"
    )

    def get_search_url(self, search_text: str) -> str:
        return self._base_url + "/?search=" + search_text
