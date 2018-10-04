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
# TODO: explore better ways to handle large reads.
# TODO: check out asyncio and if it is better than asyncore

import asyncore
import socket
import logging
import resp

# 16 kb of i/o reads at a time (redis/src/server.h)
PROTO_IOBUF_LEN = 1024*16

class ClientHandler(asyncore.dispatcher):
    """
    TODO: peek into redis's Client type definitions

    Initializes with references to the command table and logical store.
    Sets buffers used to consume requests and build responses.
    """
    def __init__(self, sock, addr, commands, store):
        asyncore.dispatcher.__init__(self, sock)
        self.logger = logging.getLogger("Client " + str(addr))

        self.commands = commands
        self.store = store
        self.query_buffer = b""
        self.reply_buffer = []


    def writable(self):
        return bool(self.reply_buffer)


    def handle_write(self):
        """
        TODO: peek into redis's writeToClient function

        Pops response data off the buffer and sends
        it in PROTO_IOBUF_LEN-sized chunks to the client.
        """
        data = self.reply_buffer.pop()
        sent = self.send(data[:PROTO_IOBUF_LEN])
        if sent < len(data):
            remaining = data[sent:]
            self.reply_buffer.append(remaining)

        self.logger.debug("handle_write() -> (%d) '%s'", sent, data[:sent].rstrip())


    def handle_read(self):
        """
        TODO: peek into redis's readQueryFromClient function

        Consumes data in PROTO_IOBUF_LEN-sized chunks.
        Delegates to resp package to deserialize (redis protocol).
        Delegates command execution to the command table.
        Builds up reply to client after command executes.
        """
        try:
            self.logger.debug("handle_read() -> entering read")
            received = self.recv(PROTO_IOBUF_LEN)
        except Exception as e:
            self.logger.debug("handle_read() -> %s", e)
            return self.close()

        self.query_buffer += received
        self.logger.debug("handle_read() -> finished reading, (%d) %s", len(received), self.query_buffer)

        # when no more data to read, parse and execute command
        if len(received) < PROTO_IOBUF_LEN:
            data = self.query_buffer.rstrip()
            self.query_buffer = b""
            self.logger.debug("handle_read() -> (%d) '%s'", len(data), data)

            parsed = resp.decode(data)
            reply = self.call_command(parsed)
            self.reply_buffer.insert(0, reply)


    def call_command(self, command_group):
        cmd_name = command_group[0]

        try:
            cmd = self.commands[cmd_name]
        except:
            self.logger.debug("call_command() -> command '%s' invalid in %s", cmd_name, repr(self.commands.keys()))
            return "INVALID COMMAND\n"
        else:
            ret = cmd.execute(self.store, *command_group[1:])
            reply = repr(ret) + "\n"
            return reply


    def handle_close(self):
        self.logger.debug("handle_close()")
        self.close()
