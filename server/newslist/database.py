import sqlite3
import requests
import fcntl
import threading
import io
import dateutil.parser
from datetime import datetime, timedelta
from newslist.sources import NewsItem


DB_VERSION = 3
UPDATE_INTERVAL = timedelta(minutes=10)


def init(path):
    conn = sqlite3.connect(path)
    try:
        c = conn.cursor()

        try:
            c.execute("""select * from "version";""")
            if c.fetchone() == (DB_VERSION,):
                print("Database is already initialized.")
                return
            else:
                print("You have to delete the database.")
                raise Exception("You have to delete the database.")
        except sqlite3.Error:
            pass
        print("Initializing database.")

        c.execute("""create table "items" (
                         "id" varchar primary key,
                         "source_id" varchar,
                         "title" varchar,
                         "summary" varchar,
                         "image" varchar,
                         "url" varchar
                     );""")
        c.execute("""create table "errors" (
                         "id" integer primary key,
                         "source_id" varchar,
                         "url" varchar,
                         "error" varchar
                     );""")
        c.execute("""create table "last_updates" (
                         "source_id" varchar primary key,
                         "time" timestamp
                     );""")
        c.execute("""create table "version" (
                         "version" integer primary key
                     );""")
        c.execute("""insert into "version" values (?);""", (DB_VERSION,))
        conn.commit()
    finally:
        conn.rollback()
        conn.close()


def _fetch_items_background(db_path, source):
    def run():
        lockfile = "/tmp/newslist-lock-" + source.id
        handle = None
        db = None
        try:
            # Check for lock
            handle = open(lockfile, "w")
            error = fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            if error:
                print("Someone already refreshes " + source + ".")
                return

            # Results
            items = []
            errors = {}

            # Get item urls
            try:
                print("GET " + source.base_url)
                r = requests.get(source.base_url)
                if r.status_code != 200:
                    raise Exception("HTTP " + r.status_code)
                article_urls = source.get_articles(r.text)
            except Exception as ex:
                errors[source.base_url] = str(ex)
                article_urls = []

            # Get items
            for url in article_urls:
                try:
                    print("GET " + url)
                    r = requests.get(url)
                    if r.status_code != 200:
                        raise Exception("HTTP " + r.status_code)
                    items.append(source.get_article(r.text, url))
                except Exception as ex:
                    errors[url] = str(ex)

            # Write results
            db = sqlite3.connect(db_path)
            c = db.cursor()
            c.execute("""delete from "items" where "source_id"=?;""",
                      (source.id,))
            c.execute("""delete from "errors" where "source_id"=?;""",
                      (source.id,))
            c.execute("""delete from "last_updates" where "source_id"=?;""",
                      (source.id,))
            for item in items:
                c.execute("""insert into "items" values (?,?,?,?,?,?);""",
                          (item.id, source.id, item.title, item.summary,
                           item.image, item.url))
            for url, error in errors.items():
                c.execute("""insert into "errors" values (?,?,?,?);""",
                          (None, source.id, url, error))
            c.execute("""insert into "last_updates" values (?,?);""",
                      (source.id, datetime.utcnow().isoformat()))
            db.commit()
        except io.BlockingIOError as ex:
            pass
        finally:
            if handle:
                fcntl.flock(handle, fcntl.LOCK_UN)
                handle.close()
            if db:
                db.rollback()
                db.close()

    t = threading.Thread(target=run)
    t.start()


def items(db, db_path, source):
    c = db.cursor()

    c.execute("""select * from "last_updates" where "source_id" = ?;""",
              (source.id,))
    last_update = c.fetchone()
    if last_update:
        last_update = dateutil.parser.parse(last_update[1])
    else:
        last_update = datetime.fromtimestamp(0)
    if datetime.utcnow() - last_update >= UPDATE_INTERVAL:
        _fetch_items_background(db_path, source)

    c.execute("""select "id", "title", "summary", "image", "url"
                 from "items"
                 where "source_id" = ?;""",
              (source.id,))
    items = []
    for row in c:
        items.append(NewsItem(*row))

    return items, last_update


def errors(db, source):
    c = db.cursor()

    c.execute("""select "url", "error"
                 from "errors"
                 where "source_id" = ?;""",
              (source.id,))
    return dict(c)
