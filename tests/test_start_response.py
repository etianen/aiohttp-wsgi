import pytest


def custom_header_application(environ, start_response):
    start_response("200 OK", [
        ("Content-Type", "text/plain; charset=utf-8"),
        ("Foo", "Bar"),
    ])
    return [b"Hello world"]

@pytest.mark.parametrize("application", [custom_header_application])
def test_custom_response_header(response, application):
    assert response.headers["Foo"] == "Bar"

CHUNK = b"Hello world" * 1024
CHUNK_COUNT = 64

def streaming_response_application(environ, start_response):
    start_response("200 OK", [
        ("Content-Type", "text/plain; charset=utf-8"),
    ])
    for _ in range(CHUNK_COUNT):
        yield CHUNK

@pytest.mark.asyncio
@pytest.mark.parametrize("application", [streaming_response_application])
def test_streaming_response(response):
    assert (yield from response.read()) == CHUNK * CHUNK_COUNT

def streaming_response_sync_application(environ, start_response):
    write = start_response("200 OK", [
        ("Content-Type", "text/plain; charset=utf-8"),
    ])
    for _ in range(CHUNK_COUNT):
        write(CHUNK)
    return []

@pytest.mark.asyncio
@pytest.mark.parametrize("application", [streaming_response_sync_application])
def test_streaming_response_sync(response):
    assert (yield from response.read()) == CHUNK * CHUNK_COUNT
