import asyncio
import pytest


@pytest.mark.parametrize("max_request_body_size", [3])
@pytest.mark.parametrize("request_data", ["foobar"])
def test_max_request_body_size_exceeded(response):
    assert response.status == 413

@asyncio.coroutine
def infinite_body():
    for _ in range(100):
        yield b"foo"

@pytest.mark.parametrize("max_request_body_size", [10])
@pytest.mark.parametrize("request_data", [infinite_body()])
def test_max_request_body_size_exceeded_streaming(response):
    assert response.status == 413
