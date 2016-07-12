from tests.base import AsyncTestCase


def infinite_body():
    for _ in range(100):
        yield b"foobar"


class MaxRequestBodySizeTest(AsyncTestCase):

    async def testMaxRequestBodySize(self):
        async with await self.start_server(max_request_body_size=3) as server:
            async with await server.request("GET", "/", data="foobar") as response:
                self.assertEqual(response.status, 413)

    async def testMaxRequestBodySizeStreaming(self):
        async with await self.start_server(max_request_body_size=20) as server:
            async with await server.request("GET", "/", data=infinite_body()) as response:
                self.assertEqual(response.status, 413)
