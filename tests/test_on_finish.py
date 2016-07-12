from aiohttp.web import Application
from tests.base import AsyncTestCase


def on_finish_callback(app):
    assert isinstance(app, Application)


class OnFinishTest(AsyncTestCase):

    async def testOnFinish(self):
        async with await self.start_server(on_finish=("tests.test_on_finish:on_finish_callback",)) as server:
            await self.assertResponse(server, "GET", "/")
