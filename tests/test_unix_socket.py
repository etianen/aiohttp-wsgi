import tempfile
from contextlib import closing

import pytest

from aiohttp.connector import UnixConnector

from .conftest import server_test


# Fixtures.

@pytest.fixture
def unix_socket():
    with closing(tempfile.NamedTemporaryFile()) as handle:
        name = handle.name
    return name

@pytest.yield_fixture
def request_connector(unix_socket):
    connector = UnixConnector(unix_socket)
    try:
        yield connector
    finally:
        connector.close()


# Tests.

@server_test
def test_server_name(environ):
    assert environ["SERVER_NAME"] == "unix"

@server_test
def test_server_port(environ):
    assert environ["SERVER_PORT"].startswith("/")

@server_test
def test_remote_addr(environ):
    assert environ["REMOTE_ADDR"] == "unix"

@server_test
def test_remote_port(environ):
    assert environ["REMOTE_PORT"] == ""
