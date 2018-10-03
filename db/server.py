"""
server.py

A TCP server that accepts client connections,
delegates message parsing and redis command execution,
then writes response back to socket

Uses python's asyncore lib for nonblocking network I/O
"""

import asyncore
import socket
import logging

from client import ClientHandler
from command import Command
from store import Store

import strings
import keys

HOST = "0.0.0.0"
PORT = 6379
TCP_BACKLOG = 10

class Server(asyncore.dispatcher):

    def __init__(self, address):
        """
        Initialize server config and redisnot commands
        """
        asyncore.dispatcher.__init__(self)
        self.logger = logging.getLogger("Server")

        self.commands = self.command_table()
        self.store = Store()

        # networking
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(address)
        self.address = self.socket.getsockname()
        self.logger.debug("binding to %s", self.address)

        self.listen(TCP_BACKLOG)


    def handle_accept(self):
        """
        As Server subclasses from asyncore.dispatcher, it expects
        a handle_accept method to handle a successful client connection.

        Delegates connection handling to ClientHandler.
        """
        client_stats = self.accept()
        if client_stats is not None:
            sock, addr = client_stats
            self.logger.debug("handle_accept() -> %s", addr)
            ClientHandler(sock, addr, self.commands, self.store)


    def command_table(self):
        """
        Maps command names to the functions that execute them.
        Server maintains this dictionary and passes reference to it
        to client handlers.

        "r" -> read
        "w" -> write
        "+" -> log to aof file
        """
        commands = [
            # String commands (incomplete)
            Command("get", strings.get_command, "r"),
            # Command("getset", strings.getset_command, "w+"),
            Command("set", strings.set_command, "w+"),

            # Key commands (incomplete)
            # Command("del", keys.del_command, "w+"),
            # Command("keys", keys.keys_command, "r"),
            # Command("exists", keys.exists_command, "r")
        ]

        command_table = {}
        for command in commands:
            command_table[command.name.upper()] = command
            command_table[command.name.lower()] = command

        self.logger.debug("command_table() -> registered commands: %s", repr(command_table.keys()))
        return command_table


def main():
    """
    Starts server and kicks off main non-blocking I/O event loop
    """
    logging.basicConfig(level=logging.DEBUG, format="%(name)s:[%(levelname)s]: %(message)s")
    s = Server((HOST, PORT))
    asyncore.loop()

if __name__ == "__main__":
    main()
