aiohttp-wsgi
=====

**aiohttp-wsgi** is a WSGI adapter for aiohttp.


Features
--------

- Run WSGI applications (e.g. Django, Flask) on `aiohttp <http://aiohttp.readthedocs.org>`_.
- Handle thousands of client connections, using the latest `evented networking library <https://docs.python.org/3.4/library/asyncio.html>`_.
- Add `websockets <http://aiohttp.readthedocs.org/en/v0.14.4/web.html#websockets>`_ to your
  existing Python webapp!


Design
------

WSGI applications are run in an asyncio `executor <https://docs.python.org/3.4/library/asyncio-eventloop.html#executor>`_.
This allows existing Python frameworks like Django and Flask to run normally without
blocking the main event loop or resorting to hacks like monkey-patching the Python
standard library. This enables you to write the majority of your application code in a safe,
predictable environment.

Asyncronous parts of your application (e.g. `websockets <http://aiohttp.readthedocs.org/en/v0.14.4/web.html#websockets>`_)
can be run on the same network port, using the `aiohttp router <http://aiohttp.readthedocs.org/en/v0.14.4/web.html#run-a-simple-web-server>`_
to switch between your WSGI app and asyncronous code.


Installation
------------

1. Install using ``pip install aiohttp-wsgi``.


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
