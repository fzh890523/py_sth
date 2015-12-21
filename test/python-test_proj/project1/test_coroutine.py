# encoding: utf-8

__author__ = 'yonka'

import types
from socket import socket, AF_INET, SOCK_STREAM
from Queue import Queue
import select


class Task(object):
    taskid = 0

    def __init__(self, target):
        Task.taskid += 1
        self.tid = Task.taskid
        self.target = target
        self.sendval = None
        self.stack = []

    def run(self):
        while True:
            try:
                result = self.target.send(self.sendval)
                if isinstance(result, SystemCall): return result
                if isinstance(result, types.GeneratorType):
                    self.stack.append(self.target)
                    self.sendval = None
                    self.target = result
                else:
                    if not self.stack: return
                    self.sendval = result
                    self.target = self.stack.pop()
            except StopIteration:
                if not self.stack: raise
                self.sendval = None
                self.target = self.stack.pop()


class SystemCall(object):
    """
    all system operations will be implemented by inheriting from this class
    """

    def __init__(self):
        self.task = None
        self.sched = None

    def handle(self):
        pass


class GetTid(SystemCall):
    def handle(self):
        self.task.sendval = self.task.tid
        self.sched.schedule(self.task)


class NewTask(SystemCall):
    def __init__(self, target):
        self.target = target

    def handle(self):
        tid = self.sched.new(self.target)
        self.task.sendval = tid
        self.sched.schedule(self.task)


class KillTask(SystemCall):
    def __init__(self, tid):
        self.tid = tid

    def handle(self):
        task = self.sched.taskmap.get(self.tid, None)
        if task:
            task.target.close()
            self.task.sendval = True
        else:
            self.task.sendval = False
        self.sched.schedule(self.task)


class WaitTask(SystemCall):
    def __init__(self, tid):
        self.tid = tid

    def handle(self):
        result = self.sched.wait_for_exit(self.task, self.tid)
        self.task.sendval = result
        if not result:
            self.sched.schedule(self.task)


class ReadWait(SystemCall):
    def __init__(self, f):
        self.f = f

    def handle(self):
        fd = self.f.fileno()
        self.sched.wait_for_read(self.task, fd)


class WriteWait(SystemCall):
    def __init__(self, f):
        self.f = f

    def handle(self):
        fd = self.f.fileno()
        self.sched.wait_for_write(self.task, fd)


class Socket(object):
    def __init__(self, sock):
        self.sock = sock

    def accept(self):
        yield ReadWait(self.sock)
        client, addr = self.sock.accept()
        yield Socket(client), addr

    def send(self, buffer):
        while buffer:
            yield WriteWait(self.sock)
            len = self.socket.send(buffer)
            buffer = buffer[len:]

    def recv(self, max_bytes):
        yield ReadWait(self.sock)
        yield self.sock.recv(max_bytes)

    def close(self):
        yield self.sock.close()


class Scheduler(object):
    def __init__(self):
        self.ready = Queue()
        self.taskmap = {}
        self.exit_waiting = {}
        self.read_waiting = {}
        self.write_waiting = {}


    def new(self, target):
        newtask = Task(target)
        self.taskmap[newtask.tid] = newtask
        self.schedule(newtask)
        return newtask.tid

    def exit(self, task):
        print "Task %d terminated" % task.tid
        del self.taskmap[task.tid]
        for task in self.exit_waiting.pop(task.tid, []):
            self.schedule(task)

    def schedule(self, task):
        self.ready.put(task)

    def wait_for_exit(self, task, wait_tid):
        if wait_tid in self.taskmap:
            self.exit_waiting.set_default(wait_tid, []).append(task)
            return True
        else:
            return False

    def wait_for_read(self, task, fd):
        self.read_waiting[fd] = task

    def wait_for_write(self, task, fd):
        self.write_waiting[fd] = task

    def io_poll(self, timeout):
        if self.read_waiting or self.write_waiting:
            r, w, e = select.select(self.read_waiting, self.write_waiting, [], timeout)
            for fd in r:
                self.schedule(self.read_waiting.pop(fd))
            for fd in w:
                self.schedule(self.write_waiting.pop(fd))

    def io_task(self):
        while True:
            if self.ready.empty():
                self.io_poll(None)
            else:
                self.io_poll(0)
            yield

    def mainloop(self):
        # self.new(self.io_task())  # 也可以这样把io polling放到单独的任务
        while self.taskmap:
            self.io_poll(0)
            task = self.ready.get()
            try:
                result = task.run()
                if isinstance(result, SystemCall):
                    # record the task and scheduler to system call
                    result.task = task
                    result.sched = self
                    result.handle()
                    continue
            except StopIteration:
                self.exit(task)
                continue
            self.schedule(task)


def foo():
    mytid = yield GetTid()
    for i in xrange(5):
        print "i'm foo, %s" % mytid
        yield


def bar():
    mytid = yield GetTid()
    for i in xrange(10):
        print "i'm bar, %s" % mytid
        yield


def bar1():
    while True:
        print "i'm bar1"
        yield


def sometask():
    # ...
    t1 = yield NewTask(bar1())
    # ...
    yield KillTask(t1)


def main():
    child = yield NewTask(foo())
    for i in xrange(5):
        yield
    yield KillTask(child)
    print "main done"


def handle_client(client, addr):
    print "connection from ", addr
    while True:
        data = yield client.recv(65536)
        if not data:
            break
        print "Client closed"
        yield client.close()


def server(port):
    print "Server starting"
    raw_sock = socket(AF_INET, SOCK_STREAM)
    raw_sock.bind(("", port))
    raw_sock.listen(5)
    sock = Socket(raw_sock)
    while True:
        client, addr = yield sock.accept()
        yield NewTask(handle_client(client, addr))


sched = Scheduler()
# sched.new(foo())
# sched.new(bar())
sched.new(server(8811))
sched.mainloop()


