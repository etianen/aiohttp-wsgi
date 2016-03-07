import asyncio, os
from collections.abc import Mapping

from aiohttp.web import Application

from aiohttp_wsgi.wsgi import WSGIHandler
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
    on_finish = (),

    # Asyncio config.
    loop = None,

    # Handler config.
    script_name = "",
    **kwargs

):
    loop = loop or asyncio.get_event_loop()
    app = Application(
        loop = loop,
    )
    # Add routes.
    for method, path, handler in routes:
        app.router.add_route(method, path, handler)
    # Add static routes.
    if isinstance(static, Mapping):
        static = static.items()
    for path, dirname in static:
        app.router.add_static(path, dirname)
    # Add on finish callbacks.
    for on_finish_callback in on_finish:
        app.on_shutdown.append(on_finish_callback)
    # The WSGI spec says that script name should not end with a slash. However,
    # aiohttp wants all route paths to start with a forward slash. This means
    # we need a special case for mounting on the root.
    if script_name.endswith("/"):  # pragma: no cover
        raise ValueError("Script name should not end with /")
    if script_name == "":
        script_name = "/"
    if not script_name.startswith("/"):  # pragma: no cover
        raise ValueError("Script name should start with /")
    # Add the wsgi application. This has to be last.
    app.router.add_route("*", "{}{{path_info:.*}}".format(script_name), WSGIHandler(application, **kwargs).handle_request)
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
