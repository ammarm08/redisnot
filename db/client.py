"""
client.py

The Server class delegates all socket connection handling
to the ClientHandler class.

This class reads a redis query from a readable socket connection,
then delegates the parsing and execution of the query to
resp.py and command.py, respectively.

ClientHandler receives references to the command table, store, and AOF
from the Server that accepted the client connection.

Many of the class methods override expected methods from asynchat:

"ac_*_buffer_size" methods dictate the buffer_size for reading and writing.
"collect_incoming_data" dictates what to do when a new chunk of data comes in.
"*_terminator" methods dictate how to delimit incoming data into separate messages.
"""

import asynchat
import logging
import resp

# 16 kb of i/o reads at a time (redis/src/server.h)
PROTO_IOBUF_LEN = 1024*16

class ClientHandler(asynchat.async_chat):
    """
    Initializes with references to the command table, store, and aof.
    Sets buffers used to consume requests and build responses.
    """

    ac_in_buffer_size = PROTO_IOBUF_LEN
    ac_out_buffer_size = PROTO_IOBUF_LEN


    def __init__(self, sock=None, addr=None, map={}, commands={}, store=None, aof=None):
        asynchat.async_chat.__init__(self, sock=sock, map=map)
        self.logger = logging.getLogger("Client " + str(addr))

        self.commands = commands
        self.store = store
        self.aof = aof

        # incoming data collects into this buffer
        self.query_buffer = []

        # readstream consumes data on channel until newline char
        self.set_terminator("\n")


    def collect_incoming_data(self, data):
        """
        Buffer up incoming data
        """
        self.logger.debug("collect_incoming_data() -> entering read of %s", data)
        self.query_buffer.append(data)


    def found_terminator(self):
        """
        Clear the buffer, decode and process the request.
        Send reply back to client.
        """

        # the contents of the query buffer denote one complete message.
        # let's handle it and reset the buffer.
        data = "".join(self.query_buffer).rstrip()
        self.query_buffer = []
        self.logger.debug("found_terminator() -> (%d) '%s'", len(data), data)

        # decode the client request and then process the redis command
        redis_command = resp.decode(data)
        reply = self.process_command(redis_command)

        # push the resulting reply onto the write-stream
        self.push(reply)


    def process_command(self, redis_command):
        """
        Execute the command, writing the return value
        to the in-memory dict and the command to aof if necessary
        """
        
        # make sure the command exists
        cmd_name = redis_command[0]
        cmd = self.lookup_command(cmd_name)
        if cmd is None:
            self.logger.debug("process_command() -> command '%s' invalid in %s", cmd_name, repr(self.commands.keys()))
            return "INVALID COMMAND\n"

        # if command exists, execute it
        cmd_args = redis_command[1:]
        ret = cmd.execute(self.store, *cmd_args)

        # only write-commands get appended
        if cmd.aof == True:
            self.aof.append(redis_command)

        # finally, construct reply to client
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
