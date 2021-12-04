"""Attribute dictionary: keys are object fields.
"""
from collections import namedtuple
from functools import reduce
import keyword


def namefor(key: str):
    key = key.replace('-', '_').replace(' ', '_')

    if keyword.iskeyword(key):
        key += "_"

    return key


def dictuple(name: str, dic: dict):
    return namedtuple(name, (namefor(k) for k in dic.keys()))(
        *(
            [dictuple(f"{name}_{k}_{i}", vi) for i, vi in enumerate(v)]
            if (isinstance(v, (list, tuple)) and reduce(lambda i, j: i and isinstance(j, dict), v, True)) else
            (v if not isinstance(v, dict) else dictuple(k, v)) for (k, v) in dic.items()
        )
    )
