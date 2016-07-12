import os
from tests.base import AsyncTestCase


STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")


class StaticTest(AsyncTestCase):

    async def testStaticMiss(self):
        async with await self.start_server(static=(("/static", STATIC_DIR),)) as server:
            async with await server.request("GET", "/") as response:
                self.assertEqual(response.status, 200)
                self.assertEqual(await response.text(), "")

    async def testStaticHit(self):
        async with await self.start_server(static=(("/static", STATIC_DIR),)) as server:
            async with await server.request("GET", "/static/text.txt") as response:
                self.assertEqual(response.status, 200)
                self.assertEqual(await response.text(), "Test file")

    async def testStaticHitMissing(self):
        async with await self.start_server(static=(("/static", STATIC_DIR),)) as server:
            async with await server.request("GET", "/static/missing.txt") as response:
                self.assertEqual(response.status, 404)
