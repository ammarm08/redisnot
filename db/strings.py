
__all__ = [
    'get_command',
    'getset_command',
    'set_command'
]

def get_command(store, key):
    # TODO: arity checks

    # TODO: wait if key is locked. guarantee freshness
    value = store.get(key)
    return value

def getset_command(store, *args):
    # TODO: arity checks
    pass

def set_command(store, key, value):
    # TODO: arity checks

    # TODO: acquire/release locking mechanism per key
    store.set(key, value)
    return "OK"
