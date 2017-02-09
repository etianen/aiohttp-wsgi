import unittest
from collections import namedtuple
from contextlib import contextmanager
from tempfile import NamedTemporaryFile
import aiohttp
from aiohttp_wsgi.__main__ import serve
from aiohttp_wsgi.utils import parse_sockname
import asyncio


Response = namedtuple("Response", ("status", "reason", "headers", "content"))


class TestClient:

    def __init__(self, test_case, loop, host, port, session):
        self._test_case = test_case
        self._loop = loop
        self._host = host
        self._port = port
        self._session = session

    def request(self, method="GET", path="/", **kwargs):
        uri = "http://{}:{}{}".format(self._host, self._port, path)
        response = self._loop.run_until_complete(self._session.request(method, uri, **kwargs))
        try:
            return Response(
                response.status,
                response.reason,
                response.headers,
                self._loop.run_until_complete(response.read()),
            )
        finally:
            self._loop.run_until_complete(response.release())

    def assert_response(self, *args, data=b"", **kwargs):
        response = self.request(*args, data=data, **kwargs)
        self._test_case.assertEqual(response.status, 200)


def noop_application(environ, start_response):
    start_response("200 OK", [
        ("Content-Type", "text/plain"),
    ])
    return []


def echo_application(environ, start_response):
    start_response("200 OK", [
        ("Content-Type", "text/plain"),
    ])
    return [environ["wsgi.input"].read()]


def streaming_request_body():
    for _ in range(100):
        yield b"foobar"


@asyncio.coroutine
def create_client_session(connector, loop):
    return aiohttp.ClientSession(connector=connector, loop=loop)


class AsyncTestCase(unittest.TestCase):

    @contextmanager
    def _serve(self, *args):
        with serve("-q", *args) as (loop, server):
            host, port = parse_sockname(server.sockets[0].getsockname())
            if host == "unix":
                connector = aiohttp.UnixConnector(path=port, loop=loop)
            else:
                connector = aiohttp.TCPConnector(loop=loop)
            session = loop.run_until_complete(create_client_session(connector=connector, loop=loop))
            try:
                yield TestClient(self, loop, host, port, session)
            finally:
                loop.run_until_complete(session.close())
                connector.close()

    def serve(self, *args, **kwargs):
        return self._serve(
            "--host", "127.0.0.1",
            "--port", "0",
            *args,
            **kwargs
        )

    def serve_unix(self, *args, **kwargs):
        socket_file = NamedTemporaryFile()
        socket_file.close()
        return self._serve(
            "--unix-socket", socket_file.name,
            *args,
            **kwargs
        )
