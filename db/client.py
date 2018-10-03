import asyncore
import socket
import logging

# borrowed from redis/src/server.h
PROTO_IOBUF_LEN = 1024*16

class Client(asyncore.dispatcher):
    """
    TODO: peek into redis's Client type definitions
    """
    def __init__(self, sock, addr):
        asyncore.dispatcher.__init__(self, sock)
        self.logger = logging.getLogger("Client " + str(addr))
        self.buffer = []

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

        # TODO: parse data into a redis-protocol structure


        # TODO: call the resulting redis command


        # TODO: send the appropriate response
        self.logger.debug("handle_read() -> (%d) '%s'", len(data), data.rstrip())
        self.buffer.insert(0, data)

    def handle_close(self):
        """
        TODO: peek into how redis's closes client connections
        """
        self.logger.debug("handle_close()")
        self.close()
