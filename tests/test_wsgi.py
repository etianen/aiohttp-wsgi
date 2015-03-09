import sys, tempfile, os
from contextlib import closing
from unittest import TestCase

from aiohttp.connector import UnixConnector

from aiohttp_wsgi.test import run_server


class WSGITest(TestCase):

    def testApplication(self):
        def application(environ, start_response):
            start_response("200 OK", [
                ("Content-Type", "text/html; charse=utf-8"),
            ])
            return [b"Hello world"]
        with run_server(application) as client:
            with client.request("GET", "/") as response:
                self.assertEqual(response.status, 200)
                self.assertEqual(response.reason, "OK")
                self.assertEqual(response.text(), "Hello world")

    # Request meta.

    def testRequestEnviron(self):
        def application(environ, start_response):
            self.assertEqual(environ["REQUEST_METHOD"], "GET")
            self.assertEqual(environ["SCRIPT_NAME"], "")
            self.assertEqual(environ["PATH_INFO"], "/foo")
            self.assertEqual(environ["CONTENT_TYPE"], "")
            self.assertEqual(environ["CONTENT_LENGTH"], "0")
            self.assertEqual(environ["SERVER_NAME"], "127.0.0.1")
            self.assertEqual(environ["SERVER_PORT"], str(client.server_port))
            self.assertEqual(environ["REMOTE_ADDR"], "127.0.0.1")
            self.assertEqual(environ["REMOTE_HOST"], "127.0.0.1")
            self.assertNotEqual(environ["REMOTE_PORT"], str(client.server_port))
            self.assertEqual(environ["SERVER_PROTOCOL"], "HTTP/1.1")
            self.assertEqual(environ["wsgi.version"], (1, 0))
            self.assertEqual(environ["wsgi.url_scheme"], "http")
            self.assertEqual(environ["wsgi.input"].read(0), b"")
            self.assertTrue(hasattr(environ["wsgi.errors"], "write"))
            self.assertEqual(environ["wsgi.multithread"], True)
            self.assertEqual(environ["wsgi.multiprocess"], False)
            self.assertEqual(environ["wsgi.run_once"], False)
            # All done!
            start_response("200 OK", [
                ("Content-Type", "text/html; charse=utf-8"),
            ])
            return [b"Hello world"]
        with run_server(application) as client:
            with client.request("GET", "/foo?bar=baz") as response:
                self.assertEqual(response.status, 200)

    def testRequestHeaders(self):
        def application(environ, start_response):
            self.assertEqual(environ["HTTP_FOO"], "Bar")
            start_response("200 OK", [
                ("Content-Type", "text/html; charse=utf-8"),
            ])
            return [b"Hello world"]
        with run_server(application) as client:
            with client.request("GET", "/", headers={"Foo": "Bar"}) as response:
                self.assertEqual(response.status, 200)

    def testCustomScriptName(self):
        def application(environ, start_response):
            self.assertEqual(environ["SCRIPT_NAME"], "/foo")
            self.assertEqual(environ["PATH_INFO"], "/bar")
            start_response("200 OK", [
                ("Content-Type", "text/html; charse=utf-8"),
            ])
            return [b"Hello world"]
        with run_server(application, script_name="/foo") as client:
            with client.request("GET", "/foo/bar") as response:
                self.assertEqual(response.status, 200)
            with client.request("GET", "/bar") as response:
                self.assertEqual(response.status, 404)

    def testCustomUrlScheme(self):
        def application(environ, start_response):
            self.assertEqual(environ["wsgi.url_scheme"], "https")
            start_response("200 OK", [
                ("Content-Type", "text/html; charse=utf-8"),
            ])
            return [b"Hello world"]
        with run_server(application, url_scheme="https") as client:
            with client.request("GET", "/") as response:
                self.assertEqual(response.status, 200)

    # Uploads.

    def testUpload(self):
        def application(environ, start_response):
            self.assertEqual(environ["CONTENT_LENGTH"], "7")
            start_response("200 OK", [
                ("Content-Type", "text/html; charse=utf-8"),
            ])
            return [environ["wsgi.input"].read(7)]
        with run_server(application) as client:
            with client.request("POST", "/", data=b"Foo bar") as response:
                self.assertEqual(response.status, 200)
                self.assertEqual(response.text(), "Foo bar")

    # Response meta.

    def testResponseStatus(self):
        def application(environ, start_response):
            start_response("209 Foo Bar", [
                ("Content-Type", "text/html; charse=utf-8"),
            ])
            return [b"Hello world"]
        with run_server(application) as client:
            with client.request("GET", "/") as response:
                self.assertEqual(response.status, 209)
                self.assertEqual(response.reason, "Foo Bar")

    def testResponseHeaders(self):
        def application(environ, start_response):
            start_response("200 OK", [
                ("Content-Type", "text/html; charse=utf-8"),
                ("Foo", "Bar"),
            ])
            return [b"Hello world"]
        with run_server(application) as client:
            with client.request("GET", "/") as response:
                self.assertEqual(response.status, 200)
                self.assertEqual(response.headers["Foo"], "Bar")

    # Streaming responses.

    def testApplicationStreamingResponse(self):
        chunk = b"Hello world" * 1024
        chunk_count = 64
        def application(environ, start_response):
            start_response("200 OK", [
                ("Content-Type", "text/html; charse=utf-8"),
            ])
            for _ in range(chunk_count):
                yield chunk
        with run_server(application) as client:
            with client.request("GET", "/") as response:
                self.assertEqual(response.status, 200)
                self.assertEqual(response.reason, "OK")
                self.assertEqual(response.read(), chunk * chunk_count)

    def testApplicationSyncStreamingResponse(self):
        chunk = b"Hello world" * 1024
        chunk_count = 64
        def application(environ, start_response):
            write = start_response("200 OK", [
                ("Content-Type", "text/html; charse=utf-8"),
            ])
            for _ in range(chunk_count):
                write(chunk)
            return []
        with run_server(application) as client:
            with client.request("GET", "/") as response:
                self.assertEqual(response.status, 200)
                self.assertEqual(response.reason, "OK")
                self.assertEqual(response.read(), chunk * chunk_count)

    # Application error handling.

    def testApplicationErrorHandling(self):
        def application(environ, start_response):
            try:
                start_response("200 OK", [
                    ("Content-Type", "text/html; charse=utf-8"),
                ])
                raise Exception("Boom!")
            except:
                start_response("509 Boom", [
                    ("Content-Type", "text/html; charse=utf-8"),
                ], sys.exc_info())
                return [b"Boom!"]
        with run_server(application) as client:
            with client.request("GET", "/") as response:
                self.assertEqual(response.status, 509)
                self.assertEqual(response.text(), "Boom!")

    # Unexpected application behavior.

    def testApplicationDidNotCallStartResponse(self):
        def application(environ, start_response):
            return [b"Hello world"]
        with run_server(application) as client:
            with client.request("GET", "/") as response:
                self.assertEqual(response.status, 500)

    def testApplicationCalledStartResponseTwice(self):
        def application(environ, start_response):
            start_response("200 OK", [
                ("Content-Type", "text/html; charse=utf-8"),
            ])
            start_response("200 OK", [
                ("Content-Type", "text/html; charse=utf-8"),
            ])
        with run_server(application) as client:
            with client.request("GET", "/") as response:
                self.assertEqual(response.status, 500)

    def testApplicationErrorAfterResponseWrite(self):
        def application(environ, start_response):
            try:
                start_response("200 OK", [
                    ("Content-Type", "text/html; charse=utf-8"),
                ])
                raise Exception("Boom!")
            except:
                write = start_response("509 Boom", [
                    ("Content-Type", "text/html; charse=utf-8"),
                ], sys.exc_info())
                write(b"Boom!")
                try:
                    raise Exception("Boom!!")
                except:
                    start_response("510 Boom", [
                        ("Content-Type", "text/html; charse=utf-8"),
                    ], sys.exc_info())
        with run_server(application) as client:
            with client.request("GET", "/") as response:
                self.assertEqual(response.status, 509)

    # Unix sockets.

    def testUnixSocket(self):
        def application(environ, start_response):
            # Check connection meta.
            self.assertEqual(environ["SERVER_NAME"], "unix")
            self.assertEqual(environ["SERVER_PORT"], unix_socket)
            self.assertEqual(environ["REMOTE_ADDR"], "unix")
            self.assertEqual(environ["REMOTE_PORT"], "")
            # All done!
            start_response("200 OK", [
                ("Content-Type", "text/html; charse=utf-8"),
            ])
            return [b"Hello world"]
        # Create a temp path.
        with closing(tempfile.NamedTemporaryFile()) as handle:
            unix_socket = handle.name
        with run_server(application, unix_socket=unix_socket) as client:
            with client.raw_request("GET", "http://127.0.0.1:8080", connector=UnixConnector(unix_socket)) as response:
                self.assertEqual(response.status, 200)

    # Static files.

    def testStatic(self):
        def application(environ, start_response):
            start_response("200 OK", [
                ("Content-Type", "text/html; charse=utf-8"),
            ])
            return [b"Hello world"]
        with run_server(application, static={"/static": os.path.join(os.path.dirname(__file__), "static")}) as client:
            with client.request("GET", "/") as response:
                self.assertEqual(response.status, 200)
                self.assertEqual(response.text(), "Hello world")
            with client.request("GET", "/static/test.txt") as response:
                self.assertEqual(response.status, 200)
                self.assertEqual(response.text(), "Test file")
            with client.request("GET", "/static/missing.txt") as response:
                self.assertEqual(response.status, 404)
