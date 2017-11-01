from collections import deque
from urllib.parse import urlparse

from .website import Website
import pickle
from datetime import datetime
import glob


def parse_url(url):
    parsed_url = urlparse(url)
    return parsed_url.scheme, parsed_url.hostname


class Frontier:
    def __init__(self, urls: {str}, allowed: {str}, dump_prefix: str):
        self.allowed = list(map(lambda url: parse_url(url)[1], allowed))
        self._websites = {}
        self._queue = deque()
        self._dump_prefix = dump_prefix

        for url in urls:
            scheme, hostname = parse_url(url)
            website = self._get_website(scheme, hostname)
            website.add_url(url)

    def is_empty(self):
        self._skip_empty_websites()
        return len(self._queue) == 0

    def get_website(self) -> Website:
        if self.is_empty():
            raise RuntimeError("no websites left")

        website = self._queue.popleft()
        self._queue.append(website)

        return website

    def add_url(self, url: str, depth: int, user_agent: str):
        scheme, hostname = parse_url(url)

        # skip url if hostname is not allowed
        if hostname not in self.allowed:
            return

        website = self._get_website(scheme, hostname)

        if website.can_fetch(user_agent, url):
            website.add_url(url, depth)

    def add_urls(self, urls: {str}, depth: int, user_agent: str):
        for url in urls:
            self.add_url(url, depth, user_agent)

    @staticmethod
    def restore_from_dump(dump_prefix: str):
        dumps = glob.glob("{}*.pickle".format(dump_prefix))
        if not dumps:
            return None
        latest_dump_name = max(dumps)
        with open(latest_dump_name, 'rb') as dump:
            return pickle.load(dump)

    def dump(self):
        dump_name = datetime.now().strftime("{}_%Y_%m_%d_%H_%M_%S.pickle".format(self._dump_prefix))
        with open(dump_name, 'wb') as dump:
            dump.write(pickle.dumps(self))

    def _get_website(self, scheme: str, hostname: str) -> Website:
        website = self._websites.get(hostname)

        if website is None:
            website = Website(scheme, hostname)
            self._websites[hostname] = website
            self._queue.append(website)

        return website

    def _skip_empty_websites(self):
        while len(self._queue) and self._queue[0].is_empty():
            self._queue.popleft()
