import argparse
import logging
import aiohttp_wsgi
from aiohttp_wsgi.api import serve, DEFAULTS, HELP


parser = argparse.ArgumentParser(
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
    if kwargs["action"] == "store":
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
    "--script-name",
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
    version="aiohttp-wsgi v{}".format(".".join(map(str, aiohttp_wsgi.__version__))),
)


def main():
    args = vars(parser.parse_args())
    # Set up logging.
    verbosity = (args.pop("verbose") - args.pop("quiet")) * 10
    logging.basicConfig(level=max(logging.ERROR - verbosity, logging.DEBUG), format="%(message)s")
    logging.getLogger("aiohttp").setLevel(max(logging.INFO - verbosity, logging.DEBUG))
    # Serve the app.
    serve(**args)


if __name__ == "__main__":
    main()
