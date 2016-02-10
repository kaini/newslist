from bs4 import BeautifulSoup, NavigableString
from urllib.parse import urljoin
from hashlib import sha1
from warnings import warn


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


def _has_class(elem, class_name):
    return "class" in elem.attrs and class_name in elem.attrs["class"]


def _has_class_r(elem, class_name):
    if _has_class(elem, class_name):
        return True
    for p in elem.parents:
        if _has_class(p, class_name):
            return True
    return False


def _get_title(soup, seps=()):
    """
    soup: The tag soup
    sep: An iterable of (str, int) pairs that describe the maximum number
         of times the string until str will be removed. If the int is negative
         the removal will work from end-to-begin of the string otherwise from
         begin-to-end.
    """
    title = soup.title.get_text()
    for (sep, num) in seps:
        for i in range(abs(num)):
            if num < 0:
                index = title.rfind(sep)
                if index != -1:
                    title = title[:index]
                else:
                    break
            else:
                index = title.find(sep)
                if index != -1:
                    title = title[index + len(sep):]
                else:
                    break
    return title.strip()


def _get_summary(soup, url, candidates_selector, *, remove_if=lambda e: False):
    elems = soup.find_all(True)
    candidates = soup.select(candidates_selector)
    candidates.sort(key=elems.index)
    for candidate in candidates:
        if not remove_if(candidate):
            text = ""
            for text_piece in candidate.strings:
                text += text_piece
            text = text.strip()
            if text:
                return text
    warn("No summary found: " + url)
    return ""


def _get_image(soup, url, images_selector, *, remove_if=lambda e: False):
    elems = soup.find_all(True)
    candidates = soup.select(images_selector)
    candidates.sort(key=elems.index)
    for candidate in candidates:
        if not remove_if(candidate):
            if "data-src" in candidate.attrs:
                src = candidate.get("data-src")
            elif "srcset" in candidate.attrs:
                src = candidate.get("srcset")
            elif "src" in candidate.attrs:
                src = candidate.get("src")
            if " " in src:
                src = src[:src.find(" ")]
            if not src.startswith("data:") and not src.endswith(".gif"):
                return urljoin(url, src)
    return None


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

        title = _get_title(soup, (("|", -1),))

        summary = _get_summary(
            soup, url,
            "#articleBody h2, #articleBody p, "
            "div.entry-content > h2, div.entry-content > p, "
            ".container_18 .grid_12 > h2, .container_18 .grid_12 > p, "
            ".content-article-body h2, .content-article-body p, "
            ".texte h2, .texte p, "
            ".container-inner-texte h2, .container-inner-texte p",
            remove_if=lambda e: _has_class_r(e, "txt_gris_moyen"))

        image = _get_image(
            soup, url,
            "#articleBody img, "
            ".entry-content img, "
            ".content-article-body img, "
            ".texte img",
            remove_if=lambda e: _has_class_r(e, "wp-socializer"))

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

        title = _get_title(soup, ((" - ", -2), (" [", -1)))

        summary = _get_summary(
            soup, url,
            "#content-main h2, "
            "div.copytext h3, "
            "#objectContent .copytext p")

        if soup.select_one(".liveticker"):
            image = None
        else:
            image = _get_image(soup, url, "#objectContent img")

        return NewsItem(title, summary, image, url)


class DiePresseNewsSource(NewsSource):
    def __init__(self, ressort=None, ressort_url=None):
        id_suffix = ("-" + ressort.lower()) if ressort else ""
        url_suffix = ("home/" + (ressort_url or ressort.lower())) if ressort else ""
        name_suffix = (": " + ressort) if ressort else ""
        super(DiePresseNewsSource, self).__init__(
              "diepresse" + id_suffix, "diepresse" if ressort else None,
              "http://diepresse.com/" + url_suffix,
              "DiePresse.com" + name_suffix,
              "de-AT")

    def get_articles(self, source):
        soup = BeautifulSoup(source, "html5lib")
        elems = soup.find_all(True)
        links = soup.select("#content h2 a, #content h3 a")
        links.sort(key=elems.index)
        links = (urljoin(self.base_url, link.get("href"))
                 for link
                 in links
                 if link.get("href") != "#")
        links = ((link[:link.find("?")] if "?" in link else link)
                 for link
                 in links)
        return list(links)

    def get_article(self, source, url):
        soup = BeautifulSoup(source, "html5lib")

        title = _get_title(soup, ((" « ", -4),))

        summary = _get_summary(
            soup, url,
            ".articlelead, "
            ".diatext, "
            ".pictext p, "
            "legend, "
            "div.content")

        image = _get_image(
            soup, url,
            "img.articleimg, "
            ".gallery_preview img, "
            ".picfield img, "
            "fieldset img, "
            ".fl a > img")

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

        title = _get_title(soup, ((" - ", -2),))

        summary = _get_summary(
            soup, url,
            "#article-body > p, "
            ".app-content p, "
            ".entry-summary",
            remove_if=lambda e: _has_class_r(e, "Embed"))

        image = _get_image(
            soup, url,
            "#sitecontent img, "
            ".content .image img, "
            ".teaser-image img",
            remove_if=lambda e: _has_class_r(e, "Embed") or _has_class_r(e, "authors"))

        return NewsItem(title, summary, image, url)


class LeFigaroNewsSource(NewsSource):
    def __init__(self):
        super(LeFigaroNewsSource, self).__init__(
            "lefigaro", None,
            "http://www.lefigaro.fr/",
            "Le Figaro",
            "fr-FR")

    def get_articles(self, source):
        soup = BeautifulSoup(source, "html5lib")
        return [urljoin(self.base_url, link.get("href"))
                for link
                in soup.select(".fig-main-col h2 a")
                if not _has_class_r(link, "fig-promo")]

    def get_article(self, source, url):
        soup = BeautifulSoup(source, "html5lib")

        title = _get_title(soup, ((" - ", -2),))

        summary = _get_summary(
            soup, url,
            ".fig-main-col > p, .fig-main-col div > p, "
            ".s24-art__content > p, .s24-art__content div > p, "
            ".main-txt > p, "
            ".article-content .field-item, "
            ".fig-article-body, "
            ".vdo-clip-txt",
            remove_if=lambda e: _has_class_r(e, "fig-main-media"))

        image = _get_image(
            soup, url,
            ".fig-article-body img, "
            ".fig-main-media img, "
            ".article-img img, "
            ".main-img img, "
            "picture source, picture img, "
            ".article-content figure img")

        return NewsItem(title, summary, image, url)


def _make_sources():
    yield LeMondeNewsSource()
    yield SueddeutscheNewsSource()
    yield DiePresseNewsSource()
    yield DerStandardNewsSorce()
    yield LeFigaroNewsSource()

    #for ressort in ("International", "Inland", "Wirtschaft", "Web", "Sport",
    #                "Panorama", "Etat", "Kultur", "Wissenschaft", "Gesundheit",
    #                "Bildung", "Reisen", "Lifestyle", "Familie"):
    #    yield DerStandardNewsSorce(ressort)
    
    #for ressort in ("Politik", "Wirtschaft", ("Geld", "meingeld"), "Panorama",
    #                "Kultur", ("Tech", "techscience"), "Sport", "Motor",
    #                "Leben", "Bildung", ("Zeitreise", "zeitgeschichte"),
    #                ("Wissen", "science"), "Recht"):
    #    if isinstance(ressort, tuple):
    #        yield DiePresseNewsSource(*ressort)
    #    else:
    #        yield DiePresseNewsSource(ressort)


NEWS_SOURCES = tuple(sorted(_make_sources(), key=lambda o: o.name.lower()))
