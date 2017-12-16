import logging

from .articleparser import ArticleParser
from crawler.webpage import WebPage
from pony.orm import db_session
from bs4 import BeautifulSoup
from text_processing import TextProcessor

import re
import dateutil.parser
import urllib.parse


class SpringerParser(ArticleParser):
    def __init__(self, text_processor: TextProcessor):
        super().__init__(text_processor)
        self._logger = logging.getLogger(self.__class__.__name__)

    # TODO: parse link.springer.com
    @db_session
    def parse(self, web_page: WebPage) -> bool:
        return self.parse_book(web_page)

    def parse_book(self, web_page: WebPage) -> bool:
        page_soup = BeautifulSoup(web_page.text, "html.parser")
        title_section = page_soup.find('div', {'class': 'product-title'})

        if not title_section:
            return False

        title = title_section.find('div', {'class': 'bibliographic-information'}).find('h1').text
        date = dateutil.parser.parse(title_section.find('div', {'class': 'copyright'}).text, fuzzy=True)
        authors_text = title_section.find('div', {'class': 'bibliographic-information'}).find('p').text.strip()

        if authors_text.startswith('Editors:'):
            author_tokens = authors_text\
                .replace('Editors:', '')\
                .replace('Editor-in-chief:', '')\
                .replace('(Ed.)', '')\
                .replace('(Eds.)', '')\
                .strip().split(',')
        elif authors_text.startswith('Authors:'):
            author_tokens = authors_text \
                .replace('Authors:', '') \
                .strip().split(',')
        else:
            print('Cannot parse: {}'.format(authors_text))
            return False

        authors = []
        for i in range(0, len(author_tokens) - 1, 2):
            authors.append(' '.join([author_tokens[i].strip(), author_tokens[i + 1].strip()]))

        link_to_pdf = ''

        about = page_soup.find('div', {'class': 'product-about'})
        if not about:
            return False
        abstract = about.find('div', {'class': 'springer-html'}).text

        self._store_parsed_article(raw_abstract=abstract,
                                   title=title,
                                   link_to_pdf=link_to_pdf,
                                   authors=authors,
                                   date=date,
                                   article_hash=web_page.page_hash)
        return True

    @staticmethod
    def _get_clean_text(soup: BeautifulSoup) -> str:
        for s in soup.find_all('span'):
            s.extract()
        return soup.text
