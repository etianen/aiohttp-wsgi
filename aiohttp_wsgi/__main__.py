import argparse
import logging
from aiohttp_wsgi.api import serve, DEFAULTS, HELP


def main():
    arg_help = HELP.copy()
    # Set up the argument parser.
    parser = argparse.ArgumentParser(
        description="Run a WSGI application.",
    )
    parser.add_argument(
        "application",
        metavar="module:application",
        type=str,
        help=arg_help.pop("application").replace("``", ""),
    )
    parser.add_argument(
        "--host",
        action="append",
        help="{}. Can be specified multiple times.".format(arg_help.pop("host").replace("``", ""))
    )
    for arg_name, arg_help in sorted(arg_help.items()):
        arg_default = DEFAULTS[arg_name]
        parser.add_argument(
            "--{}".format(arg_name.replace("_", "-")),
            default=arg_default,
            help=arg_help.replace("``", ""),
            type=type(arg_default) if arg_default is not None else str,
        )
    parser.add_argument(
        "--verbose",
        "-v",
        action="count",
        default=0,
        help="Increase verbosity. Can be specified multiple times.",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="count",
        default=0,
        help="Decrease verbosity. Can be specified multiple times.",
    )
    # Parse the arguments.
    args = vars(parser.parse_args())
    # Set up logging.
    verbosity = (args.pop("verbose") - args.pop("quiet")) * 10
    logging.basicConfig(level=max(logging.ERROR - verbosity, logging.DEBUG), format="%(message)s")
    logging.getLogger("aiohttp").setLevel(max(logging.INFO - verbosity, logging.DEBUG))
    # Serve the app.
    serve(**args)


if __name__ == "__main__":
    main()
