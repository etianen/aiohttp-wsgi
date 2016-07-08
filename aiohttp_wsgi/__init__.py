"""
aiohttp-wsgi
============

WSGI adapter for :mod:`aiohttp`.


Features
--------

-   Run WSGI applications (e.g. `Django`_, `Flask`_) on :mod:`aiohttp`.
-   Handle thousands of client connections, using :mod:`asyncio`.
-   Add :ref:`websockets <aiohttp-web-websockets>` to your existing Python web app!


Resources
---------

-   `Documentation`_ is on Read the Docs.
-   `Issue tracking`_ and `source code`_ is on GitHub.
-   `Continuous integration`_ is on Travis CI.


Usage
-----

.. toctree::
    :maxdepth: 1

    installation


More information
----------------

.. toctree::
    :maxdepth: 1

    contributing
    changelog


.. include:: /_include/links.rst
"""

try:
    import aiohttp  # noqa
except ImportError:
    # The top-level API requires aiohttp, which might not be present if setup.py
    # is importing aiohttp_wsgi to get __version__.
    pass
else:
    from aiohttp_wsgi.api import configure_server, close_server, serve  # noqa
    from aiohttp_wsgi.wsgi import WSGIHandler  # noqa


__version__ = (0, 4, 0)
