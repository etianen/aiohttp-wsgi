import time
from tests.base import AsyncTestCase


CHUNK = b"foobar" * 1024
CHUNK_COUNT = 64
RESPONSE_TEXT = str(CHUNK * CHUNK_COUNT, "latin1")


def start_response_application(environ, start_response):
    start_response("201 Created", [
        ("Foo", "Bar"),
    ])
    return [b"foobar"]


def streaming_response_application(environ, start_response):
    start_response("200 OK", [])
    for _ in range(CHUNK_COUNT):
        yield CHUNK


def streaming_response_write_application(environ, start_response):
    write = start_response("200 OK", [])
    for _ in range(CHUNK_COUNT):
        write(CHUNK)
    return []


def outbuf_overflow_slow_application(environ, start_response):
    start_response("200 OK", [])
    for _ in range(CHUNK_COUNT // 2):
        yield CHUNK
    time.sleep(1)
    for _ in range(CHUNK_COUNT // 2):
        yield CHUNK


class StartResponseTest(AsyncTestCase):

    def testStartResponse(self):
        with self.serve("tests.test_start_response:start_response_application") as client:
            response = client.request()
            self.assertEqual(response.status, 201)
            self.assertEqual(response.reason, "Created")
            self.assertEqual(response.headers["Foo"], "Bar")
            self.assertEqual(response.text, "foobar")

    def testStreamingResponse(self):
        with self.serve("tests.test_start_response:streaming_response_application") as client:
            response = client.request()
            self.assertEqual(response.text, RESPONSE_TEXT)

    def testStreamingResponseWrite(self):
        with self.serve("tests.test_start_response:streaming_response_write_application") as client:
            response = client.request()
            self.assertEqual(response.text, RESPONSE_TEXT)

    def testOutbufOverflow(self):
        with self.serve(
            "--outbuf-overflow", str(len(CHUNK) // 2),
            "tests.test_start_response:streaming_response_application",
        ) as client:
            response = client.request()
            self.assertEqual(response.text, RESPONSE_TEXT)

    def testOutbufOverflowSlow(self):
        with self.serve(
            "--outbuf-overflow", str(len(CHUNK) // 2),
            "tests.test_start_response:outbuf_overflow_slow_application",
        ) as client:
            response = client.request()
            self.assertEqual(response.text, RESPONSE_TEXT)

    def testOutbufOverflowSlowThreadStarvation(self):
        with self.serve(
            "--threads", "1",
            "--outbuf-overflow", str(len(CHUNK) // 2),
            "tests.test_start_response:outbuf_overflow_slow_application",
        ) as client:
            response = client.request()
            self.assertEqual(response.text, RESPONSE_TEXT)
