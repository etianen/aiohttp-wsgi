"""
WSGI adapter for aiohttp.
"""

from aiohttp_wsgi.api import configure_server, close_server, serve  # noqa
from aiohttp_wsgi.wsgi import WSGIHandler  # noqa


__version__ = (0, 4, 0)
