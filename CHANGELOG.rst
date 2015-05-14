aiohttp-wsgi changelog
======================


0.2.0
-----

- **BREAKING**: Removed WSGI middleware in favor of WSGIHandler (required to support aiohttp 0.15.0 without hacks).
- Added support for aiohttp 0.15.0.


0.1.2
-----

- Added `socket` argument to `serve()` and `configure_server()`.
- Added `backlog` argument to `serve()` and `configure_server()`.


0.1.1
-----

- Fixed RuntimeError in aiohttp (@jnurmine).
- Added `routes` argument to `serve()` and `configure_server()`.
- Added `static` argument to `serve()` and `configure_server()`.


0.1.0
-----

- First experimental release.
- Buffering WSGI web server with threaded workers.
- Public configure_server() and serve() API.
