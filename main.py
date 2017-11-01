import json

from crawler import Frontier, Crawler
from parser import SaverParser
from urllib.parse import urlparse
import os

if __name__ == "__main__":
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
