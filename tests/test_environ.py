import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
from io import TextIOBase
from tests.base import AsyncTestCase, noop_application


def environ_application(func):
    @wraps(func)
    def do_environ_application(environ, start_response):
        func(environ)
        return noop_application(environ, start_response)
    return do_environ_application


@environ_application
def assert_environ(environ):
    assert environ["REQUEST_METHOD"] == "GET"
    assert environ["SCRIPT_NAME"] == ""
    assert environ["PATH_INFO"] == "/"
    assert environ["CONTENT_TYPE"] == ""
    assert environ["CONTENT_LENGTH"] == "0"
    assert environ["SERVER_NAME"] == "127.0.0.1"
    assert int(environ["SERVER_PORT"]) > 0
    assert environ["REMOTE_ADDR"] == "127.0.0.1"
    assert environ["REMOTE_HOST"] == "127.0.0.1"
    assert int(environ["REMOTE_PORT"]) > 0
    assert environ["SERVER_PROTOCOL"] == "HTTP/1.1"
    assert environ["HTTP_FOO"] == "bar"
    assert environ["wsgi.version"] == (1, 0)
    assert environ["wsgi.url_scheme"] == "http"
    assert isinstance(environ["wsgi.errors"], TextIOBase)
    assert environ["wsgi.multithread"]
    assert not environ["wsgi.multiprocess"]
    assert not environ["wsgi.run_once"]
    assert isinstance(environ["asyncio.loop"], asyncio.BaseEventLoop)
    assert isinstance(environ["asyncio.executor"], ThreadPoolExecutor)
    assert "aiohttp.request" in environ


@environ_application
def assert_environ_post(environ):
    assert environ["REQUEST_METHOD"] == "POST"
    assert environ["CONTENT_TYPE"] == "text/plain"
    assert environ["CONTENT_LENGTH"] == "6"
    assert environ["wsgi.input"].read() == b"foobar"


@environ_application
def assert_environ_url_scheme(environ):
    assert environ["wsgi.url_scheme"] == "https"


@environ_application
def assert_environ_unix_socket(environ):
    assert environ["SERVER_NAME"] == "unix"
    assert environ["SERVER_PORT"].startswith("/")
    assert environ["REMOTE_HOST"] == "unix"
    assert environ["REMOTE_PORT"] == ""


@environ_application
def assert_environ_subdir(environ):
    assert environ["SCRIPT_NAME"] == ""
    assert environ["PATH_INFO"] == "/foo"


@environ_application
def assert_environ_subdir_quoted(environ):
    assert environ["SCRIPT_NAME"] == ""
    assert environ["PATH_INFO"] == "/foo%20"


@environ_application
def assert_environ_root_subdir(environ):
    assert environ["SCRIPT_NAME"] == "/foo"
    assert environ["PATH_INFO"] == ""


@environ_application
def assert_environ_root_subdir_slash(environ):
    assert environ["SCRIPT_NAME"] == "/foo"
    assert environ["PATH_INFO"] == "/"


@environ_application
def assert_environ_root_subdir_trailing(environ):
    assert environ["SCRIPT_NAME"] == "/foo"
    assert environ["PATH_INFO"] == "/bar"


class EnvironTest(AsyncTestCase):

    def testEnviron(self):
        with self.serve("tests.test_environ:assert_environ") as client:
            client.assert_response(headers={
                "Foo": "bar",
            })

    def testEnvironPost(self):
        with self.serve("tests.test_environ:assert_environ_post") as client:
            client.assert_response(
                method="POST",
                headers={"Content-Type": "text/plain"},
                data=b"foobar",
            )

    def testEnvironUrlScheme(self):
        with self.serve("--url-scheme", "https", "tests.test_environ:assert_environ_url_scheme") as client:
            client.assert_response()

    def testEnvironUnixSocket(self):
        with self.serve_unix("tests.test_environ:assert_environ_unix_socket") as client:
            client.assert_response()

    def testEnvironSubdir(self):
        with self.serve("tests.test_environ:assert_environ_subdir") as client:
            client.assert_response(path="/foo")

    def testEnvironSubdirQuoted(self):
        with self.serve("tests.test_environ:assert_environ_subdir_quoted") as client:
            client.assert_response(path="/foo%20")

    def testEnvironRootSubdir(self):
        with self.serve("--script-name", "/foo", "tests.test_environ:assert_environ_root_subdir") as client:
            client.assert_response(path="/foo")

    def testEnvironRootSubdirSlash(self):
        with self.serve(
            "--script-name", "/foo",
            "tests.test_environ:assert_environ_root_subdir_slash",
        ) as client:
            client.assert_response(path="/foo/")

    def testEnvironRootSubdirTrailing(self):
        with self.serve(
            "--script-name", "/foo",
            "tests.test_environ:assert_environ_root_subdir_trailing"
        ) as client:
            client.assert_response(path="/foo/bar")
