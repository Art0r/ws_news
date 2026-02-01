from typing import List

from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from sqlalchemy.sql import insert, select

from ws_news.database import Article, get_session
from ws_news.helpers import get_driver, get_xpath
from ws_news.types import HtmlTag


class AbcArticle:
    _url: str
    _headline: str
    _source: str
    _paragraphs_attr: HtmlTag
    _driver: webdriver.Firefox
    _wait: WebDriverWait

    def __init__(self, url: str, headline: str):
        self._url = url
        self._headline = headline
        self._driver, self._wait = get_driver(self._url)

    def get_article_text(self) -> str | None:
        try:
            xpath = get_xpath(self._paragraphs_attr)

            elements: List[WebElement] = self._wait.until(
                EC.presence_of_all_elements_located((By.XPATH, xpath))
            )

            if len(elements) <= 0:
                print("Nenhum paragrafo encontrado")

            return "".join([element.text for element in elements])

        except Exception as e:
            raise Exception(f"failed: {e.args}")
        finally:
            self._driver.close()

    def is_article_already_saved(self) -> bool:
        url = self._url

        stmt = (
            select(Article.id, Article.url)
            .select_from(Article)
            .where(Article.url == url)
        )

        with get_session() as session:
            article = session.execute(stmt).first()
            return article is not None

    def insert_article(self):
        url = self._url
        headline = self._headline
        source = self._source

        if self.is_article_already_saved():
            print(f"Article skipped: {url}")
            return

        text = self.get_article_text()

        with get_session() as session:
            stmt = insert(Article).values(
                url=url,
                headline=headline,
                text=text,
                source=source,
            )

            session.execute(stmt)
            session.commit()
            print(f"Article inserted: {url}")


class GUmArticle(AbcArticle):
    _paragraphs_attr = HtmlTag(_class="content-text__container", _tag="p")
    _source = "G1"


class CNNArticle(AbcArticle):
    _paragraphs_attr = HtmlTag(
        _class="my-5 break-words group-[.isActiveSource]:text-xl", _tag="p"
    )
    _source = "CNN"
