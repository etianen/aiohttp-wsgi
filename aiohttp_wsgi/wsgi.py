"""
Running a WSGI app
==================

.. currentmodule:: aiohttp_wsgi

:mod:`aiohttp_wsgi` allows you to run WSGI applications (e.g. `Django`_, `Flask`_) on :ref:`aiohttp <aiohttp-web>`.
This allows you to add async features like websockets and long-polling to an existing Python web app.

.. hint::

    If you don't need to add :ref:`websockets <aiohttp-web-websockets>` or
    :ref:`async request handlers <aiohttp-web-handler>` to your app, but still want to run your WSGI app on the
    :mod:`asyncio` event loop, :mod:`aiohttp_wsgi` provides a simpler :doc:`command line interface <main>`.


Run a web server
----------------

In order to implement a WSGI server, first import your WSGI application and wrap it in a :class:`WSGIHandler`.

.. code:: python

    from aiohttp import web
    from aiohttp_wsgi import WSGIHandler
    from your_project.wsgi import application

    wsgi_handler = WSGIHandler(application)


Next, create an :class:`Application <aiohttp.web.Application>` instance and register the request handler with the
application's :class:`router <aiohttp.web.UrlDispatcher>` on a particular HTTP *method* and *path*:

.. code:: python

    app = web.Application()
    app.router.add_route("*", "/{path_info:.*}", wsgi_handler)

After that, run the application by :func:`run_app() <aiohttp.web.run_app>` call:

.. code:: python

    web.run_app(app)

See the :ref:`aiohttp.web <aiohttp-web>` documentation for information on adding
:ref:`websockets <aiohttp-web-websockets>` and :ref:`async request handlers <aiohttp-web-handler>` to your app.


Serving simple WSGI apps
------------------------

If you don't need to add :ref:`websockets <aiohttp-web-websockets>` or
:ref:`async request handlers <aiohttp-web-handler>` to your app, but still want to run your WSGI app on the
:mod:`asyncio` event loop, :mod:`aiohttp_wsgi` provides a simple :func:`serve()` helper.

.. code:: python

    from aiohttp_wsgi import serve

    serve(application)


Extra environ keys
------------------

:mod:`aiohttp_wsgi` adds the following additional keys to the WSGI environ:

``asyncio.loop``
    The ``asyncio.EventLoop`` running the server.

``asyncio.executor``
    The :class:`Executor <concurrent.futures.Executor>` running the WSGI request.

``aiohttp.request``
    The raw :class:`aiohttp.web.Request` that initiated the WSGI request. Use this to access additional
    request :ref:`metadata <aiohttp-web-data-sharing>`.


API reference
-------------

.. autoclass:: WSGIHandler
    :members:

.. autofunction:: serve


.. include:: /_include/links.rst
"""

import asyncio
import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from wsgiref.util import is_hop_by_hop
from aiohttp.web import Application, AppRunner, TCPSite, UnixSite, middleware, StreamResponse
from aiohttp_wsgi.utils import parse_sockname


logger = logging.getLogger(__name__)


def read_chunk(body_iterable, size_limit=None):
    """
    Buffer the data by a size_limit. Returns a partial chunk of the data in bytes

    :param Generator body_iterable: {body_iterable}
    :param int size_limit: {size_limit}
    """

    chunks = bytearray()
    for chunk in body_iterable:
        chunks.extend(chunk)

        if size_limit is not None and len(chunks) > size_limit:
            break

    return chunks


class WSGIRequest:
    def __init__(self):
        self._response = None
        self._header_leftover = []

    # Simple start_response callable.
    def start_response(self, status, headers, exc_info=None):
        status_code, reason = status.split(None, 1)
        status_code = int(status_code)
        # Check the headers.
        for header_name, header_value in headers:
            assert not is_hop_by_hop(header_name), "hop-by-hop headers are forbidden: {}".format(header_name)

        self._response = StreamResponse(status=status_code, reason=reason, headers=headers)
        # Start the response.
        return self._header_leftover.append

    def run_application(self, application, request, environ, loop):
        # body_iterable must be an iterator and not a list
        body_iterable = iter(application(environ, self.start_response))

        if self._response is None:
            self._header_leftover.append(next(body_iterable))
        assert self._response is not None

        try:
            asyncio.run_coroutine_threadsafe(self._response.prepare(request), loop).result()
            if self._header_leftover:
                asyncio.run_coroutine_threadsafe(self._response.write(b''.join(self._header_leftover)), loop).result()

            while True:
                # buffer to 1 MB in order to not overload the event loop
                chunk = read_chunk(body_iterable, 1024 * 1024)
                if not chunk:
                    break
                asyncio.run_coroutine_threadsafe(self._response.write(chunk), loop).result()
        finally:
            if hasattr(body_iterable, "close"):
                body_iterable.close()

            asyncio.run_coroutine_threadsafe(self._response.write_eof(), loop).result()

        return self._response


