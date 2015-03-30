import asyncio, os
from collections.abc import Mapping

from aiohttp.web import Application

from aiohttp_wsgi import middleware
from aiohttp_wsgi.utils import parse_sockname


def configure_server(application, *,

    # Server config.
    host = "0.0.0.0",
    port = 8080,

    # Unix server config.
    unix_socket = None,
    unix_socket_perms = 0o600,

    # Prexisting socket config.
    socket = None,

    # Shared server config.
    backlog = 1024,

    # aiohttp config.
    routes = (),
    static = (),

    # Asyncio config.
    loop = None,

    # Handler config.
    **kwargs

):
    loop = loop or asyncio.get_event_loop()
    # Create the WSGI handler.
    wsgi_middleware = middleware.wsgi(application,
        loop = loop,
        **kwargs
    )
    # Wrap the application in an executor.
    app = Application(
        loop = loop,
        middlewares = [wsgi_middleware],
    )
    # Add routes.
    for method, path, handler in routes:
        app.router.add_route(method, path, handler)
    # Add static routes.
    if isinstance(static, Mapping):
        static = static.items()
    for path, dirname in static:
        app.router.add_static(path, dirname)
    # Set up the server.
    shared_server_kwargs = {
        "backlog": backlog,
    }
    if unix_socket is not None:
        server_future = loop.create_unix_server(app.make_handler(),
            path = unix_socket,
            **shared_server_kwargs
        )
    elif socket is not None:
        server_future = loop.create_server(app.make_handler(),
            sock = socket,
            **shared_server_kwargs
        )
    else:
        server_future = loop.create_server(app.make_handler(),
            host = host,
            port = port,
            **shared_server_kwargs
        )
    server = loop.run_until_complete(server_future)
    app.logger.info("Serving on http://%s:%s", *parse_sockname(server.sockets[0].getsockname()))
    # Set socket permissions.
    if unix_socket is not None:
        os.chmod(unix_socket, unix_socket_perms)
    # All done!
    return server, app


def close_server(server, app, *, loop=None):
    loop = loop or asyncio.get_event_loop()
    # Close the server.
    app.logger.debug("Waiting for server to shut down")
    server.close()
    loop.run_until_complete(server.wait_closed())
    # Close the http handler.
    app.logger.debug("Waiting for client connections to terminate")
    loop.run_until_complete(app.finish())
    # Close the loop.
    loop.close()
    app.logger.info("Server has shut down")


def serve(application, *, loop=None, **kwargs):  # pragma: no cover
    loop = loop or asyncio.get_event_loop()
    server, app = configure_server(application, loop=loop, **kwargs)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        close_server(server, app, loop=loop)
