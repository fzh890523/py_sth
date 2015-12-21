# encoding: utf-8

import logging
import threading
import time

__author__ = 'yonka'

logging.basicConfig(level=logging.DEBUG,format='%(asctime)s (%(threadName)-2s) %(message)s',)


def consumer(cond):
    """wait for the condition and use the resource"""
    logging.debug('Starting consumer thread')
    t = threading.currentThread()
    with cond:
        # __enter__: acquire the internal lock

        cond.wait()
        # 1. acquire to a waiter-lock specified to this current thread, add to waiters
        # 2. release and save state to tmp
        # 3. do another acquire - block or not according to timeout arg of wait method
        # 4. restore lock state to lock
        # cond内部的锁的意义就在于保证 分配waiter并添加到waiters 的操作在锁之内了
        # *?1. 为什么需要acquire两次？ --- 第一次是确保该lock已经ok了，“生产一个lock”需要一定的时间
        # ?2. 如果在2里release后其他的先restore呢？ 比当前后进入的也有可能 --- 因为先acquire and add to waiters以后才会
        # 释放 然后 waiter.acquire，而notify的实现是先入先出的release各waiter，所以... --- 还是有个问题，先被release的
        # waiter就一定先执行其 self._acquire_restore(saved_state) 吗？
        # *?3. 第一次acquire是阻塞的，那wait参数里带的timeout就没意义了 同时这一次的acquire谁来release? --- 见1

        logging.debug('Resource is available to consumer')

        # __exit__: release the internal lock


def producer(cond):
    """set up the resource to be used by the consumer"""
    logging.debug('Starting producer thread')
    with cond:
        # __enter__: acquire the internal lock

        logging.debug('Making resource available')
        cond.notifyAll()  # the wrapped lock will be released, then release all waiters
        # 1. check if own the lock
        # 2. release and remove all waiters

        # __exit__: release the internal lock


def consumer1(cond):
    """wait for the condition and use the resource"""
    logging.debug('Starting consumer thread')
    t = threading.currentThread()
    cond.wait()  # RuntimeError: cannot wait on un-acquired lock
    logging.debug('Resource is available to consumer')


def producer1(cond):
    """set up the resource to be used by the consumer"""
    logging.debug('Starting producer thread')
    with cond:
        logging.debug('Making resource available')
        cond.notifyAll()


def test1():
    condition = threading.Condition()
    c1 = threading.Thread(name='c1', target=consumer, args=(condition,))
    c2 = threading.Thread(name='c2', target=consumer, args=(condition,))
    p = threading.Thread(name='p', target=producer, args=(condition,))
    c1.start()
    time.sleep(2)
    c2.start()
    time.sleep(2)
    p.start()


def test2():
    condition = threading.Condition()
    c1 = threading.Thread(name='c1', target=consumer1, args=(condition,))
    c2 = threading.Thread(name='c2', target=consumer1, args=(condition,))
    p = threading.Thread(name='p', target=producer1, args=(condition,))
    c1.start()
    time.sleep(2)
    c2.start()
    time.sleep(2)
    p.start()


test1()
