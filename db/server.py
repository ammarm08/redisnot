"""
server.py

A TCP server that accepts client connections,
delegates message parsing and redis command execution,
then writes response back to client

Uses python's asyncore lib for nonblocking network I/O
"""

import asyncore
import socket
import logging

from client import Client

HOST = "0.0.0.0"
PORT = 6379
SOMAXCONN = 5

class Server(asyncore.dispatcher):

    def __init__(self, address):
        """
        Initialize server config and redisnot commands

        Similar to initServerConfig and initServer in
        antirez/redis/src/server.c
        """
        asyncore.dispatcher.__init__(self)
        self.logger = logging.getLogger("Server")

        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(address)

        self.address = self.socket.getsockname()

        self.logger.debug("binding to %s", self.address)
        self.listen(SOMAXCONN)

    def handle_accept(self):
        """
        Upon succesful client connection to socket, delegate
        processing to Client

        Similar to createClient in antirez/redis/src/networking.c
        """
        client_stats = self.accept()
        if client_stats is not None:
            sock, addr = client_stats
            self.logger.debug("handle_accept() -> %s", addr)
            Client(sock, addr)



def main():
    logging.basicConfig(level=logging.DEBUG, format="%(name)s:[%(levelname)s]: %(message)s")
    s = Server((HOST, PORT))
    asyncore.loop()

if __name__ == "__main__":
    main()
