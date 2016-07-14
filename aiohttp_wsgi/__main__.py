"""
Command line interface (CLI)
============================

If you don't need to add :ref:`websockets <aiohttp-web-websockets>` or
:ref:`async request handlers <aiohttp-web-handler>` to your app, but still want to run your WSGI app on the
:mod:`asyncio` event loop, :mod:`aiohttp_wsgi` provides a simple command line interface.


Example usage
-------------

Serve a WSGI application called ``application``, located in the ``your_project.wsgi`` module:

.. code:: bash

    aiohttp-wsgi-serve your_project.wsgi:application

Serve a WSGI application and include a static file directory.

.. code:: bash

    aiohttp-wsgi-serve your_project.wsgi:application --static /static=./static


Command reference
-----------------

You can view this reference at any time with ``aiohttp-wsgi-serve --help``.

.. code:: bash

{help}


.. include:: /_include/links.rst
"""

import argparse
import asyncio
import logging
import os
import sys
import textwrap
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from importlib import import_module
from aiohttp.log import access_logger
from aiohttp.web import Application, StaticRoute
import aiohttp_wsgi
from aiohttp_wsgi.utils import parse_sockname
from aiohttp_wsgi.wsgi import WSGIHandler, DEFAULTS, HELP


logger = logging.getLogger(__name__)


def import_func(func):
    assert ":" in func, "{!r} should have format 'module:callable'".format(func)
    module_name, func_name = func.split(":", 1)
    module = import_module(module_name)
    func = getattr(module, func_name)
    return func


def format_path(path):
    assert not path.endswith("/"), "{!r} name should not end with /".format(path)
    if path == "":
        path = "/"
    assert path.startswith("/"), "{!r} name should start with /".format(path)
    return path


def start_loop(*, threads=4):
    loop = asyncio.new_event_loop()
    assert threads >= 1, "threads should be >= 1"
    executor = ThreadPoolExecutor(threads)
    return loop, executor


async def start_server(
    application,
    loop,
    executor,
    *,
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
    # Aiohttp config.
    script_name="",
    **kwargs
):
    app = Application(
        loop=loop,
    )
    # Add static routes.
    for static_item in static:
        assert "=" in static_item, "{!r} should have format 'path=directory'"
        static_item = static_item.split("=", 1)
        path, dirname = static_item
        static_resource = app.router.add_resource("{}/{{filename:.*}}".format(format_path(path)))
        static_resource.add_route("*", StaticRoute(None, path + "/", dirname).handle)
    # Add the wsgi application. This has to be last.
    app.router.add_route(
        "*",
        "{}{{path_info:.*}}".format(format_path(script_name)),
        WSGIHandler(
            application,
            loop=loop,
            executor=executor,
            **kwargs,
        ),
    )
    # HACK: Access logging is broken in aiohtp for unix sockets.
    handler = app.make_handler(access_log=access_logger if unix_socket is None else None)
    # Set up the server.
    shared_server_kwargs = {
        "backlog": backlog,
    }
    if unix_socket is not None:
        server = await loop.create_unix_server(
            handler,
            path=unix_socket,
            **shared_server_kwargs
        )
    else:
        server = await loop.create_server(
            handler,
            host=host,
            port=port,
            **shared_server_kwargs
        )
    # Set socket permissions.
    if unix_socket is not None:
        os.chmod(unix_socket, unix_socket_perms)
    # Report.
    server_uri = " ".join(
        "http://{}:{}".format(*parse_sockname(socket.getsockname()))
        for socket
        in server.sockets
    )
    logger.info("Serving on %s", server_uri)
    # All done!
    return app, handler, server, server_uri


async def close_server(app, handler, server, server_uri, *, shutdown_timeout=60.0):
    # Clean up unix sockets.
    for socket in server.sockets:
        host, port = parse_sockname(socket.getsockname())
        if host == "unix":
            os.unlink(port)
    # Close the server.
    logger.debug("Shutting down server on %s", server_uri)
    server.close()
    await server.wait_closed()
    # Shut down app.
    logger.debug("Shutting down app on %s", server_uri)
    await app.shutdown()
    await handler.finish_connections(shutdown_timeout)
    await app.cleanup()


def close_loop(loop, executor, server_uri):
    # Shut down loop.
    logger.debug("Shutting down executor on %s", server_uri)
    executor.shutdown()
    # Shut down executor.
    logger.debug("Shutting down loop on %s", server_uri)
    loop.close()


DEFAULTS = DEFAULTS.copy()
DEFAULTS.update(start_loop.__kwdefaults__)
DEFAULTS.update(start_server.__kwdefaults__)
DEFAULTS.update(close_server.__kwdefaults__)

