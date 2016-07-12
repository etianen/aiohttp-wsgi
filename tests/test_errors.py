import sys
from tests.base import AsyncTestCase


class ErrorsTest(AsyncTestCase):

    def errorHandlingApplication(self, environ, start_response):
        try:
            start_response("200 OK", [])
            raise Exception("Boom!")
        except:
            start_response("509 Boom", [], sys.exc_info())
            return [b"Boom!"]

    async def testErrorHandling(self):
        async with await self.start_server(self.errorHandlingApplication) as server:
            with self.assertLogs("aiohttp.web", "ERROR"):
                async with await server.request("GET", "/") as response:
                    self.assertEqual(response.status, 509)
                    self.assertEqual(await response.text(), "Boom!")

    def noStartResponseApplication(self, environ, start_response):
        return []

    async def testNoStartResponse(self):
        async with await self.start_server(self.noStartResponseApplication) as server:
            with self.assertLogs("aiohttp.web", "ERROR"):
                async with await server.request("GET", "/") as response:
                    self.assertEqual(response.status, 500)

    def startResponseTwiceApplication(self, environ, start_response):
        start_response("200 OK", [
            ("Content-Type", "text/html; charse=utf-8"),
        ])
        start_response("200 OK", [
            ("Content-Type", "text/html; charse=utf-8"),
        ])

    async def testStartResponseTwice(self):
        async with await self.start_server(self.startResponseTwiceApplication) as server:
            with self.assertLogs("aiohttp.web", "ERROR"):
                async with await server.request("GET", "/") as response:
                    self.assertEqual(response.status, 500)

    def errorAfterWriteApplication(self, environ, start_response):
        try:
            start_response("200 OK", [])
            raise Exception("Boom!")
        except:
            write = start_response("509 Boom", [], sys.exc_info())
            write(b"Boom!")
            try:
                raise Exception("Boom!!")
            except:
                start_response("510 Boom", [], sys.exc_info())

    async def testErrorAfterWrite(self):
        with self.assertLogs("aiohttp.web", "ERROR"):
            async with await self.start_server(self.errorAfterWriteApplication) as server:
                # Don't use the response context manager as the client body is garbled.
                response = await server.request("GET", "/")
                self.assertEqual(response.status, 509)
                response.close()
                await response.wait_for_close()
