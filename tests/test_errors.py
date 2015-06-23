import sys

import pytest


# Error handling.

def error_handling_application(environ, start_response):
    try:
        start_response("200 OK", [
            ("Content-Type", "text/html; charse=utf-8"),
        ])
        raise Exception("Boom!")
    except:
        start_response("509 Boom", [
            ("Content-Type", "text/html; charse=utf-8"),
        ], sys.exc_info())
        return [b"Boom!"]

@pytest.mark.asyncio
@pytest.mark.parametrize("application", [error_handling_application])
def test_error_handling(response):
    assert response.status == 509
    assert (yield from response.text()) == "Boom!"


# Unexpected application behavior.

def no_start_response_application(environ, start_response):
    return [b"Hello world"]

@pytest.mark.parametrize("application", [no_start_response_application])
def test_no_start_response(response):
    assert response.status == 500

def start_response_twice_appliction(environ, start_response):
    start_response("200 OK", [
        ("Content-Type", "text/html; charse=utf-8"),
    ])
    start_response("200 OK", [
        ("Content-Type", "text/html; charse=utf-8"),
    ])

@pytest.mark.parametrize("application", [start_response_twice_appliction])
def test_start_response_twice(response):
    assert response.status == 500

def error_after_write_application(environ, start_response):
    try:
        start_response("200 OK", [
            ("Content-Type", "text/html; charse=utf-8"),
        ])
        raise Exception("Boom!")
    except:
        write = start_response("509 Boom", [
            ("Content-Type", "text/html; charse=utf-8"),
        ], sys.exc_info())
        write(b"Boom!")
        try:
            raise Exception("Boom!!")
        except:
            start_response("510 Boom", [
                ("Content-Type", "text/html; charse=utf-8"),
            ], sys.exc_info())

@pytest.mark.parametrize("application", [error_after_write_application])
def test_error_after_response_write(response):
    assert response.status == 509
