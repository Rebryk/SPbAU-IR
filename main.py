import json
import logging

from crawler import Frontier, Crawler, WebPage
from parser import SaverParser, ArxivParser, SpringerParser
from urllib.parse import urlparse
from text_processing import TextProcessor
from data import Document, Article
from pony.orm import db_session, commit, select
from index import InvertedIndex, IndexBuilder

import argparse
import os

INDEX_FOLDER = "index"
CRAWLER_CONFIG = "config/crawler.json"
HOSTS_CONFIG = "config/hosts.json"
DUMP_FOLDER = "dumps"

logger = logging.getLogger(__name__)


def start_crawlers():
    with open(CRAWLER_CONFIG) as file:
        # read configuration file
        config = json.load(file)

    with open(HOSTS_CONFIG) as file:
        hosts = json.load(file)["hosts"]

    parser = SaverParser("webdata")

    for host in hosts:
        if not os.path.exists(DUMP_FOLDER):
            os.mkdir(DUMP_FOLDER)

        dump_prefix = DUMP_FOLDER + "/" + urlparse(host)[1]
        frontier = Frontier.restore_from_dump(dump_prefix)

        if not frontier:
            frontier = Frontier(urls={host}, allowed={host}, dump_prefix=dump_prefix)

        crawler = Crawler(user_agent=config["user_agent"],
                          frontier=frontier,
                          parser=parser,
                          max_pages_count=int(config["max_pages_count"]),
                          max_depth=int(config["max_depth"]),
                          delay_ms=int(config["delay_ms"]),
                          frontier_dump_delay_s=config["frontier_dump_delay_s"])
        crawler.start()


@db_session
def parse_documents():
    arxiv_parser = ArxivParser(TextProcessor())
    springer_parser = SpringerParser(TextProcessor())
    for document in Document.select(lambda doc: not doc.is_processed):
        if "arxiv.org" in urlparse(document.url)[1]:
            cur_parser = arxiv_parser
        elif "springer.com" in urlparse(document.url)[1]:
            cur_parser = springer_parser
        else:
            print(document.url)
            continue
        page = WebPage.from_disk(document.url, document.file_path)
        parsed = cur_parser.parse(page)
        document.is_processed = True
        commit()

        print(("Article: {}" if parsed else "{}").format(document.url))


@db_session
def build_index():
    if not os.path.exists(INDEX_FOLDER):
        os.mkdir(INDEX_FOLDER)

    index = InvertedIndex.load(INDEX_FOLDER, InvertedIndex.NAME)

    if index:
        logging.debug("Index is successfully loaded")
        return

    logging.debug("Building index...")
    articles = select(article.id for article in Article)[:]
    index = InvertedIndex()
    IndexBuilder().build(index, articles)

    logging.debug("Saving index...")
    index.save(INDEX_FOLDER)


def run_web():
    from web import app
    app.run(host="127.0.0.1")


parser = argparse.ArgumentParser(description="Information Retrieval")
parser.add_argument("mode", choices=["crawler", "parser", "index", "web"])

if __name__ == "__main__":
    args = parser.parse_args()
    if args.mode == "crawler":
        start_crawlers()
    elif args.mode == "parser":
        parse_documents()
    elif args.mode == "index":
        build_index()
    elif args.mode == "web":
        run_web()
