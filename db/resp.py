import logging

DELIMITER = " "
NULL = "NULL"

class RedisProto(object):

    def __init__(self):
        self.logger = logging.getLogger("Redis Proto Parser")

    def decode(self, data):
        """
        Given a redis protocol-adhering bytestream,
        parse it into a list of command tokens
        """
        # TODO: implement redis protocol
        parsed = data.split(DELIMITER)


        self.logger.debug("decode() -> '%s' to '%s'", data, repr(parsed))

        if (len(parsed) > 0):
            return parsed
        else:
            return NULL

    def encode(self, *args):
        pass
