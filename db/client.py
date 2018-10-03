import asyncore
import socket
import logging

from resp import RedisProto

# 16 bytes -- buffered i/o. redis/src/server.h
PROTO_IOBUF_LEN = 1024*16

class Client(asyncore.dispatcher):
    """
    TODO: peek into redis's Client type definitions
    """
    def __init__(self, sock, addr, commands, store):
        asyncore.dispatcher.__init__(self, sock)
        self.logger = logging.getLogger("Client " + str(addr))

        self.commands = commands
        self.store = store
        self.buffer = []
        self.parser = RedisProto()

    def writable(self):
        return bool(self.buffer)

    def handle_write(self):
        """
        TODO: peek into redis's writeToClient function
        """
        data = self.buffer.pop()
        sent = self.send(data[:PROTO_IOBUF_LEN])
        if sent < len(data):
            remaining = data[sent:]
            self.buffer.append(remaining)

        self.logger.debug("handle_write() -> (%d) '%s'", sent, data[:sent].rstrip())

    def handle_read(self):
        """
        TODO: peek into redis's readQueryFromClient function
        """

        # consume readable data from socket conn
        data = b""
        while True:
            chunk = self.recv(PROTO_IOBUF_LEN)
            data += chunk
            if len(chunk) < PROTO_IOBUF_LEN:
                break

        data = data.rstrip()
        self.logger.debug("handle_read() -> (%d) '%s'", len(data), data)

        parsed = self.parser.decode(data)
        cmd_name = parsed[0]

        try:
            cmd = self.commands[cmd_name]
        except:
            self.logger.debug("handle_read() -> command '%s' not found in %s", cmd_name, repr(self.commands.keys()))
            self.buffer.insert(0, "INVALID COMMAND\n")
        else:
            ret = cmd.func(self.store, *parsed[1:])
            self.buffer.insert(0, repr(ret) + "\n")

    def handle_close(self):
        """
        TODO: peek into how redis's closes client connections
        """
        self.logger.debug("handle_close()")
        self.close()
