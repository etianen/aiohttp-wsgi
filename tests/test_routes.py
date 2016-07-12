from aiohttp.web import Response
from tests.base import AsyncTestCase


def route_handler(request):
    return Response(body=b"aiohttp handler")


class RoutesHandler(AsyncTestCase):

    async def testRoutesMiss(self):
        async with await self.start_server(routes=(("GET", "/foo", route_handler),)) as server:
            async with await server.request("GET", "/") as response:
                self.assertEqual(response.status, 200)
                self.assertEqual(await response.text(), "")

    async def testRoutesHit(self):
        async with await self.start_server(routes=(("GET", "/foo", route_handler),)) as server:
            async with await server.request("GET", "/foo") as response:
                self.assertEqual(response.status, 200)
                self.assertEqual(await response.text(), "aiohttp handler")
