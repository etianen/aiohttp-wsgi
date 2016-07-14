import time
from tests.base import AsyncTestCase


CHUNK = b"foobar" * 1024
CHUNK_COUNT = 64


class StartResponseTest(AsyncTestCase):

    def startResponseApplication(self, environ, start_response):
        start_response("201 Created", [
            ("Foo", "Bar"),
        ])
        return [b"foobar"]

    async def testStartResponse(self):
        async with await self.start_server(self.startResponseApplication) as server:
            async with await server.request("GET", "/") as response:
                self.assertEqual(response.status, 201)
                self.assertEqual(response.reason, "Created")
                self.assertEqual(response.headers["Foo"], "Bar")
                self.assertEqual(await response.text(), "foobar")

    # Streaming.

    def streamingResponseApplication(self, environ, start_response):
        start_response("200 OK", [])
        for _ in range(CHUNK_COUNT):
            yield CHUNK

    async def testStreamingResponse(self):
        async with await self.start_server(self.streamingResponseApplication) as server:
            async with await server.request("GET", "/") as response:
                self.assertEqual(await response.read(), CHUNK * CHUNK_COUNT)

    def streamingResponseWriteApplication(self, environ, start_response):
        write = start_response("200 OK", [])
        for _ in range(CHUNK_COUNT):
            write(CHUNK)
        return []

    async def testStreamingResponseWrite(self):
        async with await self.start_server(self.streamingResponseWriteApplication) as server:
            async with await server.request("GET", "/") as response:
                self.assertEqual(await response.read(), CHUNK * CHUNK_COUNT)

    # Outbuf overflow.

    async def testOutbufOverflow(self):
        async with await self.start_server(self.streamingResponseApplication, outbuf_overflow=len(CHUNK)//2) as server:
            async with await server.request("GET", "/") as response:
                self.assertEqual(await response.read(), CHUNK * CHUNK_COUNT)

    def outbufOverflowSlowApplication(self, environ, start_response):
        start_response("200 OK", [])
        for _ in range(CHUNK_COUNT // 2):
            yield CHUNK
        time.sleep(1)
        for _ in range(CHUNK_COUNT // 2):
            yield CHUNK

    async def testOutbufOverflowSlow(self):
        async with await self.start_server(self.outbufOverflowSlowApplication, outbuf_overflow=len(CHUNK)//2) as server:
            async with await server.request("GET", "/") as response:
                self.assertEqual(await response.read(), CHUNK * CHUNK_COUNT)
