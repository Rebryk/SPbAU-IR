import logging

from .parser import Parser
from pony.orm import db_session
from crawler.webpage import WebPage
from data.document import Document
import email.utils
import os


class SaverParser(Parser):
    def __init__(self, path_to_save):
        self._logger = logging.getLogger(self.__class__.__name__)
        self.path_to_save = path_to_save

        if not os.path.exists(path_to_save):
            os.makedirs(path_to_save)

    @db_session
    def parse(self, web_page: WebPage) -> bool:
        raw_text = web_page.raw_text
        page_hash = web_page.page_hash

        page_date = email.utils.parsedate_to_datetime(
            web_page.headers["last-modified"]
        ) if "last-modified" in web_page.headers else None

        file_path = os.path.join(self.path_to_save, page_hash)

        if os.path.exists(file_path):
            self._logger.warning("Duplicate page found for url: {}".format(web_page.url))
            return False

        with open(file_path, "wb") as f:
            f.write(raw_text)

        Document(url=web_page.url, file_path=file_path, document_date=page_date, document_hash=page_hash)

        self._logger.info("Saved url: {}".format(web_page.url))
        return True
