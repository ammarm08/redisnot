from nose.tools import assert_raises, eq_

import db.strings

"""
Tests Redis String operators.
- Arity checks
- Input validation
- Getting and setting to a stub store (a glorified Python dict)
"""

class StubStore(object):
    def __init__(self):
        self.dict = {}

    def get(self, key):
        return self.dict[key]

    def set(self, key, value):
        self.dict[key] = value

class TestStrings(object):
    # beforeEach
    def setup(self):
        self.store = StubStore()

    # get_command tests

    def test_get_missing_key_raises_key_error(self):
        with assert_raises(KeyError):
            db.strings.get_command(self.store, "Not in dict")

    def test_get_existing_key_returns_value(self):
        self.store.set("Key", "Value")

        expected = "Value"
        actual = db.strings.get_command(self.store, "Key")
        eq_(expected, actual)

    # set_command tests

    def test_set_key_returns_ok(self):
        expected = "OK"
        actual = db.strings.set_command(self.store, "Key", "Value")
        eq_(expected, actual)

    def test_sets_existing_key_returns_ok(self):
        self.store.set("Key", "oldval")

        expected = "OK"
        actual = db.strings.set_command(self.store, "Key", "newval")
        eq_(expected, actual)
