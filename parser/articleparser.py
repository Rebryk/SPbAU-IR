import logging

from .parser import Parser
from pony.orm import db_session
from data import Article, Author, Document
from text_processing import TextProcessor

import json
import datetime
import os
from typing import Optional


class ArticleParser(Parser):
    def __init__(self, text_processor: TextProcessor):
        self._text_processor = text_processor

        with open("config/parser.json") as file:
            config = json.load(file)
            self._path_to_raw_abstract = config["path_to_raw_abstract"]
            self._path_to_processed_abstract = config["path_to_processed_abstract"]

            if not os.path.exists(self._path_to_raw_abstract):
                os.mkdir(self._path_to_raw_abstract)
            if not os.path.exists(self._path_to_processed_abstract):
                os.mkdir(self._path_to_processed_abstract)

    @db_session
    def _store_parsed_article(self,
                              raw_abstract: str,
                              title: str,
                              link_to_pdf: Optional[str],
                              authors: [str],
                              date: datetime.datetime,
                              article_hash: str):
        raw_abstract_path = os.path.join(self._path_to_raw_abstract, article_hash)

        with open(raw_abstract_path, "w") as file:
            file.write(raw_abstract)

        processed_abstract = self._text_processor.process(raw_abstract)
        processed_abstract_path = os.path.join(self._path_to_processed_abstract, article_hash)

        with open(processed_abstract_path, "w") as file:
            file.write(" ".join(processed_abstract))

        domain_authors = set(map(lambda a: Author(name=a), authors))
        article = Article(document=Document.get(document_hash=article_hash),
                          title=title,
                          abstract_path=raw_abstract_path,
                          processed_abstract_path=processed_abstract_path,
                          words_count=len(processed_abstract),
                          link_to_pdf=link_to_pdf,
                          authors=domain_authors,
                          date=date)
