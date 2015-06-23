import warnings

import pytest

import aiohttp

from aiohttp_wsgi.api import configure_server, close_server


# Fixtures.

@pytest.fixture
def application_test():
    def application_test_(environ):
        pass
    return application_test_

@pytest.fixture
def application(application_test):
    def application_(environ, start_response):
        application_test(environ)
        start_response("200 OK", [
            ("Content-Type", "text/plain; charset=utf-8"),
        ])
        return [b"Hello world"]
    return application_

@pytest.fixture
def script_name():
    return ""

@pytest.fixture
def url_scheme():
    return None

@pytest.fixture
def unix_socket():
    return None

@pytest.fixture
def socket():
    return None

@pytest.fixture
def routes():
    return ()

@pytest.fixture
def static():
    return ()

@pytest.fixture
def on_finish():
    return ()

@pytest.yield_fixture
def server(event_loop, unused_tcp_port, application, script_name, url_scheme, unix_socket, socket, routes, static, on_finish):
    # Set up debug warnings.
    with warnings.catch_warnings():
        warnings.simplefilter("default", ResourceWarning)
        # Use asyncio debug.
        event_loop.set_debug(True)
        # Create a server.
        server, app = configure_server(application,
            host = "127.0.0.1",
            port = unused_tcp_port,
            loop = event_loop,
            script_name = script_name,
            url_scheme = url_scheme,
            unix_socket = unix_socket,
            socket = socket,
            routes = routes,
            static = static,
            on_finish = on_finish,
        )
        # Create a client.
        try:
            yield server
        finally:
            close_server(server, app, loop=event_loop)

@pytest.fixture
def request_method():
    return "GET"

@pytest.fixture
def request_path():
    return "/"

@pytest.fixture
def request_data():
    return None

@pytest.fixture
def request_headers():
    return {}

@pytest.fixture
def request_connector():
    return None

@pytest.yield_fixture
def response(event_loop, server, unused_tcp_port, request_method, request_path, request_data, request_headers, request_connector):
    uri = "http://127.0.0.1:{}{}".format(unused_tcp_port, request_path)
    response = event_loop.run_until_complete(aiohttp.request(request_method, uri, data=request_data, headers=request_headers, connector=request_connector, loop=event_loop))
    try:
        yield response
    finally:
        response.close()
        event_loop.run_until_complete(response.wait_for_close())


# Helpers.

def server_test(func):
    @pytest.mark.asyncio
    @pytest.mark.parametrize("application_test", [func])
    def client(response):
        assert response.status == 200
        assert response.reason == "OK"
        assert (yield from response.text()) == "Hello world"
    return client
