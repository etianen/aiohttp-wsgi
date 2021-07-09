from __future__ import annotations
import os
from tests.base import AsyncTestCase, noop_application


STATIC = (("/static", os.path.join(os.path.dirname(__file__), "static")),)


class StaticTest(AsyncTestCase):

    def testStaticMiss(self) -> None:
        with self.run_server(noop_application, static=STATIC) as client:
            response = client.request()
            self.assertEqual(response.status, 200)
            self.assertEqual(response.content, b"")

    def testStaticHit(self) -> None:
        with self.run_server(noop_application, static=STATIC) as client:
            response = client.request(path="/static/text.txt")
            self.assertEqual(response.status, 200)
            self.assertEqual(response.content, b"Test file")

    def testStaticHitMissing(self) -> None:
        with self.run_server(noop_application, static=STATIC) as client:
            response = client.request(path="/static/missing.txt")
            self.assertEqual(response.status, 404)

    def testStaticHitCors(self) -> None:
        with self.run_server(noop_application, static=STATIC, static_cors="*") as client:
            response = client.request(path="/static/text.txt")
            self.assertEqual(response.status, 200)
            self.assertEqual(response.content, b"Test file")
            self.assertEqual(response.headers["Access-Control-Allow-Origin"], "*")
