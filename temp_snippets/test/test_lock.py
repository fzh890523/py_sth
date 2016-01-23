# encoding: utf-8

import thread
import datetime
import threading

__author__ = 'yonka'


def test_allocate_lock():
    lk = thread.allocate_lock()
    print lk.acquire()  # output: True
    lk.acquire()  # blocked


def acquire_lock(name, lk):
    print "%s - %s - before acquire" % (datetime.datetime.now(), name)
    print "%s - %s - %s" % (datetime.datetime.now(), name, lk.acquire())
    print "%s - %s - after acquire" % (datetime.datetime.now(), name)


def test_release_unacquired_lock():
    lk = thread.allocate_lock()
    print lk.acquire()  # 如果不先require就release的话thread.error: release unlocked lock
    threading.Thread(target=acquire_lock, args=("subthread", lk)).start()
    print "%s - before release" % datetime.datetime.now()
    lk.release()
    print "%s - released" % datetime.datetime.now()
    lk.release()


if __name__ == "__main__":
    test_release_unacquired_lock()
