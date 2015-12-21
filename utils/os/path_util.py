# encoding: utf-8

import os

__author__ = 'yonka'


# 比os.path.join(p, os.path.pardir)要好
def parent_dir(p):
    return os.path.dirname(os.path.abspath(p))
