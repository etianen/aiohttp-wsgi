import asyncio
import unittest
from functools import wraps
from concurrent.futures import ThreadPoolExecutor
from tempfile import NamedTemporaryFile
from aiohttp_wsgi import start_server


def noop_application(environ, start_response):
    start_response("200 OK", [
        ("Content-Type", "text/plain"),
    ])
    return []


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
        self.executor = ThreadPoolExecutor(1)

    def tearDown(self):
        super().tearDown()
        self.loop.close()

    async def start_server(self, application=noop_application, **kwargs):
        return await start_server(
            application,
            host="127.0.0.1",
            loop=self.loop,
            executor=self.executor,
            **kwargs,
        )

    async def start_unix_server(self, application=noop_application, **kwargs):
        socket_file = NamedTemporaryFile()
        socket_file.close()
        return await start_server(
            application,
            unix_socket=socket_file.name,
            loop=self.loop,
            executor=self.executor,
            access_log=None,  # Access logging is broken in aiohtp for unix sockets.
            **kwargs,
        )

    async def assertResponse(self, server, *args, **kwargs):
        async with await server.request(*args, **kwargs) as response:
            self.assertEqual(response.status, 200)
