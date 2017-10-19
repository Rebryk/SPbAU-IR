import argparse
import json

from crawler import Frontier, Crawler
from parser import SaverParser

parser = argparse.ArgumentParser(description="Run crawler")

if __name__ == "__main__":
    args = parser.parse_args()

    with open("config/crawler.json") as file:
        # read configuration file
        config = json.load(file)

    frontier = Frontier(urls={"https://www.palantir.com/careers/"}, allowed={"www.palantir.com"})
    parser = SaverParser("webdata")

    crawler = Crawler(user_agent=config["user_agent"],
                      frontier=frontier,
                      parser=parser,
                      max_pages_count=int(config["max_pages_count"]),
                      max_depth=int(config["max_depth"]),
                      delay=int(config["delay"]))

    crawler.start()
