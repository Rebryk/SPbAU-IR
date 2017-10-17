import logging

from .parser import Parser


class EmptyParser(Parser):
    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)

    def parse(self, web_page):
        self._logger.info("Parsed url: {}".format(web_page.url))
        return True
