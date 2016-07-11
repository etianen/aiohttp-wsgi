from functools import wraps
from tests.base import AsyncTestCase, noop_application


def environ_application(func):
    @wraps(func)
    def do_environ_application(self, environ, start_response):
        func(self, environ)
        return noop_application(environ, start_response)
    return do_environ_application


class EnvironTest(AsyncTestCase):

    @environ_application
    def assertEnviron(self, environ):
        self.assertEqual(environ["REQUEST_METHOD"], "GET")
        self.assertEqual(environ["SCRIPT_NAME"], "")
        self.assertEqual(environ["PATH_INFO"], "/")
        self.assertEqual(environ["CONTENT_TYPE"], "")
        self.assertEqual(environ["CONTENT_LENGTH"], "0")
        self.assertEqual(environ["SERVER_NAME"], "127.0.0.1")
        self.assertGreater(int(environ["SERVER_PORT"]), 0)
        self.assertEqual(environ["REMOTE_ADDR"], "127.0.0.1")
        self.assertEqual(environ["REMOTE_HOST"], "127.0.0.1")
        self.assertGreater(int(environ["REMOTE_PORT"]), 0)
        self.assertEqual(environ["SERVER_PROTOCOL"], "HTTP/1.1")
        self.assertEqual(environ["HTTP_FOO"], "bar")
        self.assertEqual(environ["wsgi.version"], (1, 0))
        self.assertEqual(environ["wsgi.url_scheme"], "http")
        self.assertTrue(hasattr(environ["wsgi.errors"], "write"))
        self.assertTrue(environ["wsgi.multithread"])
        self.assertFalse(environ["wsgi.multiprocess"])
        self.assertFalse(environ["wsgi.run_once"])
        self.assertIs(environ["asyncio.loop"], self.loop)
        self.assertIs(environ["asyncio.executor"], self.executor)

    async def testEnviron(self):
        async with self.server(self.assertEnviron) as server:
            await server.assertResponse(headers={
                "Foo": "bar",
            })

    @environ_application
    def assertEnvironPost(self, environ):
        self.assertEqual(environ["REQUEST_METHOD"], "POST")
        self.assertEqual(environ["CONTENT_TYPE"], "text/plain")
        self.assertEqual(environ["CONTENT_LENGTH"], "6")
        self.assertEqual(environ["wsgi.input"].read(), b"foobar")

    async def testEnvironPost(self):
        async with self.server(self.assertEnvironPost) as server:
            await server.assertResponse(
                method="POST",
                headers={"Content-Type": "text/plain"},
                data=b"foobar",
            )

    @environ_application
    def assertEnvironSubdir(self, environ):
        self.assertEqual(environ["SCRIPT_NAME"], "")
        self.assertEqual(environ["PATH_INFO"], "/foo")

    async def testEnvironSubdir(self):
        async with self.server(self.assertEnvironSubdir) as server:
            await server.assertResponse(path="/foo")

    @environ_application
    def assertEnvironSubdirQuoted(self, environ):
        self.assertEqual(environ["SCRIPT_NAME"], "")
        self.assertEqual(environ["PATH_INFO"], "/foo%20")

    async def testEnvironSubdirQuoted(self):
        async with self.server(self.assertEnvironSubdirQuoted) as server:
            await server.assertResponse(path="/foo%20")

    @environ_application
    def assertEnvironRootSubdir(self, environ):
        self.assertEqual(environ["SCRIPT_NAME"], "/foo")
        self.assertEqual(environ["PATH_INFO"], "")

    async def testEnvironRootSubdir(self):
        async with self.server(self.assertEnvironRootSubdir, script_name="/foo") as server:
            await server.assertResponse(path="/foo")

    @environ_application
    def assertEnvironRootSubdirSlash(self, environ):
        self.assertEqual(environ["SCRIPT_NAME"], "/foo")
        self.assertEqual(environ["PATH_INFO"], "/")

    async def testEnvironRootSubdirSlash(self):
        async with self.server(self.assertEnvironRootSubdirSlash, script_name="/foo") as server:
            await server.assertResponse(path="/foo/")

    @environ_application
    def assertEnvironRootSubdirTrailing(self, environ):
        self.assertEqual(environ["SCRIPT_NAME"], "/foo")
        self.assertEqual(environ["PATH_INFO"], "/bar")

    async def testEnvironRootSubdirTrailing(self):
        async with self.server(self.assertEnvironRootSubdirTrailing, script_name="/foo") as server:
            await server.assertResponse(path="/foo/bar")

    @environ_application
    def assertEnvironUrlScheme(self, environ):
        self.assertEqual(environ["wsgi.url_scheme"], "https")

    async def testEnvironUrlScheme(self):
        async with self.server(self.assertEnvironUrlScheme, url_scheme="https") as server:
            await server.assertResponse()
