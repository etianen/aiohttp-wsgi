import pytest

from aiohttp.web import Response


def route_handler(request):
    return Response(body=b"aiohttp handler")

@pytest.mark.asyncio
@pytest.mark.parametrize("routes", [[("GET", "/foo", route_handler)]])
def test_custom_routes_miss(response):
    assert response.status == 200
    assert (yield from response.text()) == "Hello world"

@pytest.mark.asyncio
@pytest.mark.parametrize("routes", [[("GET", "/foo", route_handler)]])
@pytest.mark.parametrize("request_path", ["/foo"])
def test_custom_routes_hit(response):
    assert response.status == 200
    assert (yield from response.text()) == "aiohttp handler"
