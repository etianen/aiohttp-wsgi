"""
Simple framework for safely calling into sync code from async, and back again.

From within the event loop:

    yield from concurrent.run_in_executor(func, *args)

From within an executor:

    concurrent.run_in_loop(func, *args)

This API is currently unstable, and may be subject to change.
"""
import asyncio, threading
from concurrent.futures import Future
from functools import wraps, partial


class LoopContext(threading.local):

    def __init__(self):
        self._is_executor = False
        # Local variables used by executor threads.
        self._loop = None

    def is_executor(self):
        """
        Returns whether the current thread is running a function that was
        called using ``run_in_executor``.
        """
        return self._is_executor

    @asyncio.coroutine
    def run_in_executor(self, func, *args, loop=None, executor=None):
        """
        Runs the given func in the executor, returning a Future.

        This function can only be called from within the event loop.
        """
        assert not self.is_executor(), "Cannot call run_in_executor from within an executor."
        loop = loop or asyncio.get_event_loop()
        # Wrap the func to tag the thread as an executor.
        @wraps(func)
        def run_func(*args):
            self._is_executor = True
            self._loop = loop
            try:
                return func(*args)
            finally:
                self._is_executor = False
                self._loop = None
        # Run the func in the executor.
        return (yield from loop.run_in_executor(executor, run_func, *args))

    def run_in_loop(self, func, *args):
        """
        Runs the given func in the event loop, returning a future.

        This function can only be called from within a function that was called
        using ``run_in_executor()``.
        """
        assert self.is_executor(), "Cannot call run_in_loop from within an event loop."
        # Chain the asyncio future onto a concurrent future.
        future = Future()
        @asyncio.coroutine
        @wraps(func)
        def run_func():
            if future.set_running_or_notify_cancel():
                try:
                    future.set_result((yield from func(*args)))
                except Exception as ex:  # pragma: no cover
                    future.set_exception(ex)
        # Run the function in the loop, and wait for it to complete.
        self._loop.call_soon_threadsafe(partial(asyncio.async, run_func(), loop=self._loop))
        return future.result()


_context = LoopContext()

is_executor = _context.is_executor
run_in_executor = _context.run_in_executor
run_in_loop = _context.run_in_loop
