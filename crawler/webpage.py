import cgi
from urllib.parse import urlparse, urljoin

import requests
from bs4 import BeautifulSoup
from urltools import normalize
from hashlib import md5


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
        self.encoding = None
        self._meta_robots_tags = None

    def load(self, user_agent: str) -> bool:
        header = {"user-agent": user_agent}
        response = requests.head(self.url, headers=header)

        if not WebPage._check_response(response):
            return False

        response = requests.get(self.url, headers=header)

        if not WebPage._check_response(response):
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
    def raw_text(self):
        return self.text.encode(self.encoding)

    @property
    def page_hash(self):
        m = md5()
        m.update(self.raw_text)
        return m.hexdigest()

    @property
    def no_cache(self):
        return self.none or RobotsTag.NO_CACHE in self._meta_robots_tags

    @staticmethod
    def from_disk(url: str, file_path: str):
        with open(file_path, "r") as file:
            text = file.read()

        web_page = WebPage(url)
        web_page.text = text
        web_page.encoding = "UTF-8"

        return web_page

    @staticmethod
    def _check_response(response: requests.Response) -> bool:

        if response.is_redirect:
            return True

        if not response.ok or "content-type" not in response.headers:
            print(response.url, response.status_code, response.headers)
            return False

        # ignore extra pages
        mime_type, _ = cgi.parse_header(response.headers["content-type"])
        if mime_type not in WebPage.MIME_TYPES:
            print(response.url, mime_type)
            return False

        return True

    @staticmethod
    def _parse_meta_robots_tags(page: BeautifulSoup) -> {str}:
        meta_robots_tags = {}

        for tag in page.find_all(name="meta", attrs={"name": "ROBOTS"}):
            meta_robots_tags |= {robots_tag for robots_tag in tag.get("content").replace(" ", "").split(",")}

        return meta_robots_tags
