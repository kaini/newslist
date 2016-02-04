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
    def __init__(self, master_id, base_url, name, lang):
        self.id = sha1(base_url.encode("utf-8")).hexdigest()
        self.master_id = master_id
        self.base_url = base_url
        self.name = name
        self.lang = lang

    def json_dict(self):
        return {
            "id": self.id,
            "master_id": self.master_id,
            "base_url": self.base_url,
            "name": self.name,
            "lang": self.lang,
        }


class LeMondeNewsSource(NewsSource):
    def __init__(self):
        super(LeMondeNewsSource, self).__init__(
            "lemonde",
            "http://www.lemonde.fr/",
            "LeMonde.fr",
            "fr")

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
    def __init__(self, url="http://derstandard.at/", suffix=""):
        super(DerStandardNewsSorce, self).__init__(
            "derstandard",
            url,
            "derStandard.at" + suffix,
            "de")

    def get_articles(self, source):
        soup = BeautifulSoup(source, "html5lib")
        elems = soup.find_all(True)
        links = soup.select("#mainContent h2 a, #mainContent h3 a")
        links.sort(key=elems.index)
        return [urljoin(self.base_url, link.get("href"))
                for link
                in links
                if not link.get("href").startswith("/r")]

    def get_article(self, source, url):
        soup = BeautifulSoup(source, "html5lib")

        title = soup.h1.text.strip()

        summary = soup.select_one("#content-main h2, "
                                  "div.copytext h3, "
                                  "#objectContent .copytext p") \
                      .get_text().strip()

        image = soup.select_one("#objectContent img")
        if image:
            image = urljoin(self.base_url, image.get("src"))
        else:
            image = None

        return NewsItem(title, summary, image, url)


class DiePresseNewsSource(NewsSource):
    def __init__(self):
        super(DiePresseNewsSource, self).__init__(
            "diepresse",
            "http://diepresse.com/",
            "DiePresse.com",
            "de")

    def get_articles(self, source):
        soup = BeautifulSoup(source, "html5lib")
        elems = soup.find_all(True)
        links = soup.select("#maincontent h2 a, #content h3 a")
        links.sort(key=elems.index)
        links = (urljoin(self.base_url, link.get("href"))
                 for link
                 in links)
        links = ((link[:link.find("?")] if "?" in link else link)
                 for link
                 in links)
        return list(links)

    def get_article(self, source, url):
        soup = BeautifulSoup(source, "html5lib")

        title = soup.select_one("#maincontent h1").get_text().strip()

        summary = soup.select_one(".articlelead, .diatext")
        if not summary:
            summary = soup.select(".pictext")[1]
            for child in summary.children:
                if not isinstance(child, NavigableString) and \
                   child.name == "p" and child.get_text().strip():
                    summary = child
                    break
        summary = summary.get_text().strip()

        image = soup.select_one("img.articleimg, "
                                ".gallery_preview img, "
                                ".picfield img")
        if image:
            image = urljoin(self.base_url, image.get("src"))
        else:
            image = None

        return NewsItem(title, summary, image, url)


def _make_sources():
    yield LeMondeNewsSource()
    yield DerStandardNewsSorce()
    for ressort in ("International", "Inland", "Wirtschaft", "Web", "Sport",
                    "Panorama", "Etat", "Kultur", "Wissenschaft", "Gesundheit",
                    "Bildung", "Reisen", "Lifestyle", "Familie"):
        yield DerStandardNewsSorce(url="http://derstandard.at/" + ressort,
                                   suffix=": " + ressort)
    yield DiePresseNewsSource()


NEWS_SOURCES = tuple(_make_sources())
