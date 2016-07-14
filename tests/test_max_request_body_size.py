from tests.base import AsyncTestCase


def streaming_body():
    for _ in range(100):
        yield b"foobar"


class MaxRequestBodySizeTest(AsyncTestCase):

    def testMaxRequestBodySize(self):
        with self.serve("--max-request-body-size", "3", "tests.base:noop_application") as client:
            response = client.request(data="foobar")
            self.assertEqual(response.status, 413)

    def testMaxRequestBodySizeStreaming(self):
        with self.serve("--max-request-body-size", "20", "tests.base:noop_application") as client:
            response = client.request(data=streaming_body())
            self.assertEqual(response.status, 413)
