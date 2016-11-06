import functools
import unittest
from typing import List

# import pygraphviz as pgv
import xlrd
from queue import Queue


class Node(object):
    def __init__(self, v, p_node=None):
        self.v = v
        self.p = p_node
        self.sons = []

    def set_parent(self, p_node):
        self.p = p_node

    def merge(self, node):
        return self

    def add_son(self, s_node):
        if not isinstance(s_node, Node):
            s_node = Node(s_node, self)
        else:
            s_node.set_parent(self)
        try:
            index = self.sons.index(s_node)
            s_node = self.sons[index].merge(s_node)
        except ValueError:
            self.sons.append(s_node)
        return s_node

    def __eq__(self, other):
        return self.v == other.v


class PathCountNode(Node):
    def __init__(self, v, p_node=None, count=1):
        super().__init__(v, p_node)
        self.count = count

    def merge(self, node):
        self.count += node.count
        return self


class Tree(object):
    def __init__(self, root_node: Node = None):
        self.root = root_node

    def set_root(self, root_node: Node):
        self.root = root_node


def add_path(trees: List[Tree], paths: List):
    if not paths:
        return
    match_tree = None
    root = None
    for tree in trees:
        root = tree.root
        if root is not None and root.v == paths[0]:
            match_tree = tree
            root.merge(PathCountNode(paths[0]))
    if match_tree is None:
        root = PathCountNode(paths[0])
        match_tree = Tree(root)
        trees.append(match_tree)
    cur_node = root
    for path in paths[1:]:
        cur_node = cur_node.add_son(PathCountNode(path))


class Event(object):
    def __init__(self, user: str, page: str, ts: int):
        self.user = user
        self.page = page
        self.ts = ts

    @classmethod
    def cmp(cls, e1, e2):
        res = (e1.user > e2.user) - (e1.user < e2.user)
        if res != 0:
            return res
        return (e1.ts > e2.ts) - (e1.ts < e2.ts)


class UserEvents(object):
    def __init__(self, user, pages: List = None):
        self.user = user
        if pages is None:
            pages = []
        self.pages = pages

    def add_pages(self, *pages):
        self.pages.extend(pages)

    @classmethod
    def user_events_generater(cls, events):
        """
        :param events: iterable which return Event
        :return:
        """
        events = sorted(events, key=functools.cmp_to_key(mycmp=Event.cmp))
        cur_user_event = None
        for event in events:
            if cur_user_event is None:
                cur_user_event = UserEvents(event.user)
            if event.user != cur_user_event.user:
                yield cur_user_event
                cur_user_event = UserEvents(event.user)
            cur_user_event.add_pages(event.page)
        if cur_user_event is not None:
            yield cur_user_event


def list_picker(l, *fields):
    res = [None] * len(fields)
    l_len = len(l)
    for i, f in enumerate(fields):
        if f < l_len:
            res[i] = l[f]
    return res


def main(args, opts):
    # open
    wb = xlrd.open_workbook(opts.excel)
    sheet = wb.sheet_by_index(opts.sheet)
    trees = process((list_picker(sheet.row_values(row_num), 1, 2, 3) for row_num in range(sheet.nrows)))
    g = graph(trees)
    g.draw("t.png")


def graph(trees):
    g = pgv.AGraph()
    q = Queue()
    for tree in trees:
        q.put(tree.root)
        g.add_node(tree.root.v, label=tree.root.count)
        while not q.empty():
            cur_node = q.get()
            for node in cur_node.sons:
                g.add_node(node.v, label=node.count)
                g.add_edge(cur_node.v, node.v, label=node.count)  # may be head/tail label
                q.put(node)
        break  # for test
    return g


def eh_enumerate(l, offset):
    l_len = len(l)
    for i in range(offset, l_len):
        yield i - offset, l[i]


def truncate_path(pages: List):
    res = []
    ok = False
    while True:
        class BreakoutException(Exception):
            pass

        try:
            for i, p in enumerate(pages):
                for j, pp in eh_enumerate(pages, i + 1):
                    if p == pp:
                        res.append(pages[:i + j + 1])
                        pages = pages[i + j + 1:]
                        raise BreakoutException()
            else:
                res.append(pages)
                ok = True
        except BreakoutException:
            pass
        if ok:
            break
    return res


def process(values):
    trees = []
    user_events_generator = UserEvents.user_events_generater((Event(*v) for v in values))
    for user_events in user_events_generator:
        paths = truncate_path(user_events.pages)
        for p in paths:
            add_path(trees, p)
    return trees


class TestB(unittest.TestCase):
    def test_main(self):
        # open
        wb = xlrd.open_workbook("t.xlsx")
        sheet = wb.sheet_by_index(0)
        trees = process((list_picker(sheet.row_values(row_num), 0, 1, 2) for row_num in range(sheet.nrows)))  # XXX
        g = graph(trees)
        g.draw("t.png")

    def test_read_excel(self):
        wb = xlrd.open_workbook("t.xlsx")
        sheet = wb.sheet_by_index(0)
        l = []
        for row_num in range(sheet.nrows):
            row = sheet.row_values(row_num)
            l.append(row)
        print(l)

    def test_eh_enumerate(self):
        for i, v in enumerate([1, 2, 3], 4):
            pass
        for i, v in enumerate([1, 2, 3], 1):
            pass

    def test_truncate_path(self):
        l = [1, 2, 3, 1, 2, 1]
        l_res = truncate_path(l)
        assert l_res == [[1,2,3], [1,2], [1]]

        l = [1, 2, 3]
        l_res = truncate_path(l)
        assert l_res == [[1,2,3]]

        l = [1, 2, 3, 1]
        l_res = truncate_path(l)
        assert l_res == [[1, 2, 3], [1]]
