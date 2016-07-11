import asyncio
import unittest
from functools import wraps
import aiohttp
from aiohttp import web
from aiohttp_wsgi import WSGIHandler


class Request:

    def __init__(self, server, *, method="GET", path="/", headers=None, data=b''):
        self.server = server
        self.method = method
        self.path = path
        self.headers = headers or {}
        self.data = data

    async def __aenter__(self):
        uri = "http://127.0.0.1:{}{}".format(self.server.server.sockets[0].getsockname()[1], self.path)
        self.response = await self.server.session.request(self.method, uri, headers=self.headers, data=self.data)
        return self.response

    async def __aexit__(self, *exc_info):
        self.response.close()
        await self.response.wait_for_close()


class TestServer:

    def __init__(self, test_case, application, *, loop, **kwargs):
        self.test_case = test_case
        self.application = application
        self.loop = loop
        self.kwargs = kwargs

    async def __aenter__(self):
        wsgi_handler = WSGIHandler(self.application, loop=self.loop, **self.kwargs)
        self.app = web.Application(loop=self.loop)
        self.app.router.add_route("*", "/{path_info:.*}", wsgi_handler)
        self.handler = self.app.make_handler()
        self.server = await self.loop.create_server(self.handler, "127.0.0.1", 0)
        self.session = aiohttp.ClientSession(loop=self.loop)
        return self

    async def __aexit__(self, *exc_info):
        await self.session.close()
        self.server.close()
        await self.server.wait_closed()
        await self.app.shutdown()
        await self.handler.finish_connections(5)
        await self.app.cleanup()

    def request(self, **kwargs):
        return Request(self, **kwargs)

    async def assertResponse(self, **kwargs):
        async with self.request(**kwargs) as response:
            self.test_case.assertEqual(response.status, 200)


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
        self.addCleanup(self.loop.close)

    def server(self, application, **kwargs):
        return TestServer(self, application, loop=self.loop, **kwargs)
