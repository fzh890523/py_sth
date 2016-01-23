# encoding: utf-8

import threading
from multiprocessing import Process
import traceback

__author__ = 'yonka'


def q_item_as_args(f, item):
    f(**item)


def q_item_as_dict(f, item):
    f(*item)


def consume_queue_in_threads(
        max_t, consume_f, q=None, is_thread=True, q_max_size=100, **kwargs):
    """
    :param item_p=q_item_as_args
    :param task_name=None
    :param do_profile=False
    """
    t_list = []
    if is_thread:
        q_cls = Queue.Queue
        t_cls = threading.Thread
    else:
        q_cls = mp_queues.JoinableQueue  # multiprocessing.Queue has no task_done method
        t_cls = Process
    if q is None:
        q = q_cls(q_max_size)

    for i in range(max_t):
        t = t_cls(target=consume_queue(consume_f, **kwargs), args=(q,))
        t.daemon = True  # 否则会在主线程/主进程退出后一直block在get queue
        t.start()
        t_list.append(t)
    return q, t_list


def consume_queue(f, item_p=q_item_as_args, task_name="consume", profile_interval=0):
    """
    :param item_p=q_item_as_args
    :param task_name=None
    :param profile_interval=0 > 0 means do profile (every this value)
    """

    def consume(q):
        consume_count = 0
        if profile_interval > 0:
            st = dt.datetime.now()
        while True:
            item = q.get()
            if item is None:  # XXX
                q.task_done()
                q.put(None)
                break
            else:
                consume_count += 1
                try:
                    item_p(f, item)
                except Exception as e:
                    sys.stderr.write("meet error: %s, when consume %s\n" % (e, item))
                    traceback.print_exc()
                finally:
                    q.task_done()
                    if profile_interval > 0 and consume_count % profile_interval == 0:
                        et = dt.datetime.now()
                        print "finish %s %s item (%s), cost %s" % (consume_count, task_name, item, et - st)
                        st = et
        if profile_interval > 0 and consume_count % profile_interval != 0:
            et = dt.datetime.now()
            print "finish %s %s item, last item is (%s), cost %s" % (consume_count, task_name, item, et - st)

    return consume


def join_threads(ts):
    for t in ts:
        t.join()