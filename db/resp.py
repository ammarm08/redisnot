"""
resp.py

Implements serialization/deserialization
of a redis protocol (RESP) string.
"""


__all__ = [
    'decode',
    'encode'
]

DELIMITER = " "
NULL = "NULL"

def decode(data):
    """
    Given a redis protocol string,
    parse it into a list of command tokens
    """
    # TODO: implement redis protocol
    parsed = data.split(DELIMITER)

    if (len(parsed) > 0):
        return parsed
    else:
        return NULL


def encode(data):
    """
    Given a parsed redis command, serialize it back into
    redis-protocol string
    """
    # TODO: implement redis protocol
    serialized = DELIMITER.join(data)
    return serialized
