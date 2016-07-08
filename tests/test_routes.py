import pytest

from aiohttp.web import Response


def route_handler(request):
    return Response(body=b"aiohttp handler")


@pytest.mark.asyncio
@pytest.mark.parametrize("routes", [[("GET", "/foo", route_handler)]])
async def test_custom_routes_miss(response):
    assert response.status == 200
    assert await response.text() == "Hello world"


@pytest.mark.asyncio
@pytest.mark.parametrize("routes", [[("GET", "/foo", route_handler)]])
@pytest.mark.parametrize("request_path", ["/foo"])
async def test_custom_routes_hit(response):
    assert response.status == 200
    assert await response.text() == "aiohttp handler"
