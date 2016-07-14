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
import textwrap
import aiohttp_wsgi
from aiohttp_wsgi.api import start_server, DEFAULTS, HELP
from aiohttp_wsgi.utils import parse_sockname


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
    help=(
        "Static route mappings in the form 'path=directory'. "
        "`path` must start with a slash, but not end with a slash."
    ),
)
add_argument(
    "--script-name",
)
add_argument(
    "--shutdown-timeout",
)
add_argument(
    "--url-scheme",
    type=str,
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


def main():
    args = vars(parser.parse_args())
    shutdown_timeout = args.pop("shutdown_timeout")
    # Set up logging.
    verbosity = (args.pop("verbose") - args.pop("quiet")) * 10
    logging.basicConfig(level=max(logging.ERROR - verbosity, logging.DEBUG), format="%(message)s")
    logging.getLogger("aiohttp").setLevel(max(logging.INFO - verbosity, logging.DEBUG))
    # Serve the app.
    loop = asyncio.get_event_loop()
    server = loop.run_until_complete(start_server(loop=loop, **args))
    server_uri = " ".join(
        "http://{}:{}".format(*parse_sockname(socket.getsockname()))
        for socket
        in server.sockets
    )
    server.app.logger.info("Serving on %s", server_uri)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.app.logger.debug("Waiting for server to shut down")
        server.close()
        server.app.logger.debug("Waiting for client connections to terminate")
        loop.run_until_complete(server.wait_closed(shutdown_timeout=shutdown_timeout))
        loop.close()
        server.app.logger.info("Stopped serving on %s", server_uri)


__doc__ = __doc__.format(**HELP, help=textwrap.indent(parser.format_help(), "    "))


if __name__ == "__main__":
    main()
