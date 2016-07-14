import asyncio
import threading
from tempfile import TemporaryFile


def force_str(value):
    return str(value, "latin1") if isinstance(value, (bytes, bytearray, memoryview)) else str(value)


def parse_sockname(sockname):
    if isinstance(sockname, tuple):
        return force_str(sockname[0]), force_str(sockname[1])
    return "unix", force_str(sockname)


class WriteBuffer:

    def __init__(self, watermark, loop, executor):
        # Settings.
        self._watermark = watermark
        # Asyncio.
        self._loop = loop
        self._executor = executor
        # State.
        self._lock = threading.Lock()
        self._alock = asyncio.Lock(loop=loop)
        self._waiter = None
        self._closed = False
        # Memory buffer.
        self._buffer = []
        self._buffer_len = 0
        # File buffer.
        self._file = None
        self._file_pos = 0
        self._file_len = 0

    def _readfile(self):
        with self._lock:
            file_read_len = min(self._watermark, self._file_len)
            self._file.seek(self._file_pos)
            data = self._file.read(file_read_len)
            self._file_len -= file_read_len
            assert self._file_len >= 0
            if self._file_len == 0:
                if self._closed:
                    self._file.close()
                    self._file = None
                else:
                    self._file.truncate()
                self._file_pos = 0
            else:
                self._file.seek(0, 2)
                self._file_pos += file_read_len
            return data

    async def readany(self):
        with await self._alock, self._lock:
            assert self._waiter is None
            if self._buffer_len > 0:
                # Handle buffered data.
                data = b"".join(self._buffer)
                del self._buffer[:]
                self._buffer_len = 0
                return data
            elif self._file_len > 0:
                # Handle file data.
                waiter = self._loop.run_in_executor(self._executor, self._readfile)
            elif self._closed:
                # Handle closed buffer.
                return b""
            else:
                # Wait for more data.
                waiter = self._waiter = asyncio.Future(loop=self._loop)
        return await waiter

    def write(self, data):
        if data:
            with self._lock:
                if self._waiter is not None:
                    # Hand over data immediately.
                    self._loop.call_soon_threadsafe(self._waiter.set_result, data)
                    self._waiter = None
                elif self._buffer_len >= self._watermark or self._file_len > 0:
                    # Write to temp file.
                    if self._file is None:
                        self._file = TemporaryFile()
                    self._file.write(data)
                    self._file_len += len(data)
                else:
                    # Buffer in memory.
                    self._buffer.append(data)
                    self._buffer_len += len(data)

    async def write_eof(self):
        with await self._alock, self._lock:
            assert not self._closed
            self._closed = True
            if self._waiter is not None:
                self._waiter.set_result(b"")
                self._waiter = None

    def assert_flushed(self):
        assert self._waiter is None
        assert len(self._buffer) == 0
        assert self._buffer_len == 0
        assert self._file is None
        assert self._file_pos == 0
        assert self._file_len == 0
