"""
server.py

A TCP server that accepts client connections in a nonblocking manner,
delegates message parsing and redis command execution,
then writes response back to socket.

Uses python's asynchat lib for nonblocking network I/O.

antirez's redis implements something similar to this from scratch in C.
I decided to use Python's built-in event-looping, nonblocking library. Yay.

Both take advantage of passing around references to a map that contains state
about existing client connections or file events. The event loop uses this map
to enqueue and process both network and file I/O at the beginning of each loop.
"""

import asyncore
import socket
import os
import argparse
import logging

import strings
import keys

import resp
from client import ClientHandler
from command import Command
from store import Store
from aof import AOF



# default server settings
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 6379
DEFAULT_TCP_BACKLOG = 10
DEFAULT_AOF = os.getcwd() + "/db.aof"



# global map for event loop to track channels and events
CLIENTS = {}



class Server(asyncore.dispatcher):

    def __init__(self):
        """
        Initialize basic server.
        See init_server_config and init_server for more.
        """
        asyncore.dispatcher.__init__(self, map=CLIENTS)
        self.logger = logging.getLogger("Server")

        # these are the commands supported by the redisnot server
        self.commands = self.command_table()

        # in-memory database with a simple get/set interface
        self.store = Store()


    def handle_accept(self):
        """
        As Server subclasses from asyncore.dispatcher, it expects
        a "handle_accept" method to handle a successful client connection.

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
            redis_command = resp.decode(line.rstrip())

            # lookup command
            cmd_name = redis_command[0]
            try:
                cmd = self.commands[cmd_name]
            except KeyError as e:
                pass

            # execute command to in-memory store
            cmd_args = redis_command[1:]
            ret = cmd.execute(self.store, *cmd_args)


    def init_server_config(self, parser):
        """
        Given an "argparse" object with parsed command line opts,
        update default opts for the server
        """
        self.logger.debug("init_server_config() -> applying server settings")

        self.host = parser.host
        self.port = parser.port
        self.backlog = parser.backlog

        # the append-only filestream plugs into the main event loop.
        # it logs write-commands to file as a way to somewhat persist data.
        self.aof = AOF(file=parser.aof, map=CLIENTS)



    def init_server(self):
        # reconstruct data from current AOF file
        self.logger.debug("init_server() -> loading aof from %s", self.aof.filename)
        self.load_aof()

        # networking. bind and listen to specified address
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((self.host, self.port))

        self.address = self.socket.getsockname()
        self.logger.debug("init_server() -> binding to %s", self.address)






def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--host", help="set host for redis server to bind to", default=DEFAULT_HOST)
    parser.add_argument("--port", help="set port for redis server to listen on", type=int, default=DEFAULT_PORT)
    parser.add_argument("--aof", help="set aof file to replay from and append to", default=DEFAULT_AOF)
    parser.add_argument("--backlog", help="set max queue of incoming connections", default=DEFAULT_TCP_BACKLOG)

    return parser.parse_args()





def main():
    """
    Parses command-line opts, initializes serve settings,
    starts server, and kicks off main non-blocking I/O event loop
    """
    logging.basicConfig(level=logging.DEBUG, format="%(name)s:[%(levelname)s]: %(message)s")
    s = Server()

    cl_args = parse_args()
    s.init_server_config(cl_args)
    s.init_server()

    s.listen(s.backlog)
    asyncore.loop(map=CLIENTS)

if __name__ == "__main__":
    main()
