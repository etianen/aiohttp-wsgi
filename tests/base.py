import asyncio
import unittest
from functools import wraps
from concurrent.futures import ThreadPoolExecutor
from tempfile import NamedTemporaryFile
import aiohttp
from aiohttp_wsgi.api import start_server
from aiohttp_wsgi.utils import parse_sockname


def noop_application(environ, start_response):
    start_response("200 OK", [
        ("Content-Type", "text/plain"),
    ])
    return []


class TestServer:

    def __init__(self, server, loop):
        self.server = server
        # Set up client settion.
        self.host, self.port = parse_sockname(server.sockets[0].getsockname())
        if self.host == "unix":
            self.connector = aiohttp.UnixConnector(path=self.port, loop=loop)
        else:
            self.connector = aiohttp.TCPConnector(loop=loop)
        self.session = aiohttp.ClientSession(connector=self.connector, loop=loop)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc_info):
        # Clean up client session.
        self.session.close()
        self.connector.close()
        # Clean server.
        self.server.close()
        await self.server.wait_closed(shutdown_timeout=3.0)

    async def request(self, method, path, **kwargs):
        uri = "http://{}:{}{}".format(self.host, self.port, path)
        return await self.session.request(method, uri, **kwargs)


class AsyncTestCase(unittest.TestCase):

    def __init__(self, methodName):
        # Wrap method in coroutine.
        func = getattr(self, methodName)
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            def do_async_test(*args, **kwargs):
                self.loop.run_until_complete(func(*args, **kwargs))
            setattr(self, methodName, do_async_test)
        # All done!
        super().__init__(methodName)

    def setUp(self):
        super().setUp()
        self.loop = asyncio.new_event_loop()
        self.executor = ThreadPoolExecutor(2)

    def tearDown(self):
        super().tearDown()
        self.loop.close()

    async def _start_server(self, application="tests.base:noop_application", **kwargs):
        return TestServer(await start_server(
            application,
            loop=self.loop,
            executor=self.executor,
            **kwargs,
        ), self.loop)

    async def start_server(self, *args, **kwargs):
        return await self._start_server(
            *args,
            host="127.0.0.1",
            **kwargs,
        )

    async def start_unix_server(self, *args, **kwargs):
        socket_file = NamedTemporaryFile()
        socket_file.close()
        return await self._start_server(
            *args,
            unix_socket=socket_file.name,
            **kwargs,
        )

    async def assertResponse(self, server, *args, **kwargs):
        async with await server.request(*args, **kwargs) as response:
            self.assertEqual(response.status, 200)
