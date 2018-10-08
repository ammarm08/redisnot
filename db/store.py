"""
store.py

The logical core of the redisnot data store.
Exposes a simple 'get' and 'set' interface.
"""

import logging

class Store(object):
    def __init__(self):
        self.logger = logging.getLogger("Store")
        self.dict = {}

    def get(self, key):
        self.logger.debug("get() -> getting key '%s'", key)
        return self.dict[key]

    def set(self, key, value):
        # TODO: typecheck before setting!
        self.logger.debug("set() -> setting key:value '%s:%s'", key, value)
        self.dict[key] = value
