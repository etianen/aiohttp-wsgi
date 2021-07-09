from __future__ import annotations
from typing import Iterable
from tests.base import AsyncTestCase
from aiohttp_wsgi.wsgi import WSGIEnviron, WSGIStartResponse


CHUNK = b"foobar" * 1024
CHUNK_COUNT = 64
RESPONSE_CONTENT = CHUNK * CHUNK_COUNT


def start_response_application(environ: WSGIEnviron, start_response: WSGIStartResponse) -> Iterable[bytes]:
    start_response("201 Created", [
        ("Foo", "Bar"),
        ("Foo", "Baz"),
    ])
    return [b"foobar"]


def streaming_response_application(environ: WSGIEnviron, start_response: WSGIStartResponse) -> Iterable[bytes]:
    start_response("200 OK", [])
    for _ in range(CHUNK_COUNT):
        yield CHUNK


def streaming_response_write_application(environ: WSGIEnviron, start_response: WSGIStartResponse) -> Iterable[bytes]:
    write = start_response("200 OK", [])
    for _ in range(CHUNK_COUNT):
        write(CHUNK)
    return []


class StartResponseTest(AsyncTestCase):

    def testStartResponse(self) -> None:
        with self.run_server(start_response_application) as client:
            response = client.request()
            self.assertEqual(response.status, 201)
            self.assertEqual(response.reason, "Created")
            self.assertEqual(response.headers.getall("Foo"), ["Bar", "Baz"])
            self.assertEqual(response.content, b"foobar")

    def testStreamingResponse(self) -> None:
        with self.run_server(streaming_response_application) as client:
            response = client.request()
            self.assertEqual(response.content, RESPONSE_CONTENT)

    def testStreamingResponseWrite(self) -> None:
        with self.run_server(streaming_response_write_application) as client:
            response = client.request()
            self.assertEqual(response.content, RESPONSE_CONTENT)
