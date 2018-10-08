"""
aof.py

The AOF (append-only file) object appends write logs
asynchronously to the provided .aof file

The AOF object is passed a reference to the main server's map of
sockets/"channels". This means that all write activity to the AOF
is handled asynchronously and in a nonblocking fashion from within
the same event loop that handles all network connections.

The "writable" and "handle_write" events must be implemented, as
the asyncore.file_dispatcher interface expects to see those in order
to know how to know what to do when writing to file
"""

import resp
import asyncore
import logging

class AOF(asyncore.file_dispatcher):
    def __init__(self, file="", map={}):
        """
        Opens the file, registers it to the global event loop,
        and creates a buffer that's used by object to know when
        there is data to write to disk.
        """
        self.logger = logging.getLogger("AOF")
        self.filename = file
        self.buffer = b""

        try:
            self.fd = open(file, "ab+")
        except Exception as e:
            self.logger.debug("__init__() -> error reading file %s", file)
            raise e
        else:
            asyncore.file_dispatcher.__init__(self, self.fd, map=map)


    def writable(self):
        return len(self.buffer) > 0


    def handle_write(self):
        self.logger.debug("handle_write() -> writing aof buffer %s", self.buffer)
        written = self.write(self.buffer)
        self.buffer = self.buffer[written:]


    def append(self, redis_command):
        """
        Serializes a redis command and sets it as the buffer.
        Doing this tells the event loop that this channel is ready to write.
        """
        self.logger.debug("append() -> redis command %s", repr(redis_command))
        serialized = resp.encode(redis_command)
        self.buffer = serialized + "\n"


    def read_aof_line(self):
        """
        Sets read position to beginning of file, then returns
        a line-reading iterator for the caller to use to progressively
        read through the AOF file.
        """

        # seek to beginning. note that since this is in append mode,
        # at next write, will move automatically to end of file
        self.fd.seek(0)

        # return line-reading iterator
        return enumerate(self.fd)
