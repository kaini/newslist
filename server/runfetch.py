"""
This script runs the newslist application using a development server.
"""
from newslist.api import create_app


if __name__ == '__main__':
    from werkzeug.serving import run_simple
    app = create_app("db.sqlite3", "http://localhost:8000")
    run_simple("0.0.0.0", 5555, app, use_debugger=True, use_reloader=True)
