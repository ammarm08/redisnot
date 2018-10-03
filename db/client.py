"""
client.py

The Server class delegates all socket connection handling
to the ClientHandler class.

This class reads a redis query from a readable socket connection,
then delegates the parsing and execution of the query to
resp.py and command.py, respectively.

ClientHandler receives references to the command table and logical store
from the Server that accepted the client connection.

Many of the class methods override expected methods from asyncore.dispatcher.
"""
# TODO: include asyncore.dispatcher docs

import asyncore
import socket
import logging
import resp

# 16 bytes of i/o reads at a time (redis/src/server.h)
PROTO_IOBUF_LEN = 1024*16

class ClientHandler(asyncore.dispatcher):
    """
    TODO: peek into redis's Client type definitions

    Initializes with references to the command table and logical store.
    Sets a buffer property used to maintain to send in response to client request.
    """
    def __init__(self, sock, addr, commands, store):
        asyncore.dispatcher.__init__(self, sock)
        self.logger = logging.getLogger("Client " + str(addr))

        self.commands = commands
        self.store = store
        self.buffer = []


    def writable(self):
        return bool(self.buffer)


    def handle_write(self):
        """
        TODO: peek into redis's writeToClient function

        Pops response data off the buffer and sends
        it in PROTO_IOBUF_LEN-sized chunks to the client.
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

        Consumes data in PROTO_IOBUF_LEN-sized chunks.
        Delegates to resp package to deserialize (redis protocol).
        Delegates command execution to the command table.
        Builds up reply to client after command executes.
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

        parsed = resp.decode(data)
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
        self.logger.debug("handle_close()")
        self.close()
