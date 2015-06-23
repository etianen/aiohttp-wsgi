import os

import pytest


@pytest.mark.asyncio
@pytest.mark.parametrize("static", [{"/static": os.path.join(os.path.dirname(__file__), "static")}])
def test_static_miss(response):
    assert response.status == 200
    assert (yield from response.text()) == "Hello world"

@pytest.mark.asyncio
@pytest.mark.parametrize("static", [{"/static": os.path.join(os.path.dirname(__file__), "static")}])
@pytest.mark.parametrize("request_path", ["/static/text.txt"])
def test_static_hit(response):
    assert response.status == 200
    assert (yield from response.text()) == "Test file"

@pytest.mark.parametrize("static", [{"/static": os.path.join(os.path.dirname(__file__), "static")}])
@pytest.mark.parametrize("request_path", ["/static/missing.txt"])
def test_static_hit_missing(response):
    assert response.status == 404
