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
    def __init__(self, id, parent_id, base_url, name, lang):
        self.id = id
        self.parent_id = parent_id
        self.base_url = base_url
        self.name = name
        self.lang = lang

    def json_dict(self):
        return {
            "id": self.id,
            "parent_id": self.parent_id,
            "base_url": self.base_url,
            "name": self.name,
            "lang": self.lang,
        }


class LeMondeNewsSource(NewsSource):
    def __init__(self):
        super(LeMondeNewsSource, self).__init__(
            "lemonde", None,
            "http://www.lemonde.fr/",
            "LeMonde.fr",
            "fr-FR")

    def get_articles(self, source):
        soup = BeautifulSoup(source, "html5lib")
        titles = soup.select(".titres_edito a h1, "
                             ".titres_edito a h2, "
                             ".titres_edito a h3, "
                             ".titres_liste a h1, "
                             ".titres_liste a h2, "
                             ".titres_liste a h3")
        links = []
        for title in titles:
            for parent in title.parents:
                if parent.name == "a":
                    links.append(parent)
                    break
        return [urljoin(self.base_url, link.get("href"))
                for link
                in links]

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
               (child.name.startswith("h") or child.name == "p") and \
               ("class" not in child.attrs or "txt_gris_moyen" not in child.attrs["class"]):
                summary = child.get_text().strip()
                if summary and summary not in ("Reportage", "En images"):
                    break

        image = soup.select_one("#articleBody img, "
                                ".entry-content img, "
                                ".content-article-body img, "
                                ".texte img")
        if image:
            has_bad_parent = False
            for parent in image.parents:
                has_bad_parent = ("class" in parent.attrs and
                                  "wp-socializer" in parent["class"])
                if has_bad_parent:
                    break
            
            if has_bad_parent:
                image = None
            else:
                src = image.get("src")
                if src.startswith("data:"):
                    src = image.get("data-src")
                image = urljoin(url, src)
        else:
            image = None

        return NewsItem(title, summary, image, url)


class DerStandardNewsSorce(NewsSource):
    def __init__(self, ressort=None):
        id_suffix = ("-" + ressort.lower()) if ressort else ""
        url_suffix = ressort or ""
        name_suffix = (": " + ressort) if ressort else ""
        super(DerStandardNewsSorce, self).__init__(
            "derstandard" + id_suffix, "derstandard" if ressort else None,
            "http://derstandard.at/" + url_suffix,
            "derStandard.at" + name_suffix,
            "de-AT")

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

        if soup.select_one(".liveticker"):
            image = None
        else:
            image = soup.select_one("#objectContent img")
            if image:
                image = urljoin(url, image.get("src"))
            else:
                image = None

        return NewsItem(title, summary, image, url)


class DiePresseNewsSource(NewsSource):
    def __init__(self):
        super(DiePresseNewsSource, self).__init__(
            "diepresse", None,
            "http://diepresse.com/",
            "DiePresse.com",
            "de-AT")

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

        title = soup.select_one("#maincontent h1, "
                                "h1.hed").get_text().strip()

        summary = soup.select_one(".articlelead, .diatext")
        if not summary:
            summary = soup.select(".pictext p")
            for elem in summary:
                if elem.get_text().strip():
                    summary = elem
                    break
        summary = summary.get_text().strip()

        image = soup.select_one("img.articleimg, "
                                ".gallery_preview img, "
                                ".picfield img")
        if image:
            image = urljoin(url, image.get("src"))
        else:
            image = None

        return NewsItem(title, summary, image, url)


class SueddeutscheNewsSource(NewsSource):
    def __init__(self):
        super(SueddeutscheNewsSource, self).__init__(
            "sueddeutsche", None,
            "http://www.sueddeutsche.de/",
            "Süddeutsche Zeitung",
            "de-DE")

    def get_articles(self, source):
        soup = BeautifulSoup(source, "html5lib")
        return [urljoin(self.base_url, link.get("href"))
                for link
                in soup.select("#sitecontent a.entry-title")
                if not link.get("href").endswith("/Ihr_Forum") and
                   "//www.sueddeutsche.de/" in link.get("href")]

    def get_article(self, source, url):
        soup = BeautifulSoup(source, "html5lib")

        title = soup.select_one("h2, span.app-type").get_text().strip()
        prefix = soup.select_one("h2 strong")
        if prefix:
            prefix = prefix.get_text().strip()
        else:
            prefix = ""
        title = title[len(prefix):].strip()

        summary = soup.select_one("#article-body > p, "
                                  ".app-content p, "
                                  ".entry-summary")
        summary = summary.get_text().strip()

        image = soup.select_one("#sitecontent img, "
                                ".content .image img, "
                                ".teaser-image img")
        if image:
            if "data-src" in image.attrs:
                image.attrs["src"] = image.attrs["data-src"]
            image = urljoin(url, image.get("src"))
        else:
            image = None

        return NewsItem(title, summary, image, url)


def _make_sources():
    yield LeMondeNewsSource()
    yield DerStandardNewsSorce()
    for ressort in ("International", "Inland", "Wirtschaft", "Web", "Sport",
                    "Panorama", "Etat", "Kultur", "Wissenschaft", "Gesundheit",
                    "Bildung", "Reisen", "Lifestyle", "Familie"):
        yield DerStandardNewsSorce(ressort)
    yield DiePresseNewsSource()
    yield SueddeutscheNewsSource()


NEWS_SOURCES = tuple(_make_sources())
