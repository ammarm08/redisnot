"""
server.py

A TCP server that accepts client connections in a nonblocking manner,
delegates message parsing and redis command execution,
then writes response back to socket

Uses python's asynchat lib for nonblocking network I/O
"""

import asyncore
import socket
import os
import logging

import strings
import keys

import resp
from client import ClientHandler
from command import Command
from store import Store
from aof import AOF


HOST = "0.0.0.0"
PORT = 6379
TCP_BACKLOG = 10
CLIENTS = {}
AOF_FILE = os.getcwd() + "/db.aof"


class Server(asyncore.dispatcher):

    def __init__(self, address):
        """
        Initialize server config and redisnot commands
        """
        asyncore.dispatcher.__init__(self, map=CLIENTS)
        self.logger = logging.getLogger("Server")

        # these are the commands supported by the redisnot server
        self.commands = self.command_table()

        # in-memory database with a simple get/set interface
        self.store = Store()

        # the append-only filestream plugs into the main event loop.
        # it logs write-commands to file as a way to somewhat persist data.
        self.aof = AOF(file=AOF_FILE, map=CLIENTS)

        # reconstruct data from current AOF file
        self.load_aof()

        # networking. bind and listen to specified address
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(address)
        self.address = self.socket.getsockname()
        self.logger.debug("__init__() -> binding to %s", self.address)

        self.listen(TCP_BACKLOG)


    def handle_accept(self):
        """
        As Server subclasses from asyncore.dispatcher, it expects
        a handle_accept method to handle a successful client connection.

        Delegates connection handling to ClientHandler.
        """
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            self.logger.debug("handle_accept() -> %s", addr)

            # passes along references to socket, event loop map,
            # commands, store, and aof
            ClientHandler(
                sock=sock,
                addr=addr,
                map=CLIENTS,
                commands=self.commands,
                store=self.store,
                aof=self.aof
            )


    def command_table(self):
        """
        Maps command names to the functions that execute them.
        Server maintains this dictionary and passes reference to it
        to client handlers.
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


    def load_aof(self):
        """
        Replays the AOF from beginning to end. The AOF only
        consists of write commands, so presumably if no commands
        got lost, the AOF should fully reconstruct the data store.
        """
        for line_no, line in self.aof.read_aof_line():
            self.logger.debug("load_aof() -> reading line # %d: %s", line_no, line)

            # parse serialized command
            redis_command = resp.decode(line)

            # lookup command
            cmd_name = redis_command[0]
            try:
                cmd = self.commands[cmd_name]
            except KeyError as e:
                pass

            # execute command to in-memory store
            cmd_args = redis_command[1:]
            ret = cmd.execute(self.store, *cmd_args)


def main():
    """
    Starts server and kicks off main non-blocking I/O event loop
    """
    logging.basicConfig(level=logging.DEBUG, format="%(name)s:[%(levelname)s]: %(message)s")
    s = Server((HOST, PORT))
    asyncore.loop(map=CLIENTS)

if __name__ == "__main__":
    main()
