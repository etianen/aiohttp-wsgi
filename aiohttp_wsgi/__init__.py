"""
WSGI adapter for aiohttp.
"""

try:
    import aiohttp  # noqa
except ImportError:
    # The top-level API requires aiohttp, which might not be present if setup.py
    # is importing aiohttp_wsgi to get __version__.
    pass
else:
    from aiohttp_wsgi.api import configure_server, close_server, serve  # noqa
    from aiohttp_wsgi.wsgi import WSGIHandler  # noqa


__version__ = (0, 4, 0)
