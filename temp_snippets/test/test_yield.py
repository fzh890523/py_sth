# encoding: utf-8
import unittest

__author__ = 'yonka'


def t():
    a = 0
    print "start"
    while a < 10:
        print "yield ", str(a)
        yield a
        a += 1
        print "now a is ", str(a)


def h():
    a = 0
    cnt = 10
    print "start"
    while cnt > 0:
        print "yield "
        n = yield  # the first None will not be received
        if n is None:
            print "receive None n, return"
            return
        a += n
        print "after yield, get a n of value:", str(n)
        cnt -= 1


def do_t_test():
    """
    enter iterate of t1
    start
    yield  0
    in iterate of t1, get a of value 0
    now a is  1
    yield  1
    in iterate of t1, get a of value 1
    now a is  2
    yield  2
    in iterate of t1, get a of value 2
    now a is  3
    yield  3
    in iterate of t1, get a of value 3
    now a is  4
    yield  4
    in iterate of t1, get a of value 4
    now a is  5
    yield  5
    in iterate of t1, get a of value 5
    now a is  6
    yield  6
    in iterate of t1, get a of value 6
    now a is  7
    yield  7
    in iterate of t1, get a of value 7
    now a is  8
    yield  8
    in iterate of t1, get a of value 8
    now a is  9
    yield  9
    in iterate of t1, get a of value 9
    now a is  10
    """
    t1 = t()
    print "enter iterate of t1"
    for a in t1:
        print "in iterate of t1, get a of value", str(a)


def do_h_test():
    """
    start
    yield
    after yield, get a n of value: 2
    yield
    after yield, get a n of value: 2
    yield
    receive None n, return
     error
    """
    h1 = h()
    h1.next()  # 或者 send(None)，否则报错： TypeError: can't send non-None value to a just-started generator
    try:
        h1.send(2)
        h1.send(2)
        h1.send(None)
    except StopIteration as e:
        print e, "error"


def do_h_test1():
    """
    start
    yield
    after yield, get a n of value: 2
    yield
    after yield, get a n of value: 2
    yield
    receive None n, return
     error
    """
    h1 = h()
    h1.send(None)  # 或者 send(None)，否则报错： TypeError: can't send non-None value to a just-started generator
    try:
        h1.send(2)
        h1.send(2)
        h1.send(None)
    except StopIteration as e:
        print e, "error"


class TestYield(unittest.TestCase):

    def test_yield_once(self):
        """
        before get g
        after get g, before first next
        before yield
        after first next, before second next
        after yield

        Process finished with exit code 0

        Error
        Traceback (most recent call last):
          File "E:\yonka\git\python\yonka\py_sth\temp_snippets\test\test_yield.py", line 128, in test_yield_once
            g.next()
        StopIteration
        """
        def yield_once():
            print "before yield"
            yield 1
            print "after yield"

        print "before get g"
        g = yield_once()
        print "after get g, before first next"
        g.next()
        print "after first next, before second next"
        try:
            g.next()
            print "after second next"
        except StopIteration:
            pass
        else:
            raise AssertionError("failed as no StopIteration is met")


if __name__ == "__main__":
    do_h_test()
