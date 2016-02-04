import requests
import os
import traceback
import sys
import json
import pickle
from newslist.sources import NEWS_SOURCES
from PIL import Image
from io import BytesIO


class _MyJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, "json_dict"):
            return obj.json_dict()
        else:
            return super(_MyJSONEncoder, self).default(obj)


def _commit(repo, file, data):
    path = os.path.join(repo, file)
    with open(path + ".new", "wb") as fp:
        fp.write(json.dumps(data, cls=_MyJSONEncoder).encode("utf-8"))
    os.replace(path + ".new", path)


def _exists(repo, file):
    return os.path.exists(os.path.join(repo, file))


def fetch(repo):
    cache = {}
    try:
        with open(os.path.join(repo, "cache"), "rb") as fp:
            cache = pickle.load(fp)
    except Exception:
        print("No cache.")

    print(">>> Fetch into " + repo + " ...")
    for source in NEWS_SOURCES:
        fetch_source(repo, source, cache)

    _commit(repo, "sources.json", NEWS_SOURCES)

    with open(os.path.join(repo, "cache"), "wb") as fp:
        pickle.dump(cache, fp, pickle.HIGHEST_PROTOCOL)

    cleanup(repo)


def fetch_source(repo, source, cache):
    cache_key = "source-" + source.id
    if cache_key not in cache:
        cache[cache_key] = {}
    mycache = cache[cache_key]

    print(">>> Fetching " + source.id + " ...")

    article_urls = []
    try:
        print("GET INDEX " + source.base_url + " ...")
        article_urls = fetch_articles(source)
        print("\tgot " + str(len(article_urls)) + ".")
    except Exception:
        print(source.base_url, file=sys.stderr)
        traceback.print_exc()
        return

    if len(article_urls) > 20:
        article_urls = article_urls[:20]

    items = []
    for article_url in article_urls:
        try:
            if article_url not in mycache:
                print("GET ARTICLE " + article_url + " ...")
                item = fetch_article(source, article_url)
            else:
                print("[CACHED] GET ARTICLE " + article_url + " ...")
                item = mycache[article_url]
            items.append(item)

            if item.image_url:
                if not _exists(repo, item.image_hash + ".png"):
                    print("GET IMAGE " + item.image_url)
                    fetch_image(repo, item.image_url, item.image_hash)
                else:
                    print("[CACHED] GET IMAGE " + item.image_url)
        except Exception:
            print(article_url, file=sys.stderr)
            traceback.print_exc()

    _commit(repo, "source_" + source.id + ".json", items)
    cache[cache_key] = dict((i.url, i) for i in items)


def fetch_articles(source):
    r = requests.get(source.base_url)
    if r.status_code != 200:
        raise Exception("HTTP " + r.status_code)
    article_urls = source.get_articles(r.text)
    return article_urls


def fetch_article(source, article_url):
    r = requests.get(article_url)
    if r.status_code != 200:
        raise Exception("HTTP " + r.status_code)
    return source.get_article(r.text, article_url)


def fetch_image(repo, url, target):
    r = requests.get(url)
    if r.status_code != 200:
        return
    try:
        i = Image.open(BytesIO(r.content))
        i.save(os.path.join(repo, target + ".png"))
    except Exception:
        pass


def cleanup(repo):
    pass  # TODO
