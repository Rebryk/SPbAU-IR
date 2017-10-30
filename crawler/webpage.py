import cgi
from urllib.parse import urlparse, urljoin

import requests
from bs4 import BeautifulSoup
from urltools import normalize


class RobotsTag:
    NONE = "NONE"
    NO_INDEX = "NOINDEX"
    NO_FOLLOW = "NOFOLLOW"
    NO_ARCHIVE = "NOARCHIEVE"
    NO_CACHE = "NOCACHE"


def is_absolute_url(url):
    """Check that url is absolute"""

    return bool(urlparse(url).netloc)


def get_absolute_url(base, url):
    """Return absolute url"""

    return url if is_absolute_url(url) else urljoin(base, url)


class WebPage:
    MIME_TYPES = ["text/html", "application/x-eprint"]

    def __init__(self, url: str):
        self.url = url
        self.text = None
        self.headers = None
        self._page = None
        self.page_encoding = None
        self._meta_robots_tags = None

    def load(self, user_agent: str) -> bool:
        header = {"user-agent": user_agent}
        response = requests.head(self.url, headers=header)

        if not response.ok or "content-type" not in response.headers:
            return False

        # ignore extra pages
        mimetype, _ = cgi.parse_header(response.headers["content-type"])
        if mimetype not in WebPage.MIME_TYPES:
            print(mimetype, response.headers["content-type"])
            return False

        response = requests.get(self.url, headers=header)

        if not response.ok:
            return False

        self.text = response.text
        self.encoding = response.encoding
        self.headers = response.headers
        self._page = BeautifulSoup(response.text, "html.parser")
        self._meta_robots_tags = WebPage._parse_meta_robots_tags(self._page)
        return True

    def get_urls(self):
        return {normalize(get_absolute_url(self.url, link.get("href"))) for link in self._page.find_all(name="a")}

    @property
    def none(self):
        return RobotsTag.NONE in self._meta_robots_tags

    @property
    def no_index(self):
        return self.none or RobotsTag.NO_INDEX in self._meta_robots_tags

    @property
    def no_follow(self):
        return self.none or RobotsTag.NO_FOLLOW in self._meta_robots_tags

    @property
    def no_archive(self):
        return self.none or RobotsTag.NO_ARCHIVE in self._meta_robots_tags

    @property
    def no_cache(self):
        return self.none or RobotsTag.NO_CACHE in self._meta_robots_tags

    @staticmethod
    def _parse_meta_robots_tags(page: BeautifulSoup) -> {str}:
        meta_robots_tags = {}

        for tag in page.find_all(name="meta", attrs={"name": "ROBOTS"}):
            meta_robots_tags |= {robots_tag for robots_tag in tag.get("content").replace(" ", "").split(",")}

        return meta_robots_tags