HELP = HELP.copy()
HELP.update({
    "host": "Host interfaces to bind. Defaults to ``'0.0.0.0'`` and ``'::'``.",
    "port": "Port to bind. Defaults to ``{port!r}``.".format(**DEFAULTS),
    "unix_socket": "Path to a unix socket to bind, cannot be used with ``host``.",
    "unix_socket_perms": (
        "Filesystem permissions to apply to the unix socket. Defaults to ``{unix_socket_perms!r}``."
    ).format(**DEFAULTS),
    "backlog": "Socket connection backlog. Defaults to {backlog!r}.".format(**DEFAULTS),
    "script_name": (
        "URL prefix for the WSGI application, should start with a slash, but not end with a slash. "
        "Defaults to ``{script_name!r}``."
    ).format(**DEFAULTS),
    "threads": "Number of threads used to process application logic. Defaults to ``{threads!r}``.".format(**DEFAULTS),
    "shutdown_timeout": (
        "Timeout when closing client connections on server shutdown. Defaults to ``{shutdown_timeout!r}``."
    ).format(**DEFAULTS),
})


parser = argparse.ArgumentParser(
    prog="aiohttp-wsgi-serve",
    description="Run a WSGI application.",
    allow_abbrev=False,
)


def add_argument(name, *aliases, **kwargs):
    varname = name.strip("-").replace("-", "_")
    # Format help.
    kwargs.setdefault("help", HELP.get(varname, "").replace("``", ""))
    assert kwargs["help"]
    # Parse action.
    kwargs.setdefault("action", "store")
    if kwargs["action"] in ("append", "count"):
        kwargs["help"] += " Can be specified multiple times."
    if kwargs["action"] == "count":
        kwargs.setdefault("default", 0)
    if kwargs["action"] in ("append", "store"):
        kwargs.setdefault("default", DEFAULTS.get(varname))
        kwargs.setdefault("type", type(kwargs["default"]))
        assert not isinstance(None, kwargs["type"])
    parser.add_argument(name, *aliases, **kwargs)


add_argument(
    "application",
    metavar="module:application",
    type=str,
)
add_argument(
    "--host",
    type=str,
    action="append",
)
add_argument(
    "--port",
    "-p",
)
add_argument(
    "--unix-socket",
    type=str,
)
add_argument(
    "--unix-socket-perms",
)
add_argument(
    "--backlog",
)
add_argument(
    "--static",
    action="append",
    default=[],
    type=str,
    help=(
        "Static route mappings in the form 'path=directory'. "
        "`path` must start with a slash, but not end with a slash."
    ),
)
add_argument(
    "--script-name",
)
add_argument(
    "--url-scheme",
    type=str,
)
add_argument(
    "--threads",
)
add_argument(
    "--inbuf-overflow",
)
add_argument(
    "--max-request-body-size",
)
add_argument(
    "--outbuf-overflow",
)
add_argument(
    "--shutdown-timeout",
)
add_argument(
    "--verbose",
    "-v",
    action="count",
    help="Increase verbosity.",
)
add_argument(
    "--quiet",
    "-q",
    action="count",
    help="Decrease verbosity.",
)
add_argument(
    "--version",
    action="version",
    help="Display version information.",
    version="aiohttp-wsgi v{}".format(aiohttp_wsgi.__version__),
)


@contextmanager
def serve(*argv):
    # Parse the args.
    args = vars(parser.parse_args(argv))
    application = import_func(args.pop("application"))
    shutdown_timeout = args.pop("shutdown_timeout")
    # Set up logging.
    verbosity = (args.pop("verbose") - args.pop("quiet")) * 10
    logging.basicConfig(level=max(logging.ERROR - verbosity, logging.DEBUG), format="%(message)s")
    logging.getLogger("aiohttp").setLevel(max(logging.INFO - verbosity, logging.DEBUG))
    logger.setLevel(max(logging.INFO - verbosity, logging.DEBUG))
    # Serve the app.
    threads = args.pop("threads")
    loop, executor = start_loop(threads=threads)
    app, handler, server, server_uri = loop.run_until_complete(start_server(application, loop, executor, **args))
    try:
        yield loop, server
    finally:
        loop.run_until_complete(close_server(app, handler, server, server_uri, shutdown_timeout=shutdown_timeout))
        close_loop(loop, executor, server_uri)
        logger.info("Stopped serving on %s", server_uri)


def main():  # pragma: no cover
    sys.path.insert(0, os.getcwd())
    with serve(*sys.argv[1:]) as (loop, executor):
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass


__doc__ = __doc__.format(**HELP, help=textwrap.indent(parser.format_help(), "    "))