class WSGIBodyReader:
    def __init__(self, request, loop):
        self._request = request
        self._loop = loop

    def read(self, size=None):
        try:
            if size:
                return asyncio.run_coroutine_threadsafe(self._request.content.readexactly(size), self._loop).result()

            return asyncio.run_coroutine_threadsafe(self._request.content.read(), self._loop).result()
        except asyncio.IncompleteReadError as e:
            return e.partial

    def readline(self):
        return asyncio.run_coroutine_threadsafe(self._request.content.readline(), self._loop).result()

    def readlines(self):
        return asyncio.run_coroutine_threadsafe(self._request.content.readlines(), self._loop).result()

    def __iter__(self):
        return asyncio.run_coroutine_threadsafe(self._request.content.readany(), self._loop).result()


class WSGIHandler:

    """
    An adapter for WSGI applications, allowing them to run on :ref:`aiohttp <aiohttp-web>`.

    :param application: {application}
    :param str url_scheme: {url_scheme}
    :param io.BytesIO stderr: {stderr}
    :param concurrent.futures.Executor executor: {executor}
    :param loop: {loop}
    """

    def __init__(
        self,
        application,
        *,
        # Handler config.
        url_scheme=None,
        stderr=None,
        # asyncio config.
        executor=None,
        loop=None
    ):
        assert callable(application), "application should be callable"
        self._application = application
        # Handler config.
        self._url_scheme = url_scheme
        self._stderr = stderr or sys.stderr
        # asyncio config.
        self._executor = executor
        self._loop = loop or asyncio.get_event_loop()

    def _get_environ(self, request, body):
        # Resolve the path info.
        path_info = request.match_info["path_info"]
        script_name = request.rel_url.path[:len(request.rel_url.path)-len(path_info)]
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
            "SCRIPT_NAME": script_name,
            "PATH_INFO": path_info,
            "RAW_URI": request.raw_path,
            # RAW_URI: Gunicorn's non-standard field
            "REQUEST_URI": request.raw_path,
            # REQUEST_URI: uWSGI/Apache mod_wsgi's non-standard field
            "QUERY_STRING": request.rel_url.raw_query_string,
            "CONTENT_TYPE": request.content_type,
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

        if request.content_length is not None:
            environ["CONTENT_LENGTH"] = str(request.content_length)

        # Add in additional HTTP headers.
        for header_name in request.headers:
            header_name = header_name.upper()
            if not(is_hop_by_hop(header_name)) and header_name not in ("CONTENT-LENGTH", "CONTENT-TYPE"):
                header_value = ",".join(request.headers.getall(header_name))
                environ["HTTP_" + header_name.replace("-", "_")] = header_value
        # All done!
        return environ

    async def handle_request(self, request):
        body = WSGIBodyReader(request, self._loop)
        environ = self._get_environ(request, body)
        return await self._loop.run_in_executor(
            self._executor, WSGIRequest().run_application, self._application, request, environ, self._loop
        )

    __call__ = handle_request


def format_path(path):
    assert not path.endswith("/"), "{!r} name should not end with /".format(path)
    if path == "":
        path = "/"
    assert path.startswith("/"), "{!r} name should start with /".format(path)
    return path


def static_cors_middleware(*, static, static_cors):
    @middleware
    async def do_static_cors_middleware(request, handler):
        response = await handler(request)
        for path, _ in static:
            if request.path.startswith(path):
                response.headers["Access-Control-Allow-Origin"] = static_cors
                break
        return response
    return do_static_cors_middleware


