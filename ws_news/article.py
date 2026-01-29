from re import split
from typing import List
import requests
import json

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from sqlalchemy import insert, select, update
from selenium.common.exceptions import ElementClickInterceptedException
from ws_news.database import Article, get_connection, get_session
from selenium import webdriver

from ws_news.driver import get_driver
from ws_news.types import HtmlTag


class AbcArticle:
    _url: str
    _headline: str
    _source: str
    _paragraphs_attr: HtmlTag
    _wait: WebDriverWait
    _driver: WebDriver

    def __init__(self, url: str, headline: str):
        self._url = url
        self._headline = headline
        self._driver = get_driver(self._url)
        self._wait = WebDriverWait(self._driver, 10)

    def get_xpath(self) -> str:
        query = [
            f"contains(@class, '{attr}')"
            for attr in self._paragraphs_attr._class.split(" ")
        ]
        aggregated_query = " and ".join(query)

        xpath = f"//{self._paragraphs_attr._tag}[{aggregated_query}]"
        return xpath

    def get_article_text(self) -> str:
        xpath = self.get_xpath()
        elements: List[WebElement] = self._wait.until(
            EC.presence_of_all_elements_located((By.XPATH, xpath))
        )

        if len(elements) <= 0:
            print("Nenhum paragrafo encontrado")

        return "".join([element.text for element in elements])

    # def upsert_article(self):
    #     with get_session() as session:
    #         url = self._url
    #         headline = self._headline
    #         text = self.get_article_text()
    #         source = self._source
    #
    #         article = session.query(Article).filter(Article.url == url).first()
    #
    #         if article:
    #             stmt = (
    #                 update(Article)
    #                 .where(Article.url == url)
    #                 .values(text=text, headline=headline, updated_at=datetime.now())
    #             )
    #
    #         else:
    #             stmt = insert(Article).values(
    #                 url=url,
    #                 headline=headline,
    #                 text=text,
    #                 source=source,
    #             )
    #
    #         session.execute(stmt)
    #


#
# class EstadaoArticle(AbcArticle):
#     _paragraphs_attr = {"data-component-name": "paragraph"}
#     _source = "Estadao"
#
#
# class GUmArticle(AbcArticle):
#     _paragraphs_attr = {"class": "content-text__container"}
#     _source = "G1"
#


class CNNArticle(AbcArticle):
    _paragraphs_attr = HtmlTag(
        _class="my-5 break-words group-[.isActiveSource]:text-xl", _tag="p"
    )
    _source = "CNN"
