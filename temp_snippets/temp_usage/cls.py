# encoding: utf-8
import unittest

__author__ = 'Yonka'


class A(object):
    _d = {}


class B(A):
    def __init__(self, v):
        self.v = v
        self.__class__._d[v] = self


class C(A):
    def __init__(self, v):
        self.v = v
        self.__class__._d[v] = self


class TestCls(unittest.TestCase):
    def test_super_class_attr(self):
        B(1)
        B(2)
        C(3)
        assert len(C._d) == 3
