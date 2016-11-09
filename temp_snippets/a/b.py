import datetime
import functools
import unittest
from typing import List
import logging

# import pygraphviz as pgv
import xlrd
import pydot
import networkx as nx
from queue import Queue

from networkx.drawing.nx_pydot import graphviz_layout


class Node(object):
    def __init__(self, v, p_node=None):
        self.v = v
        self.p = p_node
        self.sons = []

    def to_json(self):
        return {
            "v": self.v,
            "sons": [s.to_json() for s in self.sons]
        }

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

    def to_json(self):
        j = super().to_json()
        j["count"] = self.count
        return j


class Tree(object):
    def __init__(self, root_node: Node = None):
        self.root = root_node

    def set_root(self, root_node: Node):
        self.root = root_node

    def to_json(self):
        return {
            "root": self.root.to_json() if self.root else None
        }


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
            break
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
    def user_events_generator(cls, events):
        """
        :param events: iterable which return Event
        :return:
        """
        events = sorted(events, key=functools.cmp_to_key(mycmp=Event.cmp))
        cur_user_event = None
        print("having finished events-sort")
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


class TreesDrawer(object):
    def graph(self, trees):
        raise NotImplementedError()


class PygraphvizTreesDrawer(TreesDrawer):
    def graph(self, trees):
        import pygraphviz as pgv
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


class GraphvizTreesDrawer(TreesDrawer):
    def graph(self, trees):
        from graphviz import Digraph
        g = []
        q = Queue()
        for tree in trees:
            cur_g = Digraph()
            q.put(tree.root)
            cur_g.node(tree.root.v, label=("%s: %d" % (tree.root.v, tree.root.count)))
            while not q.empty():
                cur_node = q.get()
                for node in cur_node.sons:
                    cur_g.node(node.v, label=("%s: %d" % (node.v, node.count)))
                    cur_g.edge(cur_node.v, node.v, weight=str(node.count), label=str(node.count))  # may be head/tail label
                    q.put(node)
            g.append(cur_g)
        return g


class NetworksTreesDrawer(TreesDrawer):
    def graph(self, trees):
        g = nx.DiGraph()
        q = Queue()
        for tree in trees:
            q.put(tree.root)
            g.add_node(tree.root.v, label=tree.root.count)
            while not q.empty():
                cur_node = q.get()
                for node in cur_node.sons:
                    g.add_node(node.v, label=node.count)
                    g.add_edge(cur_node.v, node.v, weight=node.count, label=node.count)  # may be head/tail label
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
                for j in range(i-1, -1, -1):
                    pp = pages[j]
                    if p == pp:
                        res.append(pages[:i])
                        pages = pages[i:]
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
    user_events_generator = UserEvents.user_events_generator((Event(*v) for v in values))
    for user_events in user_events_generator:
        paths = truncate_path(user_events.pages)
        for p in paths:
            add_path(trees, p)
    return trees


def main(args, opts):
    # open
    wb = xlrd.open_workbook(opts.excel)
    sheet = wb.sheet_by_index(opts.sheet)
    trees = process((list_picker(sheet.row_values(row_num), 1, 2, 3) for row_num in range(sheet.nrows)))
    # g = graph(trees)
    g.draw("t.png")


def isalnum(s: str):
    try:
        return s.encode('ascii').isalnum()
    except:
        return False


def page_converter1(page: str):
    terms = page.split("_")
    res = page
    for i, t in enumerate(reversed(terms)):
        if not isalnum(t):
            res = "_".join(terms[:len(terms) - i])
            break
    import hashlib
    res = hashlib.md5(res.encode("utf-8")).hexdigest()
    return res


def page_converter(page: str):
    terms = page.split("_")
    res = terms[0]
    import hashlib
    res = hashlib.md5(res.encode("utf-8")).hexdigest()
    return res


def main1():
    # open
    with open("C:/Users/vivian/Desktop/ccifs_672085_tahanghuankuan/hx.txt", encoding="utf-8") as f:
        def data_extractor(f):
            counter = 0
            for l in f:
                data = []
                try:
                    fields = l.split("|~|")
                    data.append(fields[0])
                    data.append(page_converter(fields[1]))
                    data.append(int(datetime.datetime.strptime(fields[2], "%Y-%m-%d %H:%M:%S\n").timestamp()))
                except Exception as e:
                    print("extra data met error, e is %s, line is %s" % (e, l))
                    continue
                yield data
                counter += 1
                if counter > 0 and counter % 1000 == 0:
                    print("having yield %d data" % counter)

        trees = process(data_extractor(f))
        # g = graph(trees)
        print("finished trees, len is %d" % len(trees))
        try:
            print("start to save trees to json")
            import json
            with open("C:/Users/vivian/Desktop/ccifs_672085_tahanghuankuan/trees.json", mode="w") as trees_json_f:
                trees_json_f.write(json.dumps([tree.to_json() for tree in trees]))
        except Exception as e:
            print(e)
        try:
            import pickle
            print("start to save trees to pickle")
            with open("C:/Users/vivian/Desktop/ccifs_672085_tahanghuankuan/trees.pickle", mode="wb") as trees_pickle_f:
                pickle.dump(trees, trees_pickle_f)
        except Exception as e:
            print(e)
        #
        # print("start to graph trees")
        # gs = GraphvizTreesDrawer().graph(trees)
        #
        # try:
        #     print("start to save graphs to dots")
        #     for i, g in enumerate(gs):
        #         g.save("C:/Users/vivian/Desktop/ccifs_672085_tahanghuankuan/dot_data_%d.dot" % i)
        # except Exception as e:
        #     print(e)
        # try:
        #     print("start to render graphs to pics")
        #     for i, g in enumerate(gs):
        #         g.render("C:/Users/vivian/Desktop/ccifs_672085_tahanghuankuan/graph_%d.pdf" % i)
        # except Exception as e:
        #     print(e)

if __name__ == "__main__":
    main1()


class TestB(unittest.TestCase):
    def test_main1(self):
        # open
        wb = xlrd.open_workbook("t.xlsx")
        sheet = wb.sheet_by_index(0)
        trees = process((list_picker(sheet.row_values(row_num), 0, 1, 2) for row_num in range(sheet.nrows)))  # XXX
        g = NetworksTreesDrawer().graph(trees)
        nx.draw(g, pos=graphviz_layout(g))
        import matplotlib.pyplot as plt
        plt.savefig("t.png")
        # g.draw("t.png")

    def test_main2(self):
        # open
        wb = xlrd.open_workbook("t.xlsx")
        sheet = wb.sheet_by_index(0)
        trees = process((list_picker(sheet.row_values(row_num), 0, 1, 2) for row_num in range(sheet.nrows)))  # XXX
        gs = GraphvizTreesDrawer().graph(trees)
        for i, g in enumerate(gs):
            g.render("graph_%d.pdf" % i)

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

        l = [1, 2, 2, 3, 1]
        l_res = truncate_path(l)
        assert l_res == [[1, 2], [2, 3, 1]]

    def test_data_extractor(self):
        s = "我们_a_1"
        assert "我们" == page_converter(s)