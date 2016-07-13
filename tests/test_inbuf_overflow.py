from tests.base import AsyncTestCase


def infinite_body():
    for _ in range(100):
        yield b"foobar"


class InbufOverflowTest(AsyncTestCase):

    async def testInbufOverflow(self):
        async with await self.start_server(inbuf_overflow=3) as server:
            await self.assertResponse(server, "GET", "/", data="foobar")

    async def testInbufOverflowStreaming(self):
        async with await self.start_server(inbuf_overflow=20) as server:
            await self.assertResponse(server, "GET", "/", data=infinite_body())
