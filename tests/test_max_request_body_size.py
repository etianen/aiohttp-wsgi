from __future__ import annotations
from tests.base import AsyncTestCase, streaming_request_body, noop_application


class MaxRequestBodySizeTest(AsyncTestCase):

    def testMaxRequestBodySize(self) -> None:
        with self.run_server(noop_application, max_request_body_size=3) as client:
            response = client.request(data="foobar")
            self.assertEqual(response.status, 413)

    def testMaxRequestBodySizeStreaming(self) -> None:
        with self.run_server(noop_application, max_request_body_size=20) as client:
            response = client.request(data=streaming_request_body())
            self.assertEqual(response.status, 413)
