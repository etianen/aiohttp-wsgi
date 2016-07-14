from tests.base import AsyncTestCase


def infinite_body():
    for _ in range(100):
        yield b"foobar"


class InbufOverflowTest(AsyncTestCase):

    def testInbufOverflow(self):
        with self.serve("--inbuf-overflow", "3", "tests.base:noop_application") as client:
            client.assert_response(data="foobar")

    def testInbufOverflowStreaming(self):
        with self.serve("--inbuf-overflow", "20", "tests.base:noop_application") as client:
            client.assert_response(data=infinite_body())
