from tests.base import AsyncTestCase, streaming_request_body


class MaxRequestBodySizeTest(AsyncTestCase):

    def testMaxRequestBodySize(self):
        with self.serve("--max-request-body-size", "3", "tests.base:noop_application") as client:
            response = client.request(data="foobar")
            self.assertEqual(response.status, 413)

    def testMaxRequestBodySizeStreaming(self):
        with self.serve("--max-request-body-size", "20", "tests.base:noop_application") as client:
            response = client.request(data=streaming_request_body())
            self.assertEqual(response.status, 413)
