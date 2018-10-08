"""
aof.py

The AOF (append-only file) object appends write logs
asynchronously to the provided .aof file

The AOF object is passed a reference to the main server's map of
sockets/"channels". This means that all write activity to the AOF
is handled asynchronously and in a nonblocking fashion from within
the same event loop that handles all network connections.
"""

import resp
import asyncore
import logging

class AOF(asyncore.file_dispatcher):
    def __init__(self, file="", map={}):
        self.logger = logging.getLogger("AOF")
        self.buffer = b""

        try:
            fd = open(file, "ab+")
        except Exception as e:
            self.logger.debug("__init__() -> error reading file %s", file)
            raise e
        else:
            asyncore.file_dispatcher.__init__(self, fd, map=map)


    def writable(self):
        return len(self.buffer) > 0


    def handle_write(self):
        self.logger.debug("handle_write() -> writing aof buffer %s", self.buffer)
        written = self.write(self.buffer)
        self.buffer = self.buffer[written:]


    def append(self, redis_command):
        self.logger.debug("append() -> redis command %s", repr(redis_command))
        serialized = resp.encode(redis_command)
        self.buffer = serialized
