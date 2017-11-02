import logging

from .articleparser import ArticleParser
from crawler.webpage import WebPage
from pony.orm import db_session
from bs4 import BeautifulSoup
from data import Article, Author
from text_processing import TextProcessor

import re
import dateutil.parser
import urllib.parse


class ArxivParser(ArticleParser):
    def __init__(self, text_processor: TextProcessor):
        super().__init__(text_processor)
        self._logger = logging.getLogger(self.__class__.__name__)
        self._text_processor = text_processor

    @db_session
    def parse(self, web_page: WebPage) -> bool:
        page_soup = BeautifulSoup(web_page.text, "html.parser")
        abstract_section = page_soup.find("div", {"id": "abs"})

        if not abstract_section:
            return False

        link_to_pdf_relative = abstract_section \
            .find("div", {"class": "extra-services"}) \
            .find("a", text=re.compile("PDF.*"))

        if link_to_pdf_relative:
            link = link_to_pdf_relative.get("href")
            link_to_pdf = urllib.parse.urljoin(web_page.url, link)
        else:
            link_to_pdf = None

        title = ArxivParser._get_clean_text(
            abstract_section.find("h1", {"class": "title mathjax"})
        )

        abstract = ArxivParser._get_clean_text(
            abstract_section.find("blockquote", {"class": "abstract mathjax"})
        )

        authors = list(
            map(lambda a: a.text, abstract_section.find("div", {"class": "authors"}).find_all("a"))
        )

        date_text = abstract_section\
            .find("div", {"class": "submission-history"})\
            .find("b", text="[v1]")\
            .next_sibling
        date = dateutil.parser.parse(date_text, fuzzy=True)

        self._store_parsed_article(raw_abstract=abstract,
                                   title=title,
                                   link_to_pdf=link_to_pdf,
                                   authors=authors,
                                   date=date,
                                   article_hash=web_page.page_hash)

    @staticmethod
    def _get_clean_text(soup: BeautifulSoup) -> str:
        for s in soup.find_all("span"):
            s.extract()
        return soup.text
