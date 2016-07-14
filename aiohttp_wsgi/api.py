import os
from importlib import import_module
from aiohttp.log import access_logger
from aiohttp.web import Application, StaticRoute
from aiohttp_wsgi.wsgi import WSGIHandler, DEFAULTS, HELP
from aiohttp_wsgi.utils import parse_sockname


class Server:

    def __init__(self, app, handler, server):
        self.app = app
        self._handler = handler
        self._server = server

    @property
    def sockets(self):
        return self._server.sockets

    def close(self):
        # Clean up unix sockets.
        for socket in self.sockets:
            host, port = parse_sockname(socket.getsockname())
            if host == "unix":
                os.unlink(port)
        # Close the server.
        self._server.close()

    async def wait_closed(self, *, shutdown_timeout=60.0):
        await self._server.wait_closed()
        await self.app.shutdown()
        await self._handler.finish_connections(shutdown_timeout)
        await self.app.cleanup()


def import_func(func):
    if isinstance(func, str):
        assert ":" in func, "{!r} should have format 'module:callable'".format(func)
        module_name, func_name = func.split(":", 1)
        module = import_module(module_name)
        func = getattr(module, func_name)
    assert callable(func), "{!r} is not callable".format(func)
    return func


def format_path(path):
    assert not path.endswith("/"), "{!r} name should not end with /".format(path)
    if path == "":
        path = "/"
    assert path.startswith("/"), "{!r} name should start with /".format(path)
    return path


async def start_server(
    application,
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
    # Asyncio config.
    loop,
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
        WSGIHandler(import_func(application), loop=loop, **kwargs),
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
    # All done!
    return Server(app, handler, server)


DEFAULTS = DEFAULTS.copy()
DEFAULTS.update(start_server.__kwdefaults__)
DEFAULTS.update(Server.wait_closed.__kwdefaults__)

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
    "shutdown_timeout": (
        "Timeout when closing client connections on server shutdown. Defaults to ``{shutdown_timeout!r}``."
    ).format(**DEFAULTS),
})
