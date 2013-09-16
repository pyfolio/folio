# -*- coding: utf-8 -*-
"""
    Helpers for Folio.
"""


class lazy_property(object):
    def __init__(self, fget):
        self.__name__ = fget.__name__
        self.__module__ = fget.__module__
        self.__doc__ = fget.__doc__
        self.fget = fget

    def __get__(self, obj, cls=None):
        if obj is None:
            return self
        val = self.fget(obj)
        obj.__dict__[self.__name__] = val
        return val
