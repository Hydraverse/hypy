"""Attribute dictionary: keys are object fields.
"""
from collections import OrderedDict


class adict(dict):
    def __init__(self, *args, **kwargs):
        super(adict, self).__init__(*args, **kwargs)

    def __repr__(self):
        return f"{self.__class__.__name__}({dict.__repr__(self)})"

    def __getattr__(self, item):
        return self[item]

    def __setattr__(self, key, value):
        self[key] = value

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state):
        self.__dict = state


# NOTE: Dictionaries are ordered by default as of 3.7.
# TODO: Either wrap this or get rid of it if not truly needed.
class oadict(OrderedDict):
    def __init__(self, *args, **kwargs):
        super(oadict, self).__init__(*args, **kwargs)

    def __repr__(self):
        return f"{self.__class__.__name__}({dict.__repr__(self)})"

    def __getattr__(self, item):
        return self[item]

    def __setattr__(self, key, value):
        self[key] = value

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state):
        self.__dict = state
