import os
from tests.base import AsyncTestCase


STATIC_ITEM = "/static={}".format(os.path.join(os.path.dirname(__file__), "static"))


class StaticTest(AsyncTestCase):

    def testStaticMiss(self):
        with self.serve("--static", STATIC_ITEM, "tests.base:noop_application") as client:
            response = client.request()
            self.assertEqual(response.status, 200)
            self.assertEqual(response.text, "")

    def testStaticHit(self):
        with self.serve("--static", STATIC_ITEM, "tests.base:noop_application") as client:
            response = client.request(path="/static/text.txt")
            self.assertEqual(response.status, 200)
            self.assertEqual(response.text, "Test file")

    def testStaticHitMissing(self):
        with self.serve("--static", STATIC_ITEM, "tests.base:noop_application") as client:
            response = client.request(path="/static/missing.txt")
            self.assertEqual(response.status, 404)
