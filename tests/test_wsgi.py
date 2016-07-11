from wsgiref.validate import validator
from tests.base import AsyncTestCase, noop_application


class EnvironTest(AsyncTestCase):

    async def testValidWsgi(self):
        async with self.server(validator(noop_application)) as server:
            server.assertResponse()
