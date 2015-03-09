import asyncio, warnings
from contextlib import contextmanager, closing
from functools import wraps
from wsgiref.validate import validator

import aiohttp

from aiohttp_wsgi.api import configure_server, close_server


@contextmanager
def asyncio_debug(*, loop=None):
    loop = loop or asyncio.get_event_loop()
    # Enable resource warnings.
    with warnings.catch_warnings():
        warnings.simplefilter("error", ResourceWarning)
        # Set debug mode for loop.
        is_debug = loop.get_debug()
        try:
            loop.set_debug(True)
            yield
        finally:
            loop.set_debug(is_debug)


@contextmanager
def debug_loop():
    existing_loop = asyncio.get_event_loop()
    with closing(asyncio.new_event_loop()) as loop:
        asyncio.set_event_loop(loop)
        try:
            with asyncio_debug(loop=loop):
                yield loop
        finally:
            asyncio.set_event_loop(existing_loop)


@contextmanager
def run_server(application, *, validate=True, **kwargs):
    with debug_loop() as loop:
        # Add a WSGI validator.
        if validate:
            application = validator(application)
        # Configure the server.
        server_config = {
            "host": "127.0.0.1",
            "port": 0,
            "loop": loop,
        }
        server_config.update(**kwargs)
        # Create the server.
        server, app = configure_server(application, **server_config)
        server_port = server.sockets[0].getsockname()[1]
        try:
            yield TestClient(server, app, server_port, loop=loop)
        finally:
            close_server(server, app, loop=loop)


class TestClient:

    def __init__(self, server, app, server_port, *, loop):
        self._server = server
        self._app = app
        self.server_port = server_port
        self._loop = loop

    @contextmanager
    def raw_request(self, *args, **kwargs):
        response = self._loop.run_until_complete(aiohttp.request(*args, loop=self._loop, **kwargs))
        try:
            yield SyncWrapper(response, loop=self._loop)
        finally:
            response.close()
            self._loop.run_until_complete(response.wait_for_close())

    def request(self, method, path, **kwargs):
        return self.raw_request(
            method,
            "http://127.0.0.1:{}{}".format(self.server_port, path),
            **kwargs
        )


class SyncWrapper:

    def __init__(self, wrapped, *, loop):
        self._wrapped = wrapped
        self._loop = loop or asyncio.get_event_loop()

    def __getattr__(self, name):
        value = getattr(self._wrapped, name)
        if asyncio.iscoroutinefunction(value):
            @wraps(value)
            def sync_wrapper(*args, **kwargs):
                return self._loop.run_until_complete(value(*args, **kwargs))
            return sync_wrapper
        return value
