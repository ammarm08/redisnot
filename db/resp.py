"""
resp.py

Implements serialization/deserialization
of a redis protocol (RESP) bytestream.
"""


__all__ = [
    'decode'
]

DELIMITER = " "
NULL = "NULL"

def decode(data):
    """
    Given a redis protocol-adhering bytestream,
    parse it into a list of command tokens
    """
    # TODO: implement redis protocol
    parsed = data.split(DELIMITER)

    if (len(parsed) > 0):
        return parsed
    else:
        return NULL
