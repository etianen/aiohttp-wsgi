aiohttp-wsgi
=====

**aiohttp-wsgi** is a WSGI adapter for aiohttp.


Features
--------

- Run WSGI applications (e.g. Django, Flask) on aiohttp.
- Handle thousands of client connections, using the latest evented Python networking library.
- Applications are run in a thread pool, to avoid blocking the event loop.
- Run websockets and blocking WSGI applications on the same network port!


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
