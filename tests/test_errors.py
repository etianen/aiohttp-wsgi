import sys
from aiohttp.errors import TransferEncodingError
from tests.base import AsyncTestCase


def error_handling_application(environ, start_response):
    try:
        start_response("200 OK", [])
        raise Exception("Boom!")
    except:
        start_response("509 Boom", [], sys.exc_info())
        return [b"Boom!"]


def no_start_response_application(environ, start_response):
    return []


def start_response_twice_application(environ, start_response):
    start_response("200 OK", [
        ("Content-Type", "text/html; charse=utf-8"),
    ])
    start_response("200 OK", [
        ("Content-Type", "text/html; charse=utf-8"),
    ])


def error_after_write_application(environ, start_response):
    try:
        start_response("200 OK", [])
        raise Exception("Boom!")
    except:
        write = start_response("509 Boom", [], sys.exc_info())
        write(b"Boom!")
        try:
            raise Exception("Boom!!")
        except:
            start_response("510 Boom", [], sys.exc_info())


class ErrorsTest(AsyncTestCase):

    def testErrorHandling(self):
        with self.serve("tests.test_errors:error_handling_application") as client:
            with self.assertLogs("aiohttp.web", "ERROR"):
                response = client.request()
                self.assertEqual(response.status, 509)
                self.assertEqual(response.text, "Boom!")

    def testNoStartResponse(self):
        with self.serve("tests.test_errors:no_start_response_application") as client:
            with self.assertLogs("aiohttp.web", "ERROR"):
                response = client.request()
                self.assertEqual(response.status, 500)

    def testStartResponseTwice(self):
        with self.serve("tests.test_errors:start_response_twice_application") as client:
            with self.assertLogs("aiohttp.web", "ERROR"):
                response = client.request()
                self.assertEqual(response.status, 500)

    def testErrorAfterWrite(self):
        with self.assertLogs("aiohttp.web", "ERROR"):
            with self.serve("tests.test_errors:error_after_write_application") as client:
                with self.assertRaises(TransferEncodingError):
                    client.request()
