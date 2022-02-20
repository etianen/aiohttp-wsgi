aiohttp-wsgi changelog
======================

.. currentmodule:: aiohttp_wsgi

0.10.0
------

- Removed ``loop`` argument from :class:`WSGIHandler` constructor.
- Fixed tests to work with aiohttp 3.8.1+.


0.9.1
-----

- **Bugfix:** Added in ``py.typed`` PEP 561 marker file.


0.9.0
-----

- Added PEP 484 / PEP 561 type annotations.
- **Bugfix:** Fixed crash when running with ``PYTHONOPTIMIZE=2``.


0.8.2
-----

- Added support for ``aiohttp >= 3.4`` (@michael-k).


0.8.1
-----

- Added ``static_cors`` argument to :func:`serve()`, allowing CORS to be configured for static files.
- Added ``--static-cors`` argument to :doc:`aiohttp-wsgi-serve <main>` command line interface.


0.8.0
-----

- Added new :func:`serve()` helper for simple WSGI applications that don't need :ref:`websockets <aiohttp-web-websockets>` or :ref:`async request handlers <aiohttp-web-handler>` (@etianen).
- Updated :mod:`aiohttp` dependency to ``>=3`` (@etianen).
- Improved error message for invalid hop-by-hop headers (@chriskuehl).
- **Breaking:** Dropped support for Python 3.4 (@etianen).


0.7.1
-----

- Compatibility with aiohttp>=2.3.1 (@etianen).


0.7.0
-----

- Compatibility with aiohttp>=2 (@etianen).
- Added ``"RAW_URI"`` and ``"REQUEST_URI"`` keys to the environ dict, allowing the original quoted path to be accessed (@dahlia).


0.6.6
-----

- Python 3.4 support (@fscherf).


0.6.5
-----

- Fixed bug with unicode errors in querystring (@Антон Огородников).


0.6.4
-----

- Updating aiohttp dependency to >= 1.2.
- Fixing aiohttp deprecation warnings.


0.6.3
-----

-   Updating aiohttp dependency to >= 1.0.


0.6.2
-----

-   Fixing incorrect quoting of ``PATH_INFO`` and ``SCRIPT_NAME`` in environ.


0.6.1
-----

-   Upgrading :mod:`aiohttp` dependency to >= 0.22.2.


0.6.0
-----

-   Fixing missing multiple headers sent from start_response.
-   **Breaking:** Removed outbuf_overflow setting. Responses are always buffered in memory.
-   **Breaking:** WSGI streaming responses are buffered fully in memory before being sent.


0.5.2
-----

-   Identical to 0.5.1, after PyPi release proved mysteriously broken.


0.5.1
-----

-   ``outbuf_overflow`` no longer creates a temporary buffer file, instead pausing the worker thread until the pending response has been flushed.


0.5.0
-----

-   Minimum :ref:`aiohttp <aiohttp-web>` version is now 0.21.2.
-   Added :doc:`aiohttp-wsgi-serve <main>` command line interface.
-   Responses over 1MB will be buffered in a temporary file. Can be configured using the ``outbuf_overflow`` argument to :class:`WSGIHandler`.
-   **Breaking:** Removed support for Python 3.4.
-   **Breaking:** Removed ``aiohttp.concurrent`` helpers, which are no longer required with Python 3.5+.
-   **Breaking:** Removed ``configure_server()`` and ``close_server()`` helpers. Use :class:`WSGIHandler` directly.
-   **Breaking:** Removed ``serve()`` helpers. Use the :doc:`command line interface <main>` directly.


0.4.0
-----

-   Requests over 512KB will be buffered in a temporary file. Can be configured using the ``inbuf_overflow`` argument to :class:`WSGIHandler`.
-   Minimum :ref:`aiohttp <aiohttp-web>` version is now 0.21.2.
-   **Breaking**: Maximum request body size is now 1GB. Can be configured using the ``max_request_body_size`` argument to :class:`WSGIHandler`.


0.3.0
-----

-   ``PATH_INFO`` and ``SCRIPT_NAME`` now contain URL-quoted non-ascii characters, as per `PEP3333`_.
-   Minimum :ref:`aiohttp <aiohttp-web>` version is now 0.19.0.
-   **Breaking**: Removed support for Python3.3.


0.2.6
-----

-   Excluded tests from distribution.


0.2.5
-----

-   Updated to work with breaking changes in :ref:`aiohttp <aiohttp-web>` 0.17.0.


0.2.4
-----

-   Workaround for error in :mod:`asyncio` debug mode on some Python versions when using a callable object, ``WSGIHandler.handle_request``.


0.2.3
-----

-   Fixed bug with parsing ``SCRIPT_NAME``.


0.2.2
-----

-   Implemented a standalone concurrent utility module for switching between the event loop and an executor.
    See ``aiohttp_wsgi.concurrent`` for more info.


0.2.1
-----

-   Added ``on_finish`` parameter to ``serve()`` and ``configure_server()``.
-   Improved performance and predictability of processing streaming iterators from WSGI applications.


0.2.0
-----

-   **BREAKING**: Removed ``WSGIMiddleware`` in favor of :class:`WSGIHandler` (required to support :ref:`aiohttp <aiohttp-web>` 0.15.0 without hacks).
-   Added support for :ref:`aiohttp <aiohttp-web>` 0.15.0.


0.1.2
-----

-   Added ``socket`` argument to ``serve()`` and ``configure_server()``.
-   Added ``backlog`` argument to ``serve()`` and ``configure_server()``.


0.1.1
-----

-   Fixed ``RuntimeError`` in :ref:`aiohttp <aiohttp-web>` (@jnurmine).
-   Added ``routes`` argument to ``serve()`` and ``configure_server()``.
-   Added ``static`` argument to ``serve()`` and ``configure_server()``.


0.1.0
-----

-   First experimental release.
-   Buffering WSGI web server with threaded workers.
-   Public ``configure_server()`` and ``serve()`` API.


.. include:: /_include/links.rst
