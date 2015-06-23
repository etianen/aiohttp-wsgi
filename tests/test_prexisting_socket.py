import socket as socketlib
from contextlib import closing

import pytest

from .conftest import server_test


# Fixtures.

@pytest.yield_fixture
def socket(unused_tcp_port):
    with closing(socketlib.socket(socketlib.AF_INET, socketlib.SOCK_STREAM)) as server_socket:
        server_socket.bind(("127.0.0.1", unused_tcp_port))
        yield server_socket


# Tests.

@server_test
def test_server_name(environ):
    assert environ["SERVER_NAME"] == "127.0.0.1"

@server_test
def test_server_port(environ):
    assert int(environ["SERVER_PORT"])
