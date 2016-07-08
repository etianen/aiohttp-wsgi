aiohttp-wsgi changelog
======================


Latest
------

- Dropped support for Python 3.4.


0.4.0
-----

- Requests over 512KB will be buffered in a temporary file. Can be configured using the ``inbuf_overflow`` setting.
- **Breaking**: Maximum request body size is now 1GB. Can be configured using the ``max_request_body_size`` setting.
- **Breaking**: Minimum aiohttp version is now 0.21.2.


0.3.0
-----

- ``PATH_INFO`` and ``SCRIPT_NAME`` now contain URL-quoted non-ascii characters, as per PEP3333.
- **Breaking**: Removed support for Python3.3.
- **Breaking**: Minimum aiohttp version is now 0.19.0.


0.2.6
-----

- Excluded tests from distribution.


0.2.5
-----

- Updated to work with breaking changes in aiohttp 0.17.0.


0.2.4
-----

- Workaround for error in asyncio debug mode on some Python versions when using a callable object, ``WSGIHandler.handle_request``.


0.2.3
-----

- Fixed bug with parsing SCRIPT_NAME.


0.2.2
-----

- Implemented a standalone concurrent utility module for switching between the event loop and an executor.
  See ``aiohttp_wsgi.concurrent`` module for more info.


0.2.1
-----

- Added `on_finish` parameter to `serve()` and `configure_server()`.
- Improved performance and predictability of processing streaming iterators from WSGI applications.


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
