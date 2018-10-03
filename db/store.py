import logging

class Store(object):
    def __init__(self):
        self.dict = {}
        self.logger = logging.getLogger("Store")

    def get(self, key):
        self.logger.debug("get() -> getting key '%s'", key)
        return self.dict[key]

    def set(self, key, value):
        # TODO: typecheck before setting!
        self.logger.debug("set() -> setting key-value '%s-%s'", key, value)
        self.dict[key] = value
