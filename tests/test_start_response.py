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
        async with self.server(self.startResponseApplication) as server:
            async with server.request() as response:
                self.assertEqual(response.status, 201)
                self.assertEqual(response.reason, "Created")
                self.assertEqual(response.headers["Foo"], "Bar")
                self.assertEqual(await response.text(), "foobar")

    def streamingResponseApplication(self, environ, start_response):
        start_response("200 OK", [])
        for _ in range(CHUNK_COUNT):
            yield CHUNK

    async def testStreamingResponse(self):
        async with self.server(self.streamingResponseApplication) as server:
            async with server.request() as response:
                self.assertEqual(await response.read(), CHUNK * CHUNK_COUNT)

    def streamingResponseWriteApplication(self, environ, start_response):
        write = start_response("200 OK", [])
        for _ in range(CHUNK_COUNT):
            write(CHUNK)
        return []

    async def testStreamingResponseWrite(self):
        async with self.server(self.streamingResponseWriteApplication) as server:
            async with server.request() as response:
                self.assertEqual(await response.read(), CHUNK * CHUNK_COUNT)
