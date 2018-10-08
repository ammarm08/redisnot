"""
client.py

The Server class delegates all socket connection handling
to the ClientHandler class.

This class reads a redis query from a readable socket connection,
then delegates the parsing and execution of the query to
resp.py and command.py, respectively.

ClientHandler receives references to the command table and logical store
from the Server that accepted the client connection.

Many of the class methods override expected methods from asynchat
"""

import asynchat
import logging
import resp

# TODO: reset to 16kb. 16 kb of i/o reads at a time (redis/src/server.h)
PROTO_IOBUF_LEN = 4

class ClientHandler(asynchat.async_chat):
    """
    TODO: peek into redis's Client type definitions

    Initializes with references to the command table and logical store.
    Sets buffers used to consume requests and build responses.
    """

    ac_in_buffer_size = PROTO_IOBUF_LEN
    ac_out_buffer_size = PROTO_IOBUF_LEN


    def __init__(self, sock=None, addr=None, map={}, commands={}, store=None):
        asynchat.async_chat.__init__(self, sock=sock, map=map)
        self.logger = logging.getLogger("Client " + str(addr))

        self.commands = commands
        self.store = store
        self.query_buffer = []

        self.set_terminator("\n")


    def collect_incoming_data(self, data):
        self.logger.debug("collect_incoming_data() -> entering read of %s", data)
        self.query_buffer.append(data)


    def found_terminator(self):
        data = "".join(self.query_buffer).rstrip()
        self.query_buffer = []
        self.logger.debug("found_terminator() -> (%d) '%s'", len(data), data)

        redis_command = resp.decode(data)
        reply = self.process_command(redis_command)

        self.push(reply)


    def process_command(self, redis_command):
        cmd_name = redis_command[0]
        cmd = self.lookup_command(cmd_name)

        if cmd is None:
            self.logger.debug("process_command() -> command '%s' invalid in %s", cmd_name, repr(self.commands.keys()))
            return "INVALID COMMAND\n"
        else:
            ret = cmd.execute(self.store, *redis_command[1:])
            reply = repr(ret) + "\n"
            return reply


    def lookup_command(self, cmd_name):
        try:
            cmd = self.commands[cmd_name]
        except KeyError:
            return None
        else:
            return cmd


    def handle_close(self):
        self.logger.debug("handle_close()")
        self.close()
