from aiohttp.web import Application
from tests.base import AsyncTestCase


class OnFinishTest(AsyncTestCase):

    def onFinish(self, app):
        self.assertIsInstance(app, Application)

    async def testOnFinish(self):
        async with await self.start_server(on_finish=(self.onFinish,)) as server:
            await self.assertResponse(server, "GET", "/")
