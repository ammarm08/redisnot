import asyncore
import socket
import logging

TRANSMISSION_SIZE = 1024

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
        sent = self.send(data[:TRANSMISSION_SIZE])
        if sent < len(data):
            remaining = data[sent:]
            self.buffer.append(remaining)

        self.logger.debug("handle_write() -> (%d) '%s'", sent, data[:sent].rstrip())

    def handle_read(self):
        """
        TODO: peek into redis's writeToClient function
        """
        data = self.recv(TRANSMISSION_SIZE)
        self.logger.debug("handle_read() -> (%d) '%s'", len(data), data.rstrip())

        # event loop only knows this is writable if buffer has data
        # TODO: for now, this is just an echo server
        self.buffer.insert(0, data)

    def handle_close(self):
        """
        TODO: peek into how redis's closes client connections
        """
        self.logger.debug("handle_close()")
        self.close()