@contextmanager
def run_server(
    application,
    *,
    # asyncio config.
    threads=4,
    # Server config.
    host=None,
    port=8080,
    # Unix server config.
    unix_socket=None,
    unix_socket_perms=0o600,
    # Shared server config.
    backlog=1024,
    # aiohttp config.
    static=(),
    static_cors=None,
    script_name="",
    shutdown_timeout=60.0,
    **kwargs
):
    # Set up async context.
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    assert threads >= 1, "threads should be >= 1"
    executor = ThreadPoolExecutor(threads)
    # Create aiohttp app.
    app = Application()
    # Add static routes.
    static = [(format_path(path), dirname) for path, dirname in static]
    for path, dirname in static:
        app.router.add_static(path, dirname)
    # Add the wsgi application. This has to be last.
    app.router.add_route(
        "*",
        "{}{{path_info:.*}}".format(format_path(script_name)),
        WSGIHandler(
            application,
            loop=loop,
            executor=executor,
            **kwargs
        ).handle_request,
    )
    # Configure middleware.
    if static_cors:
        app.middlewares.append(static_cors_middleware(
            static=static,
            static_cors=static_cors,
        ))
    # Start the app runner.
    runner = AppRunner(app)
    loop.run_until_complete(runner.setup())
    # Set up the server.
    if unix_socket is not None:
        site = UnixSite(runner, path=unix_socket, backlog=backlog, shutdown_timeout=shutdown_timeout)
    else:
        site = TCPSite(runner, host=host, port=port, backlog=backlog, shutdown_timeout=shutdown_timeout)
    loop.run_until_complete(site.start())
    # Set socket permissions.
    if unix_socket is not None:
        os.chmod(unix_socket, unix_socket_perms)
    # Report.
    server_uri = " ".join(
        "http://{}:{}".format(*parse_sockname(socket.getsockname()))
        for socket
        in site._server.sockets
    )
    logger.info("Serving on %s", server_uri)
    try:
        yield loop, site
    finally:
        # Clean up unix sockets.
        for socket in site._server.sockets:
            host, port = parse_sockname(socket.getsockname())
            if host == "unix":
                os.unlink(port)
        # Close the server.
        logger.debug("Shutting down server on %s", server_uri)
        loop.run_until_complete(site.stop())
        # Shut down app.
        logger.debug("Shutting down app on %s", server_uri)
        loop.run_until_complete(runner.cleanup())
        # Shut down executor.
        logger.debug("Shutting down executor on %s", server_uri)
        executor.shutdown()
        # Shut down loop.
        logger.debug("Shutting down loop on %s", server_uri)
        loop.close()
        asyncio.set_event_loop(None)
        # All done!
        logger.info("Stopped serving on %s", server_uri)


def serve(application, **kwargs):  # pragma: no cover
    """
    Runs the WSGI application on :ref:`aiohttp <aiohttp-web>`, serving it until keyboard interrupt.

    :param application: {application}
    :param str url_scheme: {url_scheme}
    :param io.BytesIO stderr: {stderr}
    :param int threads: {threads}
    :param str host: {host}
    :param int port: {port}
    :param str unix_socket: {unix_socket}
    :param int unix_socket_perms: {unix_socket_perms}
    :param int backlog: {backlog}
    :param list static: {static}
    :param list static_cors: {static_cors}
    :param str script_name: {script_name}
    :param int shutdown_timeout: {shutdown_timeout}
    """
    with run_server(application, **kwargs) as (loop, site):
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass


DEFAULTS = {}
DEFAULTS.update(WSGIHandler.__init__.__kwdefaults__)
DEFAULTS.update(run_server.__wrapped__.__kwdefaults__)

HELP = {
    "application": "A WSGI application callable.",
    "url_scheme": (
        "A hint about the URL scheme used to access the application. Corresponds to ``environ['wsgi.url_scheme']``. "
        "Default is auto-detected to ``'http'`` or ``'https'``."
    ),
    "stderr": (
        "A file-like value for WSGI error logging. Corresponds to ``environ['wsgi.errors']``. "
        "Defaults to ``sys.stderr``."
    ),
    "executor": "An Executor instance used to run WSGI requests. Defaults to the :mod:`asyncio` base executor.",
    "loop": "The asyncio loop. Defaults to :func:`asyncio.get_event_loop`.",
    "host": "Host interfaces to bind. Defaults to ``'0.0.0.0'`` and ``'::'``.",
    "port": "Port to bind. Defaults to ``{port!r}``.".format_map(DEFAULTS),
    "unix_socket": "Path to a unix socket to bind, cannot be used with ``host``.",
    "unix_socket_perms": (
        "Filesystem permissions to apply to the unix socket. Defaults to ``{unix_socket_perms!r}``."
    ).format_map(DEFAULTS),
    "backlog": "Socket connection backlog. Defaults to {backlog!r}.".format_map(DEFAULTS),
    "static": "Static root mappings in the form (path, directory). Defaults to {static!r}".format_map(DEFAULTS),
    "static_cors": (
        "Set to '*' to enable CORS on static files for all origins, or a string to enable CORS for a specific origin. "
        "Defaults to {static_cors!r}"
    ).format_map(DEFAULTS),
    "script_name": (
        "URL prefix for the WSGI application, should start with a slash, but not end with a slash. "
        "Defaults to ``{script_name!r}``."
    ).format_map(DEFAULTS),
    "threads": "Number of threads used to process application logic. Defaults to ``{threads!r}``.".format_map(DEFAULTS),
    "shutdown_timeout": (
        "Timeout when closing client connections on server shutdown. Defaults to ``{shutdown_timeout!r}``."
    ).format_map(DEFAULTS),
    "size_limit": "Size limit in bytes",
    "body_iterable": "A generator containing the body data returned from the WSGI request"
}

WSGIHandler.__doc__ = WSGIHandler.__doc__.format_map(HELP)

serve.__doc__ = serve.__doc__.format_map(HELP)
