from tests.base import AsyncTestCase


def infinite_body():
    for _ in range(100):
        yield b"foobar"


class MaxRequestBodySizeTest(AsyncTestCase):

    async def testMaxRequestBodySize(self):
        async with self.server(max_request_body_size=3) as server:
            async with server.request(data="foobar") as response:
                self.assertEqual(response.status, 413)

    async def testMaxRequestBodySizeStreaming(self):
        async with self.server(max_request_body_size=20) as server:
            async with server.request(data=infinite_body()) as response:
                self.assertEqual(response.status, 413)
