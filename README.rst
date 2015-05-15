aiohttp-wsgi
============

**aiohttp-wsgi** is a WSGI adapter for aiohttp.


Features
--------

- Run WSGI applications (e.g. Django, Flask) on `aiohttp <http://aiohttp.readthedocs.org>`_.
- Handle thousands of client connections, using the latest `evented networking library <https://docs.python.org/3.4/library/asyncio.html>`_.
- Add `websockets <http://aiohttp.readthedocs.org/en/v0.15.3/web.html#websockets>`_ to your
  existing Python app!


Installation
------------

1. Install using ``pip install aiohttp-wsgi``.


Usage
-----


``WSGIHandler(application, **kwargs)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`Handler <http://aiohttp.readthedocs.org/en/v0.15.3/web.html#handler>`_ that wraps a WSGI application for use inside an aiohttp `Application <http://aiohttp.readthedocs.org/en/v0.15.3/web_reference.html#aiohttp.web.Application>`_.

::
    
    from aiohttp.web import Application
    from aiohttp_wsgi import WSGIHandler
    from your_app.wsgi import application

    aiohttp_application = Application()
    aiohttp_application.router.add_route("*", "{path_info:.*}")


**Available arguments:**

``url_scheme``
    hint about the URL scheme used to access the application. Corresponds to ``environ["wsgi.uri_scheme"]``. Default value auto-detected to ``"http"`` or ``"https"``.

``stderr``
    A file-like value for WSGI error logging. Corresponds to ``environ["wsgi.errors"]``.  Defaults to ``sys.stderr``.

``executor``
    An `Executor <https://docs.python.org/dev/library/concurrent.futures.html#executor-objects>`_ instance used to run WSGI requests. Defaults to the asyncio base executor.

``loop``
    The asyncio `loop <https://docs.python.org/3.4/library/asyncio-eventloop.html#base-event-loop>`_. Defaults to ``asyncio.get_event_loop()``.


``configure_server(application, **kwargs)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

High-level factory method that wraps a WSGI application in an asyncio `server <https://docs.python.org/3.4/library/asyncio-eventloop.html#server>`_ and aiohttp `Application <http://aiohttp.readthedocs.org/en/v0.15.3/web_reference.html#aiohttp.web.Application>`_.

::

    from aiohttp_wsgi import configure_server
    from your_app.wsgi import application

    server, app = configure_server(application)


**Available arguments:**

``host``
    The IP address to bind the server. Defaults to ``"0.0.0.0"``.

``port``
    The network port to bind the server. Defaults to ``8080``.

``unix_socket``
    The path to a unix socket to bind the server. Overrides ``host``.

``unix_socket_perms``
    A set of filesystem permissions to apply to the unix socket. Defaults to ``0o600``.

``socket``
    A preexisting socket object to use for the server. Overrides ``host``.

``backlog``
    The maximum number of queued connections for the socket. Defaults to ``1024``.

``routes``
    A list of ``(method, path, handler)`` routes to add to the aiohttp `Application <http://aiohttp.readthedocs.org/en/v0.15.3/web_reference.html#aiohttp.web.Application>`_. Defaults to ``[]``.

``static``
    A list of ``(path, dirname)`` static routes to add to the aiohttp `Application <http://aiohttp.readthedocs.org/en/v0.15.3/web_reference.html#aiohttp.web.Application>`_. Defaults to ``[]``.

``on_finish``
    A list of zero-argument callbacks to be executed when the server shuts down.

``script_name``
    The URL prefix to mount the WSGI application. Corresponds to ``environ["SCRIPT_NAME"]``. This should **not** end with a slash. Defaults to ``""``.


``configure_server()`` also accepts all arguments available to ``WSGIHandler()``.



``serve(application, **kwargs)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

High-level factory method that starts a `server <https://docs.python.org/3.4/library/asyncio-eventloop.html#server>`_ running a WSGI application.

::

    from aiohttp_wsgi import serve
    from your_app.wsgi import application

    serve(application)


``serve()`` accepts all arguments available to ``configure_server()``.


Design
------

WSGI applications are run on an asyncio `executor <https://docs.python.org/3.4/library/asyncio-eventloop.html#executor>`_.
This allows existing Python frameworks like Django and Flask to run normally without
blocking the main event loop or resorting to hacks like monkey-patching the Python
standard library. This enables you to write the majority of your application code in a safe,
predictable environment.

Asyncronous parts of your application (e.g. `websockets <http://aiohttp.readthedocs.org/en/v0.15.3/web.html#websockets>`_)
can be run on the same network port, using the `aiohttp router <http://aiohttp.readthedocs.org/en/v0.15.3/web.html#run-a-simple-web-server>`_
to switch between your WSGI app and asyncronous code.


Build status
------------

This project is built on every push using the Travis-CI service.

.. image:: https://travis-ci.org/etianen/aiohttp-wsgi.svg?branch=master
    :target: https://travis-ci.org/etianen/aiohttp-wsgi


Support and announcements
-------------------------

Downloads and bug tracking can be found at the `main project
website <http://github.com/etianen/aiohttp-wsgi>`_.

    
More information
----------------

The aiohttp-wsgi project was developed by Dave Hall. You can get the code
from the `aiohttp-wsgi project site <http://github.com/etianen/aiohttp-wsgi>`_.
    
Dave Hall is a freelance web developer, based in Cambridge, UK. You can usually
find him on the Internet in a number of different places:

-  `Website <http://www.etianen.com/>`_
-  `Twitter <http://twitter.com/etianen>`_
-  `Google Profile <http://www.google.com/profiles/david.etianen>`_
