from tests.base import AsyncTestCase, streaming_request_body, echo_application


class InbufOverflowTest(AsyncTestCase):

    def testInbufOverflow(self):
        with self.run_server(echo_application, inbuf_overflow=3) as client:
            response = client.request(data="foobar")
            self.assertEqual(response.content, b"foobar")

    def testInbufOverflowStreaming(self):
        with self.run_server(echo_application, inbuf_overflow=20) as client:
            response = client.request(data=streaming_request_body())
            self.assertEqual(response.content, b"foobar" * 100)
