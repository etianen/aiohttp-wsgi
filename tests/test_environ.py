import pytest

from .conftest import server_test


@pytest.mark.parametrize("request_method", ["GET"])
@server_test
def test_request_method_get(environ):
    assert environ["REQUEST_METHOD"] == "GET"

@pytest.mark.parametrize("request_method", ["POST"])
@server_test
def test_request_method_post(environ):
    assert environ["REQUEST_METHOD"] == "POST"

@server_test
def test_path_root(environ):
    assert environ["SCRIPT_NAME"] == ""
    assert environ["PATH_INFO"] == "/"

@pytest.mark.parametrize("request_path", ["/foo"])
@server_test
def test_path_subdir(environ):
    assert environ["SCRIPT_NAME"] == ""
    assert environ["PATH_INFO"] == "/foo"

@pytest.mark.parametrize("script_name", ["/foo"])
@pytest.mark.parametrize("request_path", ["/foo"])
@server_test
def test_path_root_subdir(environ):
    assert environ["SCRIPT_NAME"] == "/foo"
    assert environ["PATH_INFO"] == ""

@pytest.mark.parametrize("script_name", ["/foo"])
@pytest.mark.parametrize("request_path", ["/foo/"])
@server_test
def test_path_root_subdir_slash(environ):
    assert environ["SCRIPT_NAME"] == "/foo"
    assert environ["PATH_INFO"] == "/"

@pytest.mark.parametrize("script_name", ["/foo"])
@pytest.mark.parametrize("request_path", ["/foo/bar"])
@server_test
def test_path_root_subdir_trailing(environ):
    assert environ["SCRIPT_NAME"] == "/foo"
    assert environ["PATH_INFO"] == "/bar"

@server_test
def test_content_type_empty(environ):
    assert environ["CONTENT_TYPE"] == ""

@pytest.mark.parametrize("request_headers", [{"Content-Type": "text/plain"}])
@server_test
def test_content_type_set(environ):
    assert environ["CONTENT_TYPE"] == "text/plain"

@server_test
def test_content_length_empty(environ):
    assert environ["CONTENT_LENGTH"] == "0"

@pytest.mark.parametrize("request_method", ["POST"])
@pytest.mark.parametrize("request_data", [b"foobar"])    
@server_test
def test_content_length_post(environ):
    assert environ["CONTENT_LENGTH"] == "6"

@server_test
def test_server_name(environ):
    assert environ["SERVER_NAME"] == "127.0.0.1"

@server_test
def test_server_port(environ):
    assert int(environ["SERVER_PORT"])

@server_test
def test_remote_addr(environ):
    assert environ["REMOTE_ADDR"] == "127.0.0.1"
    
@server_test
def test_remote_host(environ):
    assert environ["REMOTE_HOST"] == "127.0.0.1"

@server_test
def test_remote_port(environ):
    assert int(environ["REMOTE_PORT"])

@server_test
def test_server_protocol(environ):
    assert environ["SERVER_PROTOCOL"] == "HTTP/1.1"

@server_test
def test_wsgi_version(environ):
    assert environ["wsgi.version"] == (1, 0)

@server_test
def test_url_scheme(environ):
    assert environ["wsgi.url_scheme"] == "http"

@pytest.mark.parametrize("url_scheme", ["https"])
@server_test
def test_url_scheme_https(environ):
    assert environ["wsgi.url_scheme"] == "https"

@pytest.mark.parametrize("request_method", ["POST"])
@pytest.mark.parametrize("request_data", [b"foobar"])
@server_test
def test_wsgi_input(environ):
    assert environ["wsgi.input"].read(6) == b"foobar"

@server_test
def test_wsgi_errors(environ):
    assert hasattr(environ["wsgi.errors"], "write")

@server_test
def test_multithread(environ):
    assert environ["wsgi.multithread"] == True

@server_test
def test_multiprocess(environ):
    assert environ["wsgi.multiprocess"] == False

@server_test
def test_run_once(environ):
    assert environ["wsgi.run_once"] == False

@pytest.mark.parametrize("request_headers", [{"Foo": "Bar"}])
@server_test
def test_custom_header(environ):
    assert environ["HTTP_FOO"] == "Bar"
