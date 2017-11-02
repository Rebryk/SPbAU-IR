import json

from crawler import Frontier, Crawler, WebPage
from parser import SaverParser, ArxivParser
from urllib.parse import urlparse
from text_processing import TextProcessor
from data import Document
from pony.orm import db_session, commit

import argparse
import os


def start_crawlers():
    with open("config/crawler.json") as file:
        # read configuration file
        config = json.load(file)

    with open("config/hosts.json") as file:
        hosts = json.load(file)["hosts"]

    parser = SaverParser("webdata")

    for host in hosts:
        if not os.path.exists("dumps"):
            os.mkdir("dumps")

        dump_prefix = "dumps/" + urlparse(host)[1]
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
    arxivParser = ArxivParser(TextProcessor())

    for document in Document.select(lambda doc: not doc.is_processed):
        if "arxiv.org" in urlparse(document.url)[1]:
            parsed = arxivParser.parse(WebPage.from_disk(document.url, document.file_path))
            if parsed:
                print("Article: " + document.url)
            else:
                print(document.url)
            document.is_processed = True
            commit()


parser = argparse.ArgumentParser(description="Information Retrieval")
parser.add_argument('mode', choices=['crawler', 'parser'])

if __name__ == "__main__":
    args = parser.parse_args()
    if args.mode == 'crawler':
        start_crawlers()
    elif args.mode == 'parser':
        parse_documents()
