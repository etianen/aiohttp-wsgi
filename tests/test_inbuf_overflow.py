from tests.base import AsyncTestCase, streaming_request_body


class InbufOverflowTest(AsyncTestCase):

    def testInbufOverflow(self):
        with self.serve("--inbuf-overflow", "3", "tests.base:echo_application") as client:
            response = client.request(data="foobar")
            self.assertEqual(response.content, b"foobar")

    def testInbufOverflowStreaming(self):
        with self.serve("--inbuf-overflow", "20", "tests.base:echo_application") as client:
            response = client.request(data=streaming_request_body())
            self.assertEqual(response.content, b"foobar" * 100)
