import json

from crawler import Frontier, Crawler
from parser import SaverParser

if __name__ == "__main__":
    with open("config/crawler.json") as file:
        # read configuration file
        config = json.load(file)

    with open("config/hosts.json") as file:
        hosts = json.load(file)["hosts"]

    parser = SaverParser("webdata")

    for host in hosts:
        frontier = Frontier(urls={host}, allowed={host})
        crawler = Crawler(user_agent=config["user_agent"],
                          frontier=frontier,
                          parser=parser,
                          max_pages_count=int(config["max_pages_count"]),
                          max_depth=int(config["max_depth"]),
                          delay=int(config["delay"]))
        crawler.start()
