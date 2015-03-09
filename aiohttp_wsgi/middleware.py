import asyncio

from aiohttp_wsgi.wsgi import WSGIHandler


def wsgi(application, *, script_name="", **kwargs):
    # Create the WSGI handler.
    wsgi_handler = WSGIHandler(application,
        script_name = script_name,
        **kwargs
    )
    # Create the middleware factory.
    @asyncio.coroutine
    def middleware_factory(app, handler):
        # Create the middleware.
        @asyncio.coroutine
        def middleware(request):
            # See if the script name matches.
            if request.path.startswith(script_name):
                # See if a specific route matches the app.
                route = (yield from app.router.resolve(request))
                if route.route is None:
                    # Run the WSGI app.
                    return (yield from wsgi_handler(request))
            return (yield from handler(request))
        # All done!
        return middleware
    # All done!
    return middleware_factory
