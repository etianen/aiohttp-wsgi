from __future__ import annotations
import sys
from typing import Iterable
from tests.base import AsyncTestCase
from aiohttp_wsgi.wsgi import WSGIEnviron, WSGIStartResponse


def error_handling_application(environ: WSGIEnviron, start_response: WSGIStartResponse) -> Iterable[bytes]:
    try:
        start_response("200 OK", [])
        raise Exception("Boom!")
    except Exception:
        start_response("509 Boom", [], sys.exc_info())  # type: ignore
        return [b"Boom!"]


class ErrorsTest(AsyncTestCase):

    def testErrorHandling(self) -> None:
        with self.run_server(error_handling_application) as client:
            response = client.request()
            self.assertEqual(response.status, 509)
            self.assertEqual(response.content, b"Boom!")
