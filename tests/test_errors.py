import sys
from tests.base import AsyncTestCase


def error_handling_application(environ, start_response):
    try:
        start_response("200 OK", [])
        raise Exception("Boom!")
    except Exception:
        start_response("509 Boom", [], sys.exc_info())
        return [b"Boom!"]


class ErrorsTest(AsyncTestCase):

    def testErrorHandling(self):
        with self.run_server(error_handling_application) as client:
            response = client.request()
            self.assertEqual(response.status, 509)
            self.assertEqual(response.content, b"Boom!")
