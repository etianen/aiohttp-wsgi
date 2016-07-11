import asyncio
import sys
import tempfile
from wsgiref.util import is_hop_by_hop
from urllib.parse import quote
from aiohttp.web import Response, StreamResponse
from aiohttp_wsgi.utils import parse_sockname


class WSGIHandler:

    def __init__(
        self,
        application, *,
        # Handler config.
        url_scheme=None,
        stderr=sys.stderr,
        inbuf_overflow=524288,
        max_request_body_size=1073741824,
        # asyncio config.
        executor=None,
        loop=None
    ):
        self._application = application
        # Handler config.
        self._url_scheme = url_scheme
        self._stderr = stderr
        self._inbuf_overflow = inbuf_overflow
        self._max_request_body_size = max_request_body_size
        # asyncio config.
        self._executor = executor
        self._loop = loop or asyncio.get_event_loop()

    async def _get_environ(self, request, body, content_length):
        # Resolve the path info.
        path_info = request.match_info["path_info"]
        script_name = request.path[:len(request.path)-len(path_info)]
        # Special case: If the app was mounted on the root, then the script name will
        # currently be set to "/", which is illegal in the WSGI spec. The script name
        # could also end with a slash if the WSGIHandler was mounted as a route
        # manually with a trailing slash before the path_info. In either case, we
        # correct this according to the WSGI spec by transferring the trailing slash
        # from script_name to the start of path_info.
        if script_name.endswith("/"):
            script_name = script_name[:-1]
            path_info = "/" + path_info
        # Parse the connection info.
        server_name, server_port = parse_sockname(request.transport.get_extra_info("sockname"))
        remote_addr, remote_port = parse_sockname(request.transport.get_extra_info("peername"))
        # Detect the URL scheme.
        url_scheme = self._url_scheme
        if url_scheme is None:
            url_scheme = "http" if request.transport.get_extra_info("sslcontext") is None else "https"
        # Create the environ.
        environ = {
            "REQUEST_METHOD": request.method,
            "SCRIPT_NAME": quote(script_name),  # WSGI spec expects URL-quoted path components.
            "PATH_INFO": quote(path_info),  # WSGI spec expects URL-quoted path components.
            "QUERY_STRING": request.query_string,
            "CONTENT_TYPE": request.headers.get("Content-Type", ""),
            "CONTENT_LENGTH": str(content_length),
            "SERVER_NAME": server_name,
            "SERVER_PORT": server_port,
            "REMOTE_ADDR": remote_addr,
            "REMOTE_HOST": remote_addr,
            "REMOTE_PORT": remote_port,
            "SERVER_PROTOCOL": "HTTP/{}.{}".format(*request.version),
            "wsgi.version": (1, 0),
            "wsgi.url_scheme": url_scheme,
            "wsgi.input": body,
            "wsgi.errors": self._stderr,
            "wsgi.multithread": True,
            "wsgi.multiprocess": False,
            "wsgi.run_once": False,
        }
        # Add in additional HTTP headers.
        for header_name in request.headers:
            header_name = header_name.upper()
            if not(is_hop_by_hop(header_name)) and header_name not in ("CONTENT-LENGTH", "CONTENT-TYPE"):
                header_value = ",".join(request.headers.getall(header_name))
                environ["HTTP_" + header_name.replace("-", "_")] = header_value
        # All done!
        return environ

    def _run_application(self, environ, response):
        body_iterable = self._application(environ, response.start_response)
        try:
            # Run through all the data.
            for data in body_iterable:
                response.write(data)
            else:
                # Ensure that empty responses are still started.
                response.write(b"")
        finally:
            # Close the body.
            if hasattr(body_iterable, "close"):
                body_iterable.close()

    async def handle_request(self, request):
        # Check for body size overflow.
        if request.content_length is not None and request.content_length > self._max_request_body_size:
            return Response(status=413)
        # Read the body.
        content_length = 0
        with tempfile.SpooledTemporaryFile(max_size=self._inbuf_overflow) as body:
            while True:
                block = await request.content.readany()
                if not block:
                    break
                content_length += len(block)
                # Check for body size overflow. The request might be streaming, so we check with every chunk.
                if content_length > self._max_request_body_size:
                    return Response(status=413)
                body.write(block)
            body.seek(0)
            # Run the app.
            environ = await self._get_environ(request, body, content_length)
            response = WSGIResponse(self, request)
            await self._loop.run_in_executor(self._executor, self._run_application, environ, response)
            # ALll done!
            return response._response

    async def __call__(self, request):
        return await self.handle_request(request)


class WSGIResponse:

    __slots__ = ("_handler", "_request", "_response",)

    def __init__(self, handler, request):
        self._handler = handler
        self._request = request
        # State.
        self._response = None

    def start_response(self, status, headers, exc_info=None):
        if exc_info:
            # Log the error.
            self._request.app.logger.error("Unexpected error", exc_info=exc_info)
            # Attempt to modify the response.
            try:
                if self._response and self._response.prepared:
                    raise exc_info[1].with_traceback(exc_info[2])
                self._response = None
            finally:
                exc_info = None
        # Cannot start response twice.
        assert not self._response, "Cannot call start_response() twice"
        # Parse the status.
        assert isinstance(status, str), "Response status should be str"
        status_code, reason = status.split(None, 1)
        status_code = int(status_code)
        # Store the response.
        self._response = StreamResponse(
            status=status_code,
            reason=reason,
        )
        # Store the headers.
        for header_name, header_value in headers:
            assert not is_hop_by_hop(header_name), "Hop-by-hop headers are forbidden"
            self._response.headers.add(header_name, header_value)
        # Return the stream writer interface.
        return self.write

    async def _write(self, data):
        assert self._response, "Application did not call start_response()"
        if not self._response.prepared:
            await self._response.prepare(self._request)
        if data:
            self._response.write(data)

    def write(self, data):
        assert isinstance(data, (bytes, bytearray, memoryview)), "Data should be bytes"
        asyncio.run_coroutine_threadsafe(self._write(data), loop=self._handler._loop).result()
