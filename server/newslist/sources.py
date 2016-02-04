from bs4 import BeautifulSoup, NavigableString
from urllib.parse import urljoin
from hashlib import sha1


class NewsItem:
    def __init__(self, title, summary, image_url, url):
        self.id = sha1(url.encode("utf-8")).hexdigest()
        self.title = title
        self.summary = summary
        self.image_url = image_url
        if image_url:
            self.image_hash = sha1(image_url.encode("utf-8")).hexdigest()
        else:
            self.image_hash = None
        self.url = url

    def json_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "summary": self.summary,
            "image": self.image_hash,
            "url": self.url,
        }


class NewsSource:
    def __init__(self, id, base_url, name, lang):
        self.id = id
        self.base_url = base_url
        self.name = name
        self.lang = lang

    def json_dict(self):
        return {
            "id": self.id,
            "base_url": self.base_url,
            "name": self.name,
            "lang": self.lang,
        }


class LeMondeNewsSource(NewsSource):
    def __init__(self):
        super(LeMondeNewsSource, self).__init__("lemonde",
                                                "http://www.lemonde.fr/",
                                                "LeMonde.fr", "fr")

    def get_articles(self, source):
        soup = BeautifulSoup(source, "html5lib")
        return [urljoin(self.base_url, link.get("href"))
                for link
                in soup.select(".titres_edito a")]

    def get_article(self, source, url):
        soup = BeautifulSoup(source, "html5lib")

        title = soup.title.string
        if "|" in title:
            title = title[:title.find("|")]
        title = title.strip()

        container = soup.select_one("#articleBody, "
                                    "div.entry-content, "
                                    "div.container_18 div.grid_12, "
                                    ".content-article-body, "
                                    ".texte")
        summary = ""
        for child in container.children:
            if not isinstance(child, NavigableString) and \
               (child.name.startswith("h") or child.name == "p"):
                summary = child.get_text().strip()
                if summary and summary != "Reportage":
                    break

        image = soup.select_one("#articleBody img, "
                                ".entry-content img, "
                                ".content-article-body img, "
                                ".texte img")
        if image:
            src = image.get("src")
            if src.startswith("data:"):
                src = image.get("data-src")
            image = urljoin(self.base_url, src)
        else:
            image = None

        return NewsItem(title, summary, image, url)


class DerStandardNewsSorce(NewsSource):
    def __init__(self):
        super(DerStandardNewsSorce, self).__init__("derstandard",
                                                   "http://derstandard.at/",
                                                   "derStandard.at", "de")

    def get_articles(self, source):
        soup = BeautifulSoup(source, "html5lib")
        return [urljoin(self.base_url, link.get("href"))
                for link
                in soup.select("#mainContent h2 a, #mainContent h3 a")]

    def get_article(self, source, url):
        soup = BeautifulSoup(source, "html5lib")

        title = soup.h1.text.strip()

        summary = soup.select_one("#content-main h2, "
                                  "div.copytext h3").get_text().strip()

        image = soup.select_one("#objectContent img")
        if image:
            image = urljoin(self.base_url, image.get("src"))
        else:
            image = None

        return NewsItem(title, summary, image, url)


def _make_sources():
    yield LeMondeNewsSource()
    yield DerStandardNewsSorce()


NEWS_SOURCES = tuple(_make_sources())
