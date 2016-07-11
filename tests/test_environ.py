from functools import wraps
from tests.base import AsyncTestCase


def asserts_environ(func):
    @wraps(func)
    def do_asserts_environ(self, environ, start_response):
        func(self, environ)
        start_response("200 OK", [])
        return [b""]
    return do_asserts_environ


class EnvironTest(AsyncTestCase):

    @asserts_environ
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
        self.assertEqual(environ["wsgi.url_scheme"], "http")
        self.assertTrue(hasattr(environ["wsgi.errors"], "write"))
        self.assertTrue(environ["wsgi.multithread"])
        self.assertFalse(environ["wsgi.multiprocess"])
        self.assertFalse(environ["wsgi.run_once"])
        self.assertIs(environ["asyncio.loop"], self.loop)

    async def testEnviron(self):
        async with self.server(self.assertEnviron) as server:
            await server.assertResponse()

    @asserts_environ
    def assertEnvironSubdir(self, environ):
        self.assertEqual(environ["SCRIPT_NAME"], "")
        self.assertEqual(environ["PATH_INFO"], "/foo")

    async def testEnvironSubdir(self):
        async with self.server(self.assertEnvironSubdir) as server:
            await server.assertResponse(path="/foo")


# @pytest.mark.parametrize("request_method", ["POST"])
# @server_test
# def test_request_method_post(environ):
#     self.assertEqual(environ["REQUEST_METHOD"], "POST")


# @pytest.mark.parametrize("request_path", ["/foo"])
# @server_test
# def test_path_subdir(environ):
#
#
#
#
# # https://github.com/etianen/aiohttp-wsgi/issues/5
# @pytest.mark.parametrize("request_path", ["/Test%20%C3%A1%20%C3%B3"])
# @server_test
# def test_path_quoted(environ):
#     self.assertEqual(environ["SCRIPT_NAME"], "")
#     self.assertEqual(environ["PATH_INFO"], "/Test%20%C3%A1%20%C3%B3")
#
#
# @pytest.mark.parametrize("script_name", ["/foo"])
# @pytest.mark.parametrize("request_path", ["/foo"])
# @server_test
# def test_path_root_subdir(environ):
#     self.assertEqual(environ["SCRIPT_NAME"], "/foo")
#     self.assertEqual(environ["PATH_INFO"], "")
#
#
# @pytest.mark.parametrize("script_name", ["/foo"])
# @pytest.mark.parametrize("request_path", ["/foo/"])
# @server_test
# def test_path_root_subdir_slash(environ):
#     self.assertEqual(environ["SCRIPT_NAME"], "/foo")
#     self.assertEqual(environ["PATH_INFO"], "/")
#
#
# @pytest.mark.parametrize("script_name", ["/foo"])
# @pytest.mark.parametrize("request_path", ["/foo/bar"])
# @server_test
# def test_path_root_subdir_trailing(environ):
#     self.assertEqual(environ["SCRIPT_NAME"], "/foo")
#     self.assertEqual(environ["PATH_INFO"], "/bar")
#
#
# @pytest.mark.parametrize("request_headers", [{"Content-Type": "text/plain"}])
# @server_test
# def test_content_type_set(environ):
#     self.assertEqual(environ["CONTENT_TYPE"], "text/plain")

# @pytest.mark.parametrize("request_method", ["POST"])
# @pytest.mark.parametrize("request_data", [b"foobar"])
# @server_test
# def test_content_length_post(environ):
#     self.assertEqual(environ["CONTENT_LENGTH"], "6")

#
# @server_test
# def test_wsgi_version(environ):
#     self.assertEqual(environ["wsgi.version"], (1, 0))
#
#
# @server_test
# def test_url_scheme(environ):
#
#
#
# @pytest.mark.parametrize("url_scheme", ["https"])
# @server_test
# def test_url_scheme_https(environ):
#     self.assertEqual(environ["wsgi.url_scheme"], "https")
#
#
# @pytest.mark.parametrize("request_method", ["POST"])
# @pytest.mark.parametrize("request_data", [b"foobar"])
# @server_test
# def test_wsgi_input(environ):
#     self.assertEqual(environ["wsgi.input"].read(6), b"foobar")


# @pytest.mark.parametrize("request_headers", [{"Foo": "Bar"}])
# @server_test
# def test_custom_header(environ):
#     self.assertEqual(environ["HTTP_FOO"], "Bar")
