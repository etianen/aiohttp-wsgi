from wsgiref.validate import validator
from tests.base import AsyncTestCase, noop_application


class EnvironTest(AsyncTestCase):

    async def testValidWsgi(self):
        async with await self.start_server(validator(noop_application)) as server:
            await self.assertResponse(server, "GET", "/")
