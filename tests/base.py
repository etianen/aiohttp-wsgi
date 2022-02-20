from asyncio.base_events import Server
import unittest
from collections import namedtuple
from contextlib import contextmanager
from tempfile import NamedTemporaryFile
from typing import Any, AsyncGenerator, ContextManager, Generator, Iterable
import aiohttp
import asyncio
from aiohttp_wsgi.wsgi import run_server, WSGIEnviron, WSGIStartResponse
from aiohttp_wsgi.utils import parse_sockname


Response = namedtuple("Response", ("status", "reason", "headers", "content"))


class TestClient:

    def __init__(
        self,
        test_case: unittest.TestCase,
        loop: asyncio.AbstractEventLoop,
        host: str,
        port: str,
        session: aiohttp.ClientSession,
    ) -> None:
        self._test_case = test_case
        self._loop = loop
        self._host = host
        self._port = port
        self._session = session

    def request(self, method: str = "GET", path: str = "/", **kwargs: Any) -> Response:
        uri = f"http://{self._host}:{self._port}{path}"
        response = self._loop.run_until_complete(self._session.request(method, uri, **kwargs))
        return Response(
            response.status,
            response.reason,
            response.headers,
            self._loop.run_until_complete(response.read()),
        )

    def assert_response(self, *args: Any, data: bytes = b"", **kwargs: Any) -> None:
        response = self.request(*args, data=data, **kwargs)
        self._test_case.assertEqual(response.status, 200)


def noop_application(environ: WSGIEnviron, start_response: WSGIStartResponse) -> Iterable[bytes]:
    start_response("200 OK", [
        ("Content-Type", "text/plain"),
    ])
    return []


def echo_application(environ: WSGIEnviron, start_response: WSGIStartResponse) -> Iterable[bytes]:
    start_response("200 OK", [
        ("Content-Type", "text/plain"),
    ])
    return [environ["wsgi.input"].read()]


async def streaming_request_body() -> AsyncGenerator:
    for _ in range(100):
        yield b"foobar"


class AsyncTestCase(unittest.TestCase):

    @contextmanager
    def _run_server(self, *args: Any, **kwargs: Any) -> Generator[TestClient, None, None]:
        with run_server(*args, **kwargs) as (loop, site):
            assert site._server is not None
            assert isinstance(site._server, Server)
            assert site._server.sockets is not None
            host, port = parse_sockname(site._server.sockets[0].getsockname())
            async def create_session() -> aiohttp.ClientSession:
                if host == "unix":
                    connector: aiohttp.BaseConnector = aiohttp.UnixConnector(path=port)
                else:
                    connector = aiohttp.TCPConnector()
                return aiohttp.ClientSession(connector=connector)
            session = loop.run_until_complete(create_session())
            try:
                yield TestClient(self, loop, host, port, session)
            finally:
                loop.run_until_complete(session.close())

    def run_server(self, *args: Any, **kwargs: Any) -> ContextManager[TestClient]:
        return self._run_server(
            *args,
            host="127.0.0.1",
            port="0",
            **kwargs,
        )

    def run_server_unix(self, *args: Any, **kwargs: Any) -> ContextManager[TestClient]:
        socket_file = NamedTemporaryFile()
        socket_file.close()
        return self._run_server(
            *args,
            unix_socket=socket_file.name,
            **kwargs
        )
