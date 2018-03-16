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
import logging
import os
import sys
import textwrap
from importlib import import_module
import aiohttp_wsgi
from aiohttp_wsgi.wsgi import serve, DEFAULTS, HELP


logger = logging.getLogger(__name__)


parser = argparse.ArgumentParser(
    prog="aiohttp-wsgi-serve",
    description="Run a WSGI application.",
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


def import_func(func):
    assert ":" in func, "{!r} should have format 'module:callable'".format(func)
    module_name, func_name = func.split(":", 1)
    module = import_module(module_name)
    func = getattr(module, func_name)
    return func


def parse_static_item(static_item):
    assert "=" in static_item, "{!r} should have format 'path=directory'"
    return static_item.split("=", 1)


def main():
    sys.path.insert(0, os.getcwd())
    # Parse the args.
    kwargs = vars(parser.parse_args(sys.argv[1:]))
    application = import_func(kwargs.pop("application"))
    static = list(map(parse_static_item, kwargs.pop("static")))
    # Set up logging.
    verbosity = (kwargs.pop("verbose") - kwargs.pop("quiet")) * 10
    logging.basicConfig(level=max(logging.ERROR - verbosity, logging.DEBUG), format="%(message)s")
    logging.getLogger("aiohttp").setLevel(max(logging.INFO - verbosity, logging.DEBUG))
    logger.setLevel(max(logging.INFO - verbosity, logging.DEBUG))
    # Serve!
    serve(application, static=static, **kwargs)


__doc__ = __doc__.format(help=textwrap.indent(parser.format_help(), "    "), **HELP)
