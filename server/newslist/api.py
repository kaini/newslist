"""
Routes and views for the flask application.
"""
import json
import inspect
import sqlite3
from newslist.sources import NEWS_SOURCES
from newslist import database
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound


class MyJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, "json_dict"):
            return obj.json_dict()
        else:
            return super(MyJSONEncoder, self).default(obj)


class API:
    def __init__(self, db_path, origin):
        self.db_path = db_path
        self.origin = origin
        self.url_map = Map([
            Rule("/sources/", endpoint=API.on_sources),
            Rule("/sources/<source_id>/items/", endpoint=API.on_sources_items),
            Rule("/sources/<source_id>/errors/", endpoint=API.on_sources_errors),
        ])

    def on_sources(self):
        return tuple(NEWS_SOURCES.values())

    def on_sources_items(self, db, source_id):
        if source_id not in NEWS_SOURCES:
            raise NotFound()
        items, lu = database.items(db, self.db_path, NEWS_SOURCES[source_id])
        return {
            "items": items,
            "last_update": lu.isoformat(),
        }

    def on_sources_errors(self, db, source_id):
        if source_id not in NEWS_SOURCES:
            raise NotFound()
        errors = database.errors(db, NEWS_SOURCES[source_id])
        return errors

    def dispatch_request(self, request):
        adapter = self.url_map.bind_to_environ(request.environ)
        db = None
        try:
            endpoint, values = adapter.match()
            sig = inspect.signature(endpoint)
            if "request" in sig.parameters and "request" not in values:
                values["request"] = request
            if "db" in sig.parameters and "db" not in values:
                db = sqlite3.connect(self.db_path)
                values["db"] = db
            result = endpoint(self, **values)
            if db:
                db.commit()
            return result
        except HTTPException as e:
            return e
        finally:
            if db:
                db.rollback()
                db.close()

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        result = self.dispatch_request(request)
        if isinstance(result, HTTPException):
            response = result
        else:
            response = Response(json.dumps(result, cls=MyJSONEncoder),
                                mimetype="application/json")
            response.headers.add("Access-Control-Allow-Origin", self.origin)
            response.headers.add("Access-Control-Allow-Methods",
                                 "GET,HEAD,OPTIONS")

        return response(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)


def create_app(db_path, origin):
    app = API(db_path, origin)
    database.init(db_path)
    return app
