from abc import ABC, ABCMeta, abstractmethod
from datetime import datetime
from time import sleep
from typing import Dict, Generic, List, Optional, Type, TypeVar
from bs4 import BeautifulSoup
import requests
import json

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from sqlalchemy import insert, select, update

from ws_news.common.database import Article, get_connection, get_session
from selenium import webdriver


class AbcArticle:
    _url: str
    _headline: str
    _source: str
    _paragraphs_attr: Dict[str, str]

    def __init__(self, url: str, headline: str):
        self._url = url
        self._headline = headline

    def get_url(self) -> str:
        return self._url

    def get_headline(self) -> str:
        return self._headline

    def get_source(self) -> str:
        return self._source

    def get_article_attr(self) -> Dict[str, str]:
        return self._paragraphs_attr

    def get_article_text(self) -> str:
        res = requests.get(self._url)
        soup = BeautifulSoup(res.content.decode("utf-8"), "html.parser")
        elements = soup.find_all(attrs=self._paragraphs_attr)

        if len(elements) <= 0:
            print("Nenhum paragrafo encontrado")

        return "".join([element.text for element in elements])

    def upsert_article(self):
        with get_session() as session:
            url = self.get_url()
            headline = self.get_headline()
            text = self.get_article_text()
            source = self.get_source()

            article = session.query(Article).filter(Article.url == url).first()

            if article:
                stmt = (
                    update(Article)
                    .where(Article.url == url)
                    .values(text=text, headline=headline, updated_at=datetime.now())
                )

            else:
                stmt = insert(Article).values(
                    url=url,
                    headline=headline,
                    text=text,
                    source=source,
                )

            session.execute(stmt)


class EstadaoArticle(AbcArticle):
    _paragraphs_attr = {"data-component-name": "paragraph"}
    _source = "Estadao"


class AbcNews(ABC):
    _base_url: str
    _article_class: Type[AbcArticle]
    _articles_attr: Dict[str, str]
    _navigation_attr: Dict[str, str]
    _next_page_attr: Dict[str, str]
    _maximum_depth: int
    _current_depth: int
    _driver: WebDriver

    def __init__(self, maximum_depth: int = 5):
        self._maximum_depth = maximum_depth
        self._current_depth = 0
        self._driver = webdriver.Firefox()

    @abstractmethod
    def get_search_url(self, search_text: str) -> str:
        raise Exception("Not implemented")

    def get_articles(self) -> List[AbcArticle]:
        wait = WebDriverWait(self._driver, 10)
        elements: List[WebElement] = wait.until(
            EC.presence_of_all_elements_located(
                (By.CLASS_NAME, self._articles_attr["class"])
            )
        )

        if len(elements) <= 0:
            print("Nenhum artigo encontrado")

        return [
            self._article_class(
                url=element.get_attribute("href") or "",
                headline=element.get_attribute("title") or "",
            )
            for element in elements
        ]

    def go_to_search_page(self, search_text: str) -> str:
        url = self.get_search_url(search_text)

        self._driver.get(url)
        return self._driver.page_source

    def go_to_next_page(self):
        next_button = self._driver.find_element(
            by=By.XPATH,
            value="//button[contains(@class, 'arrow') and contains(@class, 'right')]",
        )

        next_button.click()

    def run(self, search: str):
        self.go_to_search_page(search)

        while self._current_depth < self._maximum_depth:
            articles = self.get_articles()
            print(articles)
            self.go_to_next_page()
            self._current_depth += 1

        self._driver.close()


class EstadaoNews(AbcNews):
    _base_url = "https://www.estadao.com.br"
    _articles_attr = {"class": "image-noticias"}
    _article_class = EstadaoArticle
    _navigation_attr = {"class": "container-pagination"}
    _next_page_attr = {"class": "arrow right "}

    def get_search_url(self, search_text: str) -> str:
        query = {"query": search_text}
        return self._base_url + "/busca?token=" + json.dumps(query)
